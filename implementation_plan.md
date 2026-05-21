# Hızlı Çeviri (Instant Translation) Uygulaması

Kopyaladığınız veya seçtiğiniz metinleri anında Türkçe'ye çevirip şık bir açılır pencerede (popup) gösteren, arka planda çalışan bir masaüstü uygulaması geliştireceğiz.

## Önerilen Çözüm ve Teknolojiler

En etkili ve performanslı çözüm için **Python** kullanılacaktır. Web teknolojilerine kıyasla, işletim sisteminin panosuna (clipboard) ve küresel klavye kısayollarına (global hotkeys) doğrudan erişim sağlamak Python ile çok daha stabil ve sistem kaynaklarını yormayan bir yapıda gerçekleştirilebilir.

Kullanılacak Kütüphaneler:
- **`customtkinter`**: Modern ve şık bir kullanıcı arayüzü (koyu/açık tema destekli, yuvarlatılmış köşeler) oluşturmak için.
- **`keyboard`**: Arka planda klavye kısayollarını (örneğin: `Ctrl+Alt+T`) dinlemek için.
- **`pyperclip`**: Panodaki (clipboard) kopyalanmış metni okumak için.
- **`deep-translator`**: Metni ücretsiz ve hızlı bir şekilde Türkçe'ye çevirmek için (API anahtarı gerektirmez).

## Çalışma Mantığı
1. Uygulama çalıştırıldığında arka planda sessizce bekler.
2. Kullanıcı herhangi bir uygulamada (tarayıcı, Word, PDF vs.) bir metni kopyalar (`Ctrl+C`).
3. Kullanıcı belirlediğimiz kısayol tuşuna (Örn: `Ctrl + Alt + T`) basar.
4. Uygulama anında panodaki metni alır, Türkçe'ye çevirir ve ekranın merkezinde şık bir kutu (popup) içerisinde hem orijinal metni hem de çevirisini gösterir.
5. Kullanıcı `ESC` tuşuna basarak veya pencereyi kapatarak kutuyu gizleyebilir.

> [!TIP]
> Daha ileri bir senaryoda, uygulama sadece seçili metni kısayola basıldığında otomatik kopyalayıp (`Ctrl+C` simüle ederek) ardından çevirisini gösterecek şekilde de ayarlanabilir.

## Proposed Changes

### [NEW] translator_app.py
Ana Python script dosyası. Arka plan dinleyicisi ve kullanıcı arayüzünü barındıracak.

### [NEW] requirements.txt
Projenin çalışması için gereken Python kütüphanelerini içerecek dosya.

## User Review Required

> [!IMPORTANT]
> 1. **Kısayol Tuşu:** Varsayılan olarak `Ctrl + Alt + T` kısayolunu kullanmayı planlıyorum. Sizin için uygun mu veya farklı bir kısayol mu istersiniz?
> 2. **Python Kurulumu:** Bilgisayarınızda Python yüklü olduğunu varsayarak ilerliyorum. Bu kodu doğrudan `.py` olarak çalıştıracağız. Eğer isterseniz en sonunda bunu `.exe` formatına da dönüştürebiliriz (ancak testler için önce `.py` kullanacağız).
> 
> Lütfen planı onaylayın veya değişiklik isteklerinizi belirtin.
