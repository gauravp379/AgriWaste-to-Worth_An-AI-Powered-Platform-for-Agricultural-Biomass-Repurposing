// ==============================================================================
// AgriWaste to Worth - Marketplace Engine
// High-Craft Editorial Agrarian Marketplace with Real-time Filters,
// Skeletons, Active Chips, Wishlist, Quick-View & 3-Step Wizard
// ==============================================================================

// Verified Mock Listings Grounded in Real Indian Agro-Climatic Zones & Mandis
const defaultListings = [
    {
        id: 'L001',
        name: 'Rice Paddy Straw (Basmati Grade-A)',
        category: 'straw',
        imageKey: 'rice',
        price: 5200,
        quantity: 80,
        location: 'Ludhiana, Punjab',
        seller: 'Farmer Ramesh Singh (Punjab Agri Co-op)',
        rating: 4.9,
        date: new Date('2026-03-24'),
        moisture: '12.0%',
        calorific: '15.2 MJ/kg',
        density: '140 kg/m³',
        co2Offset: '1.45 T/T',
        quality: 5,
        aiBestMatch: true,
        distanceKm: 14
    },
    {
        id: 'L002',
        name: 'Wheat Straw Bales (Turi / Bhusa)',
        category: 'straw',
        imageKey: 'wheat',
        price: 4500,
        quantity: 60,
        location: 'Karnal, Haryana',
        seller: 'Kumar Kisan Hub (Karnal Mandi)',
        rating: 4.8,
        date: new Date('2026-03-23'),
        moisture: '13.5%',
        calorific: '16.0 MJ/kg',
        density: '155 kg/m³',
        co2Offset: '1.50 T/T',
        quality: 5,
        aiBestMatch: true,
        distanceKm: 28
    },
    {
        id: 'L003',
        name: 'Sugarcane Bagasse (Mill Dry)',
        category: 'bagasse',
        imageKey: 'sugarcane',
        price: 3800,
        quantity: 150,
        location: 'Muzaffarnagar, UP',
        seller: 'Kisan Sugar Mill Co-op',
        rating: 4.6,
        date: new Date('2026-03-22'),
        moisture: '28.0%',
        calorific: '11.5 MJ/kg',
        density: '180 kg/m³',
        co2Offset: '1.20 T/T',
        quality: 4,
        distanceKm: 45
    },
    {
        id: 'L004',
        name: 'Cotton Stalks (Chipped & Baled)',
        category: 'crop-residue',
        imageKey: 'cotton',
        price: 2800,
        quantity: 90,
        location: 'Akola, Maharashtra',
        seller: 'Vidarbha Cotton Hub',
        rating: 4.7,
        date: new Date('2026-03-21'),
        moisture: '12.5%',
        calorific: '15.8 MJ/kg',
        density: '135 kg/m³',
        co2Offset: '1.48 T/T',
        quality: 4,
        distanceKm: 60
    },
    {
        id: 'L005',
        name: 'Corn / Maize Stover Bales',
        category: 'crop-residue',
        imageKey: 'maize',
        price: 3200,
        quantity: 110,
        location: 'Davanagere, Karnataka',
        seller: 'Maize Producers Union',
        rating: 4.5,
        date: new Date('2026-03-20'),
        moisture: '14.0%',
        calorific: '14.8 MJ/kg',
        density: '130 kg/m³',
        co2Offset: '1.38 T/T',
        quality: 4,
        distanceKm: 75
    },
    {
        id: 'L006',
        name: 'Groundnut Shells (Boiler Ready)',
        category: 'husk',
        imageKey: 'groundnut',
        price: 4800,
        quantity: 70,
        location: 'Rajkot, Gujarat',
        seller: 'Saurashtra Oilseeds Agro',
        rating: 4.9,
        date: new Date('2026-03-19'),
        moisture: '9.5%',
        calorific: '17.5 MJ/kg',
        density: '190 kg/m³',
        co2Offset: '1.65 T/T',
        quality: 5,
        aiBestMatch: true,
        distanceKm: 32
    },
    {
        id: 'L007',
        name: 'Rice Husk (Boiler Grade)',
        category: 'husk',
        imageKey: 'rice',
        price: 5500,
        quantity: 100,
        location: 'Burdwan, West Bengal',
        seller: 'Bengal Rice Millers Association',
        rating: 4.8,
        date: new Date('2026-03-18'),
        moisture: '10.0%',
        calorific: '13.8 MJ/kg',
        density: '120 kg/m³',
        co2Offset: '1.30 T/T',
        quality: 5,
        distanceKm: 90
    },
    {
        id: 'L008',
        name: 'Mustard Stalk Bundles',
        category: 'straw',
        imageKey: 'sunflower',
        price: 3500,
        quantity: 85,
        location: 'Alwar, Rajasthan',
        seller: 'Green Fields Agri Sangh',
        rating: 4.3,
        date: new Date('2026-03-17'),
        moisture: '14.5%',
        calorific: '15.0 MJ/kg',
        density: '140 kg/m³',
        co2Offset: '1.40 T/T',
        quality: 4,
        distanceKm: 55
    },
    {
        id: 'L009',
        name: 'Soybean Residue Straw',
        category: 'crop-residue',
        imageKey: 'soybean',
        price: 3100,
        quantity: 120,
        location: 'Indore, Madhya Pradesh',
        seller: 'Malwa Soya Growers Co-op',
        rating: 4.6,
        date: new Date('2026-03-16'),
        moisture: '11.0%',
        calorific: '14.6 MJ/kg',
        density: '135 kg/m³',
        co2Offset: '1.35 T/T',
        quality: 4,
        distanceKm: 80
    },
    {
        id: 'L010',
        name: 'Jute Sticks (Patson Dandi)',
        category: 'crop-residue',
        imageKey: 'jute',
        price: 2800,
        quantity: 140,
        location: 'Nadia, West Bengal',
        seller: 'Bengal Jute Farmers Co-op',
        rating: 4.4,
        date: new Date('2026-03-15'),
        moisture: '12.0%',
        calorific: '16.4 MJ/kg',
        density: '110 kg/m³',
        co2Offset: '1.55 T/T',
        quality: 4,
        distanceKm: 110
    },
    {
        id: 'L011',
        name: 'Sunflower Stalks',
        category: 'crop-residue',
        imageKey: 'sunflower',
        price: 3300,
        quantity: 65,
        location: 'Bellary, Karnataka',
        seller: 'Deccan Sunflower Federation',
        rating: 4.6,
        date: new Date('2026-03-14'),
        moisture: '13.0%',
        calorific: '15.0 MJ/kg',
        density: '130 kg/m³',
        co2Offset: '1.42 T/T',
        quality: 5,
        distanceKm: 65
    },
    {
        id: 'L012',
        name: 'Coffee Husk (Dry Pellets)',
        category: 'husk',
        imageKey: 'coffee',
        price: 5800,
        quantity: 45,
        location: 'Coorg, Karnataka',
        seller: 'Highland Coffee Estates Co-op',
        rating: 4.9,
        date: new Date('2026-03-13'),
        moisture: '10.5%',
        calorific: '16.8 MJ/kg',
        density: '220 kg/m³',
        co2Offset: '1.60 T/T',
        quality: 5,
        distanceKm: 120
    },
    {
        id: 'L013',
        name: 'Tea Waste Leaves & Fluff',
        category: 'other',
        imageKey: 'tea',
        price: 4500,
        quantity: 50,
        location: 'Dibrugarh, Assam',
        seller: 'Assam Tea Planters Union',
        rating: 4.5,
        date: new Date('2026-03-12'),
        moisture: '16.0%',
        calorific: '16.0 MJ/kg',
        density: '160 kg/m³',
        co2Offset: '1.52 T/T',
        quality: 4,
        distanceKm: 140
    },
    {
        id: 'L014',
        name: 'Banana Fiber & Pseudostem Bales',
        category: 'other',
        imageKey: 'banana',
        price: 7200,
        quantity: 40,
        location: 'Jalgaon, Maharashtra',
        seller: 'Khandesh Banana Federation',
        rating: 4.9,
        date: new Date('2026-03-11'),
        moisture: '18.0%',
        calorific: '12.2 MJ/kg',
        density: '170 kg/m³',
        co2Offset: '1.25 T/T',
        quality: 5,
        aiBestMatch: true,
        distanceKm: 42
    },
    {
        id: 'L015',
        name: 'Bamboo Processing Shavings',
        category: 'other',
        imageKey: 'bamboo',
        price: 4100,
        quantity: 130,
        location: 'Guwahati, Assam',
        seller: 'Brahmaputra Green Fuel Hub',
        rating: 4.5,
        date: new Date('2026-03-10'),
        moisture: '14.0%',
        calorific: '18.5 MJ/kg',
        density: '185 kg/m³',
        co2Offset: '1.75 T/T',
        quality: 5,
        distanceKm: 95
    },
    {
        id: 'L016',
        name: 'Palm Fronds & Biomass',
        category: 'other',
        imageKey: 'palm',
        price: 3700,
        quantity: 95,
        location: 'Godavari, Andhra Pradesh',
        seller: 'East Coast Palm Growers',
        rating: 4.3,
        date: new Date('2026-03-09'),
        moisture: '16.0%',
        calorific: '14.2 MJ/kg',
        density: '150 kg/m³',
        co2Offset: '1.35 T/T',
        quality: 3,
        distanceKm: 105
    },
    {
        id: 'L017',
        name: 'Cattle Dung (Dry Gobar Cakes / Fertilizer)',
        category: 'livestock',
        imageKey: 'cattle',
        price: 1500,
        quantity: 300,
        location: 'Mathura, Uttar Pradesh',
        seller: 'Braj Gau Seva Bio-Gas Co-op',
        rating: 4.6,
        date: new Date('2026-03-08'),
        moisture: '18.0%',
        calorific: '11.0 MJ/kg',
        density: '260 kg/m³',
        co2Offset: '1.10 T/T',
        quality: 4,
        distanceKm: 38
    },
    {
        id: 'L018',
        name: 'Poultry Litter & Manure',
        category: 'livestock',
        imageKey: 'poultry',
        price: 2200,
        quantity: 250,
        location: 'Namakkal, Tamil Nadu',
        seller: 'Tamil Nadu Poultry Union',
        rating: 4.5,
        date: new Date('2026-03-07'),
        moisture: '22.0%',
        calorific: '10.5 MJ/kg',
        density: '240 kg/m³',
        co2Offset: '1.05 T/T',
        quality: 4,
        distanceKm: 85
    },
    {
        id: 'L019',
        name: 'Rice Straw Heavy Square Bales',
        category: 'straw',
        imageKey: 'rice',
        price: 5100,
        quantity: 120,
        location: 'Amritsar, Punjab',
        seller: 'Majha Kisan Co-operative',
        rating: 4.8,
        date: new Date('2026-03-06'),
        moisture: '11.5%',
        calorific: '15.4 MJ/kg',
        density: '150 kg/m³',
        co2Offset: '1.48 T/T',
        quality: 5,
        distanceKm: 22
    },
    {
        id: 'L020',
        name: 'Barley Straw Baled Lots',
        category: 'straw',
        imageKey: 'wheat',
        price: 3900,
        quantity: 75,
        location: 'Hisar, Haryana',
        seller: 'Haryana Grains Union',
        rating: 4.4,
        date: new Date('2026-03-05'),
        moisture: '13.0%',
        calorific: '15.1 MJ/kg',
        density: '145 kg/m³',
        co2Offset: '1.44 T/T',
        quality: 4,
        distanceKm: 48
    }
];

