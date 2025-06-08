from flask import Flask, jsonify
from sqlalchemy.orm import Session
from .database import get_db, Product
import os
import logging

# Configure logging
logger = logging.getLogger(__name__)

app = Flask(__name__)

@app.route("/get-products", methods=["GET"])
def get_products():
    try:
        db = next(get_db())
        products = db.query(Product).all()
        return jsonify([{
            "name": p.name,
            "price": p.price,
            "store": p.store,
            "category": p.category,
            "calories": p.calories,
            "protein": p.protein,
            "carbs": p.carbs,
            "fat": p.fat,
            "created_at": p.created_at.isoformat()
        } for p in products])
    except Exception as e:
        logger.error(f"Error getting products: {str(e)}")
        return jsonify({"error": str(e)}), 500
    finally:
        db.close()

@app.route("/health", methods=["GET"])
def health_check():
    return jsonify({"status": "healthy"}), 200

if __name__ == "__main__":
    port = int(os.getenv("PORT", 10000))
    logger.info(f"Starting server on port {port}")
    app.run(host="0.0.0.0", port=port)
