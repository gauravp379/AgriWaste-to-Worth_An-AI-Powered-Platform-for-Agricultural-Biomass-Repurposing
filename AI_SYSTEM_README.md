# 🤖 AI System - Complete Implementation & Accuracy Metrics

## 📋 Summary

Comprehensive AI system for Agriculture Waste Marketplace with 5 integrated modules:

| Module | Type | Accuracy Metric | Goal |
|--------|------|-----------------|------|
| **Waste Classification** | CNN (Image) | Accuracy, Precision, Recall, F1 | > 85% |
| **Price Prediction** | ML Regression | MAE, RMSE, MAPE, R² | MAPE < 10% |
| **Quality Assessment** | Parameter Validation | Moisture/Calorific/Purity MAE | MAE < 1% |
| **Buyer Recommendations** | Collaborative Filtering | Hit Rate, Accuracy | > 70% |
| **Carbon Impact** | Factor-based Calculation | MAPE, R² | MAPE < 5% |

---

## 🚀 Getting Started

### Option 1: Interactive Demo Menu
```bash
python run_ai_demos.py
```
Choose from 9 options to run individual demos or complete test suite.

### Option 2: Run Complete Tests
```bash
python ai_metrics_test.py
```
Runs all 7 tests with accuracy measurements and benchmarks.

### Option 3: Use as Python Module
```python
from ai_system import AgriculturalAISystem

ai = AgriculturalAISystem()
analysis = ai.analyze_waste_complete("image.jpg", quantity_kg=5000)
ai.print_analysis_summary(analysis)
```

---

## 📊 Files Overview

### Core Modules
| File | Purpose | Key Functions |
|------|---------|---------------|
| `plant_waste_pipeline.py` | CNN model training & inference | `train_pipeline()`, `predict_class()` |
| `model_evaluation.py` | Accuracy metrics for all 5 modules | `ModelEvaluator` class |
| `ai_system.py` | Integrated AI system + Flask API | `AgriculturalAISystem` class |

### Testing & Demos
| File | Purpose | Commands |
|------|---------|----------|
| `ai_metrics_test.py` | Comprehensive test suite | `python ai_metrics_test.py` |
| `run_ai_demos.py` | Interactive demo menu | `python run_ai_demos.py` |
| `AI_METRICS_GUIDE.md` | Complete metrics documentation | Reference guide |

### Output Files (Auto-generated)
| File | Contents | Generation |
|------|----------|-----------|
| `results/test_report.json` | All test results with metrics | `ai_metrics_test.py` |
| `results/analysis_report.json` | Sample waste analysis | `ai_system.py` |
| `results/model_metrics.json` | Model evaluation metrics | `ModelEvaluator` |

---

## 🧪 Test Suite Breakdown

### 7 Comprehensive Tests:

```
TEST 1: Classification Accuracy
  ✓ Trains model on test dataset
  ✓ Measures: Accuracy, Precision, Recall, F1-Score
  ✓ Generates confusion matrix
  ✓ Goal: Accuracy > 80%

TEST 2: Confidence Distribution
  ✓ Gets confidence scores for all classes
  ✓ Shows top 3 predictions
  ✓ Validates top prediction > 50%

TEST 3: Price Prediction
  ✓ 8 test samples with known prices
  ✓ Measures: MAE, RMSE, MAPE, R²
  ✓ Goal: MAPE < 10%, R² > 0.8

TEST 4: Quality Assessment
  ✓ 4 samples with predicted vs actual
  ✓ Measures: Moisture MAE, Calorific MAE, Purity MAE
  ✓ Goal: MAE < 1%

TEST 5: Buyer Recommendations
  ✓ Tests recommendation matching
  ✓ Measures: Top-5 Hit Rate, Accuracy
  ✓ Goal: Hit Rate > 70%

TEST 6: Carbon Impact
  ✓ 6 samples with predicted vs actual CO₂
  ✓ Measures: MAE, MAPE, R²
  ✓ Goal: MAPE < 5%

TEST 7: Complete Pipeline
  ✓ End-to-end analysis on real image
  ✓ Validates all 5 modules work together
  ✓ Generates complete analysis report
```

---