// Application State
let allListings = [...defaultListings];
let filteredListings = [...defaultListings];
let currentPage = 1;
const itemsPerPage = 9;
let wishlist = JSON.parse(localStorage.getItem('userWishlist') || '[]');
let currentSort = 'recommended';
let currentView = 'grid';
let wizardStep = 1;
let wizardImageBase64 = null;

let currentFilters = {
    search: '',
    categories: [],
    minPrice: null,
    maxPrice: null,
    minQuantity: 0,
    location: '',
    maxMoisture: null
};

// ==============================================================================
// INITIALIZATION
// ==============================================================================
document.addEventListener('DOMContentLoaded', () => {
    loadListingsData();
    initializeFilterControls();
    initializeSortAndViews();
    initializeWizardModal();
    checkPendingAnalyzerPreFill();
});

// Load Listings from LocalStorage or Default
async function loadListingsData() {
    renderSkeletons();

    try {
        const saved = localStorage.getItem('marketplaceListings');
        if (saved) {
            const parsed = JSON.parse(saved);
            if (Array.isArray(parsed) && parsed.length > 0) {
                allListings = parsed;
                finalizeListings();
                return;
            }
        }
    } catch (e) {
        console.warn('LocalStorage load error, using default listings', e);
    }

    allListings = [...defaultListings];
    finalizeListings();
}

