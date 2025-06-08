import time
import json
from selenium import webdriver
from selenium.webdriver.edge.service import Service
from selenium.webdriver.common.by import By
from webdriver_manager.microsoft import EdgeChromiumDriverManager
from bs4 import BeautifulSoup
from pathlib import Path
from datetime import datetime
from sqlalchemy.orm import Session
from api.database import get_db, Product

class ProductScraper:
    def __init__(self, map_path="scraper/product_category_map.json"):
        self.map_path = Path(map_path)
        self.product_list = []
        self.driver = None

    def setup_driver(self):
        service = Service(EdgeChromiumDriverManager().install())
        self.driver = webdriver.Edge(service=service)

    def scrape_page(self, url, category, subcategory, item_category):
        page = 1
        while True:
            full_url = f"{url}?page={page}"
            self.driver.get(full_url)
            time.sleep(2)
            soup = BeautifulSoup(self.driver.page_source, "html.parser")

            names = [tag.get_text(strip=True) for tag in soup.find_all("div", class_="ProductCard_productName__35zi5")]
            markets = [m.find("img")["alt"] if m.find("img") else "Bilinmiyor"
                       for m in soup.find_all("div", class_="WrapperBox_wrapper__1_OBD")]
            prices = []
            for footer in soup.find_all("div", class_="ProductCard_footer__Fc9OL"):
                spans = footer.find_all("span", class_="ProductCard_price__10UHp")
                price_text = spans[0].get_text(strip=True) if spans else "Fiyat Bilinmiyor"
                # Convert price text to float, removing currency symbol and commas
                try:
                    price = float(price_text.replace('TL', '').replace('.', '').replace(',', '.').strip())
                except ValueError:
                    price = 0.0
                prices.append(price)

            for i, name in enumerate(names):
                self.product_list.append({
                    "name": name,
                    "price": prices[i] if i < len(prices) else 0.0,
                    "store": markets[i] if i < len(markets) else "Bilinmiyor",
                    "category": item_category
                })

            # Sayfa kontrolü
            next_page_btn = self.driver.find_elements(By.CSS_SELECTOR, "a[btnmode='next']")
            if not next_page_btn:
                break
            page += 1

    def run(self):
        print("📦 Scraping başlatılıyor...")
        self.setup_driver()
        with open(self.map_path, "r", encoding="utf-8") as f:
            category_map = json.load(f)

        for entry in category_map:
            print(f"🔍 {entry['item_category']} scrape ediliyor...")
            self.scrape_page(entry["url"], entry["category"], entry["subcategory"], entry["item_category"])
        
        self.driver.quit()
        self.save_to_db()

    def save_to_db(self):
        print("💾 Veriler veritabanına kaydediliyor...")
        db = next(get_db())
        try:
            # Clear old products
            db.query(Product).delete()
            
            # Add new products
            for product_data in self.product_list:
                product = Product(**product_data)
                db.add(product)
            
            db.commit()
            print(f"✅ {len(self.product_list)} ürün veritabanına kaydedildi.")
        except Exception as e:
            db.rollback()
            print(f"❌ Veritabanına kayıt sırasında hata: {str(e)}")
        finally:
            db.close()
