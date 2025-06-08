import pandas as pd
import re
from pathlib import Path
from datetime import datetime

class NutritionMatcher:
    def __init__(self, raw_dir="data/raw_products", nutrition_path="data/nutrition_values.csv", output_dir="data/enriched_products"):
        self.raw_dir = Path(raw_dir)
        self.nutrition_path = Path(nutrition_path)
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
    
    def get_latest_raw_csv(self):
        csv_files = list(self.raw_dir.glob("products_*.csv"))
        if not csv_files:
            raise FileNotFoundError("Hiçbir scraping dosyası bulunamadı.")
        latest = max(csv_files, key=lambda f: f.stat().st_mtime)
        return latest

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
        latest_csv = self.get_latest_raw_csv()
        df = pd.read_csv(latest_csv)
        nutrition_df = pd.read_csv(self.nutrition_path)

        enriched_rows = []
        for _, row in df.iterrows():
            nutrition = self.match_nutrition(row["name"], nutrition_df)
            enriched_rows.append({**row, **nutrition})

        enriched_df = pd.DataFrame(enriched_rows)

        today = datetime.today().strftime("%Y_%m_%d")
        enriched_path = self.output_dir / f"enriched_{today}.csv"
        enriched_df.to_csv(enriched_path, index=False, encoding="utf-8-sig")
        print(f"✅ Zenginleştirilmiş veri kaydedildi: {enriched_path.resolve()}")