function finalizeListings() {
    filteredListings = [...allListings];
    applyFilters();
}

// ==============================================================================
// IMAGE RESOLUTION & ZERO-BROKEN-IMAGE FALLBACK
// ==============================================================================

function getListingImageHtml(listing) {
    if (listing.image && listing.image.length > 20) {
        return `<img src="${listing.image}" alt="${listing.name}" loading="lazy" onerror="window.handleListingImageError(this, '${listing.imageKey || 'rice'}')">`;
    }

    const key = (listing.imageKey || 'rice').toLowerCase();
    const map = window.CROP_IMAGE_MAP || {};
    const imgList = map[key];

    let imgSrc = '';
    if (imgList && imgList.length > 0) {
        imgSrc = imgList[0];
    } else {
        imgSrc = `Dataset/crop_images/rice/rice001a%20-%20Copy%20%2810%29.jpeg`;
    }

    return `<img src="${imgSrc}" alt="${listing.name}" loading="lazy" onerror="window.handleListingImageError(this, '${key}')">`;
}

// Fallback to inline styled SVG data URI if image network fails
window.handleListingImageError = function(imgElement, cropKey) {
    const key = (cropKey || 'crop').toUpperCase();
    const svg = `
        <svg xmlns="http://www.w3.org/2000/svg" width="400" height="260" viewBox="0 0 400 260">
            <rect width="100%" height="100%" fill="#1B6A45"/>
            <circle cx="200" cy="110" r="48" fill="#FAF8F3" fill-opacity="0.12"/>
            <path d="M190 120 C185 95, 205 85, 215 100 C220 115, 205 130, 190 120 Z" fill="#BA7612"/>
            <path d="M185 135 C175 110, 195 100, 205 115 C210 130, 195 145, 185 135 Z" fill="#FAF8F3"/>
            <text x="200" y="185" font-family="system-ui, -apple-system, sans-serif" font-size="14" font-weight="700" fill="#FAF8F3" text-anchor="middle" letter-spacing="1.5">${key} RESIDUE LOT</text>
            <text x="200" y="208" font-family="system-ui, -apple-system, sans-serif" font-size="11" fill="#FAF8F3" fill-opacity="0.75" text-anchor="middle">Lab Tested • Mandi Benchmarked</text>
        </svg>
    `;
    imgElement.src = 'data:image/svg+xml;utf8,' + encodeURIComponent(svg.trim());
};

// ==============================================================================
// SKELETON LOADERS
// ==============================================================================
function renderSkeletons() {
    const grid = document.getElementById('listingsGrid');
    if (!grid) return;
    let html = '';
    for (let i = 0; i < 6; i++) {
        html += `
            <div class="skeleton-card">
                <div class="skeleton-img"></div>
                <div class="skeleton-body">
                    <div class="skeleton-line w-30"></div>
                    <div class="skeleton-line w-80"></div>
                    <div class="skeleton-line w-50"></div>
                    <div class="skeleton-line w-80" style="margin-top:auto;"></div>
                </div>
            </div>
        `;
    }
    grid.innerHTML = html;
}

