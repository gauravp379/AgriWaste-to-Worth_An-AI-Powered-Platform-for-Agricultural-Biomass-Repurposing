# AI Models - Accuracy Metrics & Implementation Guide

## 📊 Overview

This document details the 5 AI modules implemented in the Agriculture Waste Marketplace with comprehensive accuracy measurement for each.

---

## 🤖 AI System Components

### 1. **Waste Classification (CNN)**
**Purpose:** Identify waste type from image using deep learning
**Model:** MobileNetV2 with transfer learning

#### Accuracy Metrics:
- **Accuracy**: Percentage of correctly classified images
  - Formula: (TP + TN) / (TP + TN + FP + FN)
  - Goal: > 85%
  
- **Precision**: When model predicts positive, how often is it correct?
  - Formula: TP / (TP + FP)
  - Goal: > 0.85
  
- **Recall**: When true positive exists, how often does model find it?
  - Formula: TP / (TP + FN)
  - Goal: > 0.85
  
- **F1-Score**: Harmonic mean of Precision and Recall
  - Formula: 2 * (Precision * Recall) / (Precision + Recall)
  - Goal: > 0.85
  
- **Confidence Score**: Model's certainty for each prediction (0-1)
  - Interpreted as "Model is X% sure about prediction"

#### Confusion Matrix:
Shows which waste types are confused with others

**Expected Accuracy Ranges:**
- Excellent: > 90%
- Good: 80-90%
- Fair: 70-80%
- Poor: < 70%

---

### 2. **Price Prediction (ML Regression)**
**Purpose:** Predict market price based on waste type, quality, quantity
**Model:** Statistical regression with market factors

#### Accuracy Metrics:

- **Mean Absolute Error (MAE)**: Average price difference
  - Formula: Σ|Actual - Predicted| / n
  - Unit: ₹ (Rupees)
  - Goal: < ₹500

- **Root Mean Squared Error (RMSE)**: Penalizes large errors more
  - Formula: √(Σ(Actual - Predicted)² / n)
  - Unit: ₹
  - Goal: < ₹600

- **Mean Absolute Percentage Error (MAPE)**: % error relative to actual price
  - Formula: Σ|Actual - Predicted| / Actual × 100 / n
  - Unit: %
  - Goal: < 10%

- **R² Score**: How much variance does model explain (0-1)
  - Formula: 1 - (Residual Sum of Squares / Total Sum of Squares)
  - Interpretation:
    - 1.0 = Perfect fit
    - 0.8-1.0 = Excellent
    - 0.6-0.8 = Good
    - 0.4-0.6 = Fair
    - < 0.4 = Poor

---

### 3. **Quality Assessment**
**Purpose:** Assess waste quality parameters (moisture, calorific value, purity, carbon content)
**Model:** Reference-based parameter validation

#### Quality Parameters by Waste Type:

| Parameter | Rice Husk | Wheat Straw | Cotton Stalks | Groundnut Shells |
|-----------|-----------|-------------|----------------|------------------|
| Moisture (%) | 10-12 | 12-15 | 10-13 | 8-10 |
| Calorific (MJ/kg) | 14-16 | 15-17 | 16-18 | 18-20 |
| Purity (%) | 92-98 | 85-95 | 80-90 | 90-97 |
| Carbon (%) | 35-45 | 40-50 | 42-52 | 45-55 |

#### Accuracy Metrics:

- **Moisture MAE**: Mean error in moisture prediction
  - Goal: < 1%
  
- **Calorific MAE**: Mean error in calorific value
  - Goal: < 0.5 MJ/kg
  
- **Purity MAE**: Mean error in purity prediction
  - Goal: < 2%

#### Quality Score (0-100):
Quality Score = (Moisture_Score + Calorific_Score + Purity_Score + Carbon_Score) / 4

---

### 4. **Buyer Recommendations**
**Purpose:** Match waste sellers with potential buyers based on type, price, interests
**Model:** Collaborative filtering with rule-based matching

#### Matching Criteria:
1. **Interest Match**: Buyer's interests align with waste type
2. **Price Match**: Buyer's price range includes predicted price
3. **Quality Match**: Buyer accepts waste quality grade
4. **Location Match**: Geographic proximity bonus

#### Accuracy Metrics:

- **Top-5 Hit Rate**: % of actual buyers in top 5 recommendations
  - Formula: (Buyers in top-5 / Total actual buyers) × 100
  - Goal: > 70%

- **Recommendation Accuracy**: How accurate are recommendations
  - Formula: (Correct recommendations / Total recommendations) × 100
  - Goal: > 80%

- **Match Score**: Individual buyer relevance (0-1)
  - Based on: Buyer rating, interest overlap, price proximity

---

### 5. **Carbon Impact Calculation**
**Purpose:** Calculate environmental impact (CO₂ avoided, tree equivalents, energy savings)
**Model:** Factor-based calculation with waste-specific coefficients

#### Carbon Factors by Waste Type:

| Waste Type | Energy (kg CO₂/kg) | Biochar (kg CO₂/kg) | Compost (kg CO₂/kg) |
|-----------|-------------------|-------------------|-------------------|
| Rice Husk | 2.5 | 3.2 | 1.8 |
| Wheat Straw | 2.3 | 3.0 | 1.6 |
| Cotton Stalks | 2.7 | 3.4 | 2.0 |
| Groundnut Shells | 2.4 | 3.1 | 1.9 |

#### Accuracy Metrics:

- **MAE (kg CO₂)**: Mean absolute error in CO₂ calculation
  - Goal: < 100 kg CO₂
  
- **MAPE (%)**: Percentage error
  - Goal: < 5%
  
- **R² Score**: Consistency of predictions
  - Goal: > 0.9

---

## 📈 Complete Analysis Pipeline

The `ai_system.py` provides an integrated analysis combining all 5 modules.

### Overall Marketplace Score (0-100%):
```
Weight Distribution:
  - Classification: 20% (accuracy of waste identification)
  - Quality: 25% (quality of waste)
  - Price: 20% (confidence in price prediction)
  - Buyer Match: 20% (availability of suitable buyers)
  - Carbon Impact: 15% (environmental benefit)

Final Score = 100 × (0.2×clf + 0.25×qual + 0.2×price + 0.2×buyer + 0.15×carbon)
```

---

## 🧪 Testing & Benchmarking

### Run Complete Test Suite:
```bash
python ai_metrics_test.py
```

### Performance Benchmarks:
- Average inference time
- Min/Max inference time
- Throughput (images/second)

---

## 📊 Expected Performance Targets

| Module | Metric | Target |
|--------|--------|--------|
| Classification | Accuracy | > 85% |
| Classification | Confidence | > 50% (top-1) |
| Price Prediction | MAPE | < 10% |
| Price Prediction | R² | > 0.8 |
| Quality | Moisture MAE | < 1% |
| Quality | Grade Accuracy | > 90% |
| Recommendations | Hit Rate | > 70% |
| Carbon | MAPE | < 5% |

---

**Version**: 1.0.0
**Status**: Ready for Integration
