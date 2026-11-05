import mimetypes
mimetypes.add_type('image/avif', '.avif')
mimetypes.add_type('image/webp', '.webp')
mimetypes.add_type('image/jpeg', '.jfif')
#!/usr/bin/env python
"""
Master Flask Server - Unified Frontend + Backend
Combines AI System API + Chatbot + Static Frontend
"""

import os
import sys
import json
from pathlib import Path

# Ensure UTF-8 output encoding for Windows terminals
if sys.stdout and hasattr(sys.stdout, 'reconfigure'):
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass
if sys.stderr and hasattr(sys.stderr, 'reconfigure'):
    try:
        sys.stderr.reconfigure(encoding='utf-8')
    except Exception:
        pass

# Load environment variables from .env if available
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

from flask import Flask, render_template, request, jsonify, send_from_directory
from werkzeug.utils import secure_filename
from datetime import datetime
import traceback

# Try to import AI system components
try:
    from ai_system import AgriculturalAISystem, create_api_app
    AI_AVAILABLE = True
    print("[OK] AI System loaded")
except Exception as e:
    AI_AVAILABLE = False
    print(f"[WARN] AI System not available: {e}")

# Try to import chatbot components
try:
    from groq import Groq
    from gtts import gTTS
    from agri_market_knowledge import AgriMarketKnowledge, agri_knowledge
    CHATBOT_AVAILABLE = True
    print("[OK] Chatbot & Agricultural Intelligence Engine loaded")
except Exception as e:
    try:
        from agri_market_knowledge import AgriMarketKnowledge, agri_knowledge
        CHATBOT_AVAILABLE = True
        print("[OK] Chatbot Agricultural Intelligence Engine loaded (Groq/gTTS optional)")
    except Exception as e2:
        CHATBOT_AVAILABLE = False
        print(f"[WARN] Chatbot not available: {e2}")


# Create main Flask app
app = Flask(__name__, 
    static_folder='.',
    static_url_path='',
    template_folder='.'
)

# Configuration
app.config['MAX_CONTENT_LENGTH'] = 50 * 1024 * 1024  # 50MB max
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['ALLOWED_EXTENSIONS'] = {'webm', 'wav', 'mp3', 'm4a', 'jpg', 'jpeg', 'png', 'gif'}

# Create upload folders
Path(app.config['UPLOAD_FOLDER']).mkdir(parents=True, exist_ok=True)
Path('uploads/analysis').mkdir(parents=True, exist_ok=True)

# Initialize AI System if available
if AI_AVAILABLE:
    try:
        ai_system = AgriculturalAISystem()
        print("✓ AI System initialized")
    except Exception as e:
        print(f"⚠ Failed to initialize AI System: {e}")
        AI_AVAILABLE = False

# Initialize Chatbot if available
groq_client = None
if CHATBOT_AVAILABLE:
    try:
        groq_api_key = os.getenv('GROQ_API_KEY')
        if groq_api_key:
            groq_client = Groq(api_key=groq_api_key)
            print("✓ Chatbot Groq LLM initialized")
        else:
            print("ℹ Chatbot running with local Agricultural Knowledge Engine")
    except Exception as e:
        print(f"⚠ Groq initialization notice: {e}")
        groq_client = None


# =====================
# FRONTEND ROUTES
# =====================

@app.route('/')
def index():
    """Home page"""
    return send_from_directory('.', 'index.html')

@app.route('/<path:filename>')
def serve_static(filename):
    """Serve static files"""
    if filename.endswith('.html'):
        return send_from_directory('.', filename)
    elif filename.startswith('css/'):
        return send_from_directory('css', filename.replace('css/', ''))
    elif filename.startswith('js/'):
        return send_from_directory('js', filename.replace('js/', ''))
    elif filename.startswith('data/'):
        return send_from_directory('data', filename.replace('data/', ''))
    elif filename.startswith('Dataset/'):
        # Serve crop images from the Dataset directory (handles spaces/special chars)
        sub = filename[len('Dataset/'):]
        return send_from_directory('Dataset', sub)
    return send_from_directory('.', filename)


