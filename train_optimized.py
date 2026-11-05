#!/usr/bin/env python
"""
=============================================================
  Agriculture Waste Marketplace — High Accuracy Model Training
=============================================================
Key Improvements for High Accuracy & High Confidence:
  1. Proper MobileNetV2 input normalization: maps [0, 255] -> [-1, 1]
     using keras.applications.mobilenet_v2.preprocess_input.
  2. Compact, regularized classifier head (prevents overfitting).
  3. Tuned two-phase learning rates:
     - Phase 1 (Frozen Backbone): lr=1e-3
     - Phase 2 (Fine-tune top 40 layers): lr=1e-4
  4. Dynamic data augmentation: RandomFlip, RandomRotation(0.2),
     RandomZoom(0.2), RandomContrast(0.2).
  5. Saves to plant_classifier.keras and plant_classifier_improved.keras.
"""

import os, sys, json, shutil
os.environ.setdefault("TF_CPP_MIN_LOG_LEVEL", "2")
from pathlib import Path
from typing import List, Tuple

for _s in (sys.stdout, sys.stderr):
    if _s and hasattr(_s, "reconfigure"):
        try: _s.reconfigure(encoding="utf-8")
        except: pass

import numpy as np
import tensorflow as tf
from tensorflow import keras
from tensorflow.keras import layers
tf.get_logger().setLevel("ERROR")

PROJECT_ROOT  = Path(__file__).resolve().parent
DATA_DIR      = PROJECT_ROOT / "Dataset" / "prepared_dataset_final"
MODEL_DIR     = PROJECT_ROOT / "models"
MODEL_PATH    = MODEL_DIR / "plant_classifier.keras"
LABELS_PATH   = MODEL_DIR / "plant_classifier_labels.json"

IMG_SIZE      = (224, 224)
BATCH_SIZE    = 32
VAL_SPLIT     = 0.20
SEED          = 42


def make_datasets(data_dir: Path):
    common = dict(
        directory=str(data_dir),
        image_size=IMG_SIZE,
        batch_size=BATCH_SIZE,
        label_mode="categorical",
        seed=SEED,
        validation_split=VAL_SPLIT,
        shuffle=True,
    )
    train_ds = keras.utils.image_dataset_from_directory(subset="training", **common)
    val_ds   = keras.utils.image_dataset_from_directory(subset="validation", **common)
    class_names: List[str] = train_ds.class_names

    AUTOTUNE = tf.data.AUTOTUNE

    # Data augmentation pipeline
    augment_layer = keras.Sequential([
        layers.RandomFlip("horizontal"),
        layers.RandomRotation(0.2),
        layers.RandomZoom(0.2),
        layers.RandomContrast(0.2),
    ], name="augmentation")

    # MobileNetV2 preprocess_input takes [0, 255] and converts to [-1, 1]
    def prep_train(x, y):
        x = augment_layer(x, training=True)
        x = keras.applications.mobilenet_v2.preprocess_input(x)
        return x, y

    def prep_val(x, y):
        x = keras.applications.mobilenet_v2.preprocess_input(x)
        return x, y

    train_ds = train_ds.map(prep_train, num_parallel_calls=AUTOTUNE).prefetch(AUTOTUNE)
    val_ds   = val_ds.map(prep_val,   num_parallel_calls=AUTOTUNE).prefetch(AUTOTUNE)
    return train_ds, val_ds, class_names


def build_model(num_classes: int) -> Tuple[keras.Model, keras.Model]:
    inputs = layers.Input(shape=IMG_SIZE + (3,), name="input_image")

    base = keras.applications.MobileNetV2(
        input_shape=IMG_SIZE + (3,),
        include_top=False,
        weights="imagenet",
        pooling=None,
    )
    base.trainable = False

    x = base(inputs, training=False)
    x = layers.GlobalAveragePooling2D(name="gap")(x)
    x = layers.BatchNormalization()(x)
    x = layers.Dropout(0.35)(x)
    x = layers.Dense(192, activation="relu", kernel_regularizer=keras.regularizers.l2(1e-4))(x)
    x = layers.BatchNormalization()(x)
    x = layers.Dropout(0.25)(x)
    outputs = layers.Dense(num_classes, activation="softmax", name="predictions")(x)

    model = keras.Model(inputs, outputs, name="agri_waste_optimized")
    return model, base


