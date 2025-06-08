from flask import Flask, jsonify
from sqlalchemy.orm import Session
from .database import get_db, Product
import os

app = Flask(__name__)

@app.route("/get-products", methods=["GET"])
def get_products():
    db = next(get_db())
    try:
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
    finally:
        db.close()

if __name__ == "__main__":
    port = int(os.getenv("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