# =====================
# AI SYSTEM API ROUTES
# =====================

@app.route('/api/analyze', methods=['POST'])
def analyze_waste():
    """Analyze waste from uploaded image"""
    if not AI_AVAILABLE:
        return jsonify({"error": "AI System not available"}), 503
    
    try:
        # Collect up to 15 uploaded images
        files = request.files.getlist('images')
        if not files or all(getattr(f, 'filename', '') == '' for f in files):
            files = request.files.getlist('image')

        valid_files = [f for f in files if f and getattr(f, 'filename', '') != '' and allowed_file(f.filename)][:15]
        if not valid_files:
            return jsonify({"error": "No valid image provided"}), 400

        filepaths = []
        for f in valid_files:
            fname = secure_filename(f.filename)
            fpath = os.path.join('uploads/analysis', f"{datetime.now().strftime('%Y%m%d%H%M%S%f')}_{fname}")
            f.save(fpath)
            filepaths.append(fpath)

        quantity = float(request.form.get('quantity', 1000))
        waste_type = request.form.get('waste_type', None)

        # Run AI analysis across all uploaded images (multi-image ensembling)
        analysis = ai_system.analyze_waste_complete(
            filepaths if len(filepaths) > 1 else filepaths[0],
            waste_type,
            quantity
        )
        
        # Save primary result
        save_analysis_result(analysis, valid_files[0].filename)
        
        return jsonify(analysis), 200
    
    except Exception as e:
        print(f"Error in analyze: {e}")
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500


@app.route('/api/performance', methods=['GET'])
def get_performance():
    """Get system performance report"""
    if not AI_AVAILABLE:
        return jsonify({"error": "AI System not available"}), 503
    
    try:
        report = ai_system.get_performance_report()
        return jsonify(report), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/api/classify', methods=['POST'])
def classify_image():
    """Classify waste from image"""
    if not AI_AVAILABLE:
        return jsonify({"error": "AI System not available"}), 503
    
    try:
        if 'image' not in request.files:
            return jsonify({"error": "No image provided"}), 400

        file = request.files['image']
        if file.filename == '':
            return jsonify({"error": "No file selected"}), 400

        filename = secure_filename(file.filename)
        filepath = os.path.join('uploads/analysis', filename)
        file.save(filepath)

        # Get classification
        classification = ai_system._step_classify_waste(filepath)
        
        return jsonify(classification), 200
    
    except Exception as e:
        print(f"Error in classify: {e}")
        return jsonify({"error": str(e)}), 500


@app.route('/api/price-predict', methods=['POST'])
def predict_price():
    """Predict price for waste"""
    if not AI_AVAILABLE:
        return jsonify({"error": "AI System not available"}), 503
    
    try:
        data = request.json
        waste_type = data.get('waste_type', 'rice')
        quantity = float(data.get('quantity', 1000))
        season = data.get('season', 'kharif')

        price_data = ai_system._step_predict_price(waste_type, quantity, season)
        
        return jsonify(price_data), 200
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/api/quality-assess', methods=['POST'])
def assess_quality():
    """Assess quality parameters"""
    if not AI_AVAILABLE:
        return jsonify({"error": "AI System not available"}), 503
    
    try:
        data = request.json
        moisture = float(data.get('moisture', 10))
        calorific = float(data.get('calorific', 15))
        purity = float(data.get('purity', 98))
        carbon = float(data.get('carbon', 45))

        quality = ai_system._step_assess_quality(moisture, calorific, purity, carbon)
        quality['quality_score'] = ai_system._calculate_quality_score(quality)
        
        return jsonify(quality), 200
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/api/recommendations', methods=['POST'])
def get_recommendations():
    """Get buyer recommendations"""
    if not AI_AVAILABLE:
        return jsonify({"error": "AI System not available"}), 503
    
    try:
        data = request.json
        waste_type = data.get('waste_type', 'rice')
        quality_score = float(data.get('quality_score', 80))

        recommendations = ai_system._step_recommend_buyers(waste_type, quality_score)
        
        return jsonify(recommendations), 200
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/api/carbon', methods=['POST'])
def calculate_carbon():
    """Calculate carbon impact"""
    if not AI_AVAILABLE:
        return jsonify({"error": "AI System not available"}), 503
    
    try:
        data = request.json
        waste_type = data.get('waste_type', 'rice')
        quantity = float(data.get('quantity', 1000))

        carbon_data = ai_system._step_calculate_carbon(waste_type, quantity)
        
        return jsonify(carbon_data), 200
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# =====================
# LIVE MARKETPLACE & DATASET PERSISTENCE
# =====================

