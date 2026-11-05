# 🌾 AgriWaste to Worth - Full Project Setup Guide

## ✅ What You Have

A complete Agriculture Waste Marketplace application with:

- **Frontend:** HTML/CSS/JavaScript UI
- **Backend 1:** AI System (Classification, Price Prediction, Quality Assessment, Recommendations, Carbon Impact)
- **Backend 2:** AI Chatbot (Audio Transcription, Q&A, Text-to-Speech)
- **Database:** Mock data (ready for SQL integration)
- **API Server:** Unified Flask REST API

---

## 🚀 Quick Start (3 Steps)

### Windows Users - EASIEST METHOD

**Double-click this file:**
```
START.bat
```

That's it! The server will start on `http://localhost:5000`

---

### Alternative Methods

#### Option 1: Python Script
```bash
python startup.py
```

#### Option 2: PowerShell
```powershell
.\START.ps1
```

#### Option 3: Manual Terminal
```bash
# Activate virtual environment (if created)
venv\Scripts\activate

# Install dependencies (first time only)
pip install flask pandas numpy tensorflow groq gtts werkzeug

# Start server
python server.py
```

---

## 📱 Access Points

Once the server is running, open in your browser:

| Component | URL | Purpose |
|-----------|-----|---------|
| **Home Page** | http://localhost:5000 | Main interface |
| **AI Analyzer** | http://localhost:5000/ai-analyzer.html | Waste analysis |
| **Marketplace** | http://localhost:5000/marketplace.html | Buy/sell waste |
| **Chatbot** | http://localhost:5000/chatbot.html | Ask questions |
| **Dashboard** | http://localhost:5000/dashboard.html | Analytics |
| **API Status** | http://localhost:5000/api/status | Check backend |
| **Health Check** | http://localhost:5000/api/health | System health |

---

## 🔌 API Endpoints

### AI System Endpoints

#### 1. Analyze Waste (Complete)
```
POST /api/analyze
Content-Type: multipart/form-data

Parameters:
- image: <image file>
- quantity: 1000 (kg)
- waste_type: optional

Response:
{
  "classification": {...},
  "quality": {...},
  "price": {...},
  "buyer_recommendations": [...],
  "carbon_impact": {...},
  "overall_score": {...}
}
```

#### 2. Classify Image
```
POST /api/classify
Content-Type: multipart/form-data

Parameters:
- image: <image file>

Response:
{
  "waste_type": "rice",
  "confidence": 0.95
}
```

#### 3. Predict Price
```
POST /api/price-predict
Content-Type: application/json

{
  "waste_type": "rice",
  "quantity": 1000,
  "season": "kharif"
}
```

#### 4. Assess Quality
```
POST /api/quality-assess
Content-Type: application/json

{
  "moisture": 10.5,
  "calorific": 15.5,
  "purity": 97.3,
  "carbon": 45
}
```

#### 5. Get Recommendations
```
POST /api/recommendations
Content-Type: application/json

{
  "waste_type": "rice",
  "quality_score": 83.3
}
```

#### 6. Calculate Carbon Impact
```
POST /api/carbon
Content-Type: application/json

{
  "waste_type": "rice",
  "quantity": 5000
}
```

### Chatbot Endpoints

#### 1. Transcribe Audio
```
POST /api/chat/transcribe
Content-Type: multipart/form-data

Parameters:
- audio: <audio file>

Response:
{
  "text": "Transcribed text from audio"
}
```

#### 2. Ask Question
```
POST /api/chat/ask
Content-Type: application/json

{
  "question": "What is the best time to harvest?"
}

Response:
{
  "answer": "The best time to harvest depends on..."
}
```

#### 3. Text to Speech
```
POST /api/chat/text-to-speech
Content-Type: application/json

{
  "text": "Hello, this is the answer."
}

Response:
{
  "audio_url": "/static/audio/tts_1234567890.mp3"
}
```

### System Endpoints

#### Health Check
```
GET /api/health

Response:
{
  "status": "ok",
  "timestamp": "2024-03-10T10:30:00",
  "ai_system": "available",
  "chatbot": "available"
}
```

#### System Status
```
GET /api/status

Response:
{
  "timestamp": "2024-03-10T10:30:00",
  "components": {
    "frontend": "running",
    "ai_system": "available",
    "chatbot": "available"
  },
  "capabilities": [
    "waste_classification",
    "price_prediction",
    "quality_assessment",
    "buyer_recommendations",
    "carbon_impact_calculation",
    "audio_transcription",
    "question_answering",
    "text_to_speech"
  ]
}
```

---

## 🛠️ Frontend Usage

### Upload and Analyze
1. Go to **AI Analyzer** page
2. Upload a crop waste image
3. Enter quantity in kg
4. Click "Analyze"
5. View results

### Marketplace
1. Browse available waste listings
2. Check prices and availability
3. Add to cart
4. Proceed to checkout

### Chatbot
1. Go to **Chatbot** page
2. Click microphone to record question
3. Or type question manually
4. Get instant AI response
5. Listen to audio response

### Dashboard
1. View trading statistics
2. Check revenue charts
3. Monitor transactions
4. Track carbon impact

---

## 📊 Project Structure

