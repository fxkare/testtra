# Hızlı Çeviri (Instant Translation) Uygulaması Hazır!

Geliştirme tamamlandı ve uygulama başarıyla çalıştırıldı.

## Uygulama Özellikleri
- Arka planda çalışır.
- Herhangi bir ortamda (Web tarayıcısı, PDF, Word vb.) metin seçtikten sonra belirlediğimiz kısayolu kullandığınızda otomatik olarak kopyalanır ve çevirilir.
- Çeviri ekranı modern ve koyu mod destekli **customtkinter** ile geliştirilmiştir.

## Nasıl Kullanılır?

1. İstediğiniz herhangi bir metni farenizle **seçin**.
2. Klavyenizden **`Ctrl + Alt + T`** tuşlarına birlikte basın.
3. Uygulama otomatik olarak `Ctrl+C` işlemi yapacak, kopyalanan metni alıp saniyeler içinde çevirerek ekranın tam ortasında şık bir pencerede gösterecektir.
4. Pencereyi kapatmak için **`ESC`** tuşuna basabilir veya pencere dışına tıklayabilirsiniz.

## Teknik Detaylar
- Gerekli kütüphaneler (`customtkinter`, `keyboard`, `pyperclip`, `deep-translator`) kuruldu.
- Uygulama kodu `translator_app.py` dosyasına yazıldı.
- `Google Translator` API'si entegre edildiği için tamamen ücretsiz ve sınırsız çalışır.

> [!NOTE]
> Uygulama şu an arka planda **çalışır durumdadır**, hemen şimdi bir metin seçip `Ctrl + Alt + T` ile test edebilirsiniz. Uygulamayı durdurmak veya yeniden başlatmak isterseniz proje klasörü içindeki `translator_app.py` dosyasını çalıştırabilirsiniz.
