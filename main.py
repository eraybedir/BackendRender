import threading
from scraper.scheduler import ScrapingScheduler
from api.server import app
import os

def run_flask():
    port = int(os.getenv("PORT", 10000))
    app.run(host="0.0.0.0", port=port, debug=False)

def run_scheduler():
    scheduler = ScrapingScheduler()
    scheduler.run_daily()

if __name__ == "__main__":
    threading.Thread(target=run_flask).start()
    threading.Thread(target=run_scheduler).start()
