#!/usr/bin/env python
"""
AI Model Utilities - Model Management, Testing, and Deployment
Provides utilities for training, evaluating, and deploying AI models
"""

import json
import shutil
from pathlib import Path
from typing import Dict, List, Optional, Tuple
import argparse
from datetime import datetime
import numpy as np
import pandas as pd

from plant_waste_pipeline import (
    load_or_train,
    DEFAULT_MODEL_PATH,
    DEFAULT_LABELS_PATH,
    DEFAULT_DATA_DIR,
)
from model_evaluation import ModelEvaluator
from ai_system import AgriculturalAISystem


class ModelManager:
    """Manage AI models - training, evaluation, backup, deployment"""

    def __init__(self, model_dir: Path = Path("models"), results_dir: Path = Path("results")):
        self.model_dir = model_dir
        self.results_dir = results_dir
        self.model_dir.mkdir(parents=True, exist_ok=True)
        self.results_dir.mkdir(parents=True, exist_ok=True)

    # ======================
    # MODEL TRAINING
    # ======================

    def train_model(
        self,
        dataset_dir: Path = DEFAULT_DATA_DIR,
        epochs: int = 15,
        batch_size: int = 32,
    ) -> Dict:
        """Train classification model"""
        print(f"\n🚀 Starting model training...")
        print(f"  Dataset: {dataset_dir}")
        print(f"  Epochs: {epochs}")
        print(f"  Batch Size: {batch_size}")

        try:
            model, labels = load_or_train(
                model_path=DEFAULT_MODEL_PATH,
                labels_path=DEFAULT_LABELS_PATH,
                data_dir=dataset_dir,
                epochs=epochs,
                batch_size=batch_size,
                retrain=True,
            )

            result = {
                "status": "success",
                "timestamp": datetime.now().isoformat(),
                "model_path": str(DEFAULT_MODEL_PATH),
                "labels_path": str(DEFAULT_LABELS_PATH),
                "num_classes": len(labels),
                "labels": labels,
                "epochs": epochs,
                "batch_size": batch_size,
            }

            print(f"✅ Training completed!")
            print(f"  Classes: {len(labels)}")
            print(f"  Model saved to: {DEFAULT_MODEL_PATH}")

            return result

        except Exception as e:
            print(f"❌ Training failed: {e}")
            return {"status": "failed", "error": str(e)}

    # ======================
    # MODEL EVALUATION
    # ======================

    def evaluate_model(self, test_dir: Path) -> Dict:
        """Evaluate model on test set"""
        print(f"\n📊 Evaluating model...")
        print(f"  Test directory: {test_dir}")

        evaluator = ModelEvaluator()

        try:
            results = evaluator.evaluate_classification(test_dir)

            evaluation_report = {
                "timestamp": datetime.now().isoformat(),
                "model": str(DEFAULT_MODEL_PATH),
                "test_dataset": str(test_dir),
                "metrics": results,
                "status": "PASS" if results["accuracy"] > 0.80 else "WARN" if results["accuracy"] > 0.70 else "FAIL",
            }

            # Save report
            report_path = self.results_dir / f"evaluation_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            with open(report_path, "w") as f:
                json.dump(evaluation_report, f, indent=2, default=str)

            print(f"✅ Evaluation completed!")
            print(f"  Accuracy:  {results['accuracy']:.2%}")
            print(f"  Precision: {results['precision']:.2%}")
            print(f"  Recall:    {results['recall']:.2%}")
            print(f"  F1-Score:  {results['f1_score']:.2%}")
            print(f"  Report saved to: {report_path}")

            return evaluation_report

        except Exception as e:
            print(f"❌ Evaluation failed: {e}")
            return {"status": "failed", "error": str(e)}

    # ======================
    # MODEL BACKUP & RESTORE
    # ======================

    def backup_model(self, backup_dir: Optional[Path] = None) -> Path:
        """Backup current model"""
        if backup_dir is None:
            backup_dir = self.model_dir / "backups"

        backup_dir.mkdir(parents=True, exist_ok=True)

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_name = f"model_backup_{timestamp}"
        backup_path = backup_dir / backup_name

        try:
            backup_path.mkdir(parents=True, exist_ok=True)

            # Copy model files
            if DEFAULT_MODEL_PATH.exists():
                shutil.copy2(DEFAULT_MODEL_PATH, backup_path / DEFAULT_MODEL_PATH.name)
            if DEFAULT_LABELS_PATH.exists():
                shutil.copy2(DEFAULT_LABELS_PATH, backup_path / DEFAULT_LABELS_PATH.name)

            print(f"✅ Model backed up to: {backup_path}")
            return backup_path

        except Exception as e:
            print(f"❌ Backup failed: {e}")
            return None

    def restore_model(self, backup_path: Path) -> bool:
        """Restore model from backup"""
        try:
            model_file = backup_path / DEFAULT_MODEL_PATH.name
            labels_file = backup_path / DEFAULT_LABELS_PATH.name

            if model_file.exists():
                shutil.copy2(model_file, DEFAULT_MODEL_PATH)
            if labels_file.exists():
                shutil.copy2(labels_file, DEFAULT_LABELS_PATH)

            print(f"✅ Model restored from: {backup_path}")
            return True

        except Exception as e:
            print(f"❌ Restore failed: {e}")
            return False

    # ======================
    # MODEL COMPARISON
    # ======================

    def compare_models(self, test_dir: Path, models: List[Path]) -> Dict:
        """Compare multiple models"""
        print(f"\n📊 Comparing {len(models)} models...")

        results = {
            "timestamp": datetime.now().isoformat(),
            "test_dataset": str(test_dir),
            "models": {},
        }

        for model_path in models:
            if not model_path.exists():
                print(f"  ⚠️  Model not found: {model_path}")
                continue

            try:
                # Temporarily load model for evaluation
                evaluator = ModelEvaluator(model_path)
                eval_results = evaluator.evaluate_classification(test_dir)

                results["models"][str(model_path)] = {
                    "accuracy": eval_results["accuracy"],
                    "precision": eval_results["precision"],
                    "recall": eval_results["recall"],
                    "f1_score": eval_results["f1_score"],
                }

                print(f"  ✓ {model_path.name}: Accuracy {eval_results['accuracy']:.2%}")

            except Exception as e:
                print(f"  ✗ {model_path.name}: Failed - {e}")

        # Find best model
        if results["models"]:
            best_model = max(results["models"].items(), key=lambda x: x[1]["accuracy"])
            results["best_model"] = best_model[0]
            results["best_accuracy"] = best_model[1]["accuracy"]

        return results

    # ======================
    # PERFORMANCE REPORT
    # ======================

    def generate_performance_report(self) -> Dict:
        """Generate comprehensive performance report"""
        print(f"\n📈 Generating performance report...")

        ai_system = AgriculturalAISystem()
        performance = ai_system.get_performance_report()

        # Add model info
        evaluator = ModelEvaluator()
        performance["model_metrics"] = evaluator.results or {}

        # Add system info
        performance["system_info"] = {
            "model_path": str(DEFAULT_MODEL_PATH),
            "labels_path": str(DEFAULT_LABELS_PATH),
            "num_classes": len(evaluator.labels),
            "timestamp": datetime.now().isoformat(),
        }

        # Save report
        report_path = self.results_dir / f"performance_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(report_path, "w") as f:
            json.dump(performance, f, indent=2, default=str)

        print(f"✅ Report saved to: {report_path}")
        return performance

    # ======================
    # BATCH PREDICTION
    # ======================

    def batch_predict(self, image_dir: Path, output_file: Optional[Path] = None) -> Dict:
        """Predict on batch of images"""
        print(f"\n🖼️  Batch prediction on images in: {image_dir}")

        ai_system = AgriculturalAISystem()
        predictions = []

        image_files = list(image_dir.glob("*.jpg")) + list(image_dir.glob("*.jfif")) + list(image_dir.glob("*.png"))

        print(f"Found {len(image_files)} images\n")

        for i, image_file in enumerate(image_files, 1):
            try:
                analysis = ai_system.analyze_waste_complete(image_file, quantity_kg=5000)

                pred = {
                    "image": image_file.name,
                    "waste_type": analysis.get("classification", {}).get("predicted_type"),
                    "confidence": analysis.get("classification", {}).get("confidence"),
                    "price": analysis.get("price", {}).get("predicted_price_per_kg"),
                    "quality_score": analysis.get("quality", {}).get("quality_score"),
                    "buyer_count": len(analysis.get("buyer_recommendations", [])),
                    "co2_avoided": analysis.get("carbon_impact", {}).get("co2_avoided_kg"),
                    "status": analysis.get("status"),
                }

                predictions.append(pred)
                print(f"  {i}/{len(image_files)} ✓ {image_file.name}")

            except Exception as e:
                print(f"  {i}/{len(image_files)} ✗ {image_file.name}: {e}")

        # Save predictions
        if output_file is None:
            output_file = self.results_dir / f"batch_predictions_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"

        with open(output_file, "w") as f:
            json.dump(predictions, f, indent=2)

        print(f"\n✅ Batch prediction completed!")
        print(f"  Processed: {len(predictions)} images")
        print(f"  Results saved to: {output_file}")

        return {"count": len(predictions), "output": str(output_file), "predictions": predictions}

    # ======================
    # STATISTICS
    # ======================

    def get_model_statistics(self) -> Dict:
        """Get model statistics"""
        print(f"\n📊 Model Statistics:")

        evaluator = ModelEvaluator()

        stats = {
            "model_file": str(DEFAULT_MODEL_PATH),
            "labels_file": str(DEFAULT_LABELS_PATH),
            "classes": evaluator.labels,
            "num_classes": len(evaluator.labels),
            "model_exists": DEFAULT_MODEL_PATH.exists(),
            "labels_exist": DEFAULT_LABELS_PATH.exists(),
        }

        if DEFAULT_MODEL_PATH.exists():
            model_size_mb = DEFAULT_MODEL_PATH.stat().st_size / (1024 * 1024)
            stats["model_size_mb"] = round(model_size_mb, 2)

        return stats