// ==============================================================================
// RENDER LISTINGS & CARDS
// ==============================================================================
function displayListings() {
    const grid = document.getElementById('listingsGrid');
    const countEl = document.getElementById('resultsCount');
    if (!grid) return;

    if (countEl) countEl.textContent = filteredListings.length;

    if (filteredListings.length === 0) {
        grid.innerHTML = `
            <div style="grid-column: 1 / -1; text-align:center; padding: 4.5rem 1.5rem; background:var(--bg-surface); border-radius:var(--radius-lg); border:1px dashed var(--border-subtle); margin:1rem 0;">
                <div style="font-size:3.5rem;margin-bottom:1rem;">🌾</div>
                <h3 style="font-family:var(--font-heading);font-size:1.4rem;color:var(--text-strong);margin-bottom:0.5rem;">No Verified Residues Match</h3>
                <p style="color:var(--text-muted);max-width:440px;margin:0 auto 1.5rem;font-size:0.92rem;line-height:1.5;">
                    No current lots match your exact moisture, zone, or price filters. Try widening your criteria or reset filters to browse the corridor.
                </p>
                <button type="button" class="btn-primary" onclick="window.clearAllFilters()" style="min-height:44px;padding:0.6rem 1.5rem;">
                    <i class="fas fa-rotate"></i> Reset All Filters
                </button>
            </div>
        `;
        renderPagination(0);
        return;
    }

    // Pagination slice
    const totalPages = Math.ceil(filteredListings.length / itemsPerPage);
    if (currentPage > totalPages) currentPage = 1;
    const startIndex = (currentPage - 1) * itemsPerPage;
    const paginated = filteredListings.slice(startIndex, startIndex + itemsPerPage);

    grid.className = currentView === 'list' ? 'listings-grid list-view' : 'listings-grid';
    grid.innerHTML = paginated.map(l => createListingCard(l)).join('');

    renderPagination(totalPages);
}

function createListingCard(listing) {
    const isWished = wishlist.includes(listing.id);
    const stars = '★'.repeat(Math.round(listing.rating || 5)) + '☆'.repeat(5 - Math.round(listing.rating || 5));
    const distText = listing.distanceKm ? `📍 ${listing.distanceKm} km (${listing.location})` : `📍 ${listing.location || 'India'}`;
    
    const moistNum = parseFloat((listing.moisture || '12').replace('%', ''));
    const isDry = moistNum <= 15;
    const isHighEnergy = parseFloat((listing.calorific || '15').replace(/[^0-9.]/g, '')) >= 15;

    return `
        <article class="listing-card animate-fade-in" data-id="${listing.id}">
            ${listing.aiBestMatch ? `<div class="badge-ai-match"><i class="fas fa-certificate"></i> AI Verified Spec</div>` : ''}
            
            <button type="button" class="btn-wishlist ${isWished ? 'active' : ''}" onclick="window.toggleWishlist('${listing.id}')" title="Save Lot to Wishlist" aria-label="Save to Wishlist">
                <i class="${isWished ? 'fas fa-heart' : 'far fa-heart'}"></i>
            </button>

            <div class="listing-image">
                ${getListingImageHtml(listing)}
            </div>

            <div class="listing-content">
                <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:4px;">
                    <span class="listing-category">${formatCategory(listing.category)}</span>
                    <small style="color:var(--text-muted);font-size:0.75rem;">${distText}</small>
                </div>

                <h3 class="listing-title">${listing.name}</h3>

                <div class="card-quality-strip">
                    <span class="quality-pill ${isDry ? 'optimal-dry' : ''}" title="Moisture Content">
                        <i class="fas fa-droplet"></i> ${listing.moisture || '12%'} Moisture
                    </span>
                    <span class="quality-pill ${isHighEnergy ? 'high-energy' : ''}" title="Gross Calorific Value">
                        <i class="fas fa-bolt"></i> ${listing.calorific || '15.2 MJ/kg'} GCV
                    </span>
                </div>

                <div class="listing-details">
                    <div class="detail-item">
                        <span>Available Volume</span>
                        <strong>${listing.quantity} tonnes</strong>
                    </div>
                    <div class="detail-item" style="text-align:right;">
                        <span>Lab Rating</span>
                        <strong style="color:var(--harvest-gold-600);">${stars}</strong>
                    </div>
                </div>

                <div class="listing-footer">
                    <div class="listing-price">
                        ₹${Number(listing.price).toLocaleString()}
                        <small>/tonne</small>
                    </div>
                    <div style="display:flex;gap:0.4rem;">
                        <button type="button" class="btn-outline" style="padding:0.45rem 0.75rem;min-height:40px;font-size:0.85rem;" onclick="window.openQuickView('${listing.id}')" title="View Verified Lab Specs">
                            <i class="fas fa-eye"></i> Specs
                        </button>
                        <button type="button" class="btn-add-cart" onclick="window.addListingToCart('${listing.id}')" title="Add to Purchase Order Cart" aria-label="Add to cart">
                            <i class="fas fa-cart-plus"></i>
                        </button>
                    </div>
                </div>
            </div>
        </article>
    `;
}

// ==============================================================================
// PAGINATION
// ==============================================================================
function renderPagination(totalPages) {
    const numbersEl = document.getElementById('pageNumbers');
    const prevBtn = document.getElementById('prevPage');
    const nextBtn = document.getElementById('nextPage');
    if (!numbersEl) return;

    if (totalPages <= 1) {
        numbersEl.innerHTML = '';
        if (prevBtn) prevBtn.disabled = true;
        if (nextBtn) nextBtn.disabled = true;
        return;
    }

    if (prevBtn) {
        prevBtn.disabled = currentPage === 1;
        prevBtn.onclick = () => { if (currentPage > 1) { currentPage--; displayListings(); window.scrollTo({ top: 320, behavior: 'smooth' }); } };
    }
    if (nextBtn) {
        nextBtn.disabled = currentPage === totalPages;
        nextBtn.onclick = () => { if (currentPage < totalPages) { currentPage++; displayListings(); window.scrollTo({ top: 320, behavior: 'smooth' }); } };
    }

    let html = '';
    for (let p = 1; p <= totalPages; p++) {
        html += `<button type="button" class="page-btn ${p === currentPage ? 'active' : ''}" onclick="window.goToPage(${p})">${p}</button>`;
    }
    numbersEl.innerHTML = html;
}