def main():
    print("="*60)
    print("  HIGH ACCURACY AGRICULTURE WASTE MODEL TRAINING")
    print("="*60)
    print(f"Data Dir: {DATA_DIR}")

    train_ds, val_ds, class_names = make_datasets(DATA_DIR)
    num_classes = len(class_names)
    print(f"Classes ({num_classes}): {class_names}")

    model, base = build_model(num_classes)
    model.compile(
        optimizer=keras.optimizers.Adam(learning_rate=1e-3),
        loss="categorical_crossentropy",
        metrics=["accuracy", keras.metrics.Precision(name="precision"), keras.metrics.Recall(name="recall")],
    )

    MODEL_DIR.mkdir(parents=True, exist_ok=True)

    callbacks_p1 = [
        keras.callbacks.EarlyStopping(monitor="val_accuracy", patience=4, restore_best_weights=True, verbose=1),
        keras.callbacks.ReduceLROnPlateau(monitor="val_loss", factor=0.5, patience=2, min_lr=1e-5, verbose=1),
        keras.callbacks.ModelCheckpoint(str(MODEL_PATH), monitor="val_accuracy", mode="max", save_best_only=True, verbose=1),
    ]

    print("\n>>> Phase 1: Training top layers (8 epochs, lr=1e-3)...")
    model.fit(train_ds, validation_data=val_ds, epochs=8, callbacks=callbacks_p1)

    print("\n>>> Phase 2: Fine-tuning top 40 backbone layers (7 epochs, lr=1e-4)...")
    base.trainable = True
    for layer in base.layers[:-40]:
        layer.trainable = False

    model.compile(
        optimizer=keras.optimizers.Adam(learning_rate=1e-4),
        loss="categorical_crossentropy",
        metrics=["accuracy", keras.metrics.Precision(name="precision"), keras.metrics.Recall(name="recall")],
    )

    callbacks_p2 = [
        keras.callbacks.EarlyStopping(monitor="val_accuracy", patience=4, restore_best_weights=True, verbose=1),
        keras.callbacks.ReduceLROnPlateau(monitor="val_loss", factor=0.5, patience=2, min_lr=1e-6, verbose=1),
        keras.callbacks.ModelCheckpoint(str(MODEL_PATH), monitor="val_accuracy", mode="max", save_best_only=True, verbose=1),
    ]

    model.fit(train_ds, validation_data=val_ds, epochs=7, callbacks=callbacks_p2)

    # Save best checkpoint & labels
    if MODEL_PATH.exists():
        model = keras.models.load_model(str(MODEL_PATH))
        print(f"\n✓ Loaded best checkpoint from {MODEL_PATH}")

    with open(LABELS_PATH, "w", encoding="utf-8") as f:
        json.dump(class_names, f, indent=2)

    # Also save aliases
    alias_model = MODEL_DIR / "plant_classifier_improved.keras"
    alias_labels = MODEL_DIR / "plant_classifier_labels_improved.json"
    model.save(str(alias_model))
    shutil.copy(LABELS_PATH, alias_labels)
    print(f"✓ Saved models & labels to {MODEL_DIR}")

    # Evaluate
    print("\n>>> Final Evaluation on Validation Set:")
    results = model.evaluate(val_ds, verbose=1, return_dict=True)
    for k, v in results.items():
        print(f"  {k:15s}: {v:.4f}")

    print("\n=== TRAINING COMPLETED SUCCESSFULLY ===")


if __name__ == "__main__":
    main()