LISTINGS_FILE = os.path.join('data', 'live_listings.json')
TRANSACTIONS_FILE = os.path.join('data', 'live_transactions.json')

def seed_listings_from_dataset():
    """Seed real-world listings from Agricultural Waste Core Dataset"""
    listings = []
    csv_path = os.path.join('data', 'Agricultural_Waste_Core_Dataset.csv')
    price_map = {
        'rice': 5200, 'wheat': 4500, 'sugarcane': 3800, 'cotton': 5400,
        'groundnut': 6200, 'maize': 4800, 'jute': 3200, 'banana': 6800, 'sunflower': 4600
    }
    if os.path.exists(csv_path):
        try:
            import pandas as pd
            df = pd.read_csv(csv_path)
            for idx, row in df.head(30).iterrows():
                crop = str(row.get('Crop_Type', 'Rice')).strip()
                waste = str(row.get('Waste_Type', 'Residue')).strip()
                qty = float(row.get('Quantity_tons', 10.0))
                moisture = float(row.get('Moisture_Content(%)', 12.0))
                calorific = float(row.get('Calorific_Value(MJ/kg)', 15.0))
                region = str(row.get('Region', 'Punjab')).strip()
                farmer_id = str(row.get('Farmer_ID', f'FARM{1000+idx}')).strip()
                
                crop_key = crop.lower()
                base_p = price_map.get(crop_key, 4500)
                price_ton = int(base_p * (1.0 - (moisture - 12.0) * 0.01))
                
                cat = 'straw' if 'straw' in waste.lower() or 'stover' in waste.lower() else (
                    'husk' if 'husk' in waste.lower() or 'shell' in waste.lower() or 'peel' in waste.lower() else (
                        'bagasse' if 'bagasse' in waste.lower() else 'crop-residue'
                    )
                )
                quality_score = 5 if moisture < 15 and calorific > 14 else (4 if moisture < 25 else 3)
                
                # Map crop to image key (matches CROP_IMAGE_MAP in image_map.js)
                IMAGE_KEY_MAP = {
                    'rice': 'rice', 'wheat': 'wheat', 'sugarcane': 'sugarcane',
                    'cotton': 'cotton', 'groundnut': 'groundnut', 'maize': 'maize',
                    'jute': 'jute', 'banana': 'banana', 'sunflower': 'sunflower',
                    'bamboo': 'bamboo', 'cattle': 'cattle', 'coffee': 'coffee',
                    'palm': 'palm', 'poultry': 'poultry', 'soybean': 'soybean', 'tea': 'tea'
                }
                image_key = IMAGE_KEY_MAP.get(crop_key, crop_key)
                listings.append({
                    "id": f"L{100 + idx}",
                    "name": f"{crop} {waste}",
                    "category": cat,
                    "imageKey": image_key,
                    "price": price_ton,
                    "quantity": int(qty * 10),
                    "location": region,
                    "seller": f"Farmer {farmer_id[-4:]} ({region} Agri Co-op)",
                    "rating": round(4.2 + (idx % 7) * 0.1, 1),
                    "date": f"2026-03-{10 + (idx % 18):02d}",
                    "moisture": f"{moisture:.1f}%",
                    "calorific": f"{calorific:.1f} MJ/kg",
                    "quality": quality_score,
                    "bestReuse": str(row.get('Best_Reuse_Option', 'Biofuel')),
                    "verified": True
                })
        except Exception as e:
            print(f"Error seeding listings from CSV: {e}")

    if not listings:
        listings = [
            {"id": "L101", "name": "Rice Paddy Straw", "category": "straw", "imageKey": "rice", "price": 5200, "quantity": 150, "location": "Punjab", "seller": "Farmer Singh (Punjab Co-op)", "rating": 4.8, "date": "2026-03-12", "moisture": "12.0%", "calorific": "15.0 MJ/kg", "quality": 5, "verified": True},
            {"id": "L102", "name": "Wheat Straw Bale", "category": "straw", "imageKey": "wheat", "price": 4500, "quantity": 200, "location": "Haryana", "seller": "Kumar Farm Resellers", "rating": 4.7, "date": "2026-03-14", "moisture": "13.0%", "calorific": "16.0 MJ/kg", "quality": 5, "verified": True},
            {"id": "L103", "name": "Sugarcane Bagasse", "category": "bagasse", "imageKey": "sugarcane", "price": 3800, "quantity": 300, "location": "Maharashtra", "seller": "Kisan Sugar Mill Co", "rating": 4.5, "date": "2026-03-15", "moisture": "35.0%", "calorific": "9.5 MJ/kg", "quality": 4, "verified": True},
            {"id": "L104", "name": "Cotton Stalks", "category": "crop-residue", "imageKey": "cotton", "price": 5400, "quantity": 120, "location": "Gujarat", "seller": "Vidarbha Cotton Hub", "rating": 4.6, "date": "2026-03-16", "moisture": "11.5%", "calorific": "15.5 MJ/kg", "quality": 4, "verified": True},
            {"id": "L105", "name": "Groundnut Stover", "category": "husk", "imageKey": "groundnut", "price": 6200, "quantity": 100, "location": "Karnataka", "seller": "Deccan Oilseeds Union", "rating": 4.9, "date": "2026-03-18", "moisture": "9.5%", "calorific": "17.5 MJ/kg", "quality": 5, "verified": True}
        ]
    return listings

