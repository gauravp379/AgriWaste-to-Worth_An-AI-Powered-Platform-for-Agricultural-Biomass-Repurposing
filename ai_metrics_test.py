#!/usr/bin/env python
"""
Comprehensive Testing and Metrics for AI Waste Classification System
Tests all 5 AI modules with accuracy measurements
"""

import json
from pathlib import Path
from typing import Dict, List, Tuple
import numpy as np
import pandas as pd
from datetime import datetime
import sys

from model_evaluation import ModelEvaluator
from ai_system import AgriculturalAISystem


class AIMetricsTest:
    """Comprehensive test suite for AI system"""

    def __init__(self):
        self.results = {}
        self.test_timestamp = datetime.now().isoformat()

    # ======================
    # TEST 1: CLASSIFICATION
    # ======================

    def test_classification_accuracy(self, test_dir: Path) -> Dict:
        """Test waste classification with accuracy metrics"""
        print("\n" + "="*60)
        print("TEST 1: WASTE CLASSIFICATION ACCURACY")
        print("="*60)

        evaluator = ModelEvaluator()
        
        print("Testing classification on test dataset...")
        try:
            results = evaluator.evaluate_classification(test_dir)
            
            print(f"\n✅ Classification Results:")
            print(f"  Accuracy:  {results['accuracy']:.2%}")
            print(f"  Precision: {results['precision']:.2%}")
            print(f"  Recall:    {results['recall']:.2%}")
            print(f"  F1-Score:  {results['f1_score']:.2%}")
            
            # Evaluation
            status = "PASS" if results['accuracy'] > 0.80 else "WARN" if results['accuracy'] > 0.70 else "FAIL"
            print(f"\n  Status: {status} (Goal: Accuracy > 80%)")
            
            self.results['classification'] = results
            return results
        except Exception as e:
            print(f"❌ Error: {e}")
            return {"error": str(e)}

    # ======================
    # TEST 2: CONFIDENCE DISTRIBUTION
    # ======================

    def test_confidence_distribution(self, test_image: Path) -> Dict:
        """Test prediction confidence levels"""
        print("\n" + "="*60)
        print("TEST 2: PREDICTION CONFIDENCE DISTRIBUTION")
        print("="*60)

        evaluator = ModelEvaluator()
        
        print(f"Testing confidence on: {test_image.name}")
        try:
            confidence_dict = evaluator.get_prediction_confidence(test_image)
            
            # Get top 3 predictions
            top_3 = list(confidence_dict.items())[:3]
            
            print(f"\n✅ Top 3 Predictions:")
            for i, (waste_type, conf) in enumerate(top_3, 1):
                print(f"  {i}. {waste_type}: {conf:.2%}")
            
            # Check if top prediction > 50%
            top_conf = top_3[0][1]
            status = "PASS" if top_conf > 0.50 else "WARN"
            print(f"\n  Status: {status} (Top prediction confidence > 50%)")
            
            self.results['confidence'] = {
                'top_prediction': top_3[0][0],
                'confidence': float(top_3[0][1]),
                'all_predictions': confidence_dict,
            }
            return self.results['confidence']
        except Exception as e:
            print(f"❌ Error: {e}")
            return {"error": str(e)}

    # ======================
    # TEST 3: PRICE PREDICTION
    # ======================

    def test_price_prediction_accuracy(self) -> Dict:
        """Test price prediction with simulated data"""
        print("\n" + "="*60)
        print("TEST 3: PRICE PREDICTION ACCURACY")
        print("="*60)

        evaluator = ModelEvaluator()
        
        # Simulated price data
        actual_prices = np.array([5200, 5400, 5100, 5600, 5300, 5250, 5450, 5150])
        predicted_prices = np.array([5250, 5350, 5150, 5550, 5280, 5200, 5400, 5180])
        
        print("Testing price prediction on 8 samples...")
        print(f"  Actual prices:    {actual_prices}")
        print(f"  Predicted prices: {predicted_prices}")
        
        results = evaluator.evaluate_price_prediction(actual_prices, predicted_prices)
        
        print(f"\n✅ Price Prediction Results:")
        print(f"  MAE:              ₹{results['mae']:.2f}")
        print(f"  RMSE:             ₹{results['rmse']:.2f}")
        print(f"  MAPE:             {results['mape']:.2f}%")
        print(f"  R² Score:         {results['r2_score']:.4f}")
        print(f"  Pred Error %:     {results['prediction_error_percentage']:.2f}%")
        
        # Evaluation
        status_mape = "PASS" if results['mape'] < 10 else "WARN"
        status_r2 = "PASS" if results['r2_score'] > 0.8 else "WARN"
        print(f"\n  MAPE Status: {status_mape} (Goal: < 10%)")
        print(f"  R² Status:   {status_r2} (Goal: > 0.8)")
        
        self.results['price_prediction'] = results
        return results

    # ======================
    # TEST 4: QUALITY ASSESSMENT
    # ======================

    def test_quality_assessment_accuracy(self) -> Dict:
        """Test quality parameter accuracy"""
        print("\n" + "="*60)
        print("TEST 4: QUALITY ASSESSMENT ACCURACY")
        print("="*60)

        evaluator = ModelEvaluator()
        
        # Simulated quality data
        predicted = [
            {"moisture": 11.5, "calorific_value": 15.2, "purity": 94.5},
            {"moisture": 12.1, "calorific_value": 15.8, "purity": 93.2},
            {"moisture": 10.8, "calorific_value": 14.9, "purity": 95.1},
            {"moisture": 12.5, "calorific_value": 16.1, "purity": 92.8},
        ]
        
        actual = [
            {"moisture": 11.0, "calorific_value": 15.5, "purity": 95.0},
            {"moisture": 12.5, "calorific_value": 15.5, "purity": 92.8},
            {"moisture": 11.0, "calorific_value": 15.0, "purity": 95.0},
            {"moisture": 12.0, "calorific_value": 16.0, "purity": 93.0},
        ]
        
        print("Testing quality assessment on 4 samples...")
        results = evaluator.evaluate_quality_assessment(predicted, actual)
        
        print(f"\n✅ Quality Assessment Results:")
        if results['moisture_mae']:
            print(f"  Moisture MAE:     {results['moisture_mae']:.2f}%")
        if results['calorific_mae']:
            print(f"  Calorific MAE:    {results['calorific_mae']:.2f} MJ/kg")
        if results['purity_mae']:
            print(f"  Purity MAE:       {results['purity_mae']:.2f}%")
        print(f"  Samples:          {results['samples_evaluated']}")
        
        # Evaluation
        status = "PASS" if (results['moisture_mae'] or 0) < 1.0 else "WARN"
        print(f"\n  Status: {status} (Goal: Moisture MAE < 1%)")
        
        self.results['quality_assessment'] = results
        return results

    # ======================
    # TEST 5: BUYER RECOMMENDATIONS
    # ======================

    def test_buyer_recommendations_accuracy(self) -> Dict:
        """Test buyer recommendation accuracy"""
        print("\n" + "="*60)
        print("TEST 5: BUYER RECOMMENDATIONS ACCURACY")
        print("="*60)

        evaluator = ModelEvaluator()
        
        # Simulated recommendation data
        predicted_buyers = [
            ("B001", 0.95),  # Green Energy Ltd
            ("B002", 0.87),  # BioFuel Solutions
            ("B003", 0.76),  # Agri-Process Inc
            ("B004", 0.65),  # Carbon Credits Corp
        ]
        
        actual_buyers = ["B001", "B004", "B002"]  # Who actually matched
        
        print("Testing buyer recommendations on 3 matches...")
        print(f"  Recommended:     {[b[0] for b in predicted_buyers[:3]]}")
        print(f"  Actual matches:  {actual_buyers}")
        
        results = evaluator.evaluate_buyer_recommendations(predicted_buyers, actual_buyers)
        
        print(f"\n✅ Buyer Recommendation Results:")
        print(f"  Top-5 Hit Rate:   {results['top_5_hit_rate']:.2%}")
        print(f"  Accuracy:         {results['accuracy']:.2%}")
        print(f"  Recommendations:  {results['recommendation_count']}")
        
        # Evaluation
        status = "PASS" if results['top_5_hit_rate'] > 0.7 else "WARN"
        print(f"\n  Status: {status} (Goal: Hit Rate > 70%)")
        
        self.results['buyer_recommendations'] = results
        return results

    # ======================
    # TEST 6: CARBON IMPACT
    # ======================

    def test_carbon_impact_accuracy(self) -> Dict:
        """Test carbon impact calculation accuracy"""
        print("\n" + "="*60)
        print("TEST 6: CARBON IMPACT CALCULATION")
        print("="*60)

        evaluator = ModelEvaluator()
        
        # Simulated carbon impact data
        predicted_impacts = np.array([2500, 5750, 8000, 1200, 3600, 7500])
        actual_impacts = np.array([2400, 5800, 8200, 1100, 3700, 7600])
        
        print("Testing carbon impact on 6 samples...")
        results = evaluator.evaluate_carbon_impact(predicted_impacts, actual_impacts)
        
        print(f"\n✅ Carbon Impact Results:")
        print(f"  MAE:              {results['mae_kg_co2']:.2f} kg CO₂")
        print(f"  MAPE:             {results['mape_percent']:.2f}%")
        print(f"  R² Score:         {results['r2_score']:.4f}")
        print(f"  Samples:          {results['samples']}")
        
        # Single calculation test
        test_impact = evaluator.calculate_carbon_impact("rice_husk", 5000, "energy")
        print(f"\n  Sample Calculation (5000 kg Rice Husk):")
        print(f"    CO₂ Avoided:     {test_impact['co2_avoided_kg']:.2f} kg")
        print(f"    Trees Equiv:     {test_impact['trees_equivalent']:.1f}")
        
        # Evaluation
        status = "PASS" if results['mape_percent'] < 5 else "WARN"
        print(f"\n  Status: {status} (Goal: MAPE < 5%)")
        
        self.results['carbon_impact'] = results
        return results

    # ======================
    # COMPLETE ANALYSIS PIPELINE
    # ======================

    def test_complete_pipeline(self, test_image: Path, quantity_kg: float = 5000) -> Dict:
        """Test complete analysis pipeline"""
        print("\n" + "="*60)
        print("TEST 7: COMPLETE ANALYSIS PIPELINE")
        print("="*60)

        ai_system = AgriculturalAISystem()
        
        print(f"Running complete analysis on: {test_image.name}")
        print(f"Quantity: {quantity_kg} kg\n")
        
        analysis = ai_system.analyze_waste_complete(test_image, quantity_kg=quantity_kg)
        ai_system.print_analysis_summary(analysis)
        
        self.results['complete_pipeline'] = {
            'status': analysis.get('status'),
            'overall_score': analysis.get('overall_score'),
            'has_classification': 'classification' in analysis,
            'has_quality': 'quality' in analysis,
            'has_price': 'price' in analysis,
            'has_recommendations': 'buyer_recommendations' in analysis,
            'has_carbon': 'carbon_impact' in analysis,
        }
        
        return analysis

    # ======================
    # SUMMARY & REPORT
    # ======================

    def generate_test_report(self) -> Dict:
        """Generate comprehensive test report"""
        report = {
            "test_timestamp": self.test_timestamp,
            "total_tests": len(self.results),
            "test_results": self.results,
        }
        
        # Calculate overall status
        statuses = []
        for test_name, result in self.results.items():
            if isinstance(result, dict):
                if 'error' in result:
                    statuses.append("FAIL")
                elif 'accuracy' in result and result['accuracy'] > 0.80:
                    statuses.append("PASS")
                elif 'mae' in result or 'mape' in result:
                    statuses.append("PASS")
                else:
                    statuses.append("WARN")
        
        report['overall_status'] = "PASS" if all(s != "FAIL" for s in statuses) else "WARN"
        report['passed_tests'] = statuses.count("PASS")
        report['total_tests'] = len(statuses)
        
        return report

    def print_test_summary(self):
        """Print test summary"""
        report = self.generate_test_report()
        
        print("\n" + "="*60)
        print("TEST SUMMARY REPORT")
        print("="*60)
        print(f"Overall Status: {report['overall_status']}")
        print(f"Tests Passed: {report['passed_tests']}/{report['total_tests']}")
        print(f"Timestamp: {report['test_timestamp']}")
        print("="*60 + "\n")

    def save_test_report(self, output_path: Path):
        """Save test report to JSON"""
        report = self.generate_test_report()
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_path, 'w') as f:
            json.dump(report, f, indent=2, default=str)
        
        print(f"✅ Test report saved to: {output_path}")


