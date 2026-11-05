#!/usr/bin/env python
"""
Train a CNN (MobileNetV2 transfer learning) on the crop_images dataset and save the model.
Usage:
  python train_crop_cnn.py --dataset-dir data/crop_images --epochs 12 --batch-size 32
"""
import argparse
from pathlib import Path

from plant_waste_pipeline import (
    DEFAULT_DATA_DIR,
    DEFAULT_LABELS_PATH,
    DEFAULT_MODEL_PATH,
    train_pipeline,
)


def main():
    parser = argparse.ArgumentParser(description="Train crop image CNN and save model")
    parser.add_argument("--dataset-dir", type=str, default=str(DEFAULT_DATA_DIR))
    parser.add_argument("--model", type=str, default=str(DEFAULT_MODEL_PATH))
    parser.add_argument("--labels", type=str, default=str(DEFAULT_LABELS_PATH))
    parser.add_argument("--epochs", type=int, default=12)
    parser.add_argument("--batch-size", type=int, default=32)
    args = parser.parse_args()

    data_dir = Path(args.dataset_dir)
    model_out = Path(args.model)
    labels_out = Path(args.labels)

    train_pipeline(
        data_dir=data_dir,
        model_out=model_out,
        labels_out=labels_out,
        epochs=args.epochs,
        batch_size=args.batch_size,
    )


if __name__ == "__main__":
    main()
