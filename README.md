# Tarım Parsel Verilerinin Coğrafi ve Sayısal Olarak İşlenmesi

Bu proje, tarımsal üretim verileri ile tarım parsel geometrilerini birleştirerek ürün bazlı coğrafi analiz yapılmasını sağlar. Üretilen çıktılar, tarımsal karar destek sistemleri ve coğrafi bilgi sistemleri (CBS) uygulamaları için değerlidir.

##  Temel Özellikler

-  Excel dosyasındaki verileri temizleme, yeniden adlandırma ve dönüştürme
-  GML formatındaki parsel geometrilerini işleme
-  Geometrilerle üretim verilerini "Parsel Kodu" üzerinden eşleştirme
-  Her bitki türü için ayrı GeoPackage, Excel ve GeoJSON dosyaları oluşturma
-  Bitki adlarını otomatik sınıflandırma (ör. buğday → Hububat)
-  Tüm işlemleri kayıt altına alan log sistemi

##  Kullanım Adımları

1. `Geocrop.py` dosyasındaki `excel_path` ve `gml_klasor` yollarını kendi verilerinize göre düzenleyin.
2. Terminalden çalıştırın:

```bash
python Geocrop.py
```

3. Çıktılar otomatik olarak `cikti_dosyalar/` klasörü altında üç formatta oluşturulacaktır:
   - `gpkg/` → GeoPackage
   - `excel/` → Excel
   - `geojson/` → GeoJSON

##  Girdi Beklentisi

**Excel Dosyası** (başlıklar 11. satırdan itibaren):
- İlçe, Köy, Ada No, Parsel No, Parsel Alanı, Ekili Alan, Ürün

**GML Dosyaları**:
- IlceAd, MahalleAd, AdaNo, ParselNo, geometry

##  Sorun Giderme

 Aşağıdaki hatalarla karşılaşırsanız:

- **"Excel dosyası bulunamadı!"** → `excel_path` değişkenindeki yolu ve dosya adını kontrol edin.
- **"GML klasörü bulunamadı!"** → `gml_klasor` klasörünün gerçekten var olduğundan emin olun.
- **"Hiçbir GML dosyası okunamadı!"** → Klasörde `.gml` uzantılı dosyaların olduğuna ve dosya adlarında özel karakterler bulunmadığına dikkat edin.
- **GeoJSON oluşturulamıyor** → Geometri tipi `Polygon` veya `MultiPolygon` değilse GeoJSON üretimi başarısız olabilir.

 Detaylı hata mesajları `islem.log` dosyasına yazılır. Gelişmiş hata takibi için bu dosyayı inceleyin.

##  Ek Bilgiler

- Tüm işlemler `islem.log` dosyasına detaylı şekilde kaydedilir.
- Kod, Türkçe alan adları ve yerel formatlarla uyumlu çalışacak şekilde yapılandırılmıştır.

##  Geliştirici

**Harun Kapdan**  
  Mail: hrnkpdn@gmail.com
