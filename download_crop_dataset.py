#!/usr/bin/env python
"""
Automated Fast Parallel Agricultural Crop & Waste Dataset Downloader
Downloads real, public-domain crop and crop-residue images across 10 classes:
- 9 crops: banana, cotton, groundnut, jute, maize, rice, sugarcane, sunflower, wheat
- 1 other: non-agricultural images (certificates, badges, documents, objects)
"""

import os
import sys
import io
import time
import json
import urllib.request
import urllib.parse
from pathlib import Path
from PIL import Image
import concurrent.futures

if sys.stdout and hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')
if sys.stderr and hasattr(sys.stderr, 'reconfigure'):
    sys.stderr.reconfigure(encoding='utf-8')

PROJECT_ROOT = Path(__file__).resolve().parent
DATA_DIR = PROJECT_ROOT / "data" / "crop_images"
TEST_DIR = PROJECT_ROOT / "data" / "test_crop_image"

CROP_SEARCH_QUERIES = {
    'banana': [
        'banana plant',
        'banana tree',
        'banana crop',
        'banana pseudostem',
        'banana plantation',
        'banana harvest',
        'banana fiber agriculture'
    ],
    'cotton': [
        'cotton field',
        'cotton plant',
        'cotton crop',
        'cotton harvest',
        'cotton stalk',
        'cotton boll',
        'raw cotton agriculture'
    ],
    'groundnut': [
        'peanut crop',
        'groundnut plant',
        'peanut harvest',
        'groundnut field',
        'peanut shells',
        'groundnut agriculture'
    ],
    'jute': [
        'jute plant',
        'jute crop',
        'jute field',
        'jute cultivation',
        'jute stalks drying',
        'jute fiber harvest'
    ],
    'maize': [
        'maize plant',
        'corn field',
        'maize crop harvest',
        'corn stalks',
        'maize stover',
        'corn cobs agriculture'
    ],
    'rice': [
        'paddy field',
        'rice crop harvest',
        'paddy straw',
        'rice husk',
        'rice straw bales',
        'paddy cultivation'
    ],
    'sugarcane': [
        'sugarcane field',
        'sugarcane crop',
        'sugarcane harvest',
        'sugarcane bagasse',
        'sugarcane plantation'
    ],
    'sunflower': [
        'sunflower field',
        'sunflower crop',
        'sunflower harvest',
        'sunflower stalks',
        'sunflower agriculture'
    ],
    'wheat': [
        'wheat field',
        'wheat crop',
        'wheat straw',
        'wheat harvest',
        'wheat stubble',
        'wheat bales'
    ],
    'other': [
        'certificate document',
        'award badge logo',
        'office document paper',
        'computer screenshot',
        'diploma certificate',
        'id badge card'
    ]
}


def search_wikimedia_files(query, limit=20):
    params = {
        'action': 'query',
        'format': 'json',
        'generator': 'search',
        'gsrsearch': query,
        'gsrnamespace': 6,
        'gsrlimit': limit,
        'prop': 'imageinfo',
        'iiprop': 'url|mime|size'
    }
    url = f"https://commons.wikimedia.org/w/api.php?{urllib.parse.urlencode(params)}"
    req = urllib.request.Request(url, headers={'User-Agent': 'AgriWasteDatasetBot/3.0 (agriwaste-marketplace@edu.in)'})
    
    urls = []
    try:
        with urllib.request.urlopen(req, timeout=12) as response:
            data = json.loads(response.read().decode('utf-8'))
            pages = data.get('query', {}).get('pages', {})
            for page in pages.values():
                info_list = page.get('imageinfo', [])
                if info_list:
                    img_url = info_list[0].get('url')
                    mime = info_list[0].get('mime', '')
                    if img_url and ('jpeg' in mime or 'jpg' in mime or 'png' in mime or img_url.lower().endswith(('.jpg', '.jpeg', '.png'))):
                        urls.append(img_url)
    except Exception as e:
        pass
    return urls


def download_and_validate_image(url, save_path):
    req = urllib.request.Request(url, headers={'User-Agent': 'AgriWasteDatasetBot/3.0 (agriwaste-marketplace@edu.in)'})
    try:
        with urllib.request.urlopen(req, timeout=15) as res:
            content = res.read()
            img = Image.open(io.BytesIO(content))
            img = img.convert('RGB')
            if img.size[0] < 64 or img.size[1] < 64:
                return False
            img.save(save_path, 'JPEG', quality=90)
            return True
    except Exception:
        return False


def process_crop(crop, queries, target_per_crop=22, test_per_crop=4):
    crop_dir = DATA_DIR / crop
    test_crop_dir = TEST_DIR / crop
    crop_dir.mkdir(parents=True, exist_ok=True)
    test_crop_dir.mkdir(parents=True, exist_ok=True)

    existing_train = len([f for f in os.listdir(crop_dir) if f.lower().endswith(('.jpg', '.jpeg', '.png'))])
    existing_test = len([f for f in os.listdir(test_crop_dir) if f.lower().endswith(('.jpg', '.jpeg', '.png'))])

    found_urls = set()
    for q in queries:
        if len(found_urls) >= (target_per_crop + test_per_crop) * 2:
            break
        urls = search_wikimedia_files(q, limit=25)
        for u in urls:
            found_urls.add(u)
        time.sleep(0.2)

    success_count = existing_train
    test_count = existing_test
    img_idx = existing_train + 1

    for url in found_urls:
        if success_count >= target_per_crop and test_count >= test_per_crop:
            break

        if test_count < test_per_crop:
            filename = f"{crop}_test_{test_count + 1}.jpg"
            save_path = test_crop_dir / filename
            if not save_path.exists():
                if download_and_validate_image(url, save_path):
                    test_count += 1
                    time.sleep(0.1)
                    continue
            else:
                test_count += 1
                continue

        if success_count < target_per_crop:
            filename = f"{crop}_{img_idx:03d}.jpg"
            save_path = crop_dir / filename
            if not save_path.exists():
                if download_and_validate_image(url, save_path):
                    success_count += 1
                    img_idx += 1
                    time.sleep(0.1)
            else:
                success_count += 1
                img_idx += 1

    print(f"   ✓ Finished [{crop.upper()}]: {success_count} training + {test_count} test images.")
    return crop, success_count, test_count


def build_crop_dataset():
    print("=" * 65)
    print("🌾 FAST PARALLEL DOWNLOAD: AGRICULTURAL CROPS & NON-CROP DATASET")
    print("=" * 65)

    DATA_DIR.mkdir(parents=True, exist_ok=True)
    TEST_DIR.mkdir(parents=True, exist_ok=True)

    start_time = time.time()
    results = {}
    with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
        futures = {executor.submit(process_crop, crop, queries): crop for crop, queries in CROP_SEARCH_QUERIES.items()}
        for future in concurrent.futures.as_completed(futures):
            crop, train_cnt, test_cnt = future.result()
            results[crop] = {'train': train_cnt, 'test': test_cnt}

    elapsed = time.time() - start_time
    print("\n" + "=" * 65)
    print(f"📊 DATASET SUMMARY (completed in {elapsed:.1f}s):")
    print("=" * 65)
    for c in sorted(results.keys()):
        counts = results[c]
        print(f"   • {c:12}: {counts['train']} train | {counts['test']} test")
    print(f"\n📁 Dataset location: {DATA_DIR}")
    print(f"📁 Test set location: {TEST_DIR}")


if __name__ == "__main__":
    build_crop_dataset()
    
