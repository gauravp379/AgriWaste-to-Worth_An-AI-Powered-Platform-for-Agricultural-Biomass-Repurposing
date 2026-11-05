#!/usr/bin/env python
"""
Data Preprocessing Pipeline for Crop Classification
- Standardizes image format and size
- Cleans bad/duplicate images
- Organizes dataset properly
- Prepares for model training
"""

import os
import sys
import shutil
import hashlib
from pathlib import Path
from PIL import Image
import numpy as np
from tqdm import tqdm

if sys.stdout and hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')
if sys.stderr and hasattr(sys.stderr, 'reconfigure'):
    sys.stderr.reconfigure(encoding='utf-8')

PROJECT_ROOT = Path(__file__).resolve().parent
STANDARD_SIZE = (224, 224)  # Modern CNN standard
STANDARD_FORMAT = "jpg"
INPUT_DIR = PROJECT_ROOT / "data" / "crop_images"
OUTPUT_DIR = PROJECT_ROOT / "data" / "processed_dataset"
BACKUP_DIR = PROJECT_ROOT / "data" / "crop_images_backup"

# Crop categories (including 'other' for non-agricultural rejection)
CROP_CATEGORIES = ['banana', 'cotton', 'groundnut', 'jute', 'maize', 'other', 'rice', 'sugarcane', 'sunflower', 'wheat']


def create_directories():
    """Create output directories"""
    print("📁 Creating directories...")
    Path(OUTPUT_DIR).mkdir(parents=True, exist_ok=True)
    for crop in CROP_CATEGORIES:
        (Path(OUTPUT_DIR) / crop).mkdir(parents=True, exist_ok=True)


def backup_original():
    """Backup original dataset"""
    print("💾 Backing up original dataset...")
    if not os.path.exists(BACKUP_DIR):
        shutil.copytree(INPUT_DIR, BACKUP_DIR)
        print(f"✓ Backup created at {BACKUP_DIR}")
    else:
        print("✓ Backup already exists")


def get_image_hash(image_path):
    """Get hash of image to detect duplicates"""
    try:
        with Image.open(image_path) as img:
            # Reduce image size for faster hash computation
            img.thumbnail((50, 50))
            return hashlib.md5(np.array(img).tobytes()).hexdigest()
    except:
        return None


def is_image_valid(image_path):
    """Check if image is valid and processable"""
    try:
        with Image.open(image_path) as img:
            # Check minimum size (too small images are usually corrupted)
            if img.size[0] < 32 or img.size[1] < 32:
                return False, "Image too small"
            
            # Check format
            if img.format and img.format.lower() not in ['jpeg', 'jpg', 'png', 'gif', 'webp']:
                return False, f"Invalid format: {img.format}"
            
            return True, "Valid"
    except Exception as e:
        return False, str(e)


def preprocess_image(input_path, output_path):
    """
    Preprocess single image:
    - Convert to RGB
    - Resize to standard size
    - Save as JPEG
    """
    try:
        # Open and convert to RGB (handles transparency, etc.)
        img = Image.open(input_path).convert('RGB')
        
        # Resize with high-quality resampling
        img = img.resize(STANDARD_SIZE, Image.Resampling.LANCZOS)
        
        # Save as JPEG
        img.save(output_path, 'JPEG', quality=95)
        
        return True, "Success"
    except Exception as e:
        return False, str(e)


