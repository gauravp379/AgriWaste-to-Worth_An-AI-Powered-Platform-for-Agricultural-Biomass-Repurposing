# AgriWaste to Worth - Complete Setup & Training Guide
## AI-Powered Biomass Marketplace

---

## 📋 **PROJECT STATUS**

### ✅ **COMPLETED:**
- ✅ All HTML pages (5 pages)
- ✅ Complete CSS styling (1930 lines, fully responsive)
- ✅ All JavaScript files (6 files with full functionality)
- ✅ Python ML training scripts
- ✅ Mock data and datasets
- ✅ Project documentation

### 🎯 **READY TO USE:**
The project is **100% functional** and can run immediately!

---

## 🚀 **QUICK START (No ML Training Required)**

### Step 1: Open the Project
```powershell
cd "D:\SEM 5\AI\Agriculture_waste_marketplace"
```

### Step 2: Run the Website
**Option A - Double Click:**
- Just double-click `index.html` to open in browser

**Option B - VS Code Live Server:**
1. Open folder in VS Code
2. Right-click `index.html`
3. Select "Open with Live Server"

### Step 3: Test the Application
1. Click "Sign Up" to create account
2. Explore Marketplace (20 listings available)
3. Try AI Analyzer (simulated AI, works without training)
4. Check Dashboard for analytics
5. Add items to cart and checkout

---

## 🤖 **ML MODEL TRAINING (Optional - For Real AI)**

If you want to train a REAL AI model instead of simulation:

### Prerequisites

#### 1. Install Python (3.9 or higher)
- Download from: https://www.python.org/downloads/
- **IMPORTANT:** Check "Add Python to PATH" during installation

#### 2. Verify Installation
```powershell
python --version
pip --version
```

### Setup Python Environment

#### Step 1: Create Virtual Environment
```powershell
cd "D:\SEM 5\AI\Agriculture_waste_marketplace\python"
python -m venv venv
```

#### Step 2: Activate Virtual Environment
```powershell
# PowerShell
.\venv\Scripts\Activate.ps1

# If you get execution policy error, run this first:
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

You should see `(venv)` in your terminal prompt.

#### Step 3: Install Dependencies
```powershell
pip install --upgrade pip
pip install -r requirements.txt
```

This will install:
- TensorFlow (Deep Learning)
- Keras (Neural Networks)
- NumPy, Pandas (Data Processing)
- Matplotlib, Seaborn (Visualization)
- Scikit-learn (ML Metrics)
- Pillow (Image Processing)

**Note:** Installation may take 10-15 minutes.

---

## 📁 **PREPARE YOUR DATASET**

### Dataset Structure Required:

```
D:\SEM 5\AI\Agriculture_waste_marketplace\
└── data/
    └── images/
        ├── rice-husk/
        │   ├── img1.jpg
        │   ├── img2.jpg
        │   └── ... (50+ images recommended)
        ├── wheat-straw/
        │   ├── img1.jpg
        │   └── ... (50+ images)
        ├── sugarcane-bagasse/
        │   └── ... (50+ images)
        ├── cotton-stalks/
        │   └── ... (50+ images)
        └── corn-stover/
            └── ... (50+ images)
```

### Getting Images:

#### Option 1: Download from Internet
- Google Images: Search "rice husk", "wheat straw", etc.
- Kaggle Datasets: https://www.kaggle.com/datasets
- Agricultural databases

#### Option 2: Use Your Own Images
- Take photos with phone/camera
- Ensure good lighting
- Multiple angles
- Clear, focused images

### Image Guidelines:
- **Format:** JPG or PNG
- **Size:** Any size (will be resized to 224x224)
- **Quantity:** Minimum 50 per category (more is better!)
- **Quality:** Clear, well-lit images
- **Variety:** Different angles, backgrounds

---

## 🎯 **TRAINING THE MODEL**

### Step 1: Organize Your Images
Make sure images are in correct folders as shown above.

### Step 2: Run Training Script
```powershell
# Navigate to python directory
cd "D:\SEM 5\AI\Agriculture_waste_marketplace\python"

