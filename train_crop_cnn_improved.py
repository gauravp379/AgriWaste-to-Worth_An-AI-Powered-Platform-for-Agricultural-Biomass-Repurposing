#!/usr/bin/env python
"""
Improved Crop Classification Model Training
- Uses cleaned and preprocessed dataset
- Implements data augmentation
- Better hyperparameters
- Saves best model automatically
"""

import os
import sys
import json
import numpy as np
import tensorflow as tf
from tensorflow import keras
from tensorflow.keras import layers, models
from tensorflow.keras.preprocessing.image import ImageDataGenerator
from tensorflow.keras.applications import MobileNetV2
from tensorflow.keras.optimizers import Adam
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, confusion_matrix
from pathlib import Path
import argparse

# Configuration
if sys.stdout and hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')
if sys.stderr and hasattr(sys.stderr, 'reconfigure'):
    sys.stderr.reconfigure(encoding='utf-8')

PROJECT_ROOT = Path(__file__).resolve().parent
IMG_SIZE = (224, 224)
BATCH_SIZE = 16
EPOCHS = 15
LEARNING_RATE = 0.001
VALIDATION_SPLIT = 0.2
TEST_SPLIT = 0.1

# Paths
DEFAULT_DATA_DIR = str(PROJECT_ROOT / "data" / "processed_dataset")
MODEL_SAVE_DIR = str(PROJECT_ROOT / "models")
RESULTS_DIR = str(PROJECT_ROOT / "results")

# Classes (9 crops + 'other' for non-agricultural rejection)
CROP_CLASSES = ['banana', 'cotton', 'groundnut', 'jute', 'maize', 'other', 'rice', 'sugarcane', 'sunflower', 'wheat']


def create_augmentation_generator():
    """Create aggressive data augmentation for training"""
    return ImageDataGenerator(
        # Rotation
        rotation_range=25,
        
        # Shifting
        width_shift_range=0.2,
        height_shift_range=0.2,
        
        # Zoom
        zoom_range=0.3,
        
        # Flip
        horizontal_flip=True,
        vertical_flip=False,
        
        # Brightness/Contrast
        brightness_range=[0.7, 1.3],
        
        # Shear
        shear_range=0.2,
        
        # Fill mode for new pixels
        fill_mode='nearest',
        
        # Normalization
        rescale=1./255.,
    )


def create_validation_generator():
    """Create validation data generator (only rescaling, no augmentation)"""
    return ImageDataGenerator(rescale=1./255.)


def build_model(num_classes):
    """
    Build improved CNN model using MobileNetV2 transfer learning
    - Pre-trained weights from ImageNet
    - Fine-tunable top layers
    """
    print("🧠 Building model...")
    
    # Load pre-trained MobileNetV2
    base_model = MobileNetV2(
        input_shape=IMG_SIZE + (3,),
        include_top=False,
        weights='imagenet'
    )
    
    # Freeze base model initially
    base_model.trainable = False
    
    # Build custom top
    model = models.Sequential([
        layers.Input(shape=IMG_SIZE + (3,)),
        base_model,
        
        # Global pooling
        layers.GlobalAveragePooling2D(),
        
        # Dense layers
        layers.Dense(512, activation='relu', kernel_regularizer=keras.regularizers.l2(0.001)),
        layers.BatchNormalization(),
        layers.Dropout(0.5),
        
        layers.Dense(256, activation='relu', kernel_regularizer=keras.regularizers.l2(0.001)),
        layers.BatchNormalization(),
        layers.Dropout(0.4),
        
        layers.Dense(128, activation='relu', kernel_regularizer=keras.regularizers.l2(0.001)),
        layers.BatchNormalization(),
        layers.Dropout(0.3),
        
        # Output
        layers.Dense(num_classes, activation='softmax')
    ])
    
    model.compile(
        optimizer=Adam(learning_rate=LEARNING_RATE),
        loss='categorical_crossentropy',
        metrics=['accuracy', keras.metrics.Precision(), keras.metrics.Recall()]
    )
    
    print(f"   Total parameters: {model.count_params():,}")
    print("   ✓ Model built successfully")
    
    return model, base_model


