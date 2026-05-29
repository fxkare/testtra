# Hizli Ceviri

Windows ve Linux masaustu icin hizli Turkce ceviri araci.

Uygulama arka planda calisir, secili metni kopyalar ve `Ctrl + Alt + Space`
kisayolu ile Turkce ceviri penceresini acar. Ayrica sistem tepsisi simgesi ve
secimden sonra gorunen kucuk ceviri butonu vardir.

## Platform Notlari

- Windows destegi mevcut haliyle korunur.
- Linux destegi X11 oturumlari icin hedeflenmistir.
- Wayland oturumlarinda global hotkey, fare dinleme ve Ctrl+C simule etme
  compositor guvenlik politikalarina baglidir. Sorun yasanirsa Xorg oturumu
  kullanin veya masaustu kisa yol sisteminden uygulamayi cagirin.

## Windows Kurulum

Python 3.13 ile test edildi.

```powershell
python -m pip install -r requirements.txt
python translator_app.py
```

## Windows EXE Derleme

```powershell
python -m pip install pyinstaller
python -m PyInstaller --noconfirm --clean --noconsole --onefile --name HizliCeviri --collect-all customtkinter translator_app.py
```

Derlenen dosya:

```text
dist\HizliCeviri.exe
```

## Linux Sistem Paketleri

Debian/Ubuntu tabanli dagitimlar:

```bash
sudo apt install python3 python3-venv python3-tk xclip
```

Fedora:

```bash
sudo dnf install python3 python3-tkinter xclip
```

Arch:

```bash
sudo pacman -S python tk xclip
```

`pyperclip` pano erisimi icin `xclip` veya `xsel` kullanabilir. Wayland
oturumlarinda `wl-clipboard` gerekebilir, fakat global hotkey destegi yine
masaustu ortamindan etkilenir.

## Linux Calistirma

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements-linux.txt
python translator_app.py
```

## Linux Binary Derleme

Linux binary Linux uzerinde derlenmelidir; Windows uzerinden Linux binary
cross-compile edilmez.

```bash
chmod +x scripts/build_linux.sh
scripts/build_linux.sh
```

Derlenen dosya:

```text
dist/HizliCeviri
```

## Linux Baslangicta Calistirma

Binary derlendikten sonra:

```bash
chmod +x scripts/install_linux_autostart.sh
scripts/install_linux_autostart.sh
```

Bu komut kullanici autostart dosyasini olusturur:

```text
~/.config/autostart/hizli-ceviri.desktop
```

## Notlar

- Ceviri icin internet baglantisi gerekir.
- Global klavye/fare dinleyicileri nedeniyle masaustu oturumu gerekir.
- Uygulama tek kopya calisacak sekilde korunur.