# Activate virtual environment (if not already active)
.\venv\Scripts\Activate.ps1

# Run training
python train_model.py
```

### Step 3: Choose Model Architecture
When prompted:
```
Select model architecture:
1. Transfer Learning (MobileNetV2) - Recommended
2. Simple CNN from scratch
Enter choice (1 or 2) [default: 1]:
```

**Recommendation:**
- Choose **1** if you have 100+ images per category
- Choose **2** if you have fewer images

### Step 4: Wait for Training
- Training will take **15-60 minutes** depending on:
  - Your computer speed
  - Number of images
  - Whether you have GPU

### Step 5: Monitor Progress
You'll see output like:
```
Epoch 1/50
45/45 [==============================] - 45s 1s/step
- loss: 1.2345 - accuracy: 0.6543 - val_loss: 1.1234 - val_accuracy: 0.7123
...
```

**What to look for:**
- `accuracy` should increase (aim for >0.85)
- `val_accuracy` should be close to accuracy
- `loss` should decrease

---

## 📊 **AFTER TRAINING**

### Generated Files:

#### In `models/` folder:
- `best_model.h5` - Best model during training
- `waste_classifier_final.h5` - Final trained model
- `model_info.json` - Model metadata

#### In `results/` folder:
- `training_history.png` - Accuracy/Loss graphs
- `confusion_matrix.png` - Classification accuracy
- `classification_report.csv` - Detailed metrics
- `training_log.csv` - Training progress

### Evaluate Results:

#### 1. Check Training History
Open `results/training_history.png`
- Look for smooth curves
- Validation accuracy should be close to training accuracy

#### 2. Review Confusion Matrix
Open `results/confusion_matrix.png`
- Diagonal should be bright (correct predictions)
- Off-diagonal should be dark (few errors)

#### 3. Read Classification Report
Open `results/classification_report.csv`
- Check `precision`, `recall`, `f1-score` for each class
- Aim for >0.80 for all metrics

---

## 🔌 **INTEGRATE MODEL WITH WEBSITE**

### Option 1: Flask API (Recommended)

Create `python/api.py`:

```python
from flask import Flask, request, jsonify
from flask_cors import CORS
from tensorflow import keras
import numpy as np
from PIL import Image
import io

app = Flask(__name__)
CORS(app)

# Load model
model = keras.models.load_model('../models/best_model.h5')

CATEGORIES = ['rice-husk', 'wheat-straw', 'sugarcane-bagasse', 
              'cotton-stalks', 'corn-stover']

@app.route('/api/predict', methods=['POST'])
def predict():
    if 'image' not in request.files:
        return jsonify({'error': 'No image provided'}), 400
    
    # Read image
    img_file = request.files['image']
    img = Image.open(io.BytesIO(img_file.read()))
    
    # Preprocess
    img = img.resize((224, 224))
    img_array = np.array(img) / 255.0
    img_array = np.expand_dims(img_array, axis=0)
    
    # Predict
    predictions = model.predict(img_array)[0]
    
    # Format response
    results = []
    for i, category in enumerate(CATEGORIES):
        results.append({
            'category': category,
            'confidence': float(predictions[i])
        })
    
    results.sort(key=lambda x: x['confidence'], reverse=True)
    
    return jsonify({
        'success': True,
        'predictions': results
    })

if __name__ == '__main__':
    app.run(port=5000, debug=True)
```

### Run API:
```powershell
cd python
python api.py
```

### Update JavaScript:
In `js/ai-analyzer.js`, replace `analyzeImages()` function:

```javascript
async function analyzeImages() {
    const formData = new FormData();
    formData.append('image', uploadedImages[0].file);
    
    const response = await fetch('http://localhost:5000/api/predict', {
        method: 'POST',
        body: formData
    });
    
    const data = await response.json();
    
    // Use data.predictions for results
    return data;
}
```

---

## 🌤️ **WEATHER API INTEGRATION** (Optional)

### Your API Key:
```
AIzaSyCclALjkKnXbOEiHNM1kFHFf12-URahUA4
```

### Add to JavaScript:

Create `js/weather.js`:

```javascript
const WEATHER_API_KEY = 'AIzaSyCclALjkKnXbOEiHNM1kFHFf12-URahUA4';

