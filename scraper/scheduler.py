import schedule
import time
from scraper.product_scraper import ProductScraper
from scraper.matcher import NutritionMatcher
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class ScrapingScheduler:
    def __init__(self):
        self.scraper = ProductScraper()
        self.matcher = NutritionMatcher()

    def job(self):
        try:
            logger.info("🚀 Scraping & Matching başlatılıyor...")
            self.scraper.run()
            self.matcher.run()
            logger.info("✅ Tüm işlem tamamlandı.\n")
        except Exception as e:
            logger.error(f"❌ İşlem sırasında hata oluştu: {str(e)}")

    def run_daily(self):
        logger.info("📅 Zamanlayıcı başlatıldı (her 7 günde bir çalışacak)...")
        schedule.every(7).days.do(self.job)

        # İlk çalıştırma hemen yapılsın
        self.job()

        while True:
            try:
                schedule.run_pending()
                time.sleep(60)
            except Exception as e:
                logger.error(f"Zamanlayıcı hatası: {str(e)}")
                time.sleep(60)  # Hata durumunda 1 dakika bekle