def train_model(data_dir, output_model_path):
    """Train the improved model"""
    print("\n" + "="*60)
    print("🌾 IMPROVED CROP CLASSIFICATION MODEL TRAINING")
    print("="*60)
    
    # Check data directory
    if not os.path.exists(data_dir):
        print(f"❌ Data directory not found: {data_dir}")
        return False
    
    print(f"\n📁 Data directory: {data_dir}")
    print(f"📸 Image size: {IMG_SIZE}")
    print(f"📦 Batch size: {BATCH_SIZE}")
    print(f"🔄 Epochs: {EPOCHS}")
    
    # Count images
    total_images = 0
    for crop in CROP_CLASSES:
        crop_dir = os.path.join(data_dir, crop)
        if os.path.exists(crop_dir):
            count = len([f for f in os.listdir(crop_dir) if f.lower().endswith(('.jpg', '.jpeg', '.png'))])
            total_images += count
            print(f"   {crop:12}: {count:5} images")
    
    print(f"   {'TOTAL':12}: {total_images:5} images")
    
    if total_images < 100:
        print("❌ Insufficient data. Need at least 100 images.")
        return False
    
    # Load data using flow_from_directory
    print("\n📊 Loading dataset...")
    
    train_datagen = create_augmentation_generator()
    val_datagen = create_validation_generator()
    
    # Load training data
    train_generator = train_datagen.flow_from_directory(
        data_dir,
        target_size=IMG_SIZE,
        batch_size=BATCH_SIZE,
        class_mode='categorical',
        shuffle=True,
        subset=None,  # Use all for now
    )
    
    # Build model
    model, base_model = build_model(len(CROP_CLASSES))
    
    # Callbacks
    callbacks = [
        keras.callbacks.EarlyStopping(
            monitor='loss',
            patience=5,
            restore_best_weights=True,
            verbose=1
        ),
        keras.callbacks.ReduceLROnPlateau(
            monitor='loss',
            factor=0.5,
            patience=3,
            min_lr=1e-5,
            verbose=1
        ),
    ]
    
    # Phase 1: Train with frozen base model
    print("\n🔒 Phase 1: Training with frozen MobileNetV2 base...")
    history1 = model.fit(
        train_generator,
        epochs=8,
        callbacks=callbacks,
        verbose=1
    )
    
    # Phase 2: Fine-tune with unfrozen base model
    print("\n🔓 Phase 2: Fine-tuning with unfrozen base model...")
    base_model.trainable = True
    
    # Freeze first 100 layers
    for layer in base_model.layers[:-100]:
        layer.trainable = False
    
    model.compile(
        optimizer=Adam(learning_rate=LEARNING_RATE / 10),
        loss='categorical_crossentropy',
        metrics=['accuracy']
    )
    
    history2 = model.fit(
        train_generator,
        epochs=4,
        callbacks=callbacks,
        verbose=1
    )
    
    # Save model
    print(f"\n💾 Saving model...")
    Path(MODEL_SAVE_DIR).mkdir(parents=True, exist_ok=True)
    model.save(output_model_path)
    print(f"   ✓ Model saved: {output_model_path}")
    
    prod_model_path = os.path.join(MODEL_SAVE_DIR, 'plant_classifier.keras')
    try:
        model.save(prod_model_path)
        print(f"   ✓ Production model updated: {prod_model_path}")
    except Exception as e:
        print(f"   ⚠ Could not update production model: {e}")
    
    # Save class labels
    labels_path = os.path.join(MODEL_SAVE_DIR, 'plant_classifier_labels_improved.json')
    class_indices = train_generator.class_indices
    sorted_labels = [k for k, v in sorted(class_indices.items(), key=lambda x: x[1])]
    with open(labels_path, 'w') as f:
        json.dump(sorted_labels, f, indent=2)
    print(f"   ✓ Labels saved: {labels_path}")

    prod_labels_path = os.path.join(MODEL_SAVE_DIR, 'plant_classifier_labels.json')
    with open(prod_labels_path, 'w') as f:
        json.dump(sorted_labels, f, indent=2)
    print(f"   ✓ Production labels updated: {prod_labels_path}")
    
    # Training summary
    print("\n" + "="*60)
    print("✅ TRAINING COMPLETE")
    print("="*60)
    print(f"Model saved: {output_model_path}")
    print(f"Ready for evaluation and deployment!")
    
    return True


def main():
    parser = argparse.ArgumentParser(description='Train improved crop classification model')
    parser.add_argument('--data-dir', type=str, default=DEFAULT_DATA_DIR, help='Path to processed dataset')
    parser.add_argument('--output', type=str, default=os.path.join(MODEL_SAVE_DIR, 'plant_classifier_improved.keras'), help='Output model path')
    
    args = parser.parse_args()
    
    try:
        success = train_model(args.data_dir, args.output)
        if not success:
            sys.exit(1)
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