## 📈 Accuracy Metrics Explained

### Classification Metrics (Waste Type Identification)
```
Accuracy  = (TP + TN) / Total
Precision = TP / (TP + FP)    "How often positive predictions correct?"
Recall    = TP / (TP + FN)    "How often true positives found?"
F1-Score  = 2 × (Precision × Recall) / (Precision + Recall)

Example:
  TP=45, TN=40, FP=5, FN=10
  Accuracy = 85/100 = 85%
  Precision = 45/50 = 90%
  Recall = 45/55 = 82%
```

### Price Prediction Metrics
```
MAE (Mean Absolute Error)    = Avg |Actual - Predicted|
RMSE (Root Mean Squared)     = √(Avg (Actual - Predicted)²)
MAPE (Mean Absolute % Error) = Avg |Actual - Predicted| / Actual × 100
R² Score                     = 1 - (Residuals / Total Variance)
                              Range: 0-1 (1.0 = Perfect)

Example:
  Prices: [5200, 5400] vs [5250, 5350]
  MAE = (50 + 50) / 2 = 50
  MAPE = ((50/5200) + (50/5400)) / 2 × 100 = 0.94%
```

### Quality Assessment Metrics
```
Quality Score = (Moisture + Calorific + Purity + Carbon) / 4
                Each normalized to 0-100

Grades:
  A: 90-100   (Premium)
  B: 70-89    (Good)
  C: <70      (Below Standard)
```

### Recommendation Accuracy
```
Top-5 Hit Rate = (Buyers in Top-5 / Total Actual Buyers) × 100
Accuracy = (Correct Recommendations / Total) × 100
```

### Carbon Impact Accuracy
```
CO₂ Avoided = Quantity × Carbon Factor × Processing Type
MAE = Avg |Predicted CO₂ - Actual CO₂|
MAPE = Avg % error
```

---

## 💻 API Endpoints

If using Flask API (`python ai_system.py`):

### Analyze Waste
```
POST /api/analyze
Content-Type: multipart/form-data

Parameters:
  - image: Image file (.jpg, .png, etc.)
  - quantity: Quantity in kg (default: 1000)
  - waste_type: Optional waste type hint

Returns:
  {
    "classification": {...},
    "quality": {...},
    "price": {...},
    "buyer_recommendations": [...],
    "carbon_impact": {...},
    "overall_score": {...},
    "status": "success"
  }
```

### Get Performance Report
```
GET /api/performance

Returns:
  {
    "summary": {...},
    "classification_stats": {...},
    "price_prediction_stats": {...},
    "carbon_impact_stats": {...}
  }
```

### Get Model Metrics
```
GET /api/model-metrics

Returns:
  {
    "metrics": {
      "classification": {...},
      "price_prediction": {...},
      "quality_assessment": {...},
      "buyer_recommendations": {...},
      "carbon_impact": {...}
    }
  }
```

### Health Check
```
GET /health

Returns:
  {"status": "healthy", "ai_system": "active"}
```

---

## 🎯 Use Cases & Examples

### Example 1: Analyze Rice Husk Batch
```python
from ai_system import AgriculturalAISystem
from pathlib import Path

ai = AgriculturalAISystem()

# Analyze waste from image
analysis = ai.analyze_waste_complete(
    Path("uploads/rice_husk_sample.jpg"),
    waste_type="rice_husk",
    quantity_kg=5000
)

# Get overall score
score = analysis["overall_score"]
print(f"Marketplace Readiness: {score['percentage']:.1f}%")
print(f"Rating: {score['rating']}")

# Get best buyer
buyers = analysis["buyer_recommendations"]
if buyers:
    print(f"Best Match: {buyers[0]['name']}")
    print(f"Match Score: {buyers[0]['match_score']:.1%}")
```

