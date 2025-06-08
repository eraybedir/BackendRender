#  Market Veri Toplama ve Besin Bilgisi Eşleştirme Uygulaması

Bu proje market ürünlerini [cimri.com](https://www.cimri.com)'dan otomatik olarak çekip, her ürünün besin değerlerini eşleştirir. 
Son olarak bu zenginleştirilmiş ürün bilgilerini bir **Flask API** üzerinden dışa açar.

Scraping işlemi her **7 günde bir** arka planda çalışır.  
Sonuçlar hem `.csv` hem de API üzerinden JSON olarak sunulur.

---

## 📦 Proje Bileşenleri

- **Scraper:** Belirli kategorilerdeki ürünleri çeker (`ProductScraper`)
- **Matcher:** Ürün isimlerini `nutrition_values.csv` ile eşleştirir
- **API:** `/get-products` endpoint’iyle en güncel veriyi dışa açar
- **Zamanlayıcı:** 7 günde bir scraping + matching işlemi çalıştırır (`schedule`)
- **Docker destekli:** Tek komutla kurulum, çalıştırma ve deploy

---

## 🗂 Klasör Yapısı
DataLayer/
├── api/ # Flask API
│ └── server.py
├── scraper/ # Scraper, Matcher, Zamanlayıcı
│ ├── product_scraper.py
│ ├── matcher.py
│ └── scheduler.py
├── data/ # CSV verileri ve nutrition tablosu
│ ├── raw_products/
│ ├── enriched_products/
│ └── nutrition_values.csv
├── main.py # Flask + Zamanlayıcı birlikte çalışır
├── Dockerfile # Docker imaj tanımı
├── docker-compose.yml # Tüm servisi ayağa kaldırır
├── .env # Ortam değişkenleri (örn: FLASK_PORT)
└── requirements.txt # Python bağımlılıkları


## ⚙️ Kurulum ve Çalıştırma (Local veya Sunucu)

### Gerekli yazılımlar:
- Docker
- Docker Compose

### 1. Projeyi bu klasöre yerleştir:
~/DataLayer/

### 2. Terminal aç ve çalıştır:

###
 cd DataLayer
docker-compose up --build

### 3. API’ye eriş: bash
http://localhost:5000/get-products
Eğer sunucuda çalıştırıyorsanız: http://<sunucu-ip>:5000/get-products
###

## Sunucuya Deploy Etme
terminalde

1. Bu projeyi sunucuya aktar:
scp -r ./DataLayer user@sunucu-ip:/home/user/

2. Sunucuda çalıştır:
cd /home/user/DataLayer
docker-compose up --build

3. Tarayıcıdan test et:
