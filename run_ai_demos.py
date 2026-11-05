#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Quick Start Guide - Running AI Model Evaluation and Testing
Execute all 5 AI modules with accuracy measurements
"""

import json
import sys
import io
from pathlib import Path
from typing import Optional

# Fix UTF-8 encoding on Windows
if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# Color output for terminal
class Colors:
    GREEN = '\033[92m'
    BLUE = '\033[94m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    BOLD = '\033[1m'
    END = '\033[0m'


def print_header(text: str):
    print(f"\n{Colors.BOLD}{Colors.BLUE}{'='*70}{Colors.END}")
    print(f"{Colors.BOLD}{Colors.BLUE}{text:^70}{Colors.END}")
    print(f"{Colors.BOLD}{Colors.BLUE}{'='*70}{Colors.END}\n")


def print_success(text: str):
    print(f"{Colors.GREEN}✅ {text}{Colors.END}")


def print_info(text: str):
    print(f"{Colors.BLUE}ℹ️  {text}{Colors.END}")


def print_warning(text: str):
    print(f"{Colors.YELLOW}⚠️  {text}{Colors.END}")


def print_error(text: str):
    print(f"{Colors.RED}❌ {text}{Colors.END}")


# =====================================================
# QUICK START FUNCTIONS
# =====================================================

def quick_demo_classification():
    """Quick demo of waste classification"""
    print_header("1️⃣  WASTE CLASSIFICATION DEMO")
    print_info("Demonstrating CNN-based image classification with accuracy metrics\n")

    try:
        from model_evaluation import ModelEvaluator
        from pathlib import Path

        evaluator = ModelEvaluator()

        # Find test image
        test_image = next(Path("data/test_crop_image").glob("*.jfif"), None)

        if not test_image:
            print_error("No test image found. Please add images to data/test_crop_image/")
            return

        print(f"Classifying: {test_image.name}\n")

        # Get confidence scores
        confidence = evaluator.get_prediction_confidence(test_image)

        # Show top 5 predictions
        print(f"{Colors.BOLD}Top 5 Predictions:{Colors.END}")
        for i, (waste_type, conf) in enumerate(list(confidence.items())[:5], 1):
            bar_length = int(conf * 40)
            bar = "█" * bar_length + "░" * (40 - bar_length)
            print(f"  {i}. {waste_type:20} {bar} {conf:.1%}")

        # Metrics info
        print(f"\n{Colors.BOLD}Classification Metrics:{Colors.END}")
        print(f"  Accuracy:  Measures correctly identified waste types")
        print(f"  Precision: When model predicts positive, how often correct")
        print(f"  Recall:    When true positive exists, how often found")
        print(f"  F1-Score:  Harmonic mean of precision and recall")
        print(f"  Goal:      Accuracy > 85%")

        print_success("Classification demo completed!\n")

    except Exception as e:
        print_error(f"Classification demo failed: {e}")


def quick_demo_price_prediction():
    """Quick demo of price prediction"""
    print_header("2️⃣  PRICE PREDICTION DEMO")
    print_info("Demonstrating ML-based price estimation with accuracy metrics\n")

    try:
        from model_evaluation import ModelEvaluator
        import numpy as np

        evaluator = ModelEvaluator()

        # Test price prediction
        actual_prices = np.array([5200, 5400, 5100, 5600, 5300])
        predicted_prices = np.array([5250, 5350, 5150, 5550, 5280])

        results = evaluator.evaluate_price_prediction(actual_prices, predicted_prices)

        print(f"{Colors.BOLD}Price Prediction Results:{Colors.END}")
        print(f"  MAE (Mean Absolute Error):  ₹{results['mae']:.2f}")
        print(f"  RMSE (Root Mean Squared):   ₹{results['rmse']:.2f}")
        print(f"  MAPE (Mean % Error):        {results['mape']:.2f}%")
        print(f"  R² Score:                   {results['r2_score']:.4f}")
        print(f"\n  Status: {'PASS' if results['mape'] < 10 else 'WARN'} (Goal: MAPE < 10%)")

        # Demo price calculation
        print(f"\n{Colors.BOLD}Sample Price Calculation (Rice Husk):{Colors.END}")
        price_pred = evaluator.predict_price("rice_husk", 1000, 11.5, [5200, 5300, 5250])
        print(f"  Quantity:           1000 kg")
        print(f"  Base Price:         ₹{price_pred['base_price']:.2f}/kg")
        print(f"  Moisture Adjust:    {price_pred['adjustments']['moisture']:.2%}")
        print(f"  Quantity Adjust:    {price_pred['adjustments']['quantity']:.2%}")
        print(f"  Predicted Price:    ₹{price_pred['predicted_price_per_kg']:.2f}/kg")
        print(f"  Total Value:        ₹{price_pred['predicted_price_per_kg'] * 1000:.2f}")
        print(f"  Confidence:         {price_pred['confidence']:.1%}")

        print_success("Price prediction demo completed!\n")

    except Exception as e:
        print_error(f"Price prediction demo failed: {e}")


def quick_demo_quality_assessment():
    """Quick demo of quality assessment"""
    print_header("3️⃣  QUALITY ASSESSMENT DEMO")
    print_info("Demonstrating quality parameter measurement and grading\n")

    try:
        from model_evaluation import ModelEvaluator

        evaluator = ModelEvaluator()

        waste_types = ["rice_husk", "wheat_straw", "cotton_stalks", "groundnut_shells"]

        print(f"{Colors.BOLD}Quality Assessment by Waste Type:{Colors.END}\n")

        for waste_type in waste_types:
            quality = evaluator.assess_waste_quality(waste_type)
            
            # Calculate quality score
            from ai_system import AgriculturalAISystem
            quality_score = AgriculturalAISystem._calculate_quality_score(quality)

            print(f"{Colors.BOLD}{waste_type.replace('_', ' ').title()}:{Colors.END}")
            print(f"  Grade:              {quality.get('quality_grade', 'A')}")
            print(f"  Score:              {quality_score:.1f}/100")
            print(f"  Moisture:           {quality['moisture_percent']:.1f}%")
            print(f"  Calorific Value:    {quality['calorific_value_mj_kg']:.1f} MJ/kg")
            print(f"  Purity:             {quality['purity_percent']:.1f}%")
            print(f"  Carbon Content:     {quality['carbon_content_percent']:.1f}%")
            print()

        print(f"{Colors.BOLD}Quality Metrics:{Colors.END}")
        print(f"  Moisture MAE:       Measure error in moisture prediction")
        print(f"  Calorific MAE:      Measure error in calorific value")
        print(f"  Purity MAE:         Measure error in purity percentage")
        print(f"  Goal:               MAE < 1% for moisture")

        print_success("Quality assessment demo completed!\n")

    except Exception as e:
        print_error(f"Quality assessment demo failed: {e}")


def quick_demo_buyer_recommendations():
    """Quick demo of buyer recommendations"""
    print_header("4️⃣  BUYER RECOMMENDATIONS DEMO")
    print_info("Demonstrating AI-powered buyer matching algorithm\n")

    try:
        from model_evaluation import ModelEvaluator

        evaluator = ModelEvaluator()

        waste_type = "rice_husk"
        price_range = (5000, 5500)

        print(f"Waste Type:   {waste_type}")
        print(f"Price Range:  ₹{price_range[0]} - ₹{price_range[1]}\n")

        recommendations = evaluator.recommend_buyers(waste_type, price_range)

        print(f"{Colors.BOLD}Recommended Buyers ({len(recommendations)} matches):{Colors.END}\n")

        for i, buyer in enumerate(recommendations, 1):
            bar_length = int(buyer['match_score'] * 40)
            bar = "█" * bar_length + "░" * (40 - bar_length)
            print(f"{i}. {buyer['name']}")
            print(f"   Type:         {buyer['type']}")
            print(f"   Match Score:  {bar} {buyer['match_score']:.1%}")
            print(f"   Rating:       {'⭐' * int(buyer['rating'])} ({buyer['rating']})")
            print()

        print(f"{Colors.BOLD}Recommendation Metrics:{Colors.END}")
        print(f"  Top-5 Hit Rate:     % of actual buyers in top 5 recommendations")
        print(f"  Accuracy:           Correctness of matches")
        print(f"  Goal:               Hit Rate > 70%")

        print_success("Buyer recommendations demo completed!\n")

    except Exception as e:
        print_error(f"Buyer recommendations demo failed: {e}")


def quick_demo_carbon_impact():
    """Quick demo of carbon impact calculation"""
    print_header("5️⃣  CARBON IMPACT CALCULATION DEMO")
    print_info("Demonstrating environmental impact tracking\n")

    try:
        from model_evaluation import ModelEvaluator

        evaluator = ModelEvaluator()

        # Test different quantities
        quantities = [1000, 5000, 10000]
        waste_type = "rice_husk"

        print(f"Waste Type: {waste_type}\n")
        print(f"{Colors.BOLD}Carbon Impact by Quantity:{Colors.END}\n")

        for qty in quantities:
            carbon = evaluator.calculate_carbon_impact(waste_type, qty, "energy")

            print(f"{qty:,} kg {waste_type.replace('_', ' ')}:")
            print(f"  CO₂ Avoided:        {carbon['co2_avoided_kg']:,.1f} kg")
            print(f"  Trees Equivalent:   {carbon['trees_equivalent']:.0f} trees")
            print(f"  Energy Equivalent:  {carbon['energy_equivalent_kwh']:,.0f} kWh")
            print(f"  Impact Category:    {carbon['impact_category']}")
            print()

        print(f"{Colors.BOLD}Carbon Metrics:{Colors.END}")
        print(f"  MAE:                Mean error in CO₂ calculation")
        print(f"  MAPE:               Percentage error")
        print(f"  R² Score:           Consistency of predictions")
        print(f"  Goal:               MAPE < 5%")

        print_success("Carbon impact demo completed!\n")

    except Exception as e:
        print_error(f"Carbon impact demo failed: {e}")


def run_complete_analysis():
    """Run complete waste analysis pipeline"""
    print_header("🔄 COMPLETE ANALYSIS PIPELINE")
    print_info("Running all 5 AI modules on a test image\n")

    try:
        from ai_system import AgriculturalAISystem
        from pathlib import Path

        # Find test image
        test_image = next(Path("data/test_crop_image").glob("*.jfif"), None)

        if not test_image:
            print_error("No test image found. Please add images to data/test_crop_image/")
            return

        ai_system = AgriculturalAISystem()

        print(f"Analyzing: {test_image.name}")
        print(f"Quantity: 5000 kg\n")

        analysis = ai_system.analyze_waste_complete(test_image, quantity_kg=5000)
        ai_system.print_analysis_summary(analysis)

        # Save report
        report_path = Path("results/complete_analysis.json")
        ai_system.save_analysis_report(analysis, report_path)
        print_success(f"Analysis report saved to {report_path}\n")

    except Exception as e:
        print_error(f"Complete analysis failed: {e}")


def run_test_suite():
    """Run comprehensive test suite"""
    print_header("🧪 COMPREHENSIVE TEST SUITE")
    print_info("Running all accuracy metric tests\n")

    try:
        from ai_metrics_test import run_all_tests

        run_all_tests()
        print_success("Test suite completed!\n")

    except Exception as e:
        print_error(f"Test suite failed: {e}")


# =====================================================
# MAIN MENU
# =====================================================

def show_menu():
    """Display main menu"""
    print_header("🌾 AGRICULTURE WASTE AI SYSTEM - QUICK START")

    print(f"""
{Colors.BOLD}Available Demos:{Colors.END}
  1. Waste Classification (CNN)
  2. Price Prediction (ML)
  3. Quality Assessment
  4. Buyer Recommendations
  5. Carbon Impact Calculation
  6. Complete Analysis Pipeline (Image → All 5 Modules)
  7. Run Complete Test Suite (All Accuracy Metrics)
  8. Run All Demos Sequentially
  
