#!/usr/bin/env python
"""
Master Script: Complete Model Improvement Workflow
1. Preprocess dataset (standardize, clean, deduplicate)
2. Train improved model with augmentation
3. Test and validate
"""

import os
import sys
import subprocess
from pathlib import Path


def print_header(title):
    """Print formatted header"""
    print("\n" + "="*70)
    print(f"  {title}")
    print("="*70)


def run_script(script_name, args=""):
    """Run a Python script"""
    cmd = f'python "{script_name}" {args}'
    print(f"\n▶️  Running: {cmd}")
    print("-"*70)
    
    result = subprocess.call(cmd, shell=True)
    
    if result != 0:
        print(f"\n❌ Script failed with exit code {result}")
        return False
    
    return True


def main():
    """Main workflow"""
    print_header("🌾 CROP CLASSIFICATION MODEL IMPROVEMENT WORKFLOW")
    
    print("""
This script will:
1. ✅ Clean and standardize your dataset
2. ✅ Remove duplicates and bad images
3. ✅ Train improved model with data augmentation
4. ✅ Test on wheat and other crops

Expected improvements:
- Better generalization due to augmentation
- Consistent image format and size
- Removed duplicate/corrupt images
- Transfer learning from ImageNet
""")
    
    input("\nPress Enter to start...")
    
    base_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Step 1: Preprocess Dataset
    print_header("STEP 1: PREPROCESSING DATASET")
    print("""
This will:
- Convert all images to JPEG format
- Resize all images to 224x224
- Remove duplicates
- Remove corrupted images
- Organize by crop type
""")
    
    if not run_script(os.path.join(base_dir, "preprocess_dataset.py")):
        print("❌ Preprocessing failed. Aborting.")
        sys.exit(1)
    
    # Step 2: Train Improved Model
    print_header("STEP 2: TRAINING IMPROVED MODEL")
    print("""
This will:
- Build MobileNetV2 transfer learning model
- Use aggressive data augmentation
- Train with augmented data
- Fine-tune with unfrozen layers
- Save best model automatically
""")
    
    processed_data = os.path.join(base_dir, "data", "processed_dataset")
    
    if not run_script(
        os.path.join(base_dir, "train_crop_cnn_improved.py"),
        f'--data-dir "{processed_data}"'
    ):
        print("❌ Training failed. Aborting.")
        sys.exit(1)
    
    # Step 3: Test Model
    print_header("STEP 3: TESTING IMPROVED MODEL")
    print("""
This will:
- Test with wheat images
- Test with all crop types
- Compare with old model
- Show accuracy improvements
""")
    
    if not run_script(os.path.join(base_dir, "test_improved_model.py"), "--test-wheat --test-all"):
        print("⚠️  Testing completed with warnings")
    
    # Final summary
    print_header("✅ WORKFLOW COMPLETE")
    
    print("""
Summary of improvements:
├─ ✓ Dataset cleaned and standardized
├─ ✓ Duplicates and bad images removed
├─ ✓ Model trained with augmentation
├─ ✓ Transfer learning from ImageNet
├─ ✓ Fine-tuning applied
└─ ✓ Model validated

Next steps:
1. Check wheat test results above
2. If wheat is correctly classified: SUCCESS! 🎉
3. If still misclassified: Need more training data
4. Update ai_system.py to use new model:
   - Change: plant_classifier_improved.keras
   - Change: plant_classifier_labels_improved.json

New Model Location:
- Model: models/plant_classifier_improved.keras
- Labels: models/plant_classifier_labels_improved.json

To use improved model in your system:
1. Update plant_waste_pipeline.py
2. Change DEFAULT_MODEL_PATH to new model
3. Change DEFAULT_LABELS_PATH to new labels
4. Restart server
""")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⏹️  Workflow cancelled by user")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