def load_listings():
    os.makedirs('data', exist_ok=True)
    if os.path.exists(LISTINGS_FILE):
        try:
            with open(LISTINGS_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception:
            pass
    seeded = seed_listings_from_dataset()
    save_listings(seeded)
    return seeded

def save_listings(listings):
    os.makedirs('data', exist_ok=True)
    with open(LISTINGS_FILE, 'w', encoding='utf-8') as f:
        json.dump(listings, f, indent=2, ensure_ascii=False)

def load_transactions():
    os.makedirs('data', exist_ok=True)
    if os.path.exists(TRANSACTIONS_FILE):
        try:
            with open(TRANSACTIONS_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception:
            pass
    initial = [
        {"id": "TXN1001", "buyer": "Punjab Bio-Energy Corp", "item": "Rice Paddy Straw", "amount": 78000, "quantity": 15, "date": "2026-03-10", "status": "completed"},
        {"id": "TXN1002", "buyer": "GreenGrid Power & Paper", "item": "Wheat Straw Bundle", "amount": 45000, "quantity": 10, "date": "2026-03-08", "status": "completed"},
        {"id": "TXN1003", "buyer": "Maharani Eco-Fuels", "item": "Sugarcane Bagasse", "amount": 57000, "quantity": 15, "date": "2026-03-05", "status": "completed"},
        {"id": "TXN1004", "buyer": "Deccan BioChar & Soil", "item": "Groundnut Stover", "amount": 49600, "quantity": 8, "date": "2026-03-03", "status": "completed"},
        {"id": "TXN1005", "buyer": "Bengal Eco-Fiber", "item": "Jute Stick", "amount": 32000, "quantity": 10, "date": "2026-03-01", "status": "completed"},
    ]
    save_transactions(initial)
    return initial

def save_transactions(txns):
    os.makedirs('data', exist_ok=True)
    with open(TRANSACTIONS_FILE, 'w', encoding='utf-8') as f:
        json.dump(txns, f, indent=2, ensure_ascii=False)


@app.route('/api/listings', methods=['GET'])
def get_listings():
    """Fetch live marketplace listings with dynamic filtering and search"""
    listings = load_listings()
    
    search = request.args.get('search', '').lower().strip()
    category = request.args.get('category', '').lower().strip()
    location = request.args.get('location', '').lower().strip()
    min_price = request.args.get('minPrice', type=float)
    max_price = request.args.get('maxPrice', type=float)
    sort_by = request.args.get('sort', 'recommended')

    filtered = []
    for item in listings:
        if search:
            match_search = (search in item.get('name', '').lower() or
                            search in item.get('seller', '').lower() or
                            search in item.get('location', '').lower() or
                            search in item.get('category', '').lower())
            if not match_search:
                continue
        if category and item.get('category', '').lower() != category:
            continue
        if location and location not in item.get('location', '').lower():
            continue
        price = float(item.get('price', 0))
        if min_price is not None and price < min_price:
            continue
        if max_price is not None and price > max_price:
            continue
        filtered.append(item)

    if sort_by == 'price-low':
        filtered.sort(key=lambda x: float(x.get('price', 0)))
    elif sort_by == 'price-high':
        filtered.sort(key=lambda x: float(x.get('price', 0)), reverse=True)
    elif sort_by == 'quantity':
        filtered.sort(key=lambda x: float(x.get('quantity', 0)), reverse=True)
    elif sort_by == 'rating':
        filtered.sort(key=lambda x: float(x.get('rating', 0)), reverse=True)
    
    return jsonify(filtered), 200


@app.route('/api/listings', methods=['POST'])
def add_listing():
    """Create a live listing in the real marketplace"""
    try:
        data = request.json or {}
        listings = load_listings()
        new_id = f"L{int(datetime.now().timestamp()) % 100000}"
        
        name = data.get('name') or data.get('wasteType') or 'Agricultural Biomass'
        price = float(data.get('price') or 4500)
        quantity = float(data.get('quantity') or 50)
        location = data.get('location') or 'Punjab'
        category = data.get('category') or 'crop-residue'
        seller = data.get('seller') or 'Verified Agri Producer'
        moisture = data.get('moisture') or '12%'
        quality = int(data.get('quality') or 5)

        new_item = {
            "id": new_id,
            "name": name,
            "category": category,
            "price": price,
            "quantity": quantity,
            "location": location,
            "seller": seller,
            "rating": 5.0,
            "date": datetime.now().strftime('%Y-%m-%d'),
            "moisture": str(moisture),
            "quality": quality,
            "verified": True
        }
        listings.insert(0, new_item)
        save_listings(listings)
        return jsonify({"status": "success", "listing": new_item}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/api/listings/<listing_id>', methods=['DELETE'])
def delete_listing(listing_id):
    """Delete a listing from the marketplace"""
    try:
        listings = load_listings()
        listings = [l for l in listings if str(l.get('id')) != str(listing_id)]
        save_listings(listings)
        return jsonify({"status": "deleted", "id": listing_id}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/api/transactions', methods=['GET'])
def get_transactions_route():
    """Get live transactions list"""
    return jsonify(load_transactions()), 200


@app.route('/api/transactions', methods=['POST'])
def create_transaction_route():
    """Record a real transaction checkout"""
    try:
        data = request.json or {}
        txns = load_transactions()
        new_id = f"TXN{int(datetime.now().timestamp()) % 100000}"
        
        new_txn = {
            "id": new_id,
            "buyer": data.get('buyer', 'Green Agro Industries'),
            "item": data.get('item', 'Biomass Residue'),
            "amount": float(data.get('amount', 50000)),
            "quantity": float(data.get('quantity', 10)),
            "date": datetime.now().strftime('%Y-%m-%d'),
            "status": "completed"
        }
        txns.insert(0, new_txn)
        save_transactions(txns)
        return jsonify({"status": "success", "transaction": new_txn}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/api/dashboard/stats', methods=['GET'])
def get_dashboard_stats():
    """Compute live dashboard metrics based on real database records"""
    try:
        listings = load_listings()
        txns = load_transactions()
        
        total_earnings = sum(t.get('amount', 0) for t in txns)
        total_traded = sum(t.get('quantity', 0) for t in txns)
        total_carbon_credits = round(total_traded * 1.5, 1)

        cat_counts = {}
        for l in listings:
            cat = l.get('name', 'Other').split()[0].title()
            cat_counts[cat] = cat_counts.get(cat, 0) + 1

        top_cats = sorted(cat_counts.items(), key=lambda x: x[1], reverse=True)[:5]
        waste_labels = [c[0] for c in top_cats] or ['Rice', 'Wheat', 'Sugarcane', 'Cotton', 'Other']
        waste_values = [c[1] for c in top_cats] or [35, 25, 20, 12, 8]

        revenue_values = [int(total_earnings * 0.18), int(total_earnings * 0.24), int(total_earnings * 0.28), int(total_earnings * 0.30)]
        if total_earnings == 0:
            revenue_values = [45000, 58000, 62000, 80000]

        return jsonify({
            "earnings": total_earnings or 261600,
            "wasteTraded": total_traded or 58,
            "transactions": len(txns),
            "carbonCredits": total_carbon_credits or 87.0,
            "revenueData": {
                "labels": ["Week 1", "Week 2", "Week 3", "Week 4"],
                "values": revenue_values
            },
            "wasteDistribution": {
                "labels": waste_labels,
                "values": waste_values
            },
            "recentTransactions": txns[:6],
            "activeListings": listings[:5]
        }), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# =====================
# CHATBOT API ROUTES
# =====================

def allowed_file(filename):
    """Check if file is allowed"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']


@app.route('/api/chat/transcribe', methods=['POST'])
def transcribe_audio():
    """Transcribe audio to text"""
    if not CHATBOT_AVAILABLE:
        return jsonify({"error": "Chatbot not available"}), 503
    
    try:
        if 'audio' not in request.files:
            return jsonify({"error": "No audio provided"}), 400

        file = request.files['audio']
        if file.filename == '':
            return jsonify({"error": "No file selected"}), 400

        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)

        transcribed_text = ""
        # Transcribe with Groq Whisper if available
        if groq_client:
            with open(filepath, 'rb') as f:
                response = groq_client.audio.transcriptions.create(
                    model='whisper-large-v3-turbo',
                    file=f,
                )
                transcribed_text = response.text

        # Clean up
        if os.path.exists(filepath):
            os.remove(filepath)
        
        if not transcribed_text:
            return jsonify({"error": "Audio transcription unavailable"}), 500

        return jsonify({"text": transcribed_text}), 200
    
    except Exception as e:
        print(f"Error in transcribe: {e}")
        return jsonify({"error": str(e)}), 500


@app.route('/api/chat/ask', methods=['POST'])
def ask_question():
    """Get grounded agricultural intelligence chatbot response"""
    if not CHATBOT_AVAILABLE:
        return jsonify({"error": "Chatbot not available"}), 503
    
    try:
        data = request.json or {}
        question = data.get('question', '').strip()
        history = data.get('history', [])
        
        if not question:
            return jsonify({"error": "No question provided"}), 400

        from agri_market_knowledge import agri_knowledge
        result = agri_knowledge.generate_expert_response(question, history)
        
        return jsonify({
            "answer": result.get("answer"),
            "source": result.get("source"),
            "model": result.get("model"),
            "detected_crops": result.get("detected_crops", []),
            "detected_topics": result.get("detected_topics", [])
        }), 200
    
    except Exception as e:
        print(f"Error in ask: {e}")
        return jsonify({"error": str(e)}), 500


@app.route('/api/chat/text-to-speech', methods=['POST'])
def text_to_speech():
    """Convert text to speech"""
    try:
        data = request.json or {}
        text = data.get('text', '').strip()
        
        if not text:
            return jsonify({"error": "No text provided"}), 400

        # Clean markdown formatting for clear audio pronunciation
        import re
        clean_text = re.sub(r'#+|\*+|_+|`+|\[.*?\]\(.*?\)', '', text)
        clean_text = re.sub(r'\|.*\|', '', clean_text)
        clean_text = re.sub(r'\s+', ' ', clean_text).strip()
        
        words = clean_text.split()
        if len(words) > 120:
            clean_text = ' '.join(words[:120]) + '... For full details and tables, please see the complete answer on your screen.'

        # Create audio file
        from gtts import gTTS
        tts = gTTS(clean_text, lang='en')
        filename = f"tts_{int(datetime.now().timestamp())}.mp3"
        audio_dir = Path('static/audio')
        audio_dir.mkdir(parents=True, exist_ok=True)
        audio_path = os.path.join('static', 'audio', filename)
        
        tts.save(audio_path)
        
        return jsonify({"audio_url": f"/static/audio/{filename}"}), 200
    
    except Exception as e:
        print(f"Error in text_to_speech: {e}")
        return jsonify({"error": str(e)}), 500


# =====================
# UTILITY ROUTES
# =====================

def save_analysis_result(analysis, filename):
    """Save analysis result to file"""
    try:
        results_dir = Path('results')
        results_dir.mkdir(parents=True, exist_ok=True)
        
        result_filename = f"analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        result_path = results_dir / result_filename
        
        with open(result_path, 'w') as f:
            json.dump(analysis, f, indent=2)
        
        print(f"✓ Analysis saved: {result_path}")
    except Exception as e:
        print(f"⚠ Could not save analysis: {e}")


@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        "status": "ok",
        "timestamp": datetime.now().isoformat(),
        "ai_system": "available" if AI_AVAILABLE else "unavailable",
        "chatbot": "available" if CHATBOT_AVAILABLE else "unavailable"
    }), 200


@app.route('/api/status', methods=['GET'])
def system_status():
    """Get full system status"""
    status = {
        "timestamp": datetime.now().isoformat(),
        "components": {
            "frontend": "running",
            "ai_system": "available" if AI_AVAILABLE else "unavailable",
            "chatbot": "available" if CHATBOT_AVAILABLE else "unavailable",
            "database": "not configured"
        },
        "capabilities": []
    }
    
    if AI_AVAILABLE:
        status["capabilities"].extend([
            "waste_classification",
            "price_prediction",
            "quality_assessment",
            "buyer_recommendations",
            "carbon_impact_calculation"
        ])
    
    if CHATBOT_AVAILABLE:
        status["capabilities"].extend([
            "audio_transcription",
            "question_answering",
            "text_to_speech"
        ])
    
    return jsonify(status), 200


# =====================
# ERROR HANDLERS
# =====================

@app.errorhandler(404)
def not_found(e):
    """Handle 404 errors"""
    return jsonify({"error": "Not found"}), 404


@app.errorhandler(500)
def internal_error(e):
    """Handle 500 errors"""
    return jsonify({"error": "Internal server error"}), 500


# =====================
# MAIN ENTRY POINT
# =====================

if __name__ == '__main__':
    print("\n" + "="*60)
    print("🌾 AgriWaste to Worth - Unified Server")
    print("="*60)
    print(f"\n📡 Starting server...")
    print(f"🌐 Frontend: http://localhost:5000")
    print(f"📊 API: http://localhost:5000/api/")
    print(f"💬 Status: http://localhost:5000/api/status")
    print(f"\n✓ AI System: {'Enabled' if AI_AVAILABLE else 'Disabled'}")
    print(f"✓ Chatbot: {'Enabled' if CHATBOT_AVAILABLE else 'Disabled'}")
    print("\nPress Ctrl+C to stop the server.")
    print("="*60 + "\n")
    
    # Run server
    app.run(
        host='0.0.0.0',
        port=5000,
        debug=True,
        use_reloader=False
    )
