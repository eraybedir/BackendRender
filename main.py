import threading
from scraper.scheduler import ScrapingScheduler
from api.server import app
import os
import logging
import time

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def run_flask():
    try:
        port = int(os.getenv("PORT", 10000))
        logger.info(f"Starting Flask server on port {port}")
        app.run(host="0.0.0.0", port=port, debug=False)
    except Exception as e:
        logger.error(f"Flask server error: {str(e)}")

def run_scheduler():
    try:
        # Wait for Flask to start
        time.sleep(5)
        logger.info("Starting scheduler...")
        scheduler = ScrapingScheduler()
        scheduler.run_daily()
    except Exception as e:
        logger.error(f"Scheduler error: {str(e)}")

if __name__ == "__main__":
    logger.info("Application starting...")
    
    # Start Flask in a separate thread
    flask_thread = threading.Thread(target=run_flask)
    flask_thread.daemon = True
    flask_thread.start()
    
    # Give Flask time to start
    time.sleep(2)
    
    # Start scheduler in the main thread
    run_scheduler()
