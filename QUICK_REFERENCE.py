#!/usr/bin/env python
"""
Quick Reference - AI System Commands and Functions
Print this guide for quick reference
"""

QUICK_REFERENCE = """
╔══════════════════════════════════════════════════════════════════════════════╗
║                  🌾 AGRICULTURE WASTE AI SYSTEM - QUICK REFERENCE            ║
╚══════════════════════════════════════════════════════════════════════════════╝

┌─ RUNNING THE SYSTEM ────────────────────────────────────────────────────────┐
│                                                                              │
│  Interactive Menu:              python run_ai_demos.py                      │
│  Run All Tests:                 python ai_metrics_test.py                   │
│  Launch API Server:             python ai_system.py                         │
│                                                                              │
└──────────────────────────────────────────────────────────────────────────────┘

┌─ PYTHON USAGE ──────────────────────────────────────────────────────────────┐
│                                                                              │
│  from model_evaluation import ModelEvaluator                                │
│  from ai_system import AgriculturalAISystem                                 │
│                                                                              │
│  # Create evaluator                                                         │
│  eval = ModelEvaluator()                                                    │
│                                                                              │
│  # Create AI system                                                         │
│  ai = AgriculturalAISystem()                                                │
│                                                                              │
└──────────────────────────────────────────────────────────────────────────────┘

┌─ AI MODULE 1: CLASSIFICATION ───────────────────────────────────────────────┐
│                                                                              │
│  Function:      Identify waste type from image (CNN)                        │
│                                                                              │
│  Metrics:       • Accuracy (goal: > 85%)                                    │
│                 • Precision (goal: > 0.85)                                  │
│                 • Recall (goal: > 0.85)                                     │
│                 • F1-Score (goal: > 0.85)                                   │
│                 • Confidence score (0-1)                                    │
│                                                                              │
│  Usage:         eval.get_prediction_confidence("image.jpg")                 │
│                 eval.evaluate_classification(test_dir)                      │
│                                                                              │
│  Expected:      Top prediction confidence > 50%                             │
│                                                                              │
└──────────────────────────────────────────────────────────────────────────────┘

┌─ AI MODULE 2: PRICE PREDICTION ─────────────────────────────────────────────┐
│                                                                              │
│  Function:      Predict market price based on waste type & quality         │
│                                                                              │
│  Metrics:       • MAE - Mean Absolute Error (goal: < ₹500)                 │
│                 • RMSE - Root Mean Squared Error (goal: < ₹600)            │
│                 • MAPE - Mean Absolute % Error (goal: < 10%)               │
│                 • R² Score (goal: > 0.8)                                    │
│                                                                              │
│  Usage:         price = eval.predict_price("rice_husk", qty, moisture)      │
│                 results = eval.evaluate_price_prediction(actual, pred)      │
│                                                                              │
│  Adjustments:   • Moisture factor (optimal: 12%)                            │
│                 • Quantity discount (5-10% for bulk)                        │
│                                                                              │
│  Expected:      MAPE < 10%, R² > 0.8                                        │
│                                                                              │
└──────────────────────────────────────────────────────────────────────────────┘

┌─ AI MODULE 3: QUALITY ASSESSMENT ───────────────────────────────────────────┐
│                                                                              │
│  Function:      Assess waste quality parameters and grade                  │
│                                                                              │
│  Metrics:       • Moisture MAE (goal: < 1%)                                │
│                 • Calorific MAE (goal: < 0.5 MJ/kg)                        │
│                 • Purity MAE (goal: < 2%)                                   │
│                 • Quality Score (0-100)                                     │
│                                                                              │
│  Parameters:    • Moisture % (optimal: 10-12%)                             │
│                 • Calorific Value MJ/kg (optimal: 14-16)                   │
│                 • Purity % (optimal: 92-98%)                               │
│                 • Carbon Content % (optimal: 35-45%)                       │
│                                                                              │
│  Grades:        • A (90-100) = Premium                                      │
│                 • B (70-89) = Good                                          │
│                 • C (< 70) = Below Standard                                 │
│                                                                              │
│  Usage:         quality = eval.assess_waste_quality("rice_husk")            │
│                 score = quality["quality_score"]  # 0-100                   │
│                                                                              │
│  Expected:      Quality score reflects actual waste quality                │
│                                                                              │
└──────────────────────────────────────────────────────────────────────────────┘

┌─ AI MODULE 4: BUYER RECOMMENDATIONS ────────────────────────────────────────┐
│                                                                              │
│  Function:      Match waste sellers with suitable buyers                   │
│                                                                              │
│  Metrics:       • Top-5 Hit Rate (goal: > 70%)                             │
│                 • Recommendation Accuracy (goal: > 80%)                     │
│                 • Match Score (0-1 per buyer)                              │
│                                                                              │
│  Matching On:   • Buyer interest alignment                                  │
│                 • Price range compatibility                                 │
│                 • Quality requirements                                      │
│                 • Buyer rating (4.0-5.0 stars)                            │
│                                                                              │
│  Usage:         buyers = eval.recommend_buyers("rice_husk", (5000, 5500))  │
│                 results = eval.evaluate_buyer_recommendations(pred, actual) │
│                                                                              │
│  Output:        [{buyer_id, name, type, match_score, rating}]              │
│                                                                              │
│  Expected:      Top buyer has match_score > 0.8                             │
│                                                                              │
└──────────────────────────────────────────────────────────────────────────────┘

┌─ AI MODULE 5: CARBON IMPACT ────────────────────────────────────────────────┐
│                                                                              │
│  Function:      Calculate environmental impact of waste processing         │
│                                                                              │
│  Metrics:       • MAE - kg CO₂ error (goal: < 100 kg)                      │
│                 • MAPE - % error (goal: < 5%)                              │
│                 • R² Score (goal: > 0.9)                                    │
│                                                                              │
│  Calculates:    • CO₂ avoided (kg)                                          │
│                 • Trees equivalent                                          │
│                 • Energy generation (kWh)                                   │
│                 • Impact category (High/Medium/Low)                         │
│                                                                              │
│  Carbon Factors:  Rice Husk (2.5), Wheat Straw (2.3), Cotton (2.7)        │
│                                                                              │
│  Usage:         carbon = eval.calculate_carbon_impact("rice_husk", 5000)    │
│                 co2_avoided = carbon["co2_avoided_kg"]                      │
│                 trees = carbon["trees_equivalent"]                          │
│                                                                              │
│  Example:       5000 kg Rice Husk → 12,500 kg CO₂ ≈ 595 trees             │
│                                                                              │
└──────────────────────────────────────────────────────────────────────────────┘

┌─ COMPLETE ANALYSIS PIPELINE ────────────────────────────────────────────────┐
│                                                                              │
│  Combines all 5 modules into one complete analysis:                        │
│                                                                              │
│  ai = AgriculturalAISystem()                                                │
│  analysis = ai.analyze_waste_complete("image.jpg", quantity_kg=5000)       │
│                                                                              │
│  Returns:       {                                                           │
│    "classification": {...},     # Waste type + confidence                  │
│    "quality": {...},            # Quality parameters + score               │
│    "price": {...},              # Predicted price                          │
│    "buyer_recommendations": [...],  # Matched buyers                       │
│    "carbon_impact": {...},      # Environmental impact                     │
│    "overall_score": {...}       # Combined score 0-100%                    │
│  }                                                                          │
│                                                                              │
│  Overall Score Weight:                                                      │
│    • Classification: 20%                                                    │
│    • Quality: 25%                                                           │
│    • Price: 20%                                                             │
│    • Buyer Match: 20%                                                       │
│    • Carbon Impact: 15%                                                     │
│                                                                              │
└──────────────────────────────────────────────────────────────────────────────┘

┌─ TESTING & BENCHMARKS ──────────────────────────────────────────────────────┐
│                                                                              │
│  Test 1: Classification Accuracy     python ai_metrics_test.py (option 1)  │
│  Test 2: Confidence Distribution     python ai_metrics_test.py (option 2)  │
│  Test 3: Price Prediction            python ai_metrics_test.py (option 3)  │
│  Test 4: Quality Assessment          python ai_metrics_test.py (option 4)  │
│  Test 5: Buyer Recommendations       python ai_metrics_test.py (option 5)  │
│  Test 6: Carbon Impact               python ai_metrics_test.py (option 6)  │
│  Test 7: Complete Pipeline           python ai_metrics_test.py (option 7)  │
│                                                                              │
│  Run All:  python ai_metrics_test.py                                        │
│  Demo All: python run_ai_demos.py → Choose 8                              │
│                                                                              │
└──────────────────────────────────────────────────────────────────────────────┘

┌─ MODEL MANAGEMENT ──────────────────────────────────────────────────────────┐
│                                                                              │
│  Train:              python model_utilities.py train --epochs 20            │
│  Evaluate:           python model_utilities.py evaluate --test-dir <dir>   │
│  Backup:             python model_utilities.py backup                       │
│  Batch Predict:      python model_utilities.py batch --image-dir <dir>    │
│  Performance Report: python model_utilities.py report                       │
│  Statistics:         python model_utilities.py stats                        │
│                                                                              │
└──────────────────────────────────────────────────────────────────────────────┘

┌─ API ENDPOINTS ─────────────────────────────────────────────────────────────┐
│                                                                              │
│  POST   /api/analyze           Upload image + analyze (all 5 modules)      │
│  GET    /api/performance       System performance report                    │
│  GET    /api/model-metrics     Model evaluation metrics                     │
│  GET    /health                Health check                                 │
│                                                                              │
└──────────────────────────────────────────────────────────────────────────────┘

┌─ FILE LOCATIONS ────────────────────────────────────────────────────────────┐
│                                                                              │
│  Code Files:                                                                 │
│    • model_evaluation.py       - All accuracy metrics                       │
│    • ai_system.py              - Integrated system + API                    │
│    • ai_metrics_test.py        - Test suite                                 │
│    • run_ai_demos.py           - Interactive demos                          │
│    • model_utilities.py        - Model management                           │
│                                                                              │
│  Documentation:                                                              │
│    • AI_METRICS_GUIDE.md       - Detailed metrics                           │
│    • AI_SYSTEM_README.md       - System documentation                       │
│    • AI_IMPLEMENTATION_SUMMARY.md - What's implemented                      │
│                                                                              │
│  Test Images:                                                                │
│    • data/test_crop_image/     - Sample waste images                        │
│                                                                              │
│  Results:                                                                    │
│    • results/test_report.json  - Test results                               │
│    • results/analysis_report.json - Sample analysis                         │
│    • results/model_metrics.json - Model evaluation                          │
│                                                                              │
└──────────────────────────────────────────────────────────────────────────────┘

┌─ COMMON TASKS ──────────────────────────────────────────────────────────────┐
│                                                                              │
│  Run demo:                                                                   │
│    python run_ai_demos.py                                                   │
│                                                                              │
│  Test everything:                                                            │
│    python ai_metrics_test.py                                                │
│                                                                              │
│  Analyze single image:                                                       │
│    eval = ModelEvaluator()                                                  │
│    confidence = eval.get_prediction_confidence("image.jpg")                 │
│                                                                              │
│  Complete analysis:                                                          │
│    ai = AgriculturalAISystem()                                              │
│    analysis = ai.analyze_waste_complete("image.jpg")                        │
│    ai.print_analysis_summary(analysis)                                      │
│                                                                              │
│  Train new model:                                                            │
│    python model_utilities.py train --epochs 20                              │
│                                                                              │
│  Batch predict on folder:                                                    │
│    python model_utilities.py batch --image-dir data/test_crop_image        │
│                                                                              │
└──────────────────────────────────────────────────────────────────────────────┘

┌─ EXPECTED ACCURACY RANGES ──────────────────────────────────────────────────┐
│                                                                              │
│  EXCELLENT (Target)                                                         │
│    Classification: > 90% accuracy                                           │
│    Price: MAPE < 10%, R² > 0.8                                             │
│    Quality: MAE < 1%                                                        │
│    Recommendations: Hit Rate > 80%                                          │
│    Carbon: MAPE < 5%                                                        │
│                                                                              │
│  GOOD (Working)                                                             │
│    Classification: 80-90% accuracy                                          │
│    Price: MAPE 10-15%, R² 0.7-0.8                                          │
│    Quality: MAE 1-2%                                                        │
│    Recommendations: Hit Rate 70-80%                                         │
│    Carbon: MAPE 5-10%                                                       │
│                                                                              │
│  POOR (Needs Work)                                                          │
│    Classification: < 80% accuracy                                           │
│    Price: MAPE > 15%, R² < 0.7                                             │
│    Quality: MAE > 2%                                                        │
│    Recommendations: Hit Rate < 70%                                          │
│    Carbon: MAPE > 10%                                                       │
│                                                                              │
└──────────────────────────────────────────────────────────────────────────────┘

╔══════════════════════════════════════════════════════════════════════════════╗
║                            Ready to get started?                             ║
║                                                                              ║
║  1. Run: python run_ai_demos.py                                             ║
║  2. Test: python ai_metrics_test.py                                         ║
║  3. Read: AI_METRICS_GUIDE.md                                               ║
║  4. Integrate: Use ai_system.py in your web platform                        ║
║                                                                              ║
║  Status: ✅ COMPLETE & PRODUCTION READY                                     ║
║  Version: 1.0.0                                                              ║
╚══════════════════════════════════════════════════════════════════════════════╝
"""

if __name__ == "__main__":
    print(QUICK_REFERENCE)
    
    # Save to file
    with open("QUICK_REFERENCE.txt", "w") as f:
        f.write(QUICK_REFERENCE)
    
    print("\n✅ Quick reference saved to QUICK_REFERENCE.txt")
