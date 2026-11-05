#!/usr/bin/env python
import argparse
import json
import os
from pathlib import Path
from typing import Dict, List, Optional, Tuple

import numpy as np
import pandas as pd
import tensorflow as tf
from tensorflow import keras
from tensorflow.keras import layers


# -----------------------------
# Constants / Defaults
# -----------------------------
PROJECT_ROOT = Path(__file__).resolve().parent
DEFAULT_DATA_DIR = PROJECT_ROOT / "data" / "crop_images"
DEFAULT_TEST_DIR = PROJECT_ROOT / "data" / "test_crop_image"
DEFAULT_MODEL_DIR = PROJECT_ROOT / "models"
DEFAULT_MODEL_PATH = DEFAULT_MODEL_DIR / "plant_classifier.keras"
DEFAULT_LABELS_PATH = DEFAULT_MODEL_DIR / "plant_classifier_labels.json"
DEFAULT_AGRI_CSV = PROJECT_ROOT / "data" / "Agricultural_Waste_Core_Dataset.csv"
DEFAULT_MAPPING_CSV = PROJECT_ROOT / "data" / "Waste_to_Product_Mapping_Dataset.csv"


# -----------------------------
# Utility helpers
# -----------------------------

def ensure_dir(path: Path) -> None:
    path.mkdir(parents=True, exist_ok=True)


def find_first_column(df: pd.DataFrame, candidates: List[str]) -> Optional[str]:
    lower_map = {c.lower(): c for c in df.columns}
    for name in candidates:
        if name.lower() in lower_map:
            return lower_map[name.lower()]
    # fuzzy contains match
    for col in df.columns:
        cl = col.lower().replace(" ", "").replace("_", "")
        for cand in candidates:
            candl = cand.lower().replace(" ", "").replace("_", "")
            if candl in cl or cl in candl:
                return col
    return None


def load_csv_safe(path: Path) -> pd.DataFrame:
    try:
        return pd.read_csv(path)
    except UnicodeDecodeError:
        return pd.read_csv(path, encoding="latin-1")


# -----------------------------
# Model building / data loading
# -----------------------------

def make_datasets(
    data_dir: Path,
    img_size: Tuple[int, int] = (224, 224),
    batch_size: int = 32,
    val_split: float = 0.2,
    seed: int = 42,
) -> Tuple[tf.data.Dataset, tf.data.Dataset, List[str]]:
    train_ds = tf.keras.preprocessing.image_dataset_from_directory(
        data_dir,
        validation_split=val_split,
        subset="training",
        seed=seed,
        image_size=img_size,
        batch_size=batch_size,
        label_mode="int",
    )
    val_ds = tf.keras.preprocessing.image_dataset_from_directory(
        data_dir,
        validation_split=val_split,
        subset="validation",
        seed=seed,
        image_size=img_size,
        batch_size=batch_size,
        label_mode="int",
    )
    class_names = train_ds.class_names

    # Skip any unreadable/corrupt files gracefully
    try:
        train_ds = train_ds.apply(tf.data.experimental.ignore_errors())
        val_ds = val_ds.apply(tf.data.experimental.ignore_errors())
    except Exception:
        # Fallback for TF versions exposing ignore_errors on Dataset
        if hasattr(tf.data.Dataset, "ignore_errors"):
            train_ds = train_ds.ignore_errors()
            val_ds = val_ds.ignore_errors()

    AUTOTUNE = tf.data.AUTOTUNE

    data_augmentation = keras.Sequential(
        [
            layers.RandomFlip("horizontal"),
            layers.RandomRotation(0.1),
            layers.RandomZoom(0.1),
            layers.RandomContrast(0.1),
        ],
        name="data_augmentation",
    )

    def augment(x, y):
        x = data_augmentation(x)
        return x, y

    train_ds = train_ds.shuffle(1024).map(augment, num_parallel_calls=AUTOTUNE)

    # Prefetch
    train_ds = train_ds.prefetch(buffer_size=AUTOTUNE)
    val_ds = val_ds.prefetch(buffer_size=AUTOTUNE)

    return train_ds, val_ds, class_names