window.goToPage = function(page) {
    currentPage = page;
    displayListings();
    window.scrollTo({ top: 320, behavior: 'smooth' });
};

// ==============================================================================
// FILTER ENGINE & CONTROLS
// ==============================================================================
function initializeFilterControls() {
    // Search Box
    const searchInput = document.getElementById('searchInput');
    if (searchInput) {
        searchInput.addEventListener('input', (e) => {
            currentFilters.search = e.target.value.toLowerCase().trim();
            currentPage = 1;
            applyFilters();
        });
    }

    // Category Checkboxes
    document.querySelectorAll('.category-filter').forEach(cb => {
        cb.addEventListener('change', () => {
            const checked = Array.from(document.querySelectorAll('.category-filter:checked')).map(c => c.value.toLowerCase());
            currentFilters.categories = checked;
            currentPage = 1;
            applyFilters();
        });
    });

    // Price Inputs
    const minP = document.getElementById('minPrice');
    const maxP = document.getElementById('maxPrice');
    const handlePriceChange = () => {
        currentFilters.minPrice = minP?.value ? parseFloat(minP.value) : null;
        currentFilters.maxPrice = maxP?.value ? parseFloat(maxP.value) : null;
        currentPage = 1;
        applyFilters();
    };
    minP?.addEventListener('input', handlePriceChange);
    maxP?.addEventListener('input', handlePriceChange);

    // Quantity Slider
    const qtySlider = document.getElementById('quantityRange');
    const qtyVal = document.getElementById('quantityValue');
    if (qtySlider) {
        qtySlider.addEventListener('input', (e) => {
            const val = parseInt(e.target.value, 10);
            if (qtyVal) qtyVal.textContent = val;
            currentFilters.minQuantity = val;
            currentPage = 1;
            applyFilters();
        });
    }

    // Location Dropdown
    const locSelect = document.getElementById('locationFilter');
    if (locSelect) {
        locSelect.addEventListener('change', (e) => {
            currentFilters.location = e.target.value.toLowerCase().trim();
            currentPage = 1;
            applyFilters();
        });
    }

    // Moisture Radios
    document.querySelectorAll('input[name="moistureConstraint"]').forEach(r => {
        r.addEventListener('change', (e) => {
            currentFilters.maxMoisture = e.target.value ? parseFloat(e.target.value) : null;
            currentPage = 1;
            applyFilters();
        });
    });

    // Apply Button (useful on mobile drawer)
    const applyBtn = document.getElementById('applyFilters');
    if (applyBtn) {
        applyBtn.addEventListener('click', () => {
            applyFilters();
            const sidebar = document.getElementById('marketplaceSidebar');
            const backdrop = document.getElementById('sheetBackdrop');
            if (sidebar) sidebar.classList.remove('sheet-open');
            if (backdrop) backdrop.classList.remove('active');
        });
    }
}

function applyFilters() {
    filteredListings = allListings.filter(item => {
        // Text Search
        if (currentFilters.search) {
            const haystack = `${item.name} ${item.location || ''} ${item.seller || ''} ${item.category || ''}`.toLowerCase();
            if (!haystack.includes(currentFilters.search)) return false;
        }

        // Category Filter
        if (currentFilters.categories.length > 0) {
            const cat = (item.category || '').toLowerCase();
            const matches = currentFilters.categories.some(c => cat.includes(c) || c.includes(cat));
            if (!matches) return false;
        }

        // Min & Max Price
        const price = Number(listingPrice(item));
        if (currentFilters.minPrice !== null && price < currentFilters.minPrice) return false;
        if (currentFilters.maxPrice !== null && price > currentFilters.maxPrice) return false;

        // Minimum Quantity
        if (currentFilters.minQuantity > 0 && Number(item.quantity) < currentFilters.minQuantity) return false;

        // Location
        if (currentFilters.location) {
            const loc = (item.location || '').toLowerCase();
            if (!loc.includes(currentFilters.location)) return false;
        }

        // Moisture Threshold
        if (currentFilters.maxMoisture !== null) {
            const m = parseFloat((item.moisture || '20').replace('%', ''));
            if (m > currentFilters.maxMoisture) return false;
        }

        return true;
    });

    applySorting();
    updateActiveFilterChips();
    displayListings();
}

function listingPrice(item) {
    return Number(item.price) || 0;
}

// ==============================================================================
// SORTING & VIEWS
// ==============================================================================
function initializeSortAndViews() {
    const sortSelect = document.getElementById('sortBy');
    if (sortSelect) {
        sortSelect.addEventListener('change', (e) => {
            currentSort = e.target.value;
            applySorting();
            displayListings();
        });
    }

    const gridBtn = document.getElementById('viewGridBtn');
    const listBtn = document.getElementById('viewListBtn');
    if (gridBtn && listBtn) {
        gridBtn.addEventListener('click', () => {
            currentView = 'grid';
            gridBtn.classList.add('active');
            listBtn.classList.remove('active');
            displayListings();
        });
        listBtn.addEventListener('click', () => {
            currentView = 'list';
            listBtn.classList.add('active');
            gridBtn.classList.remove('active');
            displayListings();
        });
    }
}

