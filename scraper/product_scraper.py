import time
import json
from selenium import webdriver
from selenium.webdriver.edge.service import Service
from selenium.webdriver.edge.options import Options
from selenium.webdriver.common.by import By
from webdriver_manager.microsoft import EdgeChromiumDriverManager
from bs4 import BeautifulSoup
from pathlib import Path
from datetime import datetime
from sqlalchemy.orm import Session
from api.database import get_db, Product
import logging

logger = logging.getLogger(__name__)

class ProductScraper:
    def __init__(self, map_path="scraper/product_category_map.json"):
        self.map_path = Path(map_path)
        self.product_list = []
        self.driver = None

    def setup_driver(self):
        try:
            edge_options = Options()
            edge_options.add_argument('--headless')
            edge_options.add_argument('--disable-gpu')
            edge_options.add_argument('--window-size=1920,1080')
            
            service = Service(EdgeChromiumDriverManager().install())
            self.driver = webdriver.Edge(service=service, options=edge_options)
            logger.info("Edge WebDriver başarıyla başlatıldı")
        except Exception as e:
            logger.error(f"Edge WebDriver başlatılırken hata: {str(e)}")
            raise

    def scrape_page(self, url, category, subcategory, item_category):
        page = 1
        while True:
            try:
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

                next_page_btn = self.driver.find_elements(By.CSS_SELECTOR, "a[btnmode='next']")
                if not next_page_btn:
                    break
                page += 1
            except Exception as e:
                logger.error(f"Sayfa scrape edilirken hata: {str(e)}")
                break

    def run(self):
        logger.info("📦 Scraping başlatılıyor...")
        try:
            self.setup_driver()
            with open(self.map_path, "r", encoding="utf-8") as f:
                category_map = json.load(f)

            for entry in category_map:
                logger.info(f"🔍 {entry['item_category']} scrape ediliyor...")
                self.scrape_page(entry["url"], entry["category"], entry["subcategory"], entry["item_category"])
            
            self.driver.quit()
            self.save_to_db()
        except Exception as e:
            logger.error(f"Scraping sırasında hata: {str(e)}")
            if self.driver:
                self.driver.quit()

    def save_to_db(self):
        logger.info("💾 Veriler veritabanına kaydediliyor...")
        db = next(get_db())
        try:
            # Clear old products
            db.query(Product).delete()
            
            # Add new products
            for product_data in self.product_list:
                product = Product(**product_data)
                db.add(product)
            
            db.commit()
            logger.info(f"✅ {len(self.product_list)} ürün veritabanına kaydedildi.")
        except Exception as e:
            db.rollback()
            logger.error(f"❌ Veritabanına kayıt sırasında hata: {str(e)}")
        finally:
            db.close()