{Colors.BOLD}Information:{Colors.END}
  9. View Metrics Guide (AI_METRICS_GUIDE.md)
  0. Exit

{Colors.BOLD}Select an option (0-9):{Colors.END} """)


def main():
    """Main entry point"""
    print_header("Welcome to Agriculture Waste Marketplace AI System")

    while True:
        show_menu()

        choice = input().strip()

        if choice == '1':
            quick_demo_classification()
        elif choice == '2':
            quick_demo_price_prediction()
        elif choice == '3':
            quick_demo_quality_assessment()
        elif choice == '4':
            quick_demo_buyer_recommendations()
        elif choice == '5':
            quick_demo_carbon_impact()
        elif choice == '6':
            run_complete_analysis()
        elif choice == '7':
            run_test_suite()
        elif choice == '8':
            print_info("Running all demos sequentially...\n")
            quick_demo_classification()
            quick_demo_price_prediction()
            quick_demo_quality_assessment()
            quick_demo_buyer_recommendations()
            quick_demo_carbon_impact()
            run_complete_analysis()
            print_success("All demos completed!")
        elif choice == '9':
            print_info("Opening AI_METRICS_GUIDE.md...")
            guide_path = Path("AI_METRICS_GUIDE.md")
            if guide_path.exists():
                print(f"File location: {guide_path.resolve()}")
                print_success("Please open the file to view the complete metrics guide\n")
            else:
                print_error("Guide file not found\n")
        elif choice == '0':
            print_success("Exiting...\n")
            break
        else:
            print_error(f"Invalid choice. Please select 0-9\n")

        input(f"{Colors.BOLD}Press Enter to continue...{Colors.END}\n")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print_error("\nInterrupted by user")
        sys.exit(1)
    except Exception as e:
        print_error(f"Unexpected error: {e}")
        sys.exit(1)
