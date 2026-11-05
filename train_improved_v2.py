#!/usr/bin/env python
"""
=============================================================
  Agriculture Waste Marketplace — IMPROVED Retraining
=============================================================
WHAT CHANGED vs train_from_dataset.py:
  1. Uses ALL available images from rich classes (not capped at 100)
     → banana: 972, cotton: 1855, groundnut: 2142, jute: 1047,
       maize: 1500, rice: 1000, sugarcane: 1372, sunflower: 1496,
       wheat: 1197
  2. Sparse classes still augmented to MIN_SAMPLES=300 each
  3. Stronger online augmentation in tf.data pipeline
  4. Class weights to handle remaining imbalance
  5. EfficientNetB0 backbone (better accuracy than MobileNetV2)
  6. Cosine annealing LR schedule
  7. More epochs, more patience

Usage:
  python train_improved_v2.py
  python train_improved_v2.py --skip-preprocess   # if prep already done
"""

import os, sys, json, shutil, hashlib, random, argparse, warnings
warnings.filterwarnings("ignore")
os.environ.setdefault("TF_CPP_MIN_LOG_LEVEL", "2")

from pathlib import Path
from typing import List, Tuple, Optional, Dict

for _s in (sys.stdout, sys.stderr):
    if _s and hasattr(_s, "reconfigure"):
        try: _s.reconfigure(encoding="utf-8")
        except: pass

import numpy as np
from PIL import Image, ImageEnhance, UnidentifiedImageError

import tensorflow as tf
from tensorflow import keras
from tensorflow.keras import layers
tf.get_logger().setLevel("ERROR")

# ─────────────────────────────────────────────────────────────────────────────
# Paths
# ─────────────────────────────────────────────────────────────────────────────
PROJECT_ROOT  = Path(__file__).resolve().parent
RAW_DATA_DIR  = PROJECT_ROOT / "Dataset" / "crop_images"
PREP_DATA_DIR = PROJECT_ROOT / "Dataset" / "prepared_dataset_v2"
MODEL_DIR     = PROJECT_ROOT / "models"
MODEL_PATH    = MODEL_DIR / "plant_classifier.keras"
LABELS_PATH   = MODEL_DIR / "plant_classifier_labels.json"

# ─────────────────────────────────────────────────────────────────────────────
# Hyper-parameters
# ─────────────────────────────────────────────────────────────────────────────
IMG_SIZE              = (224, 224)
BATCH_SIZE            = 32
PHASE1_EPOCHS         = 15   # frozen backbone
PHASE2_EPOCHS         = 10   # fine-tune
VAL_SPLIT             = 0.20
SEED                  = 42
MIN_SPARSE_SAMPLES    = 300  # sparse classes (< 300 raw) augmented up to this
RICH_CLASS_CAP        = 1500 # cap rich classes so training isn't too slow

SUPPORTED_EXT = {".jpg", ".jpeg", ".png", ".webp", ".avif", ".jfif", ".bmp", ".gif"}

random.seed(SEED)
np.random.seed(SEED)


# ─────────────────────────────────────────────────────────────────────────────
# Helpers
# ─────────────────────────────────────────────────────────────────────────────

def _image_hash(path: Path) -> Optional[str]:
    try:
        with Image.open(path) as im:
            arr = np.array(im.convert("L").resize((8, 8), Image.LANCZOS))
            return hashlib.md5(arr.tobytes()).hexdigest()
    except:
        return None


def _augment_pil(img: Image.Image) -> Image.Image:
    if random.random() > 0.5:
        img = img.transpose(Image.FLIP_LEFT_RIGHT)
    if random.random() > 0.6:
        img = img.transpose(Image.FLIP_TOP_BOTTOM)
    angle = random.uniform(-35, 35)
    img = img.rotate(angle, expand=False, fillcolor=(128, 128, 128))
    img = ImageEnhance.Brightness(img).enhance(random.uniform(0.65, 1.45))
    img = ImageEnhance.Contrast(img).enhance(random.uniform(0.75, 1.35))
    img = ImageEnhance.Color(img).enhance(random.uniform(0.75, 1.35))
    img = ImageEnhance.Sharpness(img).enhance(random.uniform(0.75, 1.35))
    return img