function applySorting() {
    if (currentSort === 'price-low') {
        filteredListings.sort((a, b) => listingPrice(a) - listingPrice(b));
    } else if (currentSort === 'price-high') {
        filteredListings.sort((a, b) => listingPrice(b) - listingPrice(a));
    } else if (currentSort === 'quantity') {
        filteredListings.sort((a, b) => Number(b.quantity || 0) - Number(a.quantity || 0));
    } else if (currentSort === 'calorific') {
        filteredListings.sort((a, b) => parseFloat(b.calorific || '0') - parseFloat(a.calorific || '0'));
    } else if (currentSort === 'moisture') {
        filteredListings.sort((a, b) => parseFloat(a.moisture || '99') - parseFloat(b.moisture || '99'));
    } else if (currentSort === 'rating') {
        filteredListings.sort((a, b) => Number(b.rating || 0) - Number(a.rating || 0));
    } else {
        // AI Recommended
        filteredListings.sort((a, b) => (b.aiBestMatch ? 1 : 0) - (a.aiBestMatch ? 1 : 0));
    }
}

// ==============================================================================
// ACTIVE FILTER CHIPS BAR
// ==============================================================================
function updateActiveFilterChips() {
    const chipsContainer = document.getElementById('activeFilterChips');
    const badgeCount = document.getElementById('activeFilterCount');
    if (!chipsContainer) return;

    let chips = [];
    if (currentFilters.search) {
        chips.push({ label: `"${currentFilters.search}"`, type: 'search' });
    }
    currentFilters.categories.forEach(c => {
        chips.push({ label: formatCategory(c), type: 'category', val: c });
    });
    if (currentFilters.minPrice !== null || currentFilters.maxPrice !== null) {
        const minL = currentFilters.minPrice ? `₹${currentFilters.minPrice}` : '₹0';
        const maxL = currentFilters.maxPrice ? `₹${currentFilters.maxPrice}` : 'Any';
        chips.push({ label: `Price: ${minL} - ${maxL}`, type: 'price' });
    }
    if (currentFilters.minQuantity > 0) {
        chips.push({ label: `≥ ${currentFilters.minQuantity}T`, type: 'quantity' });
    }
    if (currentFilters.location) {
        chips.push({ label: `Zone: ${currentFilters.location.toUpperCase()}`, type: 'location' });
    }
    if (currentFilters.maxMoisture !== null) {
        chips.push({ label: `≤ ${currentFilters.maxMoisture}% Moisture`, type: 'moisture' });
    }

    if (badgeCount) badgeCount.textContent = chips.length;

    if (chips.length === 0) {
        chipsContainer.style.display = 'none';
        chipsContainer.innerHTML = '';
        return;
    }

    chipsContainer.style.display = 'flex';
    chipsContainer.innerHTML = chips.map(c => `
        <span class="filter-chip">
            ${c.label}
            <i class="fas fa-times chip-remove" onclick="window.removeFilterChip('${c.type}', '${c.val || ''}')"></i>
        </span>
    `).join('') + `
        <button type="button" class="btn-clear-all-chips" onclick="window.clearAllFilters()">Clear All</button>
    `;
}

window.removeFilterChip = function(type, val) {
    if (type === 'search') {
        currentFilters.search = '';
        const searchInput = document.getElementById('searchInput');
        if (searchInput) searchInput.value = '';
    } else if (type === 'category') {
        currentFilters.categories = currentFilters.categories.filter(c => c !== val);
        document.querySelectorAll(`.category-filter[value="${val}"]`).forEach(cb => cb.checked = false);
    } else if (type === 'price') {
        currentFilters.minPrice = null;
        currentFilters.maxPrice = null;
        const minP = document.getElementById('minPrice');
        const maxP = document.getElementById('maxPrice');
        if (minP) minP.value = '';
        if (maxP) maxP.value = '';
    } else if (type === 'quantity') {
        currentFilters.minQuantity = 0;
        const slider = document.getElementById('quantityRange');
        const qtyVal = document.getElementById('quantityValue');
        if (slider) slider.value = 0;
        if (qtyVal) qtyVal.textContent = 0;
    } else if (type === 'location') {
        currentFilters.location = '';
        const loc = document.getElementById('locationFilter');
        if (loc) loc.value = '';
    } else if (type === 'moisture') {
        currentFilters.maxMoisture = null;
        const radio = document.querySelector('input[name="moistureConstraint"][value=""]');
        if (radio) radio.checked = true;
    }
    currentPage = 1;
    applyFilters();
};

window.clearAllFilters = function() {
    currentFilters = {
        search: '',
        categories: [],
        minPrice: null,
        maxPrice: null,
        minQuantity: 0,
        location: '',
        maxMoisture: null
    };

    const searchInput = document.getElementById('searchInput');
    if (searchInput) searchInput.value = '';
    document.querySelectorAll('.category-filter').forEach(cb => cb.checked = false);
    const minP = document.getElementById('minPrice');
    const maxP = document.getElementById('maxPrice');
    if (minP) minP.value = '';
    if (maxP) maxP.value = '';
    const slider = document.getElementById('quantityRange');
    const qtyVal = document.getElementById('quantityValue');
    if (slider) slider.value = 0;
    if (qtyVal) qtyVal.textContent = 0;
    const loc = document.getElementById('locationFilter');
    if (loc) loc.value = '';
    const radio = document.querySelector('input[name="moistureConstraint"][value=""]');
    if (radio) radio.checked = true;

    currentPage = 1;
    applyFilters();
};

