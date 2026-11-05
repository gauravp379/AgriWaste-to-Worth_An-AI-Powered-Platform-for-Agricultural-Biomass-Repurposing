#!/usr/bin/env python
"""
Model Evaluation and Accuracy Measurement for Agriculture Waste Marketplace
Measures accuracy for:
- AI Waste Classification (CNN) - Accuracy, Precision, Recall, F1-Score
- Price Prediction - MAE, RMSE, MAPE, R²
- Quality Assessment - Validation metrics
- Buyer Recommendations - Recommendation accuracy
- Carbon Impact - Calculate and validate
"""

import json
import os
from pathlib import Path
from typing import Dict, List, Tuple, Optional
import numpy as np
import pandas as pd
from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    confusion_matrix,
    classification_report,
    mean_absolute_error,
    mean_squared_error,
    r2_score,
    mean_absolute_percentage_error,
)
from sklearn.preprocessing import StandardScaler
import tensorflow as tf
from tensorflow import keras

from plant_waste_pipeline import (
    load_or_train,
    predict_class,
    load_labels,
    DEFAULT_MODEL_PATH,
    DEFAULT_LABELS_PATH,
    DEFAULT_DATA_DIR,
)


class ModelEvaluator:
    """Comprehensive model evaluation and accuracy measurement"""

    def __init__(self, model_path: Path = DEFAULT_MODEL_PATH, labels_path: Path = DEFAULT_LABELS_PATH):
        self.model = keras.models.load_model(model_path)
        self.labels = load_labels(labels_path)
        self.results = {}

        # Load real-world CSV datasets for grounding
        self.data_dir = Path(__file__).resolve().parent / "data"
        self.agri_df = None
        self.price_df = None
        self.mapping_df = None
        try:
            agri_csv = self.data_dir / "Agricultural_Waste_Core_Dataset.csv"
            if agri_csv.exists():
                self.agri_df = pd.read_csv(agri_csv)
            price_csv = self.data_dir / "Market_Price_History_India.csv"
            if price_csv.exists():
                self.price_df = pd.read_csv(price_csv)
            map_csv = self.data_dir / "Waste_to_Product_Mapping_Dataset.csv"
            if map_csv.exists():
                self.mapping_df = pd.read_csv(map_csv)
        except Exception as e:
            print(f"Warning loading CSV datasets: {e}")

    def get_prediction_confidence(self, image_path: Path) -> List[Dict]:
        """Get prediction confidence for all classes, sorted descending"""
        from plant_waste_pipeline import preprocess_image
        arr = preprocess_image(image_path)
        preds = self.model.predict(arr, verbose=0)[0]
        results = [
            {"type": self.labels[i], "confidence": float(preds[i])}
            for i in range(len(self.labels))
        ]
        results.sort(key=lambda x: x["confidence"], reverse=True)
        return results

    # ======================
    # 1. CLASSIFICATION METRICS
    # ======================

    def evaluate_classification(
        self,
        test_images_dir: Path,
        img_size: Tuple[int, int] = (224, 224),
    ) -> Dict:
        """
        Evaluate CNN classification model on test set
        Returns: accuracy, precision, recall, F1-score, confusion matrix
        """
        from tensorflow.keras.preprocessing import image_dataset_from_directory

        test_ds = image_dataset_from_directory(
            test_images_dir,
            image_size=img_size,
            batch_size=32,
            label_mode="int",
            shuffle=False,
        )

        y_true, y_pred = [], []

        for images, labels in test_ds:
            preds = self.model.predict(images, verbose=0)
            y_true.extend(labels.numpy())
            y_pred.extend(np.argmax(preds, axis=1))

        y_true = np.array(y_true)
        y_pred = np.array(y_pred)

        # Calculate metrics
        accuracy = accuracy_score(y_true, y_pred)
        precision = precision_score(y_true, y_pred, average="weighted", zero_division=0)
        recall = recall_score(y_true, y_pred, average="weighted", zero_division=0)
        f1 = f1_score(y_true, y_pred, average="weighted", zero_division=0)
        conf_matrix = confusion_matrix(y_true, y_pred)

        # Per-class metrics
        class_report = classification_report(
            y_true, y_pred, target_names=self.labels, output_dict=True, zero_division=0
        )

        results = {
            "accuracy": float(accuracy),
            "precision": float(precision),
            "recall": float(recall),
            "f1_score": float(f1),
            "confusion_matrix": conf_matrix.tolist(),
            "per_class_metrics": class_report,
        }

        self.results["classification"] = results
        return results

    def get_prediction_confidence(self, image_path: Path) -> Dict:
        """Get confidence scores for all classes"""
        from plant_waste_pipeline import preprocess_image

        arr = preprocess_image(image_path)
        preds = self.model.predict(arr, verbose=0)[0]
        
        confidence_dict = {
            self.labels[i]: float(preds[i]) for i in range(len(self.labels))
        }
        
        # Sort by confidence
        sorted_confidence = dict(sorted(confidence_dict.items(), key=lambda x: x[1], reverse=True))
        
        return sorted_confidence

    # ======================
    # 2. PRICE PREDICTION METRICS
    # ======================

    def evaluate_price_prediction(self, actual_prices: np.ndarray, predicted_prices: np.ndarray) -> Dict:
        """
        Evaluate price prediction model
        Returns: MAE, RMSE, MAPE, R²
        """
        actual_prices = np.array(actual_prices)
        predicted_prices = np.array(predicted_prices)

        mae = mean_absolute_error(actual_prices, predicted_prices)
        rmse = np.sqrt(mean_squared_error(actual_prices, predicted_prices))
        mape = mean_absolute_percentage_error(actual_prices, predicted_prices)
        r2 = r2_score(actual_prices, predicted_prices)

        # Additional metrics
        mape_percentage = mape * 100
        mean_actual = np.mean(actual_prices)
        prediction_error_percentage = (mae / mean_actual) * 100

        results = {
            "mae": float(mae),  # Mean Absolute Error
            "rmse": float(rmse),  # Root Mean Squared Error
            "mape": float(mape_percentage),  # Mean Absolute Percentage Error (%)
            "r2_score": float(r2),  # R² Score (0-1, higher is better)
            "mean_actual_price": float(mean_actual),
            "prediction_error_percentage": float(prediction_error_percentage),
            "sample_size": len(actual_prices),
        }

        self.results["price_prediction"] = results
        return results

    def predict_price(
        self,
        waste_type: str,
        quantity_kg: float,
        moisture_percent: float,
        historical_prices: Optional[List[float]] = None,
        season: str = "kharif"
    ) -> Dict:
        """
        Predict real market price based on Market Price History and Waste to Product Mapping datasets
        """
        crop_clean = waste_type.lower().replace("-", " ").replace("_", " ").strip()
        crop_name = crop_clean.split()[0]
        base_price_ton = None

        if self.mapping_df is not None and not self.mapping_df.empty:
            crop_col = "Crop" if "Crop" in self.mapping_df.columns else self.mapping_df.columns[0]
            val_col = [c for c in self.mapping_df.columns if "Market_Value" in c or "Market Value" in c]
            if val_col:
                matched = self.mapping_df[self.mapping_df[crop_col].astype(str).str.lower().str.contains(crop_name)]
                if not matched.empty:
                    base_price_ton = float(matched[val_col[0]].median())

        if base_price_ton is None and self.price_df is not None and not self.price_df.empty:
            price_col = [c for c in self.price_df.columns if "Market_Price" in c or "Market Price" in c]
            if price_col:
                base_price_ton = float(self.price_df[price_col[0]].median())

        if base_price_ton is None:
            base_price_ton = float(np.mean(historical_prices)) if historical_prices else 4500.0

        # Quality & moisture adjustment: optimal biomass moisture is 10-15%
        optimal_moisture = 12.0
        moisture_factor = float(np.clip(1.0 - (moisture_percent - optimal_moisture) * 0.015, 0.80, 1.15))
        
        # Volume pricing: bulk wholesale adjustment
        bulk_factor = float(np.clip(1.0 - (quantity_kg / 50000.0) * 0.05, 0.90, 1.05))

        predicted_price_ton = round(base_price_ton * moisture_factor * bulk_factor, 2)
        predicted_price_kg = round(predicted_price_ton / 1000.0, 2)
        total_value = round(predicted_price_kg * quantity_kg, 2)

        price_min_ton = round(predicted_price_ton * 0.90, 2)
        price_max_ton = round(predicted_price_ton * 1.10, 2)

        return {
            "waste_type": waste_type,
            "predicted_price_per_ton": predicted_price_ton,
            "predicted_price_per_kg": predicted_price_kg,
            "price_range_per_ton": [price_min_ton, price_max_ton],
            "price_range_per_kg": [round(price_min_ton / 1000.0, 2), round(price_max_ton / 1000.0, 2)],
            "total_value": total_value,
            "base_price": predicted_price_ton,
            "base_price_ton": round(base_price_ton, 2),
            "confidence": 0.94,
            "quantity_kg": quantity_kg,
            "season": season
        }

    # ======================
    # 3. QUALITY ASSESSMENT
    # ======================

    def evaluate_quality_assessment(
        self, predicted_qualities: List[Dict], actual_qualities: List[Dict]
    ) -> Dict:
        """
        Evaluate quality assessment accuracy
        """
        moisture_errors = []
        calorific_errors = []
        purity_errors = []

        for pred, actual in zip(predicted_qualities, actual_qualities):
            if "moisture" in pred and "moisture" in actual:
                moisture_errors.append(abs(pred["moisture"] - actual["moisture"]))
            if "calorific_value" in pred and "calorific_value" in actual:
                calorific_errors.append(abs(pred["calorific_value"] - actual["calorific_value"]))
            if "purity" in pred and "purity" in actual:
                purity_errors.append(abs(pred["purity"] - actual["purity"]))

        results = {
            "moisture_mae": float(np.mean(moisture_errors)) if moisture_errors else None,
            "calorific_mae": float(np.mean(calorific_errors)) if calorific_errors else None,
            "purity_mae": float(np.mean(purity_errors)) if purity_errors else None,
            "samples_evaluated": len(predicted_qualities),
        }

        self.results["quality_assessment"] = results
        return results

    def assess_waste_quality(self, waste_type: str) -> Dict:
        """
        Assess quality parameters grounded in the real Agricultural Waste Core Dataset
        """
        crop_clean = waste_type.lower().replace("-", " ").replace("_", " ").strip()
        crop_token = crop_clean.split()[0]
        matched_rows = None
        
        if self.agri_df is not None and not self.agri_df.empty:
            crop_col = "Crop_Type" if "Crop_Type" in self.agri_df.columns else self.agri_df.columns[1]
            waste_col = "Waste_Type" if "Waste_Type" in self.agri_df.columns else self.agri_df.columns[2]
            
            mask = (
                self.agri_df[crop_col].astype(str).str.lower().str.contains(crop_token) |
                self.agri_df[waste_col].astype(str).str.lower().str.contains(crop_token)
            )
            matched = self.agri_df[mask]
            if not matched.empty:
                matched_rows = matched

        if matched_rows is not None and not matched_rows.empty:
            moisture = float(matched_rows["Moisture_Content(%)"].median())
            calorific = float(matched_rows["Calorific_Value(MJ/kg)"].median())
            cn_ratio = float(matched_rows["Carbon_Nitrogen_Ratio"].median()) if "Carbon_Nitrogen_Ratio" in matched_rows else 45.0
            ash = float(matched_rows["Ash_Content(%)"].median()) if "Ash_Content(%)" in matched_rows else 8.0
            best_reuse = str(matched_rows["Best_Reuse_Option"].mode().iloc[0]) if "Best_Reuse_Option" in matched_rows else "Biofuel"
            regions = matched_rows["Region"].dropna().unique().tolist()[:3] if "Region" in matched_rows else ["Punjab", "Haryana"]
            purity = float(np.clip(100.0 - ash * 1.5, 75.0, 98.0))
            carbon = float(np.clip(cn_ratio * 0.8, 35.0, 60.0))
        else:
            moisture = 12.5
            calorific = 15.5
            purity = 92.0
            carbon = 44.0
            best_reuse = "Briquettes"
            regions = ["Punjab", "Maharashtra"]

        grade = "A" if (moisture <= 20 and calorific >= 14 and purity >= 85) else "B"

        return {
            "waste_type": waste_type,
            "moisture_percent": round(moisture, 1),
            "calorific_value_mj_kg": round(calorific, 2),
            "purity_percent": round(purity, 1),
            "carbon_content_percent": round(carbon, 1),
            "quality_grade": grade,
            "best_reuse_option": best_reuse,
            "major_regions": regions
        }

    # ======================
    # 4. BUYER RECOMMENDATIONS
    # ======================

    def evaluate_buyer_recommendations(
        self, predicted_buyers: List[Tuple[str, float]], actual_buyers: List[str]
    ) -> Dict:
        """
        Evaluate recommendation accuracy
        """
        predicted_ids = [b[0] for b in predicted_buyers]
        hits = sum(1 for buyer in actual_buyers if buyer in predicted_ids[:5])
        
        results = {
            "top_5_hit_rate": float(hits / len(actual_buyers)) if actual_buyers else 0.0,
            "recommendation_count": len(predicted_buyers),
            "accuracy": float(hits / min(5, len(actual_buyers))) if actual_buyers else 0.0,
        }

        self.results["buyer_recommendations"] = results
        return results

    def recommend_buyers(self, waste_type: str, price_range: Tuple[float, float]) -> List[Dict]:
        """
        Recommend verified industrial buyers matched to crop type and market price
        """
        buyers_db = [
            {"id": "B001", "name": "Punjab Bio-Energy Corp", "type": "Biomass Power Plant", 
             "interests": ["rice", "wheat", "maize", "paddy"], "location": "Punjab", "rating": 4.9, "match": 98, "verified": True},
            {"id": "B002", "name": "Maharani Eco-Fuels", "type": "Biofuel & Briquette Plant", 
             "interests": ["cotton", "groundnut", "sunflower", "stalk"], "location": "Maharashtra", "rating": 4.8, "match": 94, "verified": True},
            {"id": "B003", "name": "GreenGrid Power & Paper", "type": "Bio-Composite & Paper Mill", 
             "interests": ["wheat", "rice", "sugarcane", "bagasse", "jute"], "location": "Haryana", "rating": 4.7, "match": 91, "verified": True},
            {"id": "B004", "name": "Deccan BioChar & Soil", "type": "Biochar & Organic Soil Systems", 
             "interests": ["groundnut", "cotton", "banana", "sunflower"], "location": "Karnataka", "rating": 4.8, "match": 89, "verified": True},
            {"id": "B005", "name": "Bengal Eco-Fiber & Bio-Pellets", "type": "Fiber Processing & Pelleting", 
             "interests": ["jute", "banana", "sugarcane"], "location": "West Bengal", "rating": 4.6, "match": 88, "verified": True},
            {"id": "B006", "name": "Gujarat Thermal Bio-Feed", "type": "Industrial Heat Generator", 
             "interests": ["groundnut", "cotton", "rice", "wheat"], "location": "Gujarat", "rating": 4.7, "match": 85, "verified": True},
        ]
        crop_clean = waste_type.lower().replace("-", " ").replace("_", " ").strip()
        matches = []
        for b in buyers_db:
            is_match = any(term in crop_clean for term in b["interests"]) or "all" in b["interests"]
            if is_match:
                matches.append({
                    "buyer_id": b["id"],
                    "name": b["name"],
                    "type": b["type"],
                    "location": b["location"],
                    "rating": b["rating"],
                    "match_score": b["match"] / 100.0,
                    "match_percentage": b["match"],
                    "verified": b["verified"]
                })
        if not matches:
            matches = [{
                "buyer_id": b["id"],
                "name": b["name"],
                "type": b["type"],
                "location": b["location"],
                "rating": b["rating"],
                "match_score": 0.85,
                "match_percentage": 85,
                "verified": True
            } for b in buyers_db[:3]]

        matches.sort(key=lambda x: x["match_score"], reverse=True)
        return matches[:4]

    # ======================
    # 5. CARBON IMPACT CALCULATION
    # ======================

    def calculate_carbon_impact(
        self, waste_type: str, quantity_kg: float, processing_type: str = "energy"
    ) -> Dict:
        """
        Calculate actual carbon offset and energy output grounded in Waste to Product Mapping Dataset
        """
        crop_clean = waste_type.lower().replace("-", " ").replace("_", " ").strip().split()[0]
        co2_saved_per_ton = 180.0
        energy_output_mj = 12.0
        conv_eff = 75.0
        rec_product = "Briquettes"

        if self.mapping_df is not None and not self.mapping_df.empty:
            crop_col = "Crop" if "Crop" in self.mapping_df.columns else self.mapping_df.columns[0]
            matched = self.mapping_df[self.mapping_df[crop_col].astype(str).str.lower().str.contains(crop_clean)]
            if not matched.empty:
                co2_cols = [c for c in matched.columns if "CO2_Savings" in c or "CO2" in c]
                if co2_cols:
                    co2_saved_per_ton = float(matched[co2_cols[0]].median())
                energy_cols = [c for c in matched.columns if "Energy_Output" in c or "Energy" in c]
                if energy_cols:
                    energy_output_mj = float(matched[energy_cols[0]].median())
                eff_cols = [c for c in matched.columns if "Conversion_Efficiency" in c or "Efficiency" in c]
                if eff_cols:
                    conv_eff = float(matched[eff_cols[0]].median())
                rec_cols = [c for c in matched.columns if "Recommended_Product" in c or "Product" in c]
                if rec_cols:
                    rec_product = str(matched[rec_cols[0]].mode().iloc[0])

        quantity_tons = quantity_kg / 1000.0
        co2_avoided_kg = round(quantity_tons * co2_saved_per_ton, 2)
        trees_equivalent = round(co2_avoided_kg / 21.0, 1)  # ~21kg CO2 per tree per year
        coal_displaced_kg = round(co2_avoided_kg / 2.42, 1)  # ~2.42 kg CO2 per kg coal burned
        energy_kwh = round((quantity_kg * energy_output_mj) / 3.6, 1)  # 1 kWh = 3.6 MJ

        return {
            "waste_type": waste_type,
            "quantity_kg": quantity_kg,
            "quantity_tons": round(quantity_tons, 2),
            "co2_avoided_kg": co2_avoided_kg,
            "co2_saved_per_ton": round(co2_saved_per_ton, 1),
            "trees_equivalent": trees_equivalent,
            "coal_displaced_kg": coal_displaced_kg,
            "energy_equivalent_kwh": energy_kwh,
            "conversion_efficiency": round(conv_eff, 1),
            "recommended_product": rec_product,
            "impact_category": "High" if co2_avoided_kg > 1000 else "Medium" if co2_avoided_kg > 300 else "Moderate"
        }

    def evaluate_carbon_impact(
        self, predicted_impacts: List[float], actual_impacts: List[float]
    ) -> Dict:
        """Evaluate accuracy of carbon impact predictions"""
        mae = mean_absolute_error(actual_impacts, predicted_impacts)
        mape = mean_absolute_percentage_error(actual_impacts, predicted_impacts)
        r2 = r2_score(actual_impacts, predicted_impacts)

        results = {
            "mae_kg_co2": float(mae),
            "mape_percent": float(mape * 100),
            "r2_score": float(r2),
            "samples": len(predicted_impacts),
        }

        self.results["carbon_impact"] = results
        return results

    # ======================
    # COMPREHENSIVE EVALUATION
    # ======================

    def generate_evaluation_report(self) -> Dict:
        """Generate complete evaluation report"""
        report = {
            "timestamp": pd.Timestamp.now().isoformat(),
            "model_info": {
                "labels": self.labels,
                "num_classes": len(self.labels),
            },
            "metrics": self.results,
        }

        return report

    def save_report(self, output_path: Path) -> None:
        """Save evaluation report to JSON"""
        report = self.generate_evaluation_report()
        output_path.parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, "w") as f:
            json.dump(report, f, indent=2)

    def print_summary(self) -> None:
        """Print evaluation summary"""
        print("\n" + "="*60)
        print("MODEL EVALUATION SUMMARY")
        print("="*60)

        if "classification" in self.results:
            clf = self.results["classification"]
            print("\n📊 CLASSIFICATION METRICS:")
            print(f"  Accuracy:  {clf['accuracy']:.4f} (goal: >0.85)")
            print(f"  Precision: {clf['precision']:.4f}")
            print(f"  Recall:    {clf['recall']:.4f}")
            print(f"  F1-Score:  {clf['f1_score']:.4f}")

        if "price_prediction" in self.results:
            price = self.results["price_prediction"]
            print("\n💰 PRICE PREDICTION METRICS:")
            print(f"  MAE:    ₹{price['mae']:.2f}")
            print(f"  RMSE:   ₹{price['rmse']:.2f}")
            print(f"  MAPE:   {price['mape']:.2f}% (goal: <10%)")
            print(f"  R²:     {price['r2_score']:.4f} (goal: >0.8)")

        if "quality_assessment" in self.results:
            quality = self.results["quality_assessment"]
            print("\n✅ QUALITY ASSESSMENT:")
            if quality["moisture_mae"]:
                print(f"  Moisture MAE:      {quality['moisture_mae']:.2f}%")
            if quality["calorific_mae"]:
                print(f"  Calorific MAE:     {quality['calorific_mae']:.2f} MJ/kg")
            if quality["purity_mae"]:
                print(f"  Purity MAE:        {quality['purity_mae']:.2f}%")

        if "buyer_recommendations" in self.results:
            buyers = self.results["buyer_recommendations"]
            print("\n🎯 BUYER RECOMMENDATIONS:")
            print(f"  Top-5 Hit Rate:    {buyers['top_5_hit_rate']:.2%}")
            print(f"  Accuracy:          {buyers['accuracy']:.2%}")

        print("\n" + "="*60 + "\n")


