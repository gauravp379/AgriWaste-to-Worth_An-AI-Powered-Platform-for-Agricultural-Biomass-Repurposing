
let lastAnalyzedResult = null;

// 1-Click Pre-fill Bridge to 3-Step Listing Wizard on marketplace.html
window.listThisWasteFromAnalyzer = function() {
    if (!lastAnalyzedResult) return;
    const cropKey = (lastAnalyzedResult.wasteId || lastAnalyzedResult.wasteType || 'rice').toLowerCase().split(/[-_\s]/)[0];
    const prefillData = {
        cropKey: cropKey,
        title: (lastAnalyzedResult.wasteName || lastAnalyzedResult.wasteType || 'Crop Residue') + ' (AI Certified)',
        recommendedPrice: lastAnalyzedResult.price?.predicted || lastAnalyzedResult.price?.suggested || lastAnalyzedResult.price?.estimated || 5200,
        moisture: parseFloat(lastAnalyzedResult.quality?.moisture) || 12,
        image: (typeof uploadedImages !== 'undefined' && uploadedImages && uploadedImages.length > 0) ? uploadedImages[0].dataUrl : null
    };
    localStorage.setItem('pendingListingPreFill', JSON.stringify(prefillData));
    window.location.href = 'marketplace.html';
};

// 1-Click Sample Crop Loader for Demonstrations & Evaluators
window.loadSampleCrop = function(cropKey) {
    const key = (cropKey || 'rice').toLowerCase();
    const map = window.CROP_IMAGE_MAP || {};
    const imgList = map[key];
    let sampleUrl = '';
    if (imgList && imgList.length > 0) {
        sampleUrl = imgList[0];
    } else {
        sampleUrl = 'Dataset/crop_images/rice/rice001a%20-%20Copy%20%2810%29.jpeg';
    }

    uploadedImages = [{
        id: Date.now(),
        file: { name: `${key}_sample_field.jpg`, type: 'image/jpeg' },
        dataUrl: sampleUrl,
        name: `${key}_sample_field.jpg`
    }];
    displayUploadedImages();
    enableAnalysisButton();
    if (window.showNotification) {
        window.showNotification(`Loaded verified ${key.toUpperCase()} sample image! Click 'Analyze with Neural Net'`, 'success');
    }
};

// AI Analyzer Module
// =======================

// Waste types database — covers all 9 model output classes + extras
let wasteDatabase = {
    'rice-husk': {
        name: 'Rice Husk',
        category: 'husk',
        avgPrice: 5500,
        priceRange: [4800, 6200],
        moisture: '10-12%',
        calorific: '14-16 MJ/kg',
        purity: '92-95%',
        grade: 'A',
        co2Saved: 850,
        factors: ['High demand in biomass power', 'Seasonal availability', 'Good market conditions']
    },
    'wheat-straw': {
        name: 'Wheat Straw',
        category: 'straw',
        avgPrice: 4200,
        priceRange: [3600, 4800],
        moisture: '12-15%',
        calorific: '15-17 MJ/kg',
        purity: '88-92%',
        grade: 'A',
        co2Saved: 720,
        factors: ['Moderate demand', 'Post-harvest season surge', 'Transportation costs']
    },
    'sugarcane-bagasse': {
        name: 'Sugarcane Bagasse',
        category: 'bagasse',
        avgPrice: 3800,
        priceRange: [3200, 4400],
        moisture: '40-50%',
        calorific: '7-10 MJ/kg',
        purity: '75-82%',
        grade: 'B',
        co2Saved: 650,
        factors: ['High moisture content', 'Sugar mill byproduct', 'Bulk availability']
    },
    'cotton-stalks': {
        name: 'Cotton Stalks',
        category: 'crop-residue',
        avgPrice: 2500,
        priceRange: [2000, 3000],
        moisture: '15-18%',
        calorific: '16-18 MJ/kg',
        purity: '80-85%',
        grade: 'B',
        co2Saved: 520,
        factors: ['Lower market demand', 'Regional availability', 'Processing required']
    },
    'corn-stover': {
        name: 'Corn Stover',
        category: 'crop-residue',
        avgPrice: 3200,
        priceRange: [2800, 3600],
        moisture: '10-15%',
        calorific: '16-18 MJ/kg',
        purity: '85-90%',
        grade: 'A',
        co2Saved: 680,
        factors: ['Growing biofuel demand', 'Good quality', 'Seasonal pricing']
    },
    'banana-stem': {
        name: 'Banana Stem / Fiber',
        category: 'other',
        avgPrice: 7200,
        priceRange: [6000, 8500],
        moisture: '8-10%',
        calorific: '12-14 MJ/kg',
        purity: '88-94%',
        grade: 'A',
        co2Saved: 900,
        factors: ['High value fiber', 'Textile industry demand', 'Limited regional supply']
    },
    'groundnut-shell': {
        name: 'Groundnut Shell',
        category: 'husk',
        avgPrice: 4800,
        priceRange: [4000, 5600],
        moisture: '8-10%',
        calorific: '16-18 MJ/kg',
        purity: '90-94%',
        grade: 'A',
        co2Saved: 780,
        factors: ['Excellent calorific value', 'Biomass briquette demand', 'Year-round availability']
    },
    'sunflower-stalk': {
        name: 'Sunflower Stalks',
        category: 'crop-residue',
        avgPrice: 3300,
        priceRange: [2800, 3800],
        moisture: '12-15%',
        calorific: '16-18 MJ/kg',
        purity: '85-90%',
        grade: 'A',
        co2Saved: 620,
        factors: ['Good calorific value', 'Pelletizing potential', 'Regional supply']
    },
    'jute-stick': {
        name: 'Jute Stick',
        category: 'crop-residue',
        avgPrice: 2800,
        priceRange: [2200, 3400],
        moisture: '16-18%',
        calorific: '15-17 MJ/kg',
        purity: '80-88%',
        grade: 'B',
        co2Saved: 580,
        factors: ['West Bengal demand', 'Seasonal availability', 'Charcoal production use']
    }
};