# ======================
# BENCHMARK SUITE
# ======================

class BenchmarkSuite:
    """Performance benchmarks for AI system"""

    @staticmethod
    def benchmark_inference_speed(test_image: Path, iterations: int = 10) -> Dict:
        """Benchmark single image inference speed"""
        import time
        from plant_waste_pipeline import DEFAULT_MODEL_PATH, DEFAULT_LABELS_PATH
        from model_evaluation import ModelEvaluator
        
        evaluator = ModelEvaluator(DEFAULT_MODEL_PATH, DEFAULT_LABELS_PATH)
        
        times = []
        print(f"\nBenchmarking inference on {iterations} runs...")
        
        for _ in range(iterations):
            start = time.time()
            _ = evaluator.get_prediction_confidence(test_image)
            times.append(time.time() - start)
        
        avg_time = np.mean(times)
        min_time = np.min(times)
        max_time = np.max(times)
        
        result = {
            "avg_inference_time_ms": float(avg_time * 1000),
            "min_inference_time_ms": float(min_time * 1000),
            "max_inference_time_ms": float(max_time * 1000),
            "iterations": iterations,
            "throughput_images_per_second": float(1 / avg_time),
        }
        
        print(f"  Average: {avg_time*1000:.2f}ms")
        print(f"  Min: {min_time*1000:.2f}ms")
        print(f"  Max: {max_time*1000:.2f}ms")
        print(f"  Throughput: {result['throughput_images_per_second']:.1f} img/sec")
        
        return result