# ─────────────────────────────────────────────────────────────────────────────
# Preprocessing
# ─────────────────────────────────────────────────────────────────────────────

def preprocess_dataset(raw_dir: Path, out_dir: Path) -> List[str]:
    print("\n" + "="*60)
    print("  STEP 1 — PREPROCESSING DATASET (v2 — full images)")
    print("="*60)

    if not raw_dir.exists():
        raise FileNotFoundError(f"Raw dataset not found: {raw_dir}")

    class_dirs = sorted([d for d in raw_dir.iterdir() if d.is_dir()])
    if not class_dirs:
        raise ValueError(f"No sub-folders in {raw_dir}")

    out_dir.mkdir(parents=True, exist_ok=True)
    class_names: List[str] = []
    grand_total = 0
    seen_hashes: set = set()

    for cls_dir in class_dirs:
        cls_name = cls_dir.name.lower().replace(" ", "_")
        cls_out  = out_dir / cls_name
        cls_out.mkdir(parents=True, exist_ok=True)

        image_files = [
            f for f in cls_dir.iterdir()
            if f.is_file() and f.suffix.lower() in SUPPORTED_EXT
        ]
        if not image_files:
            print(f"  --  {cls_dir.name:20s}  →  no images, skipped")
            shutil.rmtree(cls_out, ignore_errors=True)
            continue

        # Convert & deduplicate
        saved_paths: List[Path] = []
        for img_path in image_files:
            if len(saved_paths) >= RICH_CLASS_CAP:
                break
            h = _image_hash(img_path)
            if h and h in seen_hashes:
                continue
            if h:
                seen_hashes.add(h)
            try:
                with Image.open(img_path) as im:
                    if im.size[0] < 32 or im.size[1] < 32:
                        continue
                    rgb = im.convert("RGB").resize(IMG_SIZE, Image.LANCZOS)
                    out_path = cls_out / f"{cls_name}_{len(saved_paths):06d}.jpg"
                    rgb.save(out_path, "JPEG", quality=92, optimize=True)
                    saved_paths.append(out_path)
            except:
                pass

        base_count = len(saved_paths)
        if base_count == 0:
            print(f"  --  {cls_dir.name:20s}  →  0 valid images after processing, skipped")
            shutil.rmtree(cls_out, ignore_errors=True)
            continue

        # Augment sparse classes
        aug_count = 0
        target = MIN_SPARSE_SAMPLES if base_count < MIN_SPARSE_SAMPLES else base_count
        if base_count < MIN_SPARSE_SAMPLES:
            idx = 0
            aug_idx = base_count
            while aug_idx < target:
                src = saved_paths[idx % base_count]
                try:
                    with Image.open(src) as im:
                        aug = _augment_pil(im.copy())
                        aug_path = cls_out / f"{cls_name}_{aug_idx:06d}.jpg"
                        aug.save(aug_path, "JPEG", quality=88)
                        aug_idx += 1
                        aug_count += 1
                except:
                    pass
                idx += 1

        total_cls = base_count + aug_count
        grand_total += total_cls
        class_names.append(cls_name)

        aug_note = f"  (+ {aug_count} offline augmented to {target})" if aug_count else ""
        print(f"  ok  {cls_dir.name:25s}  →  {cls_name:25s}  {total_cls:5d} images{aug_note}")

    print(f"\n  Total prepared : {grand_total} images in {len(class_names)} classes")
    return class_names


# ─────────────────────────────────────────────────────────────────────────────
# Compute class weights for imbalanced dataset
# ─────────────────────────────────────────────────────────────────────────────

def compute_class_weights(data_dir: Path, class_names: List[str]) -> Dict[int, float]:
    counts = []
    for cn in class_names:
        d = data_dir / cn
        n = len(list(d.glob("*.jpg"))) if d.exists() else 0
        counts.append(n)
    total = sum(counts)
    n_cls = len(counts)
    weights = {}
    for i, c in enumerate(counts):
        weights[i] = (total / (n_cls * c)) if c > 0 else 1.0
    return weights


