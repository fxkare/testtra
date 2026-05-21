import time
import threading
import keyboard
import pyperclip
import customtkinter as ctk
from deep_translator import GoogleTranslator
import pystray
from PIL import Image, ImageDraw

# Uygulama için varsayılan kısayol
HOTKEY = 'ctrl+alt+t'

class TranslatorApp:
    def __init__(self):
        self.root = None
        self.tray_icon = None
        self.is_running = True
        
        # Sürükleme (Drag) koordinatları
        self.x_offset = 0
        self.y_offset = 0
        
        print("Hızlı Çeviri başlatılıyor...")
        
        # Hotkey'i kaydet (keyboard kütüphanesi arka planda asenkron çalışır)
        keyboard.add_hotkey(HOTKEY, self.on_hotkey_pressed)
        
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

    def process_translation(self):
        # Kısayol tetiklendiğinde arka plan thread'inde çalışır
        try:
            # 1. Mevcut panodaki (clipboard) veriyi yedekle
            try:
                original_clipboard = pyperclip.paste()
            except Exception:
                original_clipboard = ""
            
            # 2. Seçili metni kopyalamak için Ctrl+C simüle et
            # Kısayol tuşlarının serbest kalmasını bekle
            keyboard.release('ctrl')
            keyboard.release('alt')
            keyboard.release('t')
            time.sleep(0.05)
            
            keyboard.send('ctrl+c')
            time.sleep(0.15) # Kopyalama işleminin panoya yansıması için bekle
            
            # 3. Kopyalanan seçili metni al
            text_to_translate = pyperclip.paste().strip()
            
            # 4. Orijinal panoyu anında geri yükle (Kullanıcının verisi kaybolmasın)
            if original_clipboard:
                try:
                    pyperclip.copy(original_clipboard)
                except Exception:
                    pass

            if not text_to_translate:
                # Çevrilecek metin yoksa pencere açma
                return

            # 5. Çeviri yap (İnternet/Bağlantı hatası kontrolü ile)
            try:
                translator = GoogleTranslator(source='auto', target='tr')
                translated_text = translator.translate(text_to_translate)
            except Exception as conn_error:
                translated_text = f"Bağlantı Hatası: Çeviri yapılamadı.\nLütfen internet bağlantınızı kontrol edin.\n({conn_error})"
            
            # 6. Arayüzü ana thread'de güncelle
            self.root.after(0, self.show_window, text_to_translate, translated_text)
            
        except Exception as e:
            print(f"Çeviri işlem hatası: {e}")

    def on_hotkey_pressed(self):
        # Arayüzün donmasını engellemek için işlemi arka planda çalıştır
        threading.Thread(target=self.process_translation, daemon=True).start()

    def setup_tray(self):
        # 64x64 boyutunda sistem tepsisi ikonu çizelim (Dünya simgesi benzeri)
        image = Image.new('RGB', (64, 64), color=(30, 30, 30))
        draw = ImageDraw.Draw(image)
        draw.ellipse([8, 8, 56, 56], fill="#3a7ebf", outline="white", width=4)
        draw.line([32, 8, 32, 56], fill="white", width=3)
        draw.line([8, 32, 56, 32], fill="white", width=3)
        
        # Sağ tık menüsü
        menu = pystray.Menu(
            pystray.MenuItem("Göster", self.show_window_from_tray),
            pystray.MenuItem("Çıkış", self.quit_app)
        )
        
        self.tray_icon = pystray.Icon("hizli_ceviri", image, "Hızlı Çeviri", menu)
        threading.Thread(target=self.tray_icon.run, daemon=True).start()

    def show_window_from_tray(self):
        # Sistem tepsisinden manuel açıldığında bilgilendirme metni göster
        self.root.after(0, self.show_window, 
                        "Bir metin seçip Ctrl+Alt+T tuşlarına basın.", 
                        "Sistem tepsisinden manuel olarak açıldı. Çeviri sistemi aktif olarak arka planda beklemektedir.")

    def quit_app(self):
        self.is_running = False
        keyboard.unhook_all()
        if self.tray_icon:
            self.tray_icon.stop()
        if self.root:
            self.root.after(0, self.root.destroy)

if __name__ == "__main__":
    app = TranslatorApp()
