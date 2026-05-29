import time
import threading
import ctypes
import sys
import keyboard
import pyperclip
import customtkinter as ctk
from deep_translator import GoogleTranslator
import pystray
from PIL import Image, ImageDraw
from pynput import mouse

# Uygulama için varsayılan kısayol
HOTKEY = 'ctrl+alt+space'
MUTEX_NAME = "Global\\HizliCeviriTranslatorApp"


def ensure_single_instance():
    mutex = ctypes.windll.kernel32.CreateMutexW(None, False, MUTEX_NAME)
    if ctypes.windll.kernel32.GetLastError() == 183:
        sys.exit(0)
    return mutex

class TranslatorApp:
    def __init__(self):
        self.root = None
        self.tray_icon = None
        self.is_running = True
        
        # Sürükleme (Drag) koordinatları (Ana pencere için)
        self.x_offset = 0
        self.y_offset = 0
        
        # Yüzen buton (Floating Button) ve seçim değişkenleri
        self.drag_start_x = 0
        self.drag_start_y = 0
        self.drag_start_time = 0
        self.last_click_time = 0
        self.float_btn_window = None
        self.last_selected_text = ""
        
        print("Hızlı Çeviri başlatılıyor...")
        
        # 1. Hotkey'i kaydet (Klavyeden tetikleme için)
        keyboard.add_hotkey(HOTKEY, self.on_hotkey_pressed)
        
        # 2. Fare dinleyicisini başlat (Seçim tespiti ve dışarı tıklama kontrolü için)
        self.mouse_listener = mouse.Listener(on_click=self.on_mouse_click)
        self.mouse_listener.start()
        
        # Arayüzü kur
        self.init_ui()

    def init_ui(self):
        # Arayüz (UI) hazırlığı
        ctk.set_appearance_mode("Dark")  # Daha modern görünüm için varsayılan olarak Dark mod
        ctk.set_default_color_theme("blue")
        
        self.root = ctk.CTk()
        self.root.title("Anında Çeviri")
        self.root.geometry("500x370")
        
        # Pencereyi her zaman en üstte tut ve title bar'ı kaldırarak modern bir kutu görünümü sağla
        self.root.attributes("-topmost", True)
        self.root.overrideredirect(True)
        
        self.center_window(500, 370)
        
        # Ana frame
        self.frame = ctk.CTkFrame(self.root, corner_radius=15, border_width=2, border_color="#3a7ebf")
        self.frame.pack(pady=5, padx=5, fill="both", expand=True)
        
        # Başlık ve Kapatma Butonu
        self.header_frame = ctk.CTkFrame(self.frame, fg_color="transparent")
        self.header_frame.pack(fill="x", padx=10, pady=(10, 0))
        
        self.title_label = ctk.CTkLabel(self.header_frame, text="Hızlı Çeviri", font=ctk.CTkFont(size=16, weight="bold"))
        self.title_label.pack(side="left")
        
        self.close_btn = ctk.CTkButton(self.header_frame, text="Kapat (ESC)", width=80, height=28, corner_radius=15, 
                                       command=self.hide_window, fg_color="#c42b2b", hover_color="#ff5c5c", text_color="white")
        self.close_btn.pack(side="right")
        
        # Sürükleme fonksiyonlarını bağla (Pencereyi başlığından tutup taşıyabilmek için)
        self.header_frame.bind("<Button-1>", self.start_drag)
        self.header_frame.bind("<B1-Motion>", self.drag_window)
        self.title_label.bind("<Button-1>", self.start_drag)
        self.title_label.bind("<B1-Motion>", self.drag_window)
        
        # Orijinal metin alanı
        self.lbl_original = ctk.CTkLabel(self.frame, text="Orijinal:", font=ctk.CTkFont(size=12, weight="bold"))
        self.lbl_original.pack(anchor="w", padx=15, pady=(10, 0))
        
        self.txt_original = ctk.CTkTextbox(self.frame, height=80, wrap="word", corner_radius=10)
        self.txt_original.pack(fill="x", padx=15, pady=(5, 10))
        
        # Çeviri alanı başlığı ve "Kopyala" Butonu içeren frame
        self.translated_header_frame = ctk.CTkFrame(self.frame, fg_color="transparent")
        self.translated_header_frame.pack(fill="x", padx=15, pady=(5, 0))
        
        self.lbl_translated = ctk.CTkLabel(self.translated_header_frame, text="Çeviri (Türkçe):", font=ctk.CTkFont(size=12, weight="bold"))
        self.lbl_translated.pack(side="left")
        
        self.copy_btn = ctk.CTkButton(self.translated_header_frame, text="Çeviriyi Kopyala", width=120, height=24, corner_radius=10,
                                      command=self.copy_translation, fg_color="#2b5c8f", hover_color="#3a7ebf")
        self.copy_btn.pack(side="right")
        
        # Çeviri metin kutusu
        self.txt_translated = ctk.CTkTextbox(self.frame, height=110, wrap="word", corner_radius=10, 
                                             fg_color="#183d2e", text_color="white")
        self.txt_translated.pack(fill="x", padx=15, pady=(5, 15))
        
        # ESC tuşuyla pencereyi gizle
        self.root.bind("<Escape>", lambda e: self.hide_window())
        
        # Pencere dışında bir yere odaklanıldığında gizle (FocusOut)
        self.root.bind("<FocusOut>", self.on_focus_out)
        
        # Pencere başlangıçta gizli
        self.root.withdraw()
        
        # Sistem tepsisi simgesini başlat
        self.setup_tray()
        
        print(f"Uygulama arka planda hazır! Bir metin seçin ve '{HOTKEY}' tuşlarına basın.")
        print("Fare ile metin veya paragraf seçtiğinizde de yanınızda küçük bir Çeviri butonu belirecektir.")
        
        # Arayüz döngüsü başlatılıyor
        try:
            self.root.mainloop()
        except KeyboardInterrupt:
            self.quit_app()

    def center_window(self, width, height):
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        x = int((screen_width / 2) - (width / 2))
        y = int((screen_height / 2) - (height / 2))
        self.root.geometry(f'{width}x{height}+{x}+{y}')

    # Sürükle-bırak ile pencere taşıma
    def start_drag(self, event):
        self.x_offset = event.x
        self.y_offset = event.y

    def drag_window(self, event):
        x = self.root.winfo_x() + event.x - self.x_offset
        y = self.root.winfo_y() + event.y - self.y_offset
        self.root.geometry(f"+{x}+{y}")

    def hide_window(self):
        self.root.withdraw()

    def show_window(self, original_text, translated_text):
        # Arayüz elemanlarını güncelle
        self.txt_original.configure(state="normal")
        self.txt_original.delete("1.0", "end")
        self.txt_original.insert("1.0", original_text)
        self.txt_original.configure(state="disabled")
        
        self.txt_translated.configure(state="normal")
        self.txt_translated.delete("1.0", "end")
        self.txt_translated.insert("1.0", translated_text)
        self.txt_translated.configure(state="disabled")
        
        # Kopyala butonunu sıfırla
        self.copy_btn.configure(text="Çeviriyi Kopyala", fg_color="#2b5c8f")
        
        # Pencereyi ekranın ortasında göster
        self.center_window(500, 370)
        self.root.deiconify()
        self.root.attributes("-topmost", True)
        self.root.focus_force()

    def copy_translation(self):
        translated_text = self.txt_translated.get("1.0", "end-1c")
        if translated_text and "Hata:" not in translated_text and "Bağlantı hatası" not in translated_text:
            pyperclip.copy(translated_text)
            self.copy_btn.configure(text="Kopyalandı!", fg_color="#183d2e")
            self.root.after(1500, lambda: self.copy_btn.configure(text="Çeviriyi Kopyala", fg_color="#2b5c8f"))

    def on_focus_out(self, event):
        # Focus kaybını kontrol etmek için kısa bir bekleme (odaklanma geçişleri için)
        self.root.after(100, self._check_focus)

    def _check_focus(self):
        # Eğer odaklanan widget bizim uygulamamızda değilse (None dönerse), pencereyi gizle
        if self.root and self.root.focus_get() is None:
            self.hide_window()

    # Çeviri yap ve göster
    def translate_and_show(self, text_to_translate):
        def _thread_job():
            try:
                try:
                    translator = GoogleTranslator(source='auto', target='tr')
                    translated_text = translator.translate(text_to_translate)
                except Exception as conn_error:
                    translated_text = f"Bağlantı Hatası: Çeviri yapılamadı.\nLütfen internet bağlantınızı kontrol edin.\n({conn_error})"
                
                # Arayüzü güncelle
                self.root.after(0, self.show_window, text_to_translate, translated_text)
            except Exception as e:
                print(f"Çeviri hatası: {e}")
                
        threading.Thread(target=_thread_job, daemon=True).start()

    # Kısayol tetiklendiğinde çalışan fonksiyon
    def process_translation(self):
        try:
            # 1. Mevcut panodaki veriyi yedekle
            try:
                original_clipboard = pyperclip.paste()
            except Exception:
                original_clipboard = ""
            
            # 2. Seçili metni kopyalamak için Ctrl+C simüle et
            keyboard.release('ctrl')
            keyboard.release('alt')
            keyboard.release('t')
            time.sleep(0.05)
            
            keyboard.send('ctrl+c')
            time.sleep(0.15) # Kopyalama işleminin panoya yansıması için bekle
            
            # 3. Kopyalanan seçili metni al
            text_to_translate = pyperclip.paste().strip()
            
            # 4. Orijinal panoyu geri yükle
            if original_clipboard:
                try:
                    pyperclip.copy(original_clipboard)
                except Exception:
                    pass

            if not text_to_translate:
                return

            self.translate_and_show(text_to_translate)
            
        except Exception as e:
            print(f"Çeviri işlem hatası: {e}")

    def on_hotkey_pressed(self):
        # Arayüzün donmasını engellemek için işlemi arka planda çalıştır
        threading.Thread(target=self.process_translation, daemon=True).start()

    # Fare dinleyicisi olayları
    def on_mouse_click(self, x, y, button, pressed):
        # 1. Sol tık basıldı/bırakıldı (Sürükleme veya Çift/Üçlü tıklama tespiti)
        if button == mouse.Button.left:
            if pressed:
                self.drag_start_x = x
                self.drag_start_y = y
                self.drag_start_time = time.time()
            else:
                # Sol tık bırakıldı
                dx = abs(x - self.drag_start_x)
                dy = abs(y - self.drag_start_y)
                dt = time.time() - self.drag_start_time
                
                # Çift veya üçlü tıklama tespiti (Çift tıklama 350ms içinde yapılır)
                current_time = time.time()
                is_double_click = False
                if current_time - self.last_click_time < 0.35:
                    is_double_click = True
                self.last_click_time = current_time
                
                # Eğer belirgin sürükleme varsa veya çift/üçlü tıklama olduysa tetikle
                if (dx > 8 or dy > 8) or is_double_click:
                    # Seçimi arka planda kontrol et
                    threading.Thread(target=self.check_selection, args=(x, y), daemon=True).start()

        # 2. Yüzen buton açıkken dışarıya tıklanırsa kapatma
        if pressed and self.float_btn_window:
            try:
                bx = self.float_btn_window.winfo_x()
                by = self.float_btn_window.winfo_y()
                bw = self.float_btn_window.winfo_width()
                bh = self.float_btn_window.winfo_height()
                
                # Eğer tıklama buton sınırlarının dışındaysa kapat
                if not (bx <= x <= bx + bw and by <= y <= by + bh):
                    self.root.after(0, self.hide_float_button)
            except Exception:
                pass

    # Seçilen metni belirle ve yüzen butonu tetikle
    def check_selection(self, x, y):
        # İşletim sisteminin seçimi tamamlaması için kısa bir bekleme
        time.sleep(0.08)
        try:
            # 1. Pano yedekleme
            try:
                original_clipboard = pyperclip.paste()
            except Exception:
                original_clipboard = ""
            
            # 2. Panoyu geçici olarak temizle
            try:
                pyperclip.copy("")
            except Exception:
                pass
                
            # 3. Ctrl+C göndererek kopyalamayı tetikle
            keyboard.release('ctrl')
            keyboard.release('shift')
            keyboard.release('alt')
            keyboard.send('ctrl+c')
            
            # 4. Kopyalamanın gerçekleşmesini bekle (maksimum 250ms boyunca sorgula)
            selected_text = ""
            start_poll = time.time()
            while time.time() - start_poll < 0.25:
                try:
                    txt = pyperclip.paste().strip()
                    if txt != "":
                        selected_text = txt
                        break
                except Exception:
                    pass
                time.sleep(0.02)
            
            # 5. Panoyu hemen eski haline geri yükle (Kullanıcı verisi bozulmasın)
            if original_clipboard:
                try:
                    pyperclip.copy(original_clipboard)
                except Exception:
                    pass
            else:
                try:
                    pyperclip.copy("")
                except Exception:
                    pass
            
            # Eğer seçilen metin anlamlı uzunluktaysa yüzen butonu göster
            if selected_text and len(selected_text) > 1:
                self.root.after(0, self.show_float_button, x, y, selected_text)
                
        except Exception as e:
            print(f"Seçim kontrol hatası: {e}")

    # Yüzen butonu (floating button) göster
    def show_float_button(self, x, y, text):
        self.hide_float_button() # Zaten varsa eskisini kapat
        
        self.last_selected_text = text
        
        # CTkToplevel kullanarak çerçevesiz küçük bir buton penceresi yarat (Typo düzeltildi!)
        self.float_btn_window = ctk.CTkToplevel(self.root)
        self.float_btn_window.overrideredirect(True)
        self.float_btn_window.attributes("-topmost", True)
        
        width = 80
        height = 30
        # Butonu imlecin hafif sağına ve altına yerleştir
        self.float_btn_window.geometry(f"{width}x{height}+{x+15}+{y+15}")
        
        # Çeviri Butonu
        btn = ctk.CTkButton(
            self.float_btn_window, 
            text="Çevir", 
            width=width, 
            height=height, 
            corner_radius=8,
            command=self.on_float_click,
            fg_color="#3a7ebf",
            hover_color="#2b5c8f",
            font=ctk.CTkFont(size=12, weight="bold")
        )
        btn.pack(fill="both", expand=True)
        
        # Fare uzaklaşma kontrolünü başlat
        self.check_distance()

    # Yüzen butona tıklanma olayı
    def on_float_click(self):
        text = self.last_selected_text
        self.hide_float_button()
        if text:
            self.translate_and_show(text)

    # Yüzen butonu gizle
    def hide_float_button(self):
        if self.float_btn_window:
            try:
                self.float_btn_window.destroy()
            except Exception:
                pass
            self.float_btn_window = None

    # Farenin butondan uzaklaşıp uzaklaşmadığını kontrol et
    def check_distance(self):
        if not self.float_btn_window:
            return
        try:
            mx, my = self.root.winfo_pointerxy()
            bx = self.float_btn_window.winfo_x() + 40
            by = self.float_btn_window.winfo_y() + 15
            dist = ((mx - bx)**2 + (my - by)**2)**0.5
            
            # Fare 150 pikselden fazla uzaklaşırsa butonu gizle
            if dist > 150:
                self.hide_float_button()
            else:
                self.root.after(200, self.check_distance)
        except Exception:
            pass

    def setup_tray(self):
        # Sistem tepsisi simgesi çiz
        image = Image.new('RGB', (64, 64), color=(30, 30, 30))
        draw = ImageDraw.Draw(image)
        draw.ellipse([8, 8, 56, 56], fill="#3a7ebf", outline="white", width=4)
        draw.line([32, 8, 32, 56], fill="white", width=3)
        draw.line([8, 32, 56, 32], fill="white", width=3)
        
        menu = pystray.Menu(
            pystray.MenuItem("Göster", self.show_window_from_tray),
            pystray.MenuItem("Çıkış", self.quit_app)
        )
        
        self.tray_icon = pystray.Icon("hizli_ceviri", image, "Hızlı Çeviri", menu)
        threading.Thread(target=self.tray_icon.run, daemon=True).start()

    def show_window_from_tray(self):
        self.root.after(0, self.show_window, 
                        "Bir metin seçip Ctrl+Alt+T tuşlarına basın veya metni sürükleyip Çevir butonunu tıklayın.", 
                        "Sistem tepsisinden manuel olarak açıldı. Çeviri sistemi aktif olarak arka planda beklemektedir.")

    def quit_app(self):
        self.is_running = False
        keyboard.unhook_all()
        if self.mouse_listener:
            self.mouse_listener.stop()
        if self.tray_icon:
            self.tray_icon.stop()
        self.hide_float_button()
        if self.root:
            self.root.after(0, self.root.destroy)

if __name__ == "__main__":
    app_mutex = ensure_single_instance()
    app = TranslatorApp()
