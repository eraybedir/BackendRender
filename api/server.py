from flask import Flask, jsonify
from flask_cors import CORS
from .database import get_db, Product
import logging
from sqlalchemy.exc import SQLAlchemyError
import os

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)

@app.route("/get-products", methods=["GET"])
def get_products():
    try:
        db = next(get_db())
        products = db.query(Product).all()
        return jsonify([{
            "id": p.id,
            "name": p.name,
            "price": p.price,
            "store": p.store,
            "category": p.category,
            "calories": p.calories,
            "protein": p.protein,
            "carbs": p.carbs,
            "fat": p.fat,
            "created_at": p.created_at.isoformat() if p.created_at else None
        } for p in products])
    except SQLAlchemyError as e:
        logger.error(f"Database error: {str(e)}")
        return jsonify({'error': 'Database error occurred'}), 500
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        return jsonify({'error': 'An unexpected error occurred'}), 500
    finally:
        db.close()

@app.route("/health", methods=["GET"])
def health_check():
    try:
        # Try to connect to the database
        db = next(get_db())
        db.execute("SELECT 1")
        db.close()
        return jsonify({'status': 'healthy', 'database': 'connected'})
    except Exception as e:
        logger.error(f"Health check failed: {str(e)}")
        return jsonify({'status': 'unhealthy', 'error': str(e)}), 500

if __name__ == "__main__":
    port = int(os.getenv("PORT", 10000))
    logger.info(f"Starting server on port {port}")
    app.run(host="0.0.0.0", port=port)