// ==============================================================================
// MOBILE BOTTOM SHEET DRAWER
// ==============================================================================
window.toggleFilterSheet = function() {
    const sidebar = document.getElementById('marketplaceSidebar');
    const backdrop = document.getElementById('sheetBackdrop');
    if (sidebar) sidebar.classList.toggle('sheet-open');
    if (backdrop) backdrop.classList.toggle('active');
};

// ==============================================================================
// WISHLIST PERSISTENCE
// ==============================================================================
window.toggleWishlist = function(id) {
    if (wishlist.includes(id)) {
        wishlist = wishlist.filter(item => item !== id);
        if (window.showNotification) window.showNotification('Lot removed from saved wishlist', 'info');
    } else {
        wishlist.push(id);
        if (window.showNotification) window.showNotification('Residue lot saved to Wishlist! ❤️', 'success');
    }
    localStorage.setItem('userWishlist', JSON.stringify(wishlist));
    displayListings();
};

// ==============================================================================
// QUICK-VIEW MODAL
// ==============================================================================
window.openQuickView = function(id) {
    const listing = allListings.find(l => l.id === id);
    if (!listing) return;

    const modal = document.getElementById('quickViewModal');
    if (!modal) return;

    document.getElementById('qvTitle').textContent = listing.name;
    document.getElementById('qvLocation').innerHTML = `<i class="fas fa-map-marker-alt" style="color:var(--primary-color);"></i> ${listing.location || 'India'}`;
    document.getElementById('qvCalorific').textContent = listing.calorific || '15.2 MJ/kg';
    document.getElementById('qvMoisture').textContent = listing.moisture || '12.0%';
    document.getElementById('qvDensity').textContent = listing.density || '140 kg/m³';
    document.getElementById('qvCarbon').textContent = listing.co2Offset || '1.45 T CO₂e/T';
    document.getElementById('qvPrice').textContent = '₹' + Number(listing.price).toLocaleString();
    document.getElementById('qvQuantity').textContent = listing.quantity + ' Tonnes';
    document.getElementById('qvSeller').textContent = listing.seller || 'Verified Local Producer';
    document.getElementById('qvCategoryBadge').textContent = formatCategory(listing.category);

    const qvImg = document.getElementById('qvImage');
    if (qvImg) {
        if (listing.image && listing.image.length > 20) {
            qvImg.src = listing.image;
        } else {
            const key = (listing.imageKey || 'rice').toLowerCase();
            const list = window.CROP_IMAGE_MAP ? window.CROP_IMAGE_MAP[key] : null;
            if (list && list.length > 0) {
                qvImg.src = list[0];
            } else {
                qvImg.src = 'Dataset/crop_images/rice/rice001a%20-%20Copy%20%2810%29.jpeg';
            }
        }
        qvImg.onerror = () => window.handleListingImageError(qvImg, listing.imageKey);
    }

    const addBtn = document.getElementById('qvAddCartBtn');
    if (addBtn) {
        addBtn.onclick = () => {
            window.addListingToCart(listing.id);
            modal.classList.remove('active');
        };
    }

    modal.classList.add('active');
};

// ==============================================================================
// 3-STEP ADD LISTING WIZARD
// ==============================================================================
function initializeWizardModal() {
    const form = document.getElementById('addListingWizardForm');
    const qtyInput = document.getElementById('wizQuantity');
    const priceInput = document.getElementById('wizPrice');
    const photoInput = document.getElementById('wizPhotoInput');

    // Live Payout Calculation
    const calcEarnings = () => {
        const q = parseFloat(qtyInput?.value || 0);
        const p = parseFloat(priceInput?.value || 0);
        const total = q * p;
        const preview = document.getElementById('wizEarningsPreview');
        if (preview) preview.value = total > 0 ? '₹' + total.toLocaleString() : '₹0';
    };
    qtyInput?.addEventListener('input', calcEarnings);
    priceInput?.addEventListener('input', calcEarnings);

    // Photo Preview
    photoInput?.addEventListener('change', (e) => {
        const file = e.target.files[0];
        if (file) {
            const reader = new FileReader();
            reader.onload = (evt) => {
                wizardImageBase64 = evt.target.result;
                const previewImg = document.getElementById('wizPreviewImg');
                const previewBox = document.getElementById('wizPhotoPreview');
                if (previewImg && previewBox) {
                    previewImg.src = wizardImageBase64;
                    previewBox.style.display = 'block';
                }
            };
            reader.readAsDataURL(file);
        }
    });

    form?.addEventListener('submit', handleWizardSubmit);
}

window.openAddListingModal = function() {
    const modal = document.getElementById('addListingModal');
    if (modal) {
        window.wizardGoTo(1);
        modal.classList.add('active');
    }
};

window.closeAddListingModal = function() {
    const modal = document.getElementById('addListingModal');
    if (modal) modal.classList.remove('active');
};