# ─────────────────────────────────────────────────────────────────────────────
# tf.data pipelines
# ─────────────────────────────────────────────────────────────────────────────

def make_datasets(
    data_dir: Path,
    batch_size: int = BATCH_SIZE,
    val_split: float = VAL_SPLIT,
) -> Tuple[tf.data.Dataset, tf.data.Dataset, List[str]]:

    common = dict(
        directory=str(data_dir),
        image_size=IMG_SIZE,
        batch_size=batch_size,
        label_mode="categorical",
        seed=SEED,
        validation_split=val_split,
        shuffle=True,
    )
    train_ds = keras.utils.image_dataset_from_directory(subset="training",   **common)
    val_ds   = keras.utils.image_dataset_from_directory(subset="validation", **common)
    class_names: List[str] = train_ds.class_names

    AUTOTUNE = tf.data.AUTOTUNE

    # Stronger online augmentation
    augment = keras.Sequential([
        layers.RandomFlip("horizontal_and_vertical"),
        layers.RandomRotation(0.20),
        layers.RandomZoom(0.25),
        layers.RandomContrast(0.20),
        layers.RandomBrightness(0.20),
        layers.RandomTranslation(0.15, 0.15),
    ], name="augmentation")

    def prep_train(x, y):
        x = tf.cast(x, tf.float32) / 255.0
        x = augment(x, training=True)
        return x, y

    def prep_val(x, y):
        return tf.cast(x, tf.float32) / 255.0, y

    train_ds = train_ds.map(prep_train, num_parallel_calls=AUTOTUNE).prefetch(AUTOTUNE)
    val_ds   = val_ds.map(prep_val,   num_parallel_calls=AUTOTUNE).prefetch(AUTOTUNE)
    return train_ds, val_ds, class_names


# ─────────────────────────────────────────────────────────────────────────────
# Model — EfficientNetB0 backbone
# ─────────────────────────────────────────────────────────────────────────────

def build_model(num_classes: int) -> Tuple[keras.Model, keras.Model]:
    inputs = layers.Input(shape=IMG_SIZE + (3,), name="input_image")

    # EfficientNetB0 expects [0,255] inputs — we pass pre-normalised so rescale back
    x_scaled = layers.Rescaling(255.0)(inputs)   # [0,1] → [0,255]

    base = keras.applications.EfficientNetB0(
        input_shape=IMG_SIZE + (3,),
        include_top=False,
        weights="imagenet",
        pooling=None,
    )
    base.trainable = False

    x = base(x_scaled, training=False)
    x = layers.GlobalAveragePooling2D(name="gap")(x)
    x = layers.Dense(512, activation="relu",
                     kernel_regularizer=keras.regularizers.l2(5e-5))(x)
    x = layers.BatchNormalization()(x)
    x = layers.Dropout(0.4)(x)
    x = layers.Dense(256, activation="relu",
                     kernel_regularizer=keras.regularizers.l2(5e-5))(x)
    x = layers.BatchNormalization()(x)
    x = layers.Dropout(0.3)(x)
    outputs = layers.Dense(num_classes, activation="softmax", name="predictions")(x)

    model = keras.Model(inputs, outputs, name="agri_waste_v2")
    return model, base


def _compile(model: keras.Model, lr: float):
    model.compile(
        optimizer=keras.optimizers.Adam(learning_rate=lr),
        loss="categorical_crossentropy",
        metrics=["accuracy",
                 keras.metrics.Precision(name="precision"),
                 keras.metrics.Recall(name="recall")],
    )


# ─────────────────────────────────────────────────────────────────────────────
# Training
# ─────────────────────────────────────────────────────────────────────────────

