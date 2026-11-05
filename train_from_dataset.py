#!/usr/bin/env python
"""
=============================================================
  Agriculture Waste Marketplace — Full Dataset Training
=============================================================
Trains a MobileNetV2-based image classifier on the actual
Dataset/crop_images folder.

Classes found:
  Rich (>= 50 images) → used directly + augmented during training
  Sparse (< 50 images) → offline augmented to MIN_SAMPLES_PER_CLASS

Pipeline:
  1. Scan Dataset/crop_images for all image files
  2. Convert + standardise to 224×224 JPEG (handles all formats)
  3. Augment sparse classes to minimum 100 samples
  4. Phase-1 training  — frozen MobileNetV2 backbone
  5. Phase-2 fine-tuning — last 50 backbone layers unfrozen
  6. Save model  → models/plant_classifier.keras
  7. Save labels → models/plant_classifier_labels.json

Usage:
  python train_from_dataset.py
  python train_from_dataset.py --phase1-epochs 15 --phase2-epochs 10
  python train_from_dataset.py --skip-preprocess   # reuse prepared data
"""

import os, sys, json, shutil, hashlib, random, argparse, warnings
warnings.filterwarnings("ignore")
os.environ.setdefault("TF_CPP_MIN_LOG_LEVEL", "2")

from pathlib import Path
from typing import List, Tuple, Optional

# ── stdout encoding ──────────────────────────────────────────────────────────
for _s in (sys.stdout, sys.stderr):
    if _s and hasattr(_s, "reconfigure"):
        try:
            _s.reconfigure(encoding="utf-8")
        except Exception:
            pass

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
PREP_DATA_DIR = PROJECT_ROOT / "Dataset" / "prepared_dataset"
MODEL_DIR     = PROJECT_ROOT / "models"
MODEL_PATH    = MODEL_DIR / "plant_classifier.keras"
LABELS_PATH   = MODEL_DIR / "plant_classifier_labels.json"

# ─────────────────────────────────────────────────────────────────────────────
# Hyper-parameters
# ─────────────────────────────────────────────────────────────────────────────
IMG_SIZE             = (224, 224)
BATCH_SIZE           = 32
PHASE1_EPOCHS        = 12
PHASE2_EPOCHS        =  8
VAL_SPLIT            = 0.20
SEED                 = 42
MIN_SAMPLES_PER_CLASS = 100   # sparse classes are augmented up to this
MIN_CLASS_THRESHOLD   =   1   # classes with 0 valid images are skipped

SUPPORTED_EXT = {".jpg", ".jpeg", ".png", ".webp", ".avif", ".jfif", ".bmp", ".gif"}

random.seed(SEED)
np.random.seed(SEED)


# ─────────────────────────────────────────────────────────────────────────────
# Helpers
# ─────────────────────────────────────────────────────────────────────────────

def _image_hash(path: Path) -> Optional[str]:
    """Cheap perceptual hash via 8×8 thumbnail for duplicate detection."""
    try:
        with Image.open(path) as im:
            arr = np.array(im.convert("L").resize((8, 8), Image.LANCZOS))
            return hashlib.md5(arr.tobytes()).hexdigest()
    except Exception:
        return None


def _augment_pil(img: Image.Image) -> Image.Image:
    """Apply random augmentations to a PIL image."""
    ops = []

    # Random horizontal flip
    if random.random() > 0.5:
        img = img.transpose(Image.FLIP_LEFT_RIGHT)

    # Random rotation (-30 to +30 deg)
    angle = random.uniform(-30, 30)
    img = img.rotate(angle, expand=False, fillcolor=(128, 128, 128))

    # Random brightness
    factor = random.uniform(0.7, 1.4)
    img = ImageEnhance.Brightness(img).enhance(factor)

    # Random contrast
    factor = random.uniform(0.8, 1.3)
    img = ImageEnhance.Contrast(img).enhance(factor)

    # Random saturation
    factor = random.uniform(0.8, 1.3)
    img = ImageEnhance.Color(img).enhance(factor)

    return img