def build_model(num_classes: int, img_size: Tuple[int, int] = (224, 224)) -> keras.Model:
    inputs = layers.Input(shape=(img_size[0], img_size[1], 3))
    # Use MobileNetV2 backbone with imagenet weights
    base = tf.keras.applications.MobileNetV2(
        include_top=False,
        weights="imagenet",
        input_tensor=inputs,
        pooling="avg",
    )
    base.trainable = False  # start with frozen base

    x = layers.BatchNormalization()(base.output)
    x = layers.Dropout(0.3)(x)
    outputs = layers.Dense(num_classes, activation="softmax")(x)

    model = keras.Model(inputs=inputs, outputs=outputs)
    model.compile(
        optimizer=keras.optimizers.Adam(learning_rate=1e-3),
        loss=keras.losses.SparseCategoricalCrossentropy(),
        metrics=["accuracy"],
    )
    return model


def fine_tune(model: keras.Model, unfrozen_from: int = 100, lr: float = 1e-4) -> None:
    # Unfreeze the base model for fine-tuning
    base_model = None
    for layer in model.layers:
        if isinstance(layer, tf.keras.Model):
            base_model = layer
            break
    if base_model is None:
        return
    for layer in base_model.layers[:unfrozen_from]:
        layer.trainable = False
    for layer in base_model.layers[unfrozen_from:]:
        layer.trainable = True
    model.compile(
        optimizer=keras.optimizers.Adam(learning_rate=lr),
        loss=keras.losses.SparseCategoricalCrossentropy(),
        metrics=["accuracy"],
    )


def save_labels(labels: List[str], path: Path) -> None:
    ensure_dir(path.parent)
    with open(path, "w", encoding="utf-8") as f:
        json.dump({"class_names": labels}, f, ensure_ascii=False, indent=2)


def load_labels(path: Path) -> List[str]:
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
    if isinstance(data, list):
        return data
    if isinstance(data, dict):
        return list(data.get("class_names", []))
    return []


# -----------------------------
# Training / Inference
# -----------------------------