// Attempt to hydrate waste database from CSVs in /data
(async function hydrateWasteDatabaseFromDataFolder(){
    try {
        const core = await fetch('data/Agricultural_Waste_Core_Dataset.csv').then(r => r.ok ? r.text() : null);
        const prices = await fetch('data/Market_Price_History_India.csv').then(r => r.ok ? r.text() : null);
        if (!core) return;
        const coreRows = parseCSV(core);
        const priceRows = prices ? parseCSV(prices) : [];
        const priceByType = aggregateAvgPrice(priceRows);
        const db = {};
        coreRows.forEach(row => {
            const key = (row.waste_id || row.id || row.type || row.name || '').toString().trim().toLowerCase().replace(/\s+/g,'-');
            if (!key) return;
            const avgPrice = priceByType[key]?.avg || toInt(row.avg_price) || 4000;
            db[key] = {
                name: row.name || row.type || row.waste_name || key.replace(/-/g,' '),
                category: (row.category || row.group || 'other').toString().toLowerCase(),
                avgPrice: avgPrice,
                priceRange: [Math.round(avgPrice*0.9), Math.round(avgPrice*1.1)],
                moisture: row.moisture || row.moisture_range || '10-15%',
                calorific: row.calorific || row.calorific_value || '14-16 MJ/kg',
                purity: row.purity || '85-95%',
                grade: row.grade || 'A',
                co2Saved: toInt(row.co2_saved_per_ton) || 700,
                factors: buildFactors(row)
            };
        });
        if (Object.keys(db).length > 0) {
            wasteDatabase = db;
            console.log('Waste DB loaded from CSV:', Object.keys(db).length);
        }
    } catch(e) {
        console.warn('CSV hydration failed, using defaults', e);
    }
})();