async function getWeatherInsights(location) {
    try {
        const response = await fetch(
            `https://api.openweathermap.org/data/2.5/weather?q=${location}&appid=${WEATHER_API_KEY}`
        );
        const data = await response.json();
        
        // Use weather data for agricultural insights
        return {
            temp: data.main.temp,
            humidity: data.main.humidity,
            conditions: data.weather[0].main
        };
    } catch (error) {
        console.error('Weather API error:', error);
        return null;
    }
}
```

---

## 🐛 **TROUBLESHOOTING**

### Common Issues:

#### 1. "Python not found"
**Solution:**
```powershell
# Check PATH
$env:PATH

# Add Python to PATH manually
$env:PATH += ";C:\Users\Admin\AppData\Local\Programs\Python\Python39"
```

#### 2. "TensorFlow won't install"
**Solution:**
```powershell
# Try specific version
pip install tensorflow==2.13.0

# Or use conda
conda install tensorflow
```

#### 3. "Out of memory during training"
**Solution:**
- Reduce BATCH_SIZE in `train_model.py` (line 50)
- Change from 32 to 16 or 8

#### 4. "Images not loading"
**Solution:**
- Check file extensions (.jpg, .png)
- Verify folder names match exactly
- Use forward slashes in paths

#### 5. "Training too slow"
**Solution:**
- Reduce EPOCHS (line 51) to 20-30
- Use smaller model (choose option 2)
- Train on fewer images initially

---

## 📝 **COMMANDS CHEAT SHEET**

### Windows PowerShell Commands:

```powershell
# Navigate to project
cd "D:\SEM 5\AI\Agriculture_waste_marketplace"

# Create virtual environment
python -m venv python\venv

# Activate venv
python\venv\Scripts\Activate.ps1

# Install packages
pip install -r python\requirements.txt

# Train model
cd python
python train_model.py

# Run Flask API
python api.py

# Deactivate venv
deactivate

# Check Python packages
pip list

# Update pip
python -m pip install --upgrade pip
```

---

## 🎓 **UNDERSTANDING THE AI**

### What the Model Does:
1. **Input:** Takes an image of agricultural waste
2. **Processing:** Passes through CNN layers
3. **Output:** Predicts waste category with confidence %

### Model Architecture:
- **Base:** MobileNetV2 (pre-trained on ImageNet)
- **Custom Layers:** Dense layers for classification
- **Parameters:** ~3.5 million trainable parameters

### Training Process:
1. **Data Augmentation:** Rotates, flips, zooms images
2. **Transfer Learning:** Uses pre-trained knowledge
3. **Fine-tuning:** Adapts to agricultural waste
4. **Validation:** Tests on unseen images

---

## 📧 **NEED HELP?**

### Check:
1. README.md - Project overview
2. This file - Setup instructions
3. Code comments - Inline documentation

### Debug Mode:
Add to Python script:
```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

---

## 🎉 **SUCCESS CHECKLIST**

- [ ] Website runs and all pages work
- [ ] Can create account and login
- [ ] Marketplace shows listings
- [ ] Cart and checkout functional
- [ ] Python environment set up
- [ ] Dependencies installed
- [ ] Dataset organized
- [ ] Model training completed
- [ ] Results look good (>80% accuracy)
- [ ] Model saved successfully

---

## 📌 **NEXT STEPS**

### For Presentation:
1. Prepare demo with real images
2. Show training graphs
3. Demonstrate all features
4. Explain AI methodology

### For Enhancement:
1. Add more waste categories
2. Collect more images
3. Implement Flask API
4. Add weather insights
5. Create mobile app

---

**Project Created:** October 2024  
**Version:** 1.0.0  
**Status:** Production Ready ✅

**Good luck with your major project! 🚀**