# ─────────────────────────────────────────────────────────────────────────────
# Step 1 — Preprocess raw dataset → prepared_dataset
# ─────────────────────────────────────────────────────────────────────────────

def preprocess_dataset(raw_dir: Path, out_dir: Path) -> List[str]:
    """
    Walk raw_dir sub-folders → standardise every valid image to 224×224 JPEG.
    Augment sparse classes to MIN_SAMPLES_PER_CLASS.
    Returns sorted list of class names that were included.
    """
    print("\n" + "="*60)
    print("  STEP 1 — PREPROCESSING DATASET")
    print("="*60)

    if not raw_dir.exists():
        raise FileNotFoundError(f"Raw dataset not found: {raw_dir}")

    class_dirs = sorted([d for d in raw_dir.iterdir() if d.is_dir()])
    if not class_dirs:
        raise ValueError(f"No sub-folders found in {raw_dir}")

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
            continue

        # ── convert & deduplicate ────────────────────────────────────────────
        saved_paths: List[Path] = []
        for img_path in image_files:
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
            except Exception:
                pass

        base_count = len(saved_paths)

        if base_count < MIN_CLASS_THRESHOLD:
            print(f"  --  {cls_dir.name:20s}  →  only {base_count} valid images, skipped")
            # clean up empty dir
            try:
                shutil.rmtree(cls_out)
            except Exception:
                pass
            continue

        # ── offline augmentation for sparse classes ──────────────────────────
        aug_count = 0
        if base_count < MIN_SAMPLES_PER_CLASS:
            target = MIN_SAMPLES_PER_CLASS
            idx    = 0
            aug_idx = base_count
            while aug_idx < target:
                src_path = saved_paths[idx % base_count]
                try:
                    with Image.open(src_path) as src:
                        aug_img = _augment_pil(src.copy())
                        aug_path = cls_out / f"{cls_name}_{aug_idx:06d}.jpg"
                        aug_img.save(aug_path, "JPEG", quality=88)
                        aug_idx += 1
                        aug_count += 1
                except Exception:
                    pass
                idx += 1

        total_cls = base_count + aug_count
        grand_total += total_cls
        class_names.append(cls_name)

        aug_note = f"  (+ {aug_count} augmented)" if aug_count else ""
        print(f"  ok  {cls_dir.name:25s}  →  {cls_name:25s}  {total_cls:5d} images{aug_note}")

    print(f"\n  Total prepared : {grand_total} images")
    print(f"  Classes        : {len(class_names)}")
    print(f"  Classes list   : {class_names}")

    return class_names


# ─────────────────────────────────────────────────────────────────────────────
# Step 2 — tf.data pipelines
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

    augment_layer = keras.Sequential([
        layers.RandomFlip("horizontal"),
        layers.RandomRotation(0.15),
        layers.RandomZoom(0.20),
        layers.RandomContrast(0.15),
        layers.RandomBrightness(0.15),
        layers.RandomTranslation(0.10, 0.10),
    ], name="augmentation")

    def prep_train(x, y):
        x = tf.cast(x, tf.float32) / 255.0
        x = augment_layer(x, training=True)
        return x, y

    def prep_val(x, y):
        return tf.cast(x, tf.float32) / 255.0, y

    train_ds = train_ds.map(prep_train, num_parallel_calls=AUTOTUNE).prefetch(AUTOTUNE)
    val_ds   = val_ds.map(prep_val,   num_parallel_calls=AUTOTUNE).prefetch(AUTOTUNE)

    return train_ds, val_ds, class_names