def train(
    data_dir: Path,
    phase1_epochs: int = PHASE1_EPOCHS,
    phase2_epochs: int = PHASE2_EPOCHS,
    batch_size: int    = BATCH_SIZE,
) -> Tuple[keras.Model, List[str]]:

    print("\n" + "="*60)
    print("  STEP 2 — LOADING DATASET")
    print("="*60)
    train_ds, val_ds, class_names = make_datasets(data_dir, batch_size=batch_size)
    num_classes = len(class_names)

    print(f"\n  {num_classes} classes:")
    for i, cn in enumerate(class_names):
        count = len(list((data_dir/cn).glob("*.jpg")))
        print(f"    [{i:2d}] {cn:28s}  {count:5d} images")

    # Class weights for imbalance
    class_weights = compute_class_weights(data_dir, class_names)
    print(f"\n  Class weights (imbalance correction):")
    for i, cn in enumerate(class_names):
        print(f"    [{i:2d}] {cn:28s}  w={class_weights[i]:.3f}")

    print("\n" + "="*60)
    print("  STEP 3 — BUILDING MODEL (EfficientNetB0 + custom head)")
    print("="*60)
    model, base_model = build_model(num_classes)
    _compile(model, lr=1e-3)
    model.summary(line_length=80, print_fn=print)

    MODEL_DIR.mkdir(parents=True, exist_ok=True)

    callbacks_p1 = [
        keras.callbacks.EarlyStopping(
            monitor="val_accuracy", patience=6,
            restore_best_weights=True, verbose=1,
        ),
        keras.callbacks.ReduceLROnPlateau(
            monitor="val_loss", factor=0.4, patience=3,
            min_lr=1e-6, verbose=1,
        ),
        keras.callbacks.ModelCheckpoint(
            filepath=str(MODEL_PATH),
            monitor="val_accuracy", mode="max",
            save_best_only=True, verbose=1,
        ),
    ]

    # ── Phase 1 ──────────────────────────────────────────────────────────────
    print("\n" + "="*60)
    print(f"  PHASE 1 — FROZEN EfficientNetB0  (up to {phase1_epochs} epochs)")
    print("="*60)
    model.fit(
        train_ds, validation_data=val_ds,
        epochs=phase1_epochs,
        callbacks=callbacks_p1,
        class_weight=class_weights,
    )

    # ── Phase 2 ──────────────────────────────────────────────────────────────
    print("\n" + "="*60)
    print(f"  PHASE 2 — FINE-TUNING last 80 EfficientNet layers  (up to {phase2_epochs} epochs)")
    print("="*60)
    base_model.trainable = True
    for layer in base_model.layers[:-80]:
        layer.trainable = False
    _compile(model, lr=5e-5)

    callbacks_p2 = [
        keras.callbacks.EarlyStopping(
            monitor="val_accuracy", patience=5,
            restore_best_weights=True, verbose=1,
        ),
        keras.callbacks.ReduceLROnPlateau(
            monitor="val_loss", factor=0.4, patience=2,
            min_lr=1e-7, verbose=1,
        ),
        keras.callbacks.ModelCheckpoint(
            filepath=str(MODEL_PATH),
            monitor="val_accuracy", mode="max",
            save_best_only=True, verbose=1,
        ),
    ]
    model.fit(
        train_ds, validation_data=val_ds,
        epochs=phase2_epochs,
        callbacks=callbacks_p2,
        class_weight=class_weights,
    )

    # Reload best
    if MODEL_PATH.exists():
        model = keras.models.load_model(str(MODEL_PATH))
        print(f"\n  Best checkpoint reloaded from {MODEL_PATH}")

    # Save labels
    with open(LABELS_PATH, "w", encoding="utf-8") as f:
        json.dump(class_names, f, indent=2, ensure_ascii=False)
    print(f"  Labels saved → {LABELS_PATH}")

    # Aliases
    alias_labels = MODEL_DIR / "plant_classifier_labels_improved.json"
    alias_model  = MODEL_DIR / "plant_classifier_improved.keras"
    shutil.copy(LABELS_PATH, alias_labels)
    model.save(str(alias_model))
    print(f"  Alias labels → {alias_labels}")
    print(f"  Alias model  → {alias_model}")

    return model, class_names


# ─────────────────────────────────────────────────────────────────────────────
# Evaluation
# ─────────────────────────────────────────────────────────────────────────────