def process_dataset():
    """Main preprocessing pipeline"""
    print("\n" + "="*60)
    print("🌾 CROP CLASSIFICATION DATA PREPROCESSING")
    print("="*60)
    
    # Step 1: Create directories
    create_directories()
    
    # Step 2: Backup original
    backup_original()
    
    # Step 3: Process images
    print("\n📊 PROCESSING DATASET...")
    print(f"Target size: {STANDARD_SIZE}")
    print(f"Target format: {STANDARD_FORMAT.upper()}")
    
    stats = {crop: {'total': 0, 'valid': 0, 'invalid': 0, 'duplicates': 0} for crop in CROP_CATEGORIES}
    seen_hashes = set()
    
    for crop in CROP_CATEGORIES:
        crop_input_dir = os.path.join(INPUT_DIR, crop)
        if not os.path.exists(crop_input_dir):
            crop_input_dir = os.path.join(INPUT_DIR, crop.capitalize())
        if not os.path.exists(crop_input_dir):
            print(f"⚠️  {crop} folder not found: {crop_input_dir}")
            continue
        
        crop_output_dir = os.path.join(OUTPUT_DIR, crop)
        os.makedirs(crop_output_dir, exist_ok=True)
        
        # Get all image files
        image_files = [f for f in os.listdir(crop_input_dir) 
                      if f.lower().endswith(('.jpg', '.jpeg', '.png', '.gif', '.webp'))]
        
        print(f"\n📸 Processing {crop.upper()}...")
        print(f"   Found: {len(image_files)} images")
        
        valid_count = 0
        invalid_count = 0
        duplicate_count = 0
        
        for filename in tqdm(image_files, desc=f"  {crop}"):
            image_path = os.path.join(crop_input_dir, filename)
            stats[crop]['total'] += 1
            
            # Check if image is valid
            is_valid, reason = is_image_valid(image_path)
            if not is_valid:
                invalid_count += 1
                print(f"    ⚠️  Invalid: {filename} ({reason})")
                continue
            
            # Check for duplicates
            img_hash = get_image_hash(image_path)
            if img_hash in seen_hashes:
                duplicate_count += 1
                print(f"    🔄 Duplicate: {filename}")
                continue
            seen_hashes.add(img_hash)
            
            # Preprocess image
            output_filename = f"{crop}_{valid_count:05d}.{STANDARD_FORMAT}"
            output_path = os.path.join(crop_output_dir, output_filename)
            
            success, msg = preprocess_image(image_path, output_path)
            if success:
                valid_count += 1
                stats[crop]['valid'] += 1
            else:
                invalid_count += 1
                stats[crop]['invalid'] += 1
                print(f"    ❌ Error: {filename} ({msg})")

        # Augment to build a rich robust dataset (45+ images per class)
        base_processed = [f for f in os.listdir(crop_output_dir) if f.endswith(f".{STANDARD_FORMAT}")]
        if len(base_processed) > 0 and len(base_processed) < 45:
            print(f"   ✨ Augmenting {crop} to 45+ training samples...")
            from PIL import ImageEnhance
            aug_idx = len(base_processed)
            while aug_idx < 45:
                for src_name in list(base_processed):
                    if aug_idx >= 45:
                        break
                    src_path = os.path.join(crop_output_dir, src_name)
                    try:
                        with Image.open(src_path) as src_img:
                            aug_img = src_img.copy()
                            if np.random.rand() > 0.4:
                                aug_img = aug_img.transpose(Image.FLIP_LEFT_RIGHT)
                            if np.random.rand() > 0.5:
                                angle = int(np.random.choice([90, 180, 270, 10, -10]))
                                aug_img = aug_img.rotate(angle)
                            enhancer = ImageEnhance.Brightness(aug_img)
                            aug_img = enhancer.enhance(float(np.random.uniform(0.85, 1.15)))
                            aug_filename = f"{crop}_{aug_idx:05d}.{STANDARD_FORMAT}"
                            aug_img.save(os.path.join(crop_output_dir, aug_filename), 'JPEG', quality=90)
                            aug_idx += 1
                            stats[crop]['valid'] += 1
                    except Exception:
                        pass
        
        stats[crop]['invalid'] = invalid_count
        stats[crop]['duplicates'] = duplicate_count
        
        print(f"   ✓ Processed: {valid_count} images")
        print(f"   ⚠️  Invalid: {invalid_count} images")
        print(f"   🔄 Duplicates: {duplicate_count} images")
    
    # Print summary
    print("\n" + "="*60)
    print("📈 PREPROCESSING SUMMARY")
    print("="*60)
    
    total_original = 0
    total_processed = 0
    
    for crop in CROP_CATEGORIES:
        original = stats[crop]['total']
        processed = stats[crop]['valid']
        invalid = stats[crop]['invalid']
        duplicates = stats[crop]['duplicates']
        
        total_original += original
        total_processed += processed
        
        ratio = (processed / original * 100) if original > 0 else 0
        print(f"{crop.upper():12} | Total: {original:4} | Valid: {processed:4} ({ratio:5.1f}%) | Invalid: {invalid:3} | Duplicates: {duplicates:3}")
    
    print("-" * 60)
    print(f"{'TOTAL':12} | Total: {total_original:4} | Valid: {total_processed:4} ({total_processed/total_original*100:.1f}%) images processed")
    print("="*60)
    
    print(f"\n✅ Preprocessing complete!")
    print(f"📁 Output directory: {OUTPUT_DIR}")
    
    return OUTPUT_DIR


if __name__ == "__main__":
    try:
        output_dir = process_dataset()
        print(f"\n🎉 Ready for model training!")
        print(f"Next step: Run train_crop_cnn.py with --data-dir {output_dir}")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
