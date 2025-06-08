import pandas as pd
import re
from pathlib import Path
from datetime import datetime
from sqlalchemy.orm import Session
from api.database import get_db, Product

class NutritionMatcher:
    def __init__(self, nutrition_path="data/nutrition_values.csv"):
        self.nutrition_path = Path(nutrition_path)
    
    def match_nutrition(self, product_name, nutrition_df):
        for _, row in nutrition_df.iterrows():
            keyword = row["AnahtarKelime"].lower()
            pattern = rf"\b{re.escape(keyword)}\b"
            if re.search(pattern, product_name.lower()):
                return {
                    "calories": row["CaloriesPer100g"],
                    "protein": row["ProteinPer100g"],
                    "carbs": row["CarbsPer100g"],
                    "fat": row["FatPer100g"]
                }
        return {"calories": None, "protein": None, "carbs": None, "fat": None}

    def run(self):
        print("🔍 Besin değerleri eşleştiriliyor...")
        nutrition_df = pd.read_csv(self.nutrition_path)
        db = next(get_db())
        
        try:
            # Get all products without nutrition values
            products = db.query(Product).all()
            
            for product in products:
                nutrition = self.match_nutrition(product.name, nutrition_df)
                product.calories = nutrition["calories"]
                product.protein = nutrition["protein"]
                product.carbs = nutrition["carbs"]
                product.fat = nutrition["fat"]
            
            db.commit()
            print(f"✅ {len(products)} ürün için besin değerleri eşleştirildi.")
        except Exception as e:
            db.rollback()
            print(f"❌ Besin değeri eşleştirme sırasında hata: {str(e)}")
        finally:
            db.close()
