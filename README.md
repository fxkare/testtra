# Hizli Ceviri

Windows masaustu icin hizli Turkce ceviri araci.

Uygulama arka planda calisir, secili metni kopyalar ve `Ctrl + Alt + Space`
kisayolu ile Turkce ceviri penceresini acar. Ayrica sistem tepsisi simgesi ve
secimden sonra gorunen kucuk ceviri butonu vardir.

## Kurulum

Python 3.13 ile test edildi.

```powershell
python -m pip install -r requirements.txt
```

## Calistirma

```powershell
python translator_app.py
```

## EXE Derleme

```powershell
python -m pip install pyinstaller
python -m PyInstaller --noconfirm --clean --noconsole --onefile --name HizliCeviri --collect-all customtkinter translator_app.py
```

Derlenen dosya:

```text
dist\HizliCeviri.exe
```

## Windows Baslangicinda Calistirma

`dist\HizliCeviri.exe` icin Windows Startup klasorune kisayol eklenebilir:

```text
%APPDATA%\Microsoft\Windows\Start Menu\Programs\Startup
```

## Notlar

- Ceviri icin internet baglantisi gerekir.
- Global klavye/fare dinleyicileri nedeniyle masaustu oturumu gerekir.
- Uygulama tek kopya calisacak sekilde korunur.