def train_pipeline(
    data_dir: Path,
    model_out: Path = DEFAULT_MODEL_PATH,
    labels_out: Path = DEFAULT_LABELS_PATH,
    epochs: int = 10,
    batch_size: int = 32,
    img_size: Tuple[int, int] = (224, 224),
    fine_tune_from: int = 100,
) -> Tuple[keras.Model, List[str]]:
    train_ds, val_ds, class_names = make_datasets(data_dir, img_size, batch_size)
    model = build_model(num_classes=len(class_names), img_size=img_size)

    callbacks = [
        keras.callbacks.EarlyStopping(
            monitor="val_accuracy", patience=5, restore_best_weights=True
        ),
        keras.callbacks.ModelCheckpoint(
            filepath=str(model_out),
            save_best_only=True,
            monitor="val_accuracy",
            mode="max",
        ),
    ]

    model.fit(train_ds, validation_data=val_ds, epochs=epochs, callbacks=callbacks)

    # Optional fine-tuning
    fine_tune(model, unfrozen_from=fine_tune_from, lr=1e-5)
    model.fit(train_ds, validation_data=val_ds, epochs=max(2, epochs // 3), callbacks=callbacks)

    ensure_dir(model_out.parent)
    model.save(model_out)
    save_labels(class_names, labels_out)

    return model, class_names


def load_or_train(
    model_path: Path,
    labels_path: Path,
    data_dir: Optional[Path],
    epochs: int,
    batch_size: int,
    retrain: bool,
) -> Tuple[keras.Model, List[str]]:
    model_exists = model_path.exists()
    labels_exist = labels_path.exists()

    if model_exists and labels_exist and not retrain:
        model = keras.models.load_model(model_path)
        labels = load_labels(labels_path)
        return model, labels

    if data_dir is None:
        raise SystemExit(
            "Model not found or retraining requested, but no dataset directory provided. "
            "Pass --dataset-dir to train."
        )

    return train_pipeline(
        data_dir=data_dir,
        model_out=model_path,
        labels_out=labels_path,
        epochs=epochs,
        batch_size=batch_size,
    )


def preprocess_image(img_path: Path, img_size: Tuple[int, int] = (224, 224)) -> tf.Tensor:
    from PIL import Image
    img = Image.open(str(img_path)).convert('RGB')
    img = img.resize(img_size, Image.Resampling.LANCZOS)
    arr = np.array(img, dtype=np.float32) / 255.0
    arr = np.expand_dims(arr, axis=0)
    return arr


def predict_class(model: keras.Model, labels: List[str], img_path: Path) -> Tuple[str, float]:
    arr = preprocess_image(img_path)
    preds = model.predict(arr, verbose=0)[0]
    idx = int(np.argmax(preds))
    return labels[idx], float(preds[idx])


# -----------------------------
# CSV mapping logic
# -----------------------------

def lookup_waste_info(
    crop_name: str,
    agri_csv: Path = DEFAULT_AGRI_CSV,
    mapping_csv: Path = DEFAULT_MAPPING_CSV,
) -> Dict:
    df_agri = load_csv_safe(agri_csv)

    crop_col = find_first_column(df_agri, ["Crop", "Crop_Name", "Plant", "Plant_Name", "CropName", "PlantName"]) or df_agri.columns[0]
    waste_col = find_first_column(df_agri, ["Waste_Type", "WasteType", "Waste", "Waste Category", "Category"]) or df_agri.columns[-1]

    # Case-insensitive match for crop
    match = df_agri[df_agri[crop_col].astype(str).str.lower() == crop_name.lower()]
    if match.empty:
        # try contains
        match = df_agri[df_agri[crop_col].astype(str).str.lower().str.contains(crop_name.lower())]
    agri_row = match.iloc[0].to_dict() if not match.empty else {}

    waste_type = str(agri_row.get(waste_col, "")).strip()

    df_map = load_csv_safe(mapping_csv)
    map_waste_col = find_first_column(df_map, ["Waste_Type", "WasteType", "Waste", "Category"]) or df_map.columns[0]

    map_match = df_map[df_map[map_waste_col].astype(str).str.lower() == waste_type.lower()]
    if map_match.empty and waste_type:
        map_match = df_map[df_map[map_waste_col].astype(str).str.lower().str.contains(waste_type.lower())]

    mapping_row = map_match.iloc[0].to_dict() if not map_match.empty else {}

    # Prefer explicit fields if present
    recommended_product = mapping_row.get("Recommended_Product") or mapping_row.get("Recommended Product")
    market_value = mapping_row.get("Market_Value") or mapping_row.get("Market Value")
    processing_time = mapping_row.get("Processing_Time") or mapping_row.get("Processing Time")

    return {
        "crop": crop_name,
        "waste_type": waste_type or None,
        "agri_record": agri_row or None,
        "mapping_record": mapping_row or None,
        "Recommended_Product": recommended_product,
        "Market_Value": market_value,
        "Processing_Time": processing_time,
    }


# -----------------------------
# CLI
# -----------------------------

def main():
    parser = argparse.ArgumentParser(description="Plant classification and waste-to-product retrieval pipeline")
    parser.add_argument("--image", type=str, help="Path to input image to classify", required=True)
    parser.add_argument("--dataset-dir", type=str, default=str(DEFAULT_DATA_DIR), help="Path to training dataset (folder with class subfolders)")
    parser.add_argument("--model", type=str, default=str(DEFAULT_MODEL_PATH), help="Path to saved model (.keras)")
    parser.add_argument("--labels", type=str, default=str(DEFAULT_LABELS_PATH), help="Path to saved labels JSON")
    parser.add_argument("--agri-csv", type=str, default=str(DEFAULT_AGRI_CSV), help="Path to Agricultural_Waste_Core_Dataset.csv")
    parser.add_argument("--mapping-csv", type=str, default=str(DEFAULT_MAPPING_CSV), help="Path to Waste_to_Product_Mapping_Dataset.csv")
    parser.add_argument("--epochs", type=int, default=10)
    parser.add_argument("--batch-size", type=int, default=32)
    parser.add_argument("--retrain", action="store_true", help="Force retrain even if a saved model exists")

    args = parser.parse_args()

    img_path = Path(args.image)
    data_dir = Path(args.dataset_dir) if args.dataset_dir else None
    model_path = Path(args.model)
    labels_path = Path(args.labels)
    agri_csv = Path(args.agri_csv)
    mapping_csv = Path(args.mapping_csv)

    # Ensure directories
    ensure_dir(model_path.parent)

    # Load or train model
    model, labels = load_or_train(
        model_path=model_path,
        labels_path=labels_path,
        data_dir=data_dir,
        epochs=args.epochs,
        batch_size=args.batch_size,
        retrain=args.retrain,
    )

    pred_label, confidence = predict_class(model, labels, img_path)

    result = lookup_waste_info(pred_label, agri_csv=agri_csv, mapping_csv=mapping_csv)
    result.update({
        "predicted_crop": pred_label,
        "confidence": round(confidence, 4),
        "model_path": str(model_path),
    })

    # Print as JSON
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    # Enable TF performance tweaks if available
    os.environ.setdefault("TF_CPP_MIN_LOG_LEVEL", "2")
    tf.get_logger().setLevel("ERROR")
    main()