window.wizardGoTo = function(step) {
    if (step === 2) {
        const title = document.getElementById('wizTitle')?.value.trim();
        if (!title) {
            if (window.showNotification) window.showNotification('Please enter a lot title or grade description', 'error');
            return;
        }
    } else if (step === 3) {
        const qty = document.getElementById('wizQuantity')?.value;
        const price = document.getElementById('wizPrice')?.value;
        if (!qty || !price || parseFloat(qty) <= 0 || parseFloat(price) <= 0) {
            if (window.showNotification) window.showNotification('Please enter valid available volume and price per tonne', 'error');
            return;
        }
    }

    wizardStep = step;
    document.querySelectorAll('.wizard-step-pane').forEach((p, idx) => {
        p.style.display = (idx + 1 === step) ? 'block' : 'none';
    });

    document.querySelectorAll('.wizard-step-node').forEach((node, idx) => {
        node.classList.remove('active', 'completed');
        if (idx + 1 === step) {
            node.classList.add('active');
        } else if (idx + 1 < step) {
            node.classList.add('completed');
        }
    });
};

function handleWizardSubmit(e) {
    e.preventDefault();
    const crop = document.getElementById('wizCropSelect').value;
    const title = document.getElementById('wizTitle').value.trim();
    const qty = parseFloat(document.getElementById('wizQuantity').value);
    const price = parseFloat(document.getElementById('wizPrice').value);
    const moisture = document.getElementById('wizMoisture').value + '%';
    const location = document.getElementById('wizLocation').value.trim();

    const user = window.AppState?.currentUser || JSON.parse(localStorage.getItem('currentUser') || '{}');
    const sellerName = user.name || 'Verified Producer';

    let category = 'crop-residue';
    if (crop === 'rice' || crop === 'wheat') category = 'straw';
    else if (crop === 'sugarcane') category = 'bagasse';
    else if (crop === 'groundnut') category = 'husk';
    else if (crop === 'cattle' || crop === 'poultry') category = 'livestock';
    else if (crop === 'banana' || crop === 'bamboo') category = 'other';

    const newListing = {
        id: 'L' + (allListings.length + 101),
        name: title,
        category: category,
        imageKey: crop,
        image: wizardImageBase64 || null,
        price: price,
        quantity: qty,
        location: location,
        seller: sellerName,
        rating: 5.0,
        date: new Date(),
        moisture: moisture,
        calorific: '15.4 MJ/kg',
        density: '145 kg/m³',
        co2Offset: '1.45 T/T',
        quality: 5,
        aiBestMatch: false,
        distanceKm: 12
    };

    allListings.unshift(newListing);
    localStorage.setItem('marketplaceListings', JSON.stringify(allListings));

    window.closeAddListingModal();
    document.getElementById('addListingWizardForm').reset();
    wizardImageBase64 = null;
    const previewBox = document.getElementById('wizPhotoPreview');
    if (previewBox) previewBox.style.display = 'none';

    window.clearAllFilters();

    if (window.showNotification) {
        window.showNotification('New Crop Residue Lot Published to Marketplace! 🌾', 'success');
    }
}

// ==============================================================================
// AUTO PRE-FILL BRIDGE FROM AI ANALYZER
// ==============================================================================
function checkPendingAnalyzerPreFill() {
    const pending = localStorage.getItem('pendingListingPreFill');
    if (pending) {
        try {
            const data = JSON.parse(pending);
            localStorage.removeItem('pendingListingPreFill');

            window.openAddListingModal();
            if (data.cropKey && document.getElementById('wizCropSelect')) {
                document.getElementById('wizCropSelect').value = data.cropKey;
            }
            if (data.title && document.getElementById('wizTitle')) {
                document.getElementById('wizTitle').value = data.title;
            }
            if (data.recommendedPrice && document.getElementById('wizPrice')) {
                document.getElementById('wizPrice').value = data.recommendedPrice;
            }
            if (data.moisture && document.getElementById('wizMoisture')) {
                document.getElementById('wizMoisture').value = parseFloat(data.moisture) || 12;
            }
            if (data.image) {
                wizardImageBase64 = data.image;
                const previewImg = document.getElementById('wizPreviewImg');
                const previewBox = document.getElementById('wizPhotoPreview');
                if (previewImg && previewBox) {
                    previewImg.src = wizardImageBase64;
                    previewBox.style.display = 'block';
                }
            }
            if (window.showNotification) {
                window.showNotification('Prefilled listing details from AI Scan!', 'success');
            }
        } catch (e) {
            console.warn('Error reading pendingListingPreFill', e);
        }
    }
}

// ==============================================================================
// CART & CHECKOUT INTEGRATION
// ==============================================================================
window.addListingToCart = function(id) {
    const listing = allListings.find(l => l.id === id);
    if (!listing) return;

    if (window.AppState && typeof window.AppState.addToCart === 'function') {
        window.AppState.addToCart(listing);
    } else {
        let cart = JSON.parse(localStorage.getItem('cart') || '[]');
        const existing = cart.find(i => i.id === listing.id);
        if (existing) {
            existing.quantity = (existing.quantity || 1) + 1;
        } else {
            cart.push({ ...listing, quantity: 1 });
        }
        localStorage.setItem('cart', JSON.stringify(cart));
        const badge = document.getElementById('cartBadge');
        if (badge) {
            badge.textContent = cart.length;
            badge.style.display = 'block';
        }
    }

    if (window.showNotification) {
        window.showNotification(`Added ${listing.name} to purchase order cart! 🛒`, 'success');
    }
};

// Category Formatter
function formatCategory(cat) {
    const map = {
        'crop-residue': 'Crop Residue',
        'husk': 'Husk & Shells',
        'straw': 'Straw Bales',
        'bagasse': 'Bagasse',
        'livestock': 'Livestock Waste',
        'other': 'Other Biomass'
    };
    return map[cat] || cat || 'General Residue';
}