# ======================
# CLI INTERFACE
# ======================

def main():
    parser = argparse.ArgumentParser(description="AI Model Management Utilities")

    subparsers = parser.add_subparsers(dest="command", help="Command to execute")

    # Train command
    train_parser = subparsers.add_parser("train", help="Train model")
    train_parser.add_argument("--dataset", type=str, default=str(DEFAULT_DATA_DIR), help="Dataset directory")
    train_parser.add_argument("--epochs", type=int, default=15, help="Number of epochs")
    train_parser.add_argument("--batch-size", type=int, default=32, help="Batch size")

    # Evaluate command
    eval_parser = subparsers.add_parser("evaluate", help="Evaluate model")
    eval_parser.add_argument("--test-dir", type=str, required=True, help="Test directory")

    # Backup command
    subparsers.add_parser("backup", help="Backup model")

    # Restore command
    restore_parser = subparsers.add_parser("restore", help="Restore model from backup")
    restore_parser.add_argument("--backup-dir", type=str, required=True, help="Backup directory")

    # Batch predict command
    batch_parser = subparsers.add_parser("batch", help="Batch prediction")
    batch_parser.add_argument("--image-dir", type=str, required=True, help="Image directory")
    batch_parser.add_argument("--output", type=str, help="Output file")

    # Performance report command
    subparsers.add_parser("report", help="Generate performance report")

    # Statistics command
    subparsers.add_parser("stats", help="Show model statistics")

    args = parser.parse_args()

    manager = ModelManager()

    if args.command == "train":
        manager.train_model(
            Path(args.dataset),
            epochs=args.epochs,
            batch_size=args.batch_size,
        )

    elif args.command == "evaluate":
        manager.evaluate_model(Path(args.test_dir))

    elif args.command == "backup":
        manager.backup_model()

    elif args.command == "restore":
        manager.restore_model(Path(args.backup_dir))

    elif args.command == "batch":
        output = Path(args.output) if args.output else None
        manager.batch_predict(Path(args.image_dir), output)

    elif args.command == "report":
        report = manager.generate_performance_report()
        print(json.dumps(report, indent=2, default=str))

    elif args.command == "stats":
        stats = manager.get_model_statistics()
        print(json.dumps(stats, indent=2, default=str))

    else:
        parser.print_help()


if __name__ == "__main__":
    main()