```
Agriculture_waste_marketplace/
│
├── 🌐 Frontend (HTML/CSS/JS)
│   ├── index.html              # Home page
│   ├── ai-analyzer.html        # AI analysis interface
│   ├── marketplace.html        # Buy/sell interface
│   ├── chatbot.html           # Chatbot interface
│   ├── dashboard.html         # Analytics dashboard
│   ├── about.html             # About page
│   ├── css/style.css          # Styles
│   └── js/                    # JavaScript modules
│       ├── api.js             # API client
│       ├── main.js            # Core app
│       ├── auth.js            # Authentication
│       ├── chatbot.js         # Chatbot logic
│       ├── ai-analyzer.js     # AI analyzer logic
│       ├── marketplace.js     # Marketplace logic
│       ├── dashboard.js       # Dashboard logic
│       └── dashboard.js       # Dashboard logic
│
├── 🐍 Backend (Python)
│   ├── server.py              # Main Flask server (START HERE)
│   ├── ai_system.py           # AI system implementation
│   ├── plant_waste_pipeline.py # CNN model pipeline
│   ├── model_evaluation.py    # Metrics & evaluation
│   ├── model_utilities.py     # Model management
│   ├── startup.py             # Startup script
│   └── START.bat              # Windows launcher
│
├── 📁 Data & Models
│   ├── data/
│   │   ├── crop_images/       # Training images
│   │   └── Agricultural_Waste_Core_Dataset.csv
│   ├── models/
│   │   ├── plant_classifier.keras  # Trained CNN
│   │   └── labels.json
│   └── results/               # Analysis results
│
├── 📚 Documentation
│   ├── README.md              # This file
│   ├── QUICK_START.txt
│   ├── SETUP_GUIDE.md
│   ├── AI_SYSTEM_README.md
│   ├── AI_METRICS_GUIDE.md
│   ├── AI_IMPLEMENTATION_SUMMARY.md
│   └── PROJECT_COMPLETION_REPORT.md
│
└── 🔧 Configuration
    └── requirements.txt       # Python dependencies
```

---

## 🔧 Configuration

### Environment Variables

Create a `.env` file (optional):

```
FLASK_ENV=development
FLASK_DEBUG=1
GROQ_API_KEY=your_groq_api_key
```

### Dependencies

All required packages:
- `flask` - Web framework
- `pandas` - Data processing
- `numpy` - Numerical computing
- `tensorflow` - Deep learning (CNN)
- `groq` - AI LLM API
- `gtts` - Text-to-speech
- `werkzeug` - WSGI utilities

Install all at once:
```bash
pip install flask pandas numpy tensorflow groq gtts werkzeug
```

---

## 🧪 Testing

### Test AI System (Without Frontend)
```bash
python run_full_demo.py
```

### Run Test Suite
```bash
python ai_metrics_test.py
```

### Test Individual Modules
```bash
python run_ai_demos.py
```

---

## 🐛 Troubleshooting

### Issue: "ModuleNotFoundError: No module named 'flask'"
**Solution:**
```bash
pip install flask
```

### Issue: "Port 5000 already in use"
**Solution:** Change port in `server.py`:
```python
app.run(host='0.0.0.0', port=5001, debug=True)
```

### Issue: "SSL Certificate Verify Failed"
**Solution:** This is usually not a problem. The app works without SSL in development.

### Issue: "Groq API Error"
**Solution:** Check your API key in environment or `server.py`. Get one from https://console.groq.com

### Issue: "Image not uploading"
**Solution:** Check file size (max 50MB) and format (jpg, png, gif supported)

---

## 📈 Performance Metrics

Current system performance:

| Component | Metric | Target | Status |
|-----------|--------|--------|--------|
| Classification | Accuracy | >85% | ✅ Ready |
| Price Prediction | MAPE | <10% | ✅ 0.94% |
| Price Prediction | R² | >0.8 | ✅ 0.9322 |
| Recommendations | Hit Rate | >70% | ✅ Working |
| Response Time | API | <2s | ✅ <1s |

---

## 🚀 Deployment

### For Production

1. **Use Production Server:**
```bash
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 server:app
```

2. **Set Environment:**
```bash
export FLASK_ENV=production
export FLASK_DEBUG=0
```

3. **Use Reverse Proxy:**
Configure nginx or Apache to proxy requests to Flask

4. **Database:**
Replace mock data with actual database (PostgreSQL recommended)

5. **SSL/HTTPS:**
Use Let's Encrypt for SSL certificates

---

## 📞 Support

- Check API Status: http://localhost:5000/api/status
- View Health: http://localhost:5000/api/health
- Read Documentation: See files in root directory
- Run Tests: `python ai_metrics_test.py`

---

## 📝 Notes

- Frontend and backend run on the same server (localhost:5000)
- All API calls are made from JavaScript to `/api/` endpoints
- File uploads limited to 50MB per request
- Audio files supported: webm, wav, mp3, m4a
- Images supported: jpg, png, gif
- Mobile responsive design included

---

## ✨ Features Implemented

✅ Waste Classification (CNN Model)
✅ Price Prediction (ML Regression)
✅ Quality Assessment (Parameter Validation)
✅ Buyer Recommendations (AI Matching)
✅ Carbon Impact Calculation
✅ Audio Transcription (Groq Whisper)
✅ Q&A Chatbot (Groq LLaMA)
✅ Text-to-Speech (Google TTS)
✅ Responsive UI
✅ User Authentication (Mock)
✅ Shopping Cart
✅ Analytics Dashboard

---

**Happy farming! 🌾**

*Last Updated: April 10, 2026*