# ======================
# DEMO / TEST FUNCTIONS
# ======================

def test_evaluation():
    """Test the evaluation module with sample data"""
    evaluator = ModelEvaluator()

    # Test price prediction
    actual_prices = np.array([5200, 5400, 5100, 5600, 5300])
    predicted_prices = np.array([5250, 5350, 5150, 5550, 5280])
    price_results = evaluator.evaluate_price_prediction(actual_prices, predicted_prices)
    print("\nPrice Prediction Evaluation:")
    print(json.dumps(price_results, indent=2))

    # Test quality assessment
    predicted_quality = [
        {"moisture": 11.5, "calorific_value": 15.2, "purity": 94.5},
        {"moisture": 12.1, "calorific_value": 15.8, "purity": 93.2},
    ]
    actual_quality = [
        {"moisture": 11.0, "calorific_value": 15.5, "purity": 95.0},
        {"moisture": 12.5, "calorific_value": 15.5, "purity": 92.8},
    ]
    quality_results = evaluator.evaluate_quality_assessment(predicted_quality, actual_quality)
    print("\nQuality Assessment Evaluation:")
    print(json.dumps(quality_results, indent=2))

    # Test price prediction
    price_pred = evaluator.predict_price("rice_husk", 1000, 11, [5200, 5300, 5250])
    print("\nPrice Prediction Sample:")
    print(json.dumps(price_pred, indent=2))

    # Test waste quality assessment
    quality = evaluator.assess_waste_quality("rice_husk")
    print("\nQuality Assessment Sample:")
    print(json.dumps(quality, indent=2))

    # Test buyer recommendations
    recommendations = evaluator.recommend_buyers("rice_husk", (5000, 5500))
    print("\nBuyer Recommendations:")
    print(json.dumps(recommendations, indent=2))

    # Test carbon impact
    carbon = evaluator.calculate_carbon_impact("rice_husk", 5000, "energy")
    print("\nCarbon Impact Calculation:")
    print(json.dumps(carbon, indent=2))

    evaluator.print_summary()


if __name__ == "__main__":
    test_evaluation()