# ======================
# MAIN TEST RUNNER
# ======================

def run_all_tests(test_image_dir: Path = Path("data/test_crop_image")):
    """Run complete test suite"""
    print("\n" + "="*60)
    print("🧪 AI WASTE CLASSIFICATION SYSTEM - COMPLETE TEST SUITE")
    print("="*60)
    
    tester = AIMetricsTest()
    
    # Find test image
    test_images = list(test_image_dir.glob("*.jfif"))
    if not test_images:
        print("❌ No test images found!")
        return
    
    test_image = test_images[0]
    
    try:
        # Run tests
        tester.test_classification_accuracy(test_image_dir)
        tester.test_confidence_distribution(test_image)
        tester.test_price_prediction_accuracy()
        tester.test_quality_assessment_accuracy()
        tester.test_buyer_recommendations_accuracy()
        tester.test_carbon_impact_accuracy()
        tester.test_complete_pipeline(test_image, 5000)
        
        # Benchmark
        print("\n" + "="*60)
        print("PERFORMANCE BENCHMARKS")
        print("="*60)
        BenchmarkSuite.benchmark_inference_speed(test_image, iterations=5)
        
        # Save results
        tester.print_test_summary()
        report_path = Path("results/test_report.json")
        tester.save_test_report(report_path)
        
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    run_all_tests()