# ─────────────────────────────────────────────────────────────────────────────
# Step 3 — Model
# ─────────────────────────────────────────────────────────────────────────────

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
    x = layers.Dense(512, activation="relu",
                     kernel_regularizer=keras.regularizers.l2(1e-4))(x)
    x = layers.BatchNormalization()(x)
    x = layers.Dropout(0.45)(x)
    x = layers.Dense(256, activation="relu",
                     kernel_regularizer=keras.regularizers.l2(1e-4))(x)
    x = layers.BatchNormalization()(x)
    x = layers.Dropout(0.35)(x)
    outputs = layers.Dense(num_classes, activation="softmax", name="predictions")(x)

    model = keras.Model(inputs, outputs, name="agri_waste_classifier")
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
# Step 4 — Training
# ─────────────────────────────────────────────────────────────────────────────

def train(
    data_dir: Path,
    phase1_epochs: int = PHASE1_EPOCHS,
    phase2_epochs: int = PHASE2_EPOCHS,
    batch_size: int    = BATCH_SIZE,
) -> Tuple[keras.Model, List[str]]:

    print("\n" + "="*60)
    print("  STEP 2 — LOADING DATASET INTO TF PIPELINES")
    print("="*60)

    train_ds, val_ds, class_names = make_datasets(data_dir, batch_size=batch_size)
    num_classes = len(class_names)

    print(f"\n  {num_classes} classes:")
    for i, cn in enumerate(class_names):
        print(f"    [{i:2d}] {cn}")

    print("\n" + "="*60)
    print("  STEP 3 — BUILDING MODEL (MobileNetV2 + custom head)")
    print("="*60)

    model, base_model = build_model(num_classes)
    _compile(model, lr=1e-3)
    model.summary(line_length=80, print_fn=print)

    MODEL_DIR.mkdir(parents=True, exist_ok=True)

    callbacks = [
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
    print(f"  PHASE 1 — FROZEN BACKBONE  ({phase1_epochs} epochs)")
    print("="*60)
    model.fit(train_ds, validation_data=val_ds,
              epochs=phase1_epochs, callbacks=callbacks)

    # ── Phase 2 ──────────────────────────────────────────────────────────────
    print("\n" + "="*60)
    print(f"  PHASE 2 — FINE-TUNING last 50 layers  ({phase2_epochs} epochs)")
    print("="*60)
    base_model.trainable = True
    for layer in base_model.layers[:-50]:
        layer.trainable = False
    _compile(model, lr=5e-5)
    model.fit(train_ds, validation_data=val_ds,
              epochs=phase2_epochs, callbacks=callbacks)

    # ── reload best checkpoint ────────────────────────────────────────────────
    if MODEL_PATH.exists():
        model = keras.models.load_model(str(MODEL_PATH))
        print(f"\n  ✓  Best checkpoint reloaded from {MODEL_PATH}")

    # ── save labels ───────────────────────────────────────────────────────────
    with open(LABELS_PATH, "w", encoding="utf-8") as f:
        json.dump(class_names, f, indent=2, ensure_ascii=False)
    print(f"  ✓  Labels saved → {LABELS_PATH}")

    # ── aliases used by the rest of the codebase ──────────────────────────────
    alias_labels = MODEL_DIR / "plant_classifier_labels_improved.json"
    alias_model  = MODEL_DIR / "plant_classifier_improved.keras"
    shutil.copy(LABELS_PATH, alias_labels)
    model.save(str(alias_model))
    print(f"  ✓  Alias labels → {alias_labels}")
    print(f"  ✓  Alias model  → {alias_model}")

    return model, class_names


# ─────────────────────────────────────────────────────────────────────────────
# Step 5 — Evaluation
# ─────────────────────────────────────────────────────────────────────────────

def evaluate(model: keras.Model, data_dir: Path, batch_size: int):
    print("\n" + "="*60)
    print("  STEP 4 — FINAL EVALUATION ON VALIDATION SET")
    print("="*60)

    _, val_ds, class_names = make_datasets(data_dir, batch_size=batch_size)
    results = model.evaluate(val_ds, verbose=1, return_dict=True)

    print("\n  ── Validation Metrics ──")
    for k, v in results.items():
        print(f"    {k:20s}: {v:.4f}")

    # per-class breakdown
    y_true_all, y_pred_all = [], []
    for x_batch, y_batch in val_ds.take(200):
        preds = model.predict(x_batch, verbose=0)
        y_true_all.extend(np.argmax(y_batch.numpy(), axis=1))
        y_pred_all.extend(np.argmax(preds, axis=1))

    y_true = np.array(y_true_all)
    y_pred = np.array(y_pred_all)

    print(f"\n  ── Per-class Accuracy ──")
    print(f"    {'Class':30s}  {'Correct':>7}  {'Total':>6}  {'Acc':>7}")
    print("    " + "-"*56)
    for i, cn in enumerate(class_names):
        mask    = (y_true == i)
        total   = mask.sum()
        correct = (y_pred[mask] == i).sum() if total > 0 else 0
        acc     = correct / total if total > 0 else 0.0
        print(f"    {cn:30s}  {correct:7d}  {total:6d}  {acc:7.2%}")

    overall = (y_true == y_pred).mean()
    print(f"\n    Overall accuracy: {overall:.2%}")


# ─────────────────────────────────────────────────────────────────────────────
# Main
# ─────────────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        description="Train agriculture waste image classifier from Dataset/crop_images"
    )
    parser.add_argument("--raw-dir",       type=str, default=str(RAW_DATA_DIR))
    parser.add_argument("--prep-dir",      type=str, default=str(PREP_DATA_DIR))
    parser.add_argument("--skip-preprocess", action="store_true",
                        help="Skip preprocessing (reuse already-prepared images)")
    parser.add_argument("--phase1-epochs", type=int, default=PHASE1_EPOCHS)
    parser.add_argument("--phase2-epochs", type=int, default=PHASE2_EPOCHS)
    parser.add_argument("--batch-size",    type=int, default=BATCH_SIZE)
    args = parser.parse_args()

    raw_dir  = Path(args.raw_dir)
    prep_dir = Path(args.prep_dir)

    print("\n" + "█"*60)
    print("  AGRICULTURE WASTE CLASSIFIER — TRAINING PIPELINE")
    print("█"*60)
    print(f"  Raw dataset    : {raw_dir}")
    print(f"  Prepared dir   : {prep_dir}")
    print(f"  Model output   : {MODEL_PATH}")
    print(f"  Labels output  : {LABELS_PATH}")
    print(f"  Phase-1 epochs : {args.phase1_epochs}")
    print(f"  Phase-2 epochs : {args.phase2_epochs}")
    print(f"  Batch size     : {args.batch_size}")
    print(f"  Min samples    : {MIN_SAMPLES_PER_CLASS} per class")
    print(f"  TensorFlow     : {tf.__version__}")

    # ── preprocess ────────────────────────────────────────────────────────────
    if not args.skip_preprocess:
        class_names = preprocess_dataset(raw_dir, prep_dir)
    else:
        class_names = sorted([d.name for d in prep_dir.iterdir() if d.is_dir()])
        print(f"\n  Skipped preprocessing — {len(class_names)} classes found in {prep_dir}")

    if not class_names:
        print("  ERROR: No valid classes found. Aborting.")
        sys.exit(1)

    # ── train ─────────────────────────────────────────────────────────────────
    model, class_names = train(
        data_dir=prep_dir,
        phase1_epochs=args.phase1_epochs,
        phase2_epochs=args.phase2_epochs,
        batch_size=args.batch_size,
    )

    # ── evaluate ──────────────────────────────────────────────────────────────
    evaluate(model, data_dir=prep_dir, batch_size=args.batch_size)

    print("\n" + "█"*60)
    print("  TRAINING COMPLETE")
    print(f"  Model  saved → {MODEL_PATH}")
    print(f"  Labels saved → {LABELS_PATH}")
    print("█"*60 + "\n")


if __name__ == "__main__":
    main()