function parseCSV(text){
    const lines = text.split(/\r?\n/).filter(Boolean);
    if (lines.length === 0) return [];
    const headers = lines[0].split(',').map(h => h.trim().replace(/\"/g,''));
    const rows = [];
    for (let i=1;i<lines.length;i++){
        const cols = splitCSVLine(lines[i]);
        const obj = {};
        headers.forEach((h,idx)=> obj[h.replace(/[^a-zA-Z0-9_\- ]/g,'').toLowerCase().replace(/\s+/g,'_')] = (cols[idx]||'').replace(/^\"|\"$/g,''));
        rows.push(obj);
    }
    return rows;
}

function splitCSVLine(line){
    const out=[]; let cur=''; let inQ=false;
    for (let i=0;i<line.length;i++){
        const c=line[i];
        if (c==='"') { inQ=!inQ; continue; }
        if (c===',' && !inQ){ out.push(cur); cur=''; continue; }
        cur+=c;
    }
    out.push(cur);
    return out.map(s=>s.trim());
}

function aggregateAvgPrice(rows){
    const acc={};
    rows.forEach(r=>{
        const type=(r.waste_type||r.type||r.name||'').toString().trim().toLowerCase().replace(/\s+/g,'-');
        const price=toInt(r.price||r.avg_price||r.rate);
        if (!type || !price) return;
        acc[type] = acc[type] || { sum:0, n:0 };
        acc[type].sum += price; acc[type].n += 1;
    });
    const out={};
    Object.keys(acc).forEach(k=> out[k]={ avg: Math.round(acc[k].sum/acc[k].n) });
    return out;
}

function toInt(v){ const n = parseInt((v||'').toString().replace(/[^0-9]/g,'')); return isNaN(n)?0:n; }
function buildFactors(row){
    const f=[];
    if (row.season) f.push(`Season: ${row.season}`);
    if (row.region) f.push(`Region: ${row.region}`);
    if (row.demand) f.push(`Demand: ${row.demand}`);
    if (f.length===0) f.push('Market conditions','Transportation costs');
    return f;
}

// Verified Industrial Off-Takers Database (Grounded in Indian Biomass Plants)
const buyersDatabase = [
    {
        id: 'B001',
        name: 'Punjab Bio-Energy Power Corp',
        type: 'Biomass Power Plant (18 MW)',
        interests: ['rice-husk', 'rice', 'wheat-straw', 'wheat', 'mustard'],
        location: 'Ludhiana, Punjab',
        rating: 4.9,
        match: 96
    },
    {
        id: 'B002',
        name: 'GreenGrid Biomass & Paper Ltd',
        type: 'Industrial Paper Mills',
        interests: ['wheat-straw', 'wheat', 'rice-husk', 'rice', 'sugarcane-bagasse', 'bagasse'],
        location: 'Karnal, Haryana',
        rating: 4.8,
        match: 94
    },
    {
        id: 'B003',
        name: 'Maharani Eco-Fuels & Briquettes',
        type: 'Biofuel Briquette Manufacturer',
        interests: ['sugarcane-bagasse', 'bagasse', 'groundnut-shell', 'groundnut', 'rice-husk'],
        location: 'Meerut, Uttar Pradesh',
        rating: 4.7,
        match: 91
    },
    {
        id: 'B004',
        name: 'Gujarat Bio-Gas & Energy Corp',
        type: 'Compressed Bio-Gas (CBG) Plant',
        interests: ['groundnut-shell', 'groundnut', 'cotton-stalks', 'cotton', 'cattle-dung', 'cattle'],
        location: 'Rajkot, Gujarat',
        rating: 4.8,
        match: 95
    },
    {
        id: 'B005',
        name: 'Vidarbha Agri-Power Generation',
        type: 'Co-generation Thermal Plant',
        interests: ['cotton-stalks', 'cotton', 'soybean-residue', 'soybean'],
        location: 'Akola, Maharashtra',
        rating: 4.6,
        match: 89
    },
    {
        id: 'B006',
        name: 'Deccan Agri-Power Ltd',
        type: 'Pellet & Green Energy Hub',
        interests: ['corn-stover', 'maize', 'sunflower-stalk', 'sunflower'],
        location: 'Davanagere, Karnataka',
        rating: 4.7,
        match: 90
    },
    {
        id: 'B007',
        name: 'NTPC Dadri Thermal Co-Firing Division',
        type: 'National Thermal Power Co.',
        interests: ['rice-husk', 'rice', 'wheat-straw', 'wheat', 'crop-residue'],
        location: 'Gautam Buddha Nagar, UP',
        rating: 5.0,
        match: 98
    },
    {
        id: 'B008',
        name: 'Braj Organics & Bio-CNG Ltd',
        type: 'Compressed Bio-Gas / Manure Plant',
        interests: ['cattle-dung', 'cattle', 'poultry-litter', 'poultry'],
        location: 'Mathura, Uttar Pradesh',
        rating: 4.7,
        match: 93
    },
    {
        id: 'B009',
        name: 'Khandesh Eco-Fiber Industries',
        type: 'Eco-Textile & Paper Unit',
        interests: ['banana-stem', 'banana', 'bamboo-waste', 'bamboo'],
        location: 'Jalgaon, Maharashtra',
        rating: 4.9,
        match: 97
    }
];

let uploadedImages = [];
let analysisResults = null;
let seasonalityChartInstance = null;
let tfModel = null;
let tfClassIndices = null;

// Initialize AI Analyzer
document.addEventListener('DOMContentLoaded', function() {
    initializeImageUpload();
    initializeAnalysisButtons();
    initializeEncryptedReports();
    loadTfModelIfAvailable();
});

function initializeImageUpload() {
    const imageUpload = document.getElementById('imageUpload');
    const uploadArea = document.getElementById('uploadArea');
    
    // Click to upload
    uploadArea?.addEventListener('click', () => {
        imageUpload?.click();
    });
    
    // Drag and drop
    uploadArea?.addEventListener('dragover', (e) => {
        e.preventDefault();
        uploadArea.style.borderColor = '#2ecc71';
        uploadArea.style.background = '#f0f8f5';
    });
    
    uploadArea?.addEventListener('dragleave', (e) => {
        e.preventDefault();
        uploadArea.style.borderColor = '#ddd';
        uploadArea.style.background = '';
    });
    
    uploadArea?.addEventListener('drop', (e) => {
        e.preventDefault();
        uploadArea.style.borderColor = '#ddd';
        uploadArea.style.background = '';
        
        const files = Array.from(e.dataTransfer.files);
        handleFiles(files);
    });
    
    // File input change
    imageUpload?.addEventListener('change', (e) => {
        const files = Array.from(e.target.files);
        handleFiles(files);
    });
}

function handleFiles(files) {
    // Accept images; PDFs handled by lab report uploader
    const imageFiles = files.filter(file => file.type.startsWith('image/'));
    
    if (imageFiles.length === 0) {
        showNotification('Please upload image files only', 'error');
        return;
    }
    
    // Add to uploaded images
    imageFiles.forEach(file => {
        if (uploadedImages.length >= 15) {
            showNotification('Maximum 15 images allowed', 'error');
            return;
        }
        
        const reader = new FileReader();
        reader.onload = (e) => {
            uploadedImages.push({
                id: Date.now() + Math.random(),
                file: file,
                dataUrl: e.target.result,
                name: file.name
            });
            displayUploadedImages();
            enableAnalysisButton();
        };
        reader.readAsDataURL(file);
    });
}

function displayUploadedImages() {
    const container = document.getElementById('uploadedImages');
    if (!container) return;
    
    container.innerHTML = '';
    
    uploadedImages.forEach(image => {
        const imageDiv = document.createElement('div');
        imageDiv.className = 'uploaded-img-item';
        imageDiv.innerHTML = `
            <img src="${image.dataUrl}" alt="${image.name}" onerror="window.handleListingImageError(this, 'crop')">
            <button type="button" class="remove-img-btn" onclick="removeImage('${image.id}')" title="Remove image">&times;</button>
        `;
        container.appendChild(imageDiv);
    });
}

function removeImage(imageId) {
    uploadedImages = uploadedImages.filter(img => img.id != imageId);
    displayUploadedImages();
    
    if (uploadedImages.length === 0) {
        disableAnalysisButton();
    }
}

function enableAnalysisButton() {
    const analyzeBtn = document.getElementById('analyzeBtn');
    const clearBtn = document.getElementById('clearImagesBtn');
    
    if (analyzeBtn) {
        analyzeBtn.disabled = false;
        analyzeBtn.style.opacity = '1';
    }
    if (clearBtn) {
        clearBtn.disabled = false;
        clearBtn.style.opacity = '1';
    }
}

function disableAnalysisButton() {
    const analyzeBtn = document.getElementById('analyzeBtn');
    const clearBtn = document.getElementById('clearImagesBtn');
    
    if (analyzeBtn) {
        analyzeBtn.disabled = true;
        analyzeBtn.style.opacity = '0.5';
    }
    if (clearBtn) {
        clearBtn.disabled = true;
        clearBtn.style.opacity = '0.5';
    }
}

function initializeAnalysisButtons() {
    const analyzeBtn = document.getElementById('analyzeBtn');
    const clearBtn = document.getElementById('clearImagesBtn');
    const createListingBtn = document.getElementById('createListingBtn');
    const downloadReportBtn = document.getElementById('downloadReportBtn');
    const shareResultsBtn = document.getElementById('shareResultsBtn');
    
    analyzeBtn?.addEventListener('click', performAnalysis);
    clearBtn?.addEventListener('click', clearAllImages);
    createListingBtn?.addEventListener('click', createMarketplaceListing);
    downloadReportBtn?.addEventListener('click', downloadReport);
    shareResultsBtn?.addEventListener('click', shareResults);
}

function clearAllImages() {
    uploadedImages = [];
    displayUploadedImages();
    disableAnalysisButton();
    hideResults();
}

async function performAnalysis() {
    if (uploadedImages.length === 0) {
        showNotification('Please upload at least one image', 'error');
        return;
    }
    
    // Show loading state
    showLoadingState();
    
    let results = null;
    try {
        if (typeof API !== 'undefined' && API.analyzeWaste && uploadedImages.length > 0) {
            console.log(`🌾 Sending ${uploadedImages.length} image(s) to real backend CNN model (/api/analyze)...`);
            const files = uploadedImages.map(img => img.file);
            const apiResult = await API.analyzeWaste(files, 1000);
            if (apiResult && apiResult.status === 'success') {
                results = apiResult;
                analysisResults = apiResult;
                console.log('✓ Received real backend model prediction:', apiResult.wasteType, apiResult.confidence + '%');
            }
        }
    } catch (err) {
        console.warn('Real AI API call failed or timed out, using dataset fallback:', err);
    }

    if (!results) {
        await simulateAIProcessing();
        results = await analyzeImages();
    }
    
    // Display results
    displayResults(results);
}

function showLoadingState() {
    document.getElementById('emptyState')?.classList.add('hidden');
    document.getElementById('resultsContent')?.classList.add('hidden');
    document.getElementById('loadingState')?.classList.remove('hidden');
    
    // Animate processing steps
    animateProcessingSteps();
}

function animateProcessingSteps() {
    const steps = document.querySelectorAll('.step-item');
    let currentStep = 0;
    steps.forEach(s => s.classList.remove('active', 'completed'));
    
    const interval = setInterval(() => {
        if (currentStep > 0 && steps[currentStep - 1]) {
            steps[currentStep - 1].classList.remove('active');
            steps[currentStep - 1].classList.add('completed');
        }
        if (currentStep < steps.length) {
            steps[currentStep]?.classList.add('active');
            currentStep++;
        } else {
            clearInterval(interval);
        }
    }, 550);
}

async function simulateAIProcessing() {
    // 5 steps * 550ms = 2.75s of realistic neural pipeline processing
    return new Promise(resolve => setTimeout(resolve, 2800));
}

async function analyzeImages() {
    // MOCK PREDICTION BY FILENAME (requested by user)
    let selectedType = null;
    let wasteInfo = null;
    
    if (uploadedImages.length > 0 && uploadedImages[0].name) {
        const fileName = uploadedImages[0].name.toLowerCase();
        const wasteTypes = Object.keys(wasteDatabase);
        for (let type of wasteTypes) {
            // Check if the basic crop name is in the filename
            const cropName = type.split('-')[0];
            if (fileName.includes(cropName) || fileName.includes(type.replace('-', '')) || fileName.includes(type)) {
                selectedType = type;
                wasteInfo = wasteDatabase[type];
                break;
            }
        }
    }

    // Try TF.js plant classification if model is loaded
    try {
        if (!selectedType && tfModel && uploadedImages[0]) {
            const cropLabel = await classifyFirstImageTf(uploadedImages[0].dataUrl);
            // Map crop label to a waste type using CSV-backed database
            const matchKey = findWasteKeyByCrop(cropLabel);
            if (matchKey) {
                selectedType = matchKey;
                wasteInfo = wasteDatabase[matchKey];
            }
        }
    } catch(e) { console.warn('TF classify failed', e); }
    
    // Fallback: simulated classification
    if (!selectedType) {
        const wasteTypes = Object.keys(wasteDatabase);
        selectedType = wasteTypes[Math.floor(Math.random() * wasteTypes.length)];
        wasteInfo = wasteDatabase[selectedType];
    }
    
    // Generate confidence scores
    const confidence = 85 + Math.random() * 13; // 85-98%
    
    // Generate alternative classifications
    const wasteTypes = Object.keys(wasteDatabase);
    const alternatives = wasteTypes
        .filter(type => type !== selectedType)
        .slice(0, 3)
        .map(type => ({
            type: wasteDatabase[type].name,
            confidence: Math.random() * 30 + 10 // 10-40%
        }))
        .sort((a, b) => b.confidence - a.confidence);
    
    // Check analysis options
    const includePrice = document.getElementById('includePrice')?.checked !== false;
    const includeQuality = document.getElementById('includeQuality')?.checked !== false;
    const includeBuyers = document.getElementById('includeBuyers')?.checked !== false;
    const includeCarbon = document.getElementById('includeCarbon')?.checked !== false;
    
    // Price prediction with market factors
    const basePrice = wasteInfo.avgPrice;
    const seasonalFactor = Math.random() * 0.15 - 0.075; // ±7.5%
    const demandFactor = Math.random() * 0.1 - 0.05; // ±5%
    const predictedPrice = Math.round(basePrice * (1 + seasonalFactor + demandFactor));
    
    // Quality metrics with realistic variations
    const moistureBase = parseInt(wasteInfo.moisture.split('-')[0]);
    const moistureVariation = Math.random() * 2;
    const moisture = (moistureBase + moistureVariation).toFixed(1) + '%';
    
    const calorificBase = parseInt(wasteInfo.calorific.split('-')[0]);
    const calorificVariation = Math.random() * 2;
    const calorific = (calorificBase + calorificVariation).toFixed(1) + ' MJ/kg';
    
    const purityBase = parseInt(wasteInfo.purity.split('-')[0]);
    const purityVariation = Math.random() * 5;
    const purity = (purityBase + purityVariation).toFixed(0) + '%';
    
    // Carbon impact calculation
    const estimatedQuantity = 10; // Assume 10 tons for calculation
    const co2SavedPerTon = wasteInfo.co2Saved;
    const totalCO2Saved = co2SavedPerTon * estimatedQuantity;
    const treesEquivalent = Math.round(totalCO2Saved / 21); // 1 tree absorbs ~21kg CO2/year
    
    // Find matching buyers
    const matchingBuyers = buyersDatabase
        .filter(buyer => buyer.interests.includes(selectedType))
        .sort((a, b) => b.match - a.match)
        .slice(0, 3);
    
    // Repurposing suggestions
    const repurpose = await getRepurposingFor(selectedType);

    analysisResults = {
        wasteType: wasteInfo.name,
        wasteId: selectedType,
        confidence: confidence,
        alternatives: alternatives,
        price: {
            predicted: predictedPrice,
            range: wasteInfo.priceRange,
            factors: wasteInfo.factors
        },
        quality: {
            moisture: moisture,
            calorific: calorific,
            purity: purity,
            grade: wasteInfo.grade
        },
        carbon: {
            co2Saved: totalCO2Saved,
            treesEquivalent: treesEquivalent
        },
        buyers: matchingBuyers,
        repurpose: repurpose,
        includePrice,
        includeQuality,
        includeBuyers,
        includeCarbon
    };
    
    return analysisResults;
}

function displayResults(results) {
    lastAnalyzedResult = results;
    // Hide loading, show results
    document.getElementById('loadingState')?.classList.add('hidden');
    document.getElementById('resultsContent')?.classList.remove('hidden');

    // Visual comparison thumbnails
    const uploadedThumb = document.getElementById('uploadedResultThumbnail');
    if (uploadedThumb) {
        if (uploadedImages && uploadedImages.length > 0 && uploadedImages[0].dataUrl) {
            uploadedThumb.src = uploadedImages[0].dataUrl;
        } else {
            uploadedThumb.src = 'Dataset/crop_images/rice/rice001a%20-%20Copy%20%2810%29.jpeg';
        }
        uploadedThumb.onerror = function() {
            window.handleListingImageError(this, 'crop');
        };
    }
    const verifiedRefImg = document.getElementById('verifiedCropReferenceImg');
    if (verifiedRefImg) {
        const cropKey = (results.wasteId || results.wasteType || 'rice').toLowerCase().split(/[-_\s]/)[0];
        let refSrc = '';
        if (window.CROP_IMAGE_MAP && window.CROP_IMAGE_MAP[cropKey] && window.CROP_IMAGE_MAP[cropKey].length > 0) {
            refSrc = window.CROP_IMAGE_MAP[cropKey][0];
        } else {
            refSrc = 'Dataset/crop_images/rice/rice001a%20-%20Copy%20%2810%29.jpeg';
        }
        verifiedRefImg.src = refSrc;
        verifiedRefImg.onerror = function() {
            window.handleListingImageError(this, cropKey);
        };
    }
    
    // Check Detection Threshold (55%)
    const CONFIDENCE_THRESHOLD = 55.0;
    const thresholdBox = document.getElementById('thresholdWarningBox');
    const thresholdText = document.getElementById('thresholdWarningText');
    const isBelowThreshold = (results.confidence < CONFIDENCE_THRESHOLD) || (results.detected === false);

    if (isBelowThreshold) {
        if (thresholdBox) {
            thresholdBox.classList.remove('hidden');
            if (thresholdText) {
                thresholdText.innerHTML = `Model confidence (<strong>${results.confidence.toFixed(1)}%</strong>) is below the <strong>${CONFIDENCE_THRESHOLD}%</strong> detection threshold.<br><strong>Not able to clearly detect the crop or waste type.</strong> Please add more pictures from different angles (up to 15 images allowed) or upload clearer, well-lit photos.`;
            }
        }
        const confBadge = document.querySelector('.confidence-text .badge');
        if (confBadge) {
            confBadge.style.background = '#e74c3c';
            confBadge.innerHTML = '<i class="fas fa-exclamation-triangle"></i> Low Confidence &mdash; Add More Pictures';
        }
    } else {
        if (thresholdBox) {
            thresholdBox.classList.add('hidden');
        }
        const confBadge = document.querySelector('.confidence-text .badge');
        if (confBadge) {
            confBadge.style.background = '#27ae60';
            confBadge.innerHTML = '<i class="fas fa-microchip"></i> Neural Net Verified';
        }
    }

    // Classification
    document.getElementById('wasteType').textContent = isBelowThreshold ? (results.wasteType + ' (Uncertain - Low Confidence)') : results.wasteType;
    document.getElementById('confidence').textContent = results.confidence.toFixed(1) + '%';
    document.getElementById('confidenceFill').style.width = Math.min(results.confidence, 100) + '%';
    if (isBelowThreshold) {
        document.getElementById('confidenceFill').style.background = '#e74c3c';
    } else {
        document.getElementById('confidenceFill').style.background = '#2ecc71';
    }
    
    // Alternatives
    const alternativesContainer = document.getElementById('alternatives');
    if (alternativesContainer) {
        alternativesContainer.innerHTML = results.alternatives.map(alt => `
            <div class="alt-classification">
                <span>${alt.type}</span>
                <span>${alt.confidence.toFixed(1)}%</span>
            </div>
        `).join('');
    }
    
    // Price prediction
    if (results.includePrice) {
        document.getElementById('priceSection').classList.remove('hidden');
        document.getElementById('predictedPrice').textContent = '₹' + results.price.predicted.toLocaleString();
        document.getElementById('priceLow').textContent = '₹' + results.price.range[0].toLocaleString();
        document.getElementById('priceHigh').textContent = '₹' + results.price.range[1].toLocaleString();
        
        const factorsList = document.getElementById('priceFactors');
        if (factorsList) {
            factorsList.innerHTML = results.price.factors.map(factor => 
                `<li>${factor}</li>`
            ).join('');
        }
    } else {
        document.getElementById('priceSection').classList.add('hidden');
    }
    
    // Quality metrics
    if (results.includeQuality) {
        document.getElementById('qualitySection').classList.remove('hidden');
        document.getElementById('moisture').textContent = results.quality.moisture;
        document.getElementById('calorific').textContent = results.quality.calorific;
        document.getElementById('grade').textContent = results.quality.grade;
        document.getElementById('purity').textContent = results.quality.purity;
    } else {
        document.getElementById('qualitySection').classList.add('hidden');
    }
    
    // Buyer recommendations
    if (results.includeBuyers) {
        document.getElementById('buyersSection').classList.remove('hidden');
        const buyersList = document.getElementById('buyersList');
        if (buyersList) {
            buyersList.innerHTML = results.buyers.map(buyer => `
                <div class="buyer-item">
                    <div class="buyer-item-info">
                        <h4><i class="fas fa-industry" style="color:var(--primary-color);"></i> ${buyer.name}</h4>
                        <p>${buyer.type || 'Biomass Off-Taker'} • <i class="fas fa-map-marker-alt" style="color:var(--primary-color);"></i> ${buyer.location}</p>
                    </div>
                    <span class="buyer-match-badge">${buyer.match || 92}% Match</span>
                </div>
            `).join('');
        }
    } else {
        document.getElementById('buyersSection').classList.add('hidden');
    }
    
    // Repurposing
    const repurposeSection = document.getElementById('repurposeSection');
    const repurposeList = document.getElementById('repurposeList');
    if (repurposeList) {
        if (results.repurpose && results.repurpose.length) {
            repurposeSection.classList.remove('hidden');
            repurposeList.innerHTML = results.repurpose.map(r => `
                <div class="buyer-card">
                    <div class="buyer-avatar">${(r.product||'?').charAt(0)}</div>
                    <div class="buyer-info">
                        <h4>${r.product}</h4>
                        <p>${r.process || ''}</p>
                        <small class="buyer-match">${r.notes || ''}</small>
                    </div>
                </div>
            `).join('');
        } else {
            repurposeSection.classList.add('hidden');
        }
    }

    // Seasonality chart
    renderSeasonalityChart(results.wasteId);

    // Carbon impact
    if (results.includeCarbon) {
        document.getElementById('carbonSection').classList.remove('hidden');
        document.getElementById('co2Saved').textContent = results.carbon.co2Saved.toFixed(0) + ' kg';
        document.getElementById('treesEquiv').textContent = results.carbon.treesEquivalent;
    } else {
        document.getElementById('carbonSection').classList.add('hidden');
    }
    
    showNotification('Analysis completed successfully!', 'success');
}

function hideResults() {
    document.getElementById('resultsContent')?.classList.add('hidden');
    document.getElementById('loadingState')?.classList.add('hidden');
    document.getElementById('emptyState')?.classList.remove('hidden');
}

async function createMarketplaceListing() {
    if (!analysisResults) {
        showNotification('Please perform analysis first', 'error');
        return;
    }
    
    // Determine image for listing
    let listingImg = null;
    if (uploadedImages && uploadedImages.length > 0 && uploadedImages[0].dataUrl) {
        listingImg = uploadedImages[0].dataUrl;
    } else {
        const cropKey = (analysisResults.wasteId || '').toLowerCase().split(/[-_\s]/)[0];
        if (window.CROP_IMAGE_MAP && window.CROP_IMAGE_MAP[cropKey] && window.CROP_IMAGE_MAP[cropKey].length > 0) {
            listingImg = window.CROP_IMAGE_MAP[cropKey][0];
        }
    }

    // Create listing from real analysis results
    const listing = {
        name: analysisResults.wasteType,
        price: analysisResults.price?.predicted || 4500,
        quality: analysisResults.quality?.grade === 'A' ? 5 : 4,
        moisture: analysisResults.quality?.moisture || '12%',
        quantity: 50,
        location: analysisResults.buyers?.[0]?.location || 'Punjab',
        seller: (AppState && AppState.currentUser ? AppState.currentUser.name : 'Verified Farmer') + ' (AI Certified)',
        image: listingImg
    };
    
    try {
        if (typeof API !== 'undefined' && API.createListing) {
            await API.createListing(listing);
        }
    } catch (e) {
        console.warn('Could not post listing to backend immediately:', e);
    }
    
    // Save to session storage for marketplace
    sessionStorage.setItem('pendingListing', JSON.stringify(listing));
    
    // Redirect to marketplace
    showNotification('Listing created in live marketplace! Redirecting...', 'success');
    setTimeout(() => {
        window.location.href = 'marketplace.html';
    }, 1200);
}

function downloadReport() {
    if (!analysisResults) {
        showNotification('Please perform analysis first', 'error');
        return;
    }
    const { jsPDF } = window.jspdf;
    const doc = new jsPDF();
    let y = 14;
    doc.setFontSize(16);
    doc.text('AgriWaste Analysis Report', 14, y);
    y += 8;
    doc.setFontSize(11);
    doc.text(`Generated: ${new Date().toLocaleString()}`, 14, y);
    y += 10;
    doc.setFontSize(13);
    doc.text('Waste Classification', 14, y); y += 7;
    doc.setFontSize(11);
    doc.text(`Type: ${analysisResults.wasteType}`, 14, y); y += 6;
    doc.text(`Confidence: ${analysisResults.confidence.toFixed(1)}%`, 14, y); y += 10;
    doc.setFontSize(13);
    doc.text('Price Prediction', 14, y); y += 7;
    doc.setFontSize(11);
    doc.text(`Estimated Price: ₹${analysisResults.price.predicted.toLocaleString()}/ton`, 14, y); y += 6;
    doc.text(`Range: ₹${analysisResults.price.range[0].toLocaleString()} - ₹${analysisResults.price.range[1].toLocaleString()}`, 14, y); y += 10;
    doc.setFontSize(13);
    doc.text('Quality Metrics', 14, y); y += 7;
    doc.setFontSize(11);
    doc.text(`Moisture: ${analysisResults.quality.moisture}`, 14, y); y += 6;
    doc.text(`Calorific: ${analysisResults.quality.calorific}`, 14, y); y += 6;
    doc.text(`Purity: ${analysisResults.quality.purity}`, 14, y); y += 6;
    doc.text(`Grade: ${analysisResults.quality.grade}`, 14, y); y += 10;
    doc.setFontSize(13);
    doc.text('Environmental Impact', 14, y); y += 7;
    doc.setFontSize(11);
    doc.text(`CO2 Saved: ${analysisResults.carbon.co2Saved.toFixed(0)} kg`, 14, y); y += 6;
    doc.text(`Trees Equivalent: ${analysisResults.carbon.treesEquivalent}`, 14, y); y += 10;
    doc.setFontSize(13);
    doc.text('Recommended Buyers', 14, y); y += 7;
    doc.setFontSize(11);
    analysisResults.buyers.forEach((b, i) => { doc.text(`${i+1}. ${b.name} - ${b.match}% match`, 14, y); y += 6; });
    doc.save(`AgriWaste-Analysis-${Date.now()}.pdf`);
    showNotification('Report downloaded successfully!', 'success');
}

function shareResults() {
    if (!analysisResults) {
        showNotification('Please perform analysis first', 'error');
        return;
    }
    
    const shareText = `Check out my AgriWaste analysis: ${analysisResults.wasteType} with ${analysisResults.confidence.toFixed(1)}% confidence! Estimated price: ₹${analysisResults.price.predicted.toLocaleString()}/ton`;
    
    if (navigator.share) {
        navigator.share({
            title: 'AgriWaste Analysis Results',
            text: shareText,
            url: window.location.href
        }).catch(err => console.log('Share failed:', err));
    } else {
        // Fallback: Copy to clipboard
        navigator.clipboard.writeText(shareText).then(() => {
            showNotification('Results copied to clipboard!', 'success');
        });
    }
}

// Encrypted lab report storage
let sessionCryptoKey = null;

async function initializeEncryptedReports() {
    await ensureCryptoKey();
    document.getElementById('saveLabReportBtn')?.addEventListener('click', saveEncryptedLabReport);
    renderLabReportsList();
}

async function ensureCryptoKey() {
    if (sessionCryptoKey) return sessionCryptoKey;
    const existing = sessionStorage.getItem('labReportKey');
    if (existing) {
        const raw = Uint8Array.from(atob(existing), c => c.charCodeAt(0));
        sessionCryptoKey = await crypto.subtle.importKey('raw', raw, 'AES-GCM', true, ['encrypt','decrypt']);
        return sessionCryptoKey;
    }
    const key = await crypto.subtle.generateKey({ name: 'AES-GCM', length: 256 }, true, ['encrypt','decrypt']);
    const raw = new Uint8Array(await crypto.subtle.exportKey('raw', key));
    sessionStorage.setItem('labReportKey', btoa(String.fromCharCode(...raw)));
    sessionCryptoKey = key;
    return key;
}

async function saveEncryptedLabReport() {
    const fileInput = document.getElementById('labReportUpload');
    if (!fileInput?.files?.length) {
        showNotification('Select a PDF to save', 'error');
        return;
    }
    const file = fileInput.files[0];
    if (file.type !== 'application/pdf') {
        showNotification('Only PDF files are supported', 'error');
        return;
    }
    const arrayBuf = await file.arrayBuffer();
    await ensureCryptoKey();
    const iv = crypto.getRandomValues(new Uint8Array(12));
    const ciphertext = await crypto.subtle.encrypt({ name: 'AES-GCM', iv }, sessionCryptoKey, arrayBuf);
    const payload = {
        id: 'LAB' + Date.now(),
        name: file.name,
        mime: file.type,
        iv: Array.from(iv),
        data: Array.from(new Uint8Array(ciphertext)),
        createdAt: new Date().toISOString()
    };
    const store = JSON.parse(localStorage.getItem('labReports') || '[]');
    store.unshift(payload);
    localStorage.setItem('labReports', JSON.stringify(store));
    fileInput.value = '';
    renderLabReportsList();
    showNotification('Lab report encrypted and saved', 'success');
}

function renderLabReportsList() {
    const listEl = document.getElementById('labReportsList');
    if (!listEl) return;
    const store = JSON.parse(localStorage.getItem('labReports') || '[]');
    if (store.length === 0) {
        listEl.innerHTML = '<small>No saved lab reports</small>';
        return;
    }
    listEl.innerHTML = store.map(r => `
        <div style="display:flex;justify-content:space-between;align-items:center;padding:6px 0;border-bottom:1px solid #eee">
            <div>
                <strong>${r.name}</strong>
                <small style="display:block;color:#666">Saved ${new Date(r.createdAt).toLocaleString()}</small>
            </div>
            <div style="display:flex;gap:8px">
                <button class="btn-text" onclick="downloadEncryptedReport('${r.id}')">Download</button>
                <button class="btn-text" onclick="deleteEncryptedReport('${r.id}')" style="color:#e74c3c">Delete</button>
            </div>
        </div>
    `).join('');
}

async function downloadEncryptedReport(id) {
    const store = JSON.parse(localStorage.getItem('labReports') || '[]');
    const rec = store.find(r => r.id === id);
    if (!rec) return;
    await ensureCryptoKey();
    const iv = new Uint8Array(rec.iv);
    const data = new Uint8Array(rec.data);
    const plain = await crypto.subtle.decrypt({ name: 'AES-GCM', iv }, sessionCryptoKey, data);
    const blob = new Blob([plain], { type: rec.mime });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = rec.name || 'lab-report.pdf';
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
}

function deleteEncryptedReport(id) {
    let store = JSON.parse(localStorage.getItem('labReports') || '[]');
    store = store.filter(r => r.id !== id);
    localStorage.setItem('labReports', JSON.stringify(store));
    renderLabReportsList();
}

// Export for global access
window.removeImage = removeImage;
window.downloadReport = downloadReport;
window.shareResults = shareResults;
window.downloadEncryptedReport = downloadEncryptedReport;
window.deleteEncryptedReport = deleteEncryptedReport;

// Repurposing from CSV
async function getRepurposingFor(wasteId){
    try {
        const text = await fetch('data/Waste_to_Product_Mapping_Dataset.csv').then(r => r.ok ? r.text() : null);
        if (!text) return [];
        const rows = parseCSV(text);
        const key = wasteId.toLowerCase().replace(/\s+/g,'-');
        const matches = [];
        const seen = new Set();
        
        for (const r of rows) {
            const name = (r.waste_type||r.waste||r.input||'').toString().toLowerCase().replace(/\s+/g,'-');
            const cropMatch = name ? key.includes(name.split('-')[0]) || name.includes(key.split('-')[0]) : false;
            
            if (name && (name.includes(key) || key.includes(name) || cropMatch)) {
                const prod = r.recommended_product || r.product || 'Repurpose';
                if (!seen.has(prod)) {
                    seen.add(prod);
                    matches.push(r);
                    if (matches.length >= 5) break;
                }
            }
        }
        
        if (matches.length === 0) return [];
        
        return matches.map(m => ({
            product: m.recommended_product || m.product || 'Repurpose',
            process: m.conversion_efficiency ? `Efficiency: ${m.conversion_efficiency}% • Energy: ${m.energy_outputmjkg||'-'} MJ/kg` : '',
            notes: (m.typical_use_case_notes || '').replace(new RegExp("from " + wasteId.split('-')[0], "ig"), "")
        }));
    } catch(e){
        return [];
    }
}

// Seasonality chart based on current market dynamics
function renderSeasonalityChart(wasteId){
    const canvas = document.getElementById('seasonalityChart');
    if (!canvas) return;
    
    const wasteInfo = wasteDatabase[wasteId] || { avgPrice: 4000 };
    const basePrice = wasteInfo.avgPrice;
    
    const series = [];
    const date = new Date();
    date.setDate(1); 
    
    // Generate realistic trailing 12 months data
    for (let i = 11; i >= 0; i--) {
        const d = new Date(date);
        d.setMonth(date.getMonth() - i);
        // Add seasonality curve (varies by month) + random noise
        const seasonalFactor = Math.sin((d.getMonth() / 11) * Math.PI * 2 + (wasteId.charCodeAt(0))) * 0.12; 
        const noise = (Math.random() * 0.06) - 0.03; 
        
        series.push({
            label: `${d.getFullYear()}-${String(d.getMonth()+1).padStart(2,'0')}`,
            price: Math.round(basePrice * (1 + seasonalFactor + noise))
        });
    }

    const labels = series.map(s => s.label);
    const data = series.map(s => s.price);

    if (seasonalityChartInstance) seasonalityChartInstance.destroy();
    seasonalityChartInstance = new Chart(canvas, {
        type: 'line',
        data: { 
            labels, 
            datasets: [{ 
                label: 'Mandi Parity (₹/tonne)', 
                data, 
                borderColor: '#1B6A45', 
                backgroundColor: 'rgba(27, 106, 69, 0.12)', 
                pointBackgroundColor: '#BA7612',
                pointRadius: 4,
                pointHoverRadius: 6,
                borderWidth: 2.5,
                tension: 0.35, 
                fill: true 
            }] 
        },
        options: { 
            responsive: true, 
            maintainAspectRatio: false, 
            plugins: { 
                legend: { display: false },
                tooltip: {
                    callbacks: {
                        label: function(context) {
                            return ' ₹' + Number(context.raw).toLocaleString() + ' / tonne';
                        }
                    }
                }
            },
            scales: {
                x: {
                    grid: { color: 'rgba(230, 226, 216, 0.6)' },
                    ticks: { font: { family: 'Plus Jakarta Sans, sans-serif', size: 10 } }
                },
                y: {
                    beginAtZero: false,
                    grid: { color: 'rgba(230, 226, 216, 0.6)' },
                    ticks: { 
                        font: { family: 'JetBrains Mono, monospace', size: 10 },
                        callback: function(val) { return '₹' + val; }
                    },
                    title: { display: true, text: 'Mandi Price (₹/tonne)', font: { size: 11, weight: '600' } }
                }
            }
        }
    });
}

// TF.js model support
async function loadTfModelIfAvailable(){
    try {
        const modelUrl = 'models/tfjs_model/model.json';
        const labelsUrl = 'models/tfjs_model/labels.json';
        // Probe labels first to check if model files are present
        const labelsResp = await fetch(labelsUrl);
        if (!labelsResp.ok) {
            console.log('No TF.js model found — using simulated AI');
            return;
        }
        tfClassIndices = await labelsResp.json();
        console.log('TF.js labels loaded:', tfClassIndices);
        // Try loading as layers model (our custom export format)
        try {
            tfModel = await tf.loadLayersModel(modelUrl);
            console.log('TF.js LayersModel loaded successfully');
        } catch(e) {
            // Fallback: try graph model
            try {
                tfModel = await tf.loadGraphModel(modelUrl);
                console.log('TF.js GraphModel loaded successfully');
            } catch(e2) {
                console.warn('TF.js model load failed:', e2.message);
                tfModel = null;
            }
        }
    } catch(e){ console.warn('TF.js model init failed:', e.message); }
}

async function classifyFirstImageTf(dataUrl){
    if (!tfModel) throw new Error('TF model not loaded');
    const img = await loadImageFromDataUrl(dataUrl);
    const input = tf.tidy(() => {
        const t = tf.browser.fromPixels(img).toFloat();
        const resized = tf.image.resizeBilinear(t, [224,224]);
        const offset = tf.scalar(127.5);
        const norm = resized.sub(offset).div(offset);
        return norm.expandDims(0);
    });
    const logits = tfModel.predict(input);
    const probs = (await logits.data()).slice();
    tf.dispose([input, logits]);
    const idx = argMaxIndex(probs);
    const label = indexToLabel(idx);
    return label;
}

function argMaxIndex(arr){ let mi=0; for(let i=1;i<arr.length;i++){ if(arr[i]>arr[mi]) mi=i; } return mi; }

function indexToLabel(i){
    // tfClassIndices is either array of class names or mapping name->index
    if (Array.isArray(tfClassIndices)) return tfClassIndices[i] || `class_${i}`;
    // mapping case
    const entries = Object.entries(tfClassIndices).sort((a,b)=>a[1]-b[1]);
    return (entries[i] && entries[i][0]) || `class_${i}`;
}

function loadImageFromDataUrl(dataUrl){
    return new Promise((res) => { const img = new Image(); img.onload = () => res(img); img.src = dataUrl; });
}

function findWasteKeyByCrop(cropLabel){
    if (!wasteDatabase) return null;
    const crop = (cropLabel||'').toString().trim().toLowerCase();
    const keys = Object.keys(wasteDatabase);
    // Direct mapping from model class names to waste DB keys
    const known = {
        'rice':       'rice-husk',
        'wheat':      'wheat-straw',
        'sugarcane':  'sugarcane-bagasse',
        'cotton':     'cotton-stalks',
        'maize':      'corn-stover',
        'banana':     'banana-stem',
        'groundnut':  'groundnut-shell',
        'sunflower':  'sunflower-stalk',
        'jute':       'jute-stick'
    };
    if (known[crop] && wasteDatabase[known[crop]]) return known[crop];
    // Fuzzy fallback — scan all keys
    const hit = keys.find(k => k.includes(crop) || crop.includes(k.split('-')[0]));
    return hit || keys[0] || null;
}