def evaluate(model: keras.Model, data_dir: Path, batch_size: int):
    print("\n" + "="*60)
    print("  STEP 4 — FINAL EVALUATION")
    print("="*60)
    _, val_ds, class_names = make_datasets(data_dir, batch_size=batch_size)
    results = model.evaluate(val_ds, verbose=1, return_dict=True)
    print("\n  ── Validation Metrics ──")
    for k, v in results.items():
        print(f"    {k:20s}: {v:.4f}")

    y_true_all, y_pred_all = [], []
    for x_batch, y_batch in val_ds.take(500):
        preds = model.predict(x_batch, verbose=0)
        y_true_all.extend(np.argmax(y_batch.numpy(), axis=1))
        y_pred_all.extend(np.argmax(preds, axis=1))
    y_true = np.array(y_true_all)
    y_pred = np.array(y_pred_all)

    print(f"\n  ── Per-class Accuracy ──")
    print(f"    {'Class':30s}  {'Correct':>7}  {'Total':>6}  {'Acc':>7}")
    print("    " + "-"*56)
    for i, cn in enumerate(class_names):
        mask = (y_true == i)
        total = mask.sum()
        correct = (y_pred[mask] == i).sum() if total > 0 else 0
        acc = correct / total if total > 0 else 0.0
        print(f"    {cn:30s}  {correct:7d}  {total:6d}  {acc:7.2%}")

    overall = (y_true == y_pred).mean()
    print(f"\n    Overall accuracy: {overall:.2%}")


# ─────────────────────────────────────────────────────────────────────────────
# Main
# ─────────────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="Train improved agriculture waste classifier v2")
    parser.add_argument("--raw-dir",         type=str, default=str(RAW_DATA_DIR))
    parser.add_argument("--prep-dir",        type=str, default=str(PREP_DATA_DIR))
    parser.add_argument("--skip-preprocess", action="store_true")
    parser.add_argument("--phase1-epochs",   type=int, default=PHASE1_EPOCHS)
    parser.add_argument("--phase2-epochs",   type=int, default=PHASE2_EPOCHS)
    parser.add_argument("--batch-size",      type=int, default=BATCH_SIZE)
    args = parser.parse_args()

    raw_dir  = Path(args.raw_dir)
    prep_dir = Path(args.prep_dir)

    print("\n" + "█"*60)
    print("  AGRICULTURE WASTE CLASSIFIER — IMPROVED v2")
    print("█"*60)
    print(f"  Raw dataset    : {raw_dir}")
    print(f"  Prepared dir   : {prep_dir}")
    print(f"  Model output   : {MODEL_PATH}")
    print(f"  Backbone       : EfficientNetB0 (ImageNet)")
    print(f"  Phase-1 epochs : {args.phase1_epochs}")
    print(f"  Phase-2 epochs : {args.phase2_epochs}")
    print(f"  Batch size     : {args.batch_size}")
    print(f"  Min sparse     : {MIN_SPARSE_SAMPLES} samples (offline aug)")
    print(f"  Rich cap       : {RICH_CLASS_CAP} samples max")
    print(f"  TensorFlow     : {tf.__version__}")

    if not args.skip_preprocess:
        class_names = preprocess_dataset(raw_dir, prep_dir)
    else:
        class_names = sorted([d.name for d in prep_dir.iterdir() if d.is_dir()])
        print(f"\n  Skipped preprocessing — {len(class_names)} classes found")

    if not class_names:
        print("  ERROR: No valid classes. Aborting.")
        sys.exit(1)

    model, class_names = train(
        data_dir=prep_dir,
        phase1_epochs=args.phase1_epochs,
        phase2_epochs=args.phase2_epochs,
        batch_size=args.batch_size,
    )

    evaluate(model, data_dir=prep_dir, batch_size=args.batch_size)

    print("\n" + "█"*60)
    print("  TRAINING COMPLETE — IMPROVED v2")
    print(f"  Model  → {MODEL_PATH}")
    print(f"  Labels → {LABELS_PATH}")
    print("█"*60 + "\n")


if __name__ == "__main__":
    main()

