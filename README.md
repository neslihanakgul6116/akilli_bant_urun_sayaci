# 🏭 Endüstriyel Çoklu Hat & Şişe Sayım ve Otomasyon Sistemi

Bu proje; yapay zeka (YOLOv8) ve bilgisayarlı görü (OpenCV) teknolojilerini kullanarak endüstriyel konveyör bantlarındaki ürünleri (şişe vb.) çoklu hat bazında eşzamanlı sayan, vardiya takibi yapan, bant duruşlarını sesli ve görsel alarmlarla bildiren ve verileri Excel raporuna dönüştüren web tabanlı bir fabrika otomasyon sistemidir.

---

## 🚀 Temel Özellikler

* **Çoklu Hat Desteği:** Fabrika genelindeki farklı konveyör hatlarını (Örn: *Hat 1: Giriş*, *Hat 2: Dolum & Paketleme*) ayrı sekmelerde bağımsız olarak izleme ve sayma.
* **Yapay Zeka Tabanlı Takip:** YOLOv8 ve OpenCV algoritmalarıyla nesne tespiti ve yön bazlı çizgi geçiş (crossing line) sayımı.
* **Akıllı Duruş Algılama & Sesli Alarm:** Bant üzerinde belirli bir süre ürün akışı kesildiğinde hem ekranda görsel hata gösterir hem de bilgisayar hoparlöründen sesli ikaz (bip) verir.
* **Vardiyalı Üretim Yönetimi:** Sabah, akşam ve gece vardiyalarına göre üretim verilerini kategorize etme.
* **Profesyonel Raporlama:** Tüm verileri SQLite veritabanında saklayıp, filtrelenmiş verileri tek tıkla Excel (`.xlsx`) formatında indirebilme.
* **Güvenli Yönetim Paneli:** Veritabanı sıfırlama işlemlerini şifre koruması (`admin123`) altına alma.

---

## 🛠️ Kullanılan Teknoloji Stack'i
* **Python** (Yazılım Altyapısı)
* **Streamlit** (Web Arayüzü)
* **Yolov8 (Ultralytics)** (Nesne Algılama ve Takip)
* **OpenCV** (Kamera ve Görüntü İşleme)
* **SQLite** (Veritabanı Yönetimi)
* **Pandas & OpenPyXL** (Veri Analizi ve Excel Raporlama)

---

## 📦 Kurulum Rehberi

Projeyi kendi bilgisayarınızda çalıştırmak için aşağıdaki adımları takip edebilirsiniz:

1. **Repoyu Klonlayın:**
   ```bash
   git clone [https://github.com/neslihanakgul6116/akilli_bant_urun_sayaci.git](https://github.com/neslihanakgul6116/akilli_bant_urun_sayaci.git)
   cd akilli_bant_urun_sayaci