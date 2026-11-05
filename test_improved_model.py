#!/usr/bin/env python
"""
Test Improved Model
- Test with wheat and other crop images
- Compare with old model
- Verify accuracy improvements
"""

import os
import json
import numpy as np
import tensorflow as tf
from PIL import Image
from pathlib import Path
import sys
import argparse

if sys.stdout and hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')
if sys.stderr and hasattr(sys.stderr, 'reconfigure'):
    sys.stderr.reconfigure(encoding='utf-8')

PROJECT_ROOT = Path(__file__).resolve().parent
IMG_SIZE = (224, 224)
MODEL_DIR = str(PROJECT_ROOT / "models")
TEST_IMAGE_DIR = str(PROJECT_ROOT / "data" / "test_crop_image")


def load_model_and_labels(model_path, labels_path):
    """Load improved model and labels"""
    try:
        print(f"📥 Loading model: {model_path}")
        model = tf.keras.models.load_model(model_path)
        
        print(f"📥 Loading labels: {labels_path}")
        with open(labels_path, 'r') as f:
            labels = json.load(f)
        
        print(f"✓ Model loaded")
        print(f"✓ Classes: {', '.join(labels)}")
        return model, labels
    except Exception as e:
        print(f"❌ Error loading model: {e}")
        return None, None


def preprocess_image(image_path):
    """Preprocess image for prediction"""
    try:
        # Open image
        img = Image.open(image_path).convert('RGB')
        
        # Resize
        img = img.resize(IMG_SIZE, Image.Resampling.LANCZOS)
        
        # Convert to array
        img_array = np.array(img) / 255.0
        
        # Add batch dimension
        img_array = np.expand_dims(img_array, axis=0)
        
        return img_array
    except Exception as e:
        print(f"❌ Error preprocessing image: {e}")
        return None


def predict_crop(model, labels, image_path):
    """Predict crop type"""
    try:
        # Preprocess
        img_array = preprocess_image(image_path)
        if img_array is None:
            return None
        
        # Predict
        predictions = model.predict(img_array, verbose=0)[0]
        
        # Get results
        top_3_idx = np.argsort(predictions)[-3:][::-1]
        results = []
        for idx in top_3_idx:
            results.append({
                'crop': labels[idx],
                'confidence': float(predictions[idx]),
                'percentage': float(predictions[idx] * 100)
            })
        
        return results
    except Exception as e:
        print(f"❌ Error in prediction: {e}")
        return None


def test_wheat_image():
    """Test with wheat image to verify improvement"""
    print("\n" + "="*60)
    print("🧪 TESTING IMPROVED MODEL WITH WHEAT")
    print("="*60)
    
    # Find wheat test image
    wheat_images = []
    if os.path.exists(TEST_IMAGE_DIR):
        for f in os.listdir(TEST_IMAGE_DIR):
            if 'wheat' in f.lower() and f.lower().endswith(('.jpg', '.jpeg', '.png')):
                wheat_images.append(os.path.join(TEST_IMAGE_DIR, f))
    
    if not wheat_images:
        print("⚠️  No wheat test images found in test_crop_image directory")
        return False
    
    # Load improved model
    improved_model_path = os.path.join(MODEL_DIR, 'plant_classifier_improved.keras')
    improved_labels_path = os.path.join(MODEL_DIR, 'plant_classifier_labels_improved.json')
    
    if not os.path.exists(improved_model_path):
        print(f"❌ Improved model not found: {improved_model_path}")
        print("   Please run: python train_crop_cnn_improved.py")
        return False
    
    improved_model, improved_labels = load_model_and_labels(improved_model_path, improved_labels_path)
    if improved_model is None:
        return False
    
    # Load old model for comparison
    old_model_path = os.path.join(MODEL_DIR, 'plant_classifier.keras')
    old_labels_path = os.path.join(MODEL_DIR, 'plant_classifier_labels.json')
    old_model = None
    old_labels = None
    
    if os.path.exists(old_model_path):
        print("\n📊 Loading old model for comparison...")
        old_model, old_labels = load_model_and_labels(old_model_path, old_labels_path)
    
    # Test
    print("\n" + "="*60)
    print("🌾 WHEAT IMAGE TEST RESULTS")
    print("="*60)
    
    for wheat_path in wheat_images:
        print(f"\n📷 Testing: {os.path.basename(wheat_path)}")
        
        # Improved model prediction
        print("\n📊 IMPROVED MODEL:")
        improved_results = predict_crop(improved_model, improved_labels, wheat_path)
        if improved_results:
            for i, result in enumerate(improved_results, 1):
                marker = "✅" if result['crop'] == 'wheat' else ("⚠️" if i == 1 else "  ")
                print(f"  {marker} #{i}: {result['crop']:12} ({result['percentage']:6.2f}%)")
        
        # Old model comparison
        if old_model:
            print("\n📊 OLD MODEL (for comparison):")
            old_results = predict_crop(old_model, old_labels, wheat_path)
            if old_results:
                for i, result in enumerate(old_results, 1):
                    marker = "✅" if result['crop'] == 'wheat' else ("❌" if i == 1 else "  ")
                    print(f"  {marker} #{i}: {result['crop']:12} ({result['percentage']:6.2f}%)")
        
        # Verdict
        if improved_results and improved_results[0]['crop'] == 'wheat':
            print("\n✅ VERDICT: Improved model correctly identifies WHEAT!")
            if old_model and old_results[0]['crop'] != 'wheat':
                print("🎉 IMPROVEMENT: Fixed previous misclassification!")
        else:
            print("\n⚠️  VERDICT: Still needs improvement")
    
    return True


def test_all_crops():
    """Test with various crop images"""
    print("\n" + "="*60)
    print("🧪 TESTING ALL CROPS")
    print("="*60)
    
    # Load model
    model_path = os.path.join(MODEL_DIR, 'plant_classifier_improved.keras')
    labels_path = os.path.join(MODEL_DIR, 'plant_classifier_labels_improved.json')
    
    if not os.path.exists(model_path):
        print(f"❌ Model not found: {model_path}")
        return False
    
    model, labels = load_model_and_labels(model_path, labels_path)
    if model is None:
        return False
    
    # Test directory
    if not os.path.exists(TEST_IMAGE_DIR):
        print(f"⚠️  Test directory not found: {TEST_IMAGE_DIR}")
        return False
    
    # Get test images recursively
    test_images = []
    test_path = Path(TEST_IMAGE_DIR)
    for p in test_path.rglob('*'):
        if p.is_file() and p.suffix.lower() in ('.jpg', '.jpeg', '.png', '.jfif', '.webp'):
            test_images.append(str(p))
    
    if not test_images:
        print("⚠️  No test images found")
        return False
    
    print(f"\n📊 Found {len(test_images)} test images across classes")
    
    # Test each
    correct = 0
    total = len(test_images)
    for image_path in test_images:
        filename = os.path.basename(image_path)
        parent_crop = Path(image_path).parent.name.lower()
        results = predict_crop(model, labels, image_path)
        
        if results:
            top_crop = results[0]['crop'].lower()
            confidence = results[0]['percentage']
            is_match = (top_crop == parent_crop) or (parent_crop in top_crop) or (top_crop in parent_crop)
            if is_match:
                correct += 1
                icon = "✅"
            else:
                icon = "❌"
            print(f"  {icon} Expected: [{parent_crop:10}] Predicted: [{top_crop:10}] ({confidence:6.2f}%) - {filename}")
    
    acc = (correct / total) * 100 if total > 0 else 0
    print(f"\n🎯 Overall Test Accuracy: {correct}/{total} ({acc:.1f}%)")
    return True


def main():
    parser = argparse.ArgumentParser(description='Test improved crop classification model')
    parser.add_argument('--test-wheat', action='store_true', default=True, help='Test with wheat images')
    parser.add_argument('--test-all', action='store_true', help='Test all crops')
    
    args = parser.parse_args()
    
    try:
        if args.test_wheat:
            test_wheat_image()
        
        if args.test_all:
            test_all_crops()
    
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