### Example 2: Track Performance Over Time
```python
from ai_system import AgriculturalAISystem
import json

ai = AgriculturalAISystem()

# Process multiple batches
batches = ["batch_1.jpg", "batch_2.jpg", "batch_3.jpg"]

for batch_file in batches:
    analysis = ai.analyze_waste_complete(batch_file, quantity_kg=5000)
    # Analysis automatically tracked in ai.performance_history

# Get performance report
report = ai.get_performance_report()
print(json.dumps(report, indent=2))

# Outputs:
# {
#   "summary": {
#     "total_classifications": 3,
#     "total_price_predictions": 3,
#     "total_analyses": 3
#   },
#   "classification_stats": {
#     "avg_confidence": 0.87,
#     "min_confidence": 0.82,
#     "max_confidence": 0.91
#   },
#   ...
# }
```

### Example 3: Run Custom Evaluations
```python
from model_evaluation import ModelEvaluator
import numpy as np

evaluator = ModelEvaluator()

# Custom price prediction evaluation
actual = np.array([5200, 5400, 5100, 5600, 5300])
predicted = np.array([5250, 5350, 5150, 5550, 5280])

results = evaluator.evaluate_price_prediction(actual, predicted)

print(f"MAE: ₹{results['mae']:.2f}")
print(f"MAPE: {results['mape']:.2f}%")
print(f"R²: {results['r2_score']:.4f}")

if results['mape'] < 10:
    print("✅ Price prediction is ACCURATE (MAPE < 10%)")
else:
    print("⚠️  Price prediction needs improvement")
```

---

## 📊 Performance Targets & Benchmarks

### Classification Performance
- **Model**: MobileNetV2 with transfer learning
- **Target Accuracy**: > 85%
- **Inference Speed**: ~500ms per image
- **Throughput**: ~2 images/second

### Price Prediction Performance
- **MAPE Target**: < 10%
- **R² Target**: > 0.8
- **MAE Target**: < ₹500

### Quality Assessment Performance
- **Moisture MAE**: < 1%
- **Calorific MAE**: < 0.5 MJ/kg
- **Grade Accuracy**: > 90%

### Recommendation Performance
- **Hit Rate**: > 70%
- **Accuracy**: > 80%

---

## 🔄 Model Retraining

When to retrain:
- Accuracy drops below 80%
- MAPE exceeds 15%
- New waste types added
- Market conditions change significantly

### Retrain Command:
```bash
python train_crop_cnn.py \
  --dataset-dir data/crop_images \
  --epochs 20 \
  --batch-size 32 \
  --retrain
```

---

## 🛠️ Troubleshooting

### Issue: "No test images found"
**Solution**: Add .jfif or .jpg files to `data/test_crop_image/`

### Issue: Model not loading
**Solution**: Run training first
```bash
python train_crop_cnn.py --dataset-dir data/crop_images
```

### Issue: Low classification accuracy
**Solution**: 
- Check image quality
- Verify dataset diversity
- Retrain with more epochs
- Check for data imbalance

### Issue: Import errors
**Solution**: Install requirements
```bash
pip install tensorflow scikit-learn pandas numpy
```

---

## 📚 Documentation Files

- **AI_METRICS_GUIDE.md** - Detailed metrics explanation
- **README.md** - Main project documentation
- **QUICK_START.txt** - Quick start instructions
- **SETUP_GUIDE.md** - Environment setup

---

## ✅ Implementation Checklist

- [x] Waste Classification (CNN) with accuracy metrics
- [x] Price Prediction (ML) with MAPE/R²
- [x] Quality Assessment with parameter MAE
- [x] Buyer Recommendations with hit rate
- [x] Carbon Impact Calculation with MAPE
- [x] Complete pipeline integration
- [x] Comprehensive test suite (7 tests)
- [x] Performance benchmarking
- [x] Flask API endpoints
- [x] Interactive demo menu
- [x] JSON report generation
- [x] Complete documentation

---

## 🚀 Next Steps

1. **Run Demo**: `python run_ai_demos.py`
2. **Test System**: `python ai_metrics_test.py`
3. **Check Results**: Open `results/test_report.json`
4. **Read Guide**: See `AI_METRICS_GUIDE.md`
5. **Integrate**: Use `ai_system.py` in web platform

---

## 📞 Support

For issues or questions:
1. Check AI_METRICS_GUIDE.md
2. Review test results in results/
3. Check Python error messages
4. Verify all dependencies installed

---

**Status**: ✅ Ready for Production  
**Version**: 1.0.0  
**Last Updated**: October 2024
