// Dynamic Dashboard Script with Dedicated Farmer, Buyer, and Admin Portals
// ==============================================================================

// Global chart references so we can destroy and recreate on resize/toggle
const activeCharts = {
    farmerRevenue: null,
    farmerCrop: null,
    farmerMandi: null,
    buyerSpend: null,
    buyerQuality: null,
    buyerCarbon: null,
    adminGmv: null,
    adminBurn: null,
    adminUser: null
};

// Current active role
let currentPortalRole = 'farmer';

document.addEventListener('DOMContentLoaded', function() {
    // 1. Determine active user role
    const currentUser = window.AppState?.currentUser || JSON.parse(localStorage.getItem('currentUser') || 'null');
    if (currentUser && currentUser.userType) {
        currentPortalRole = currentUser.userType.toLowerCase();
    } else {
        currentPortalRole = 'farmer';
    }

    // Fallback mapping for other aliases
    if (currentPortalRole === 'aggregator' || currentPortalRole === 'transporter') {
        currentPortalRole = 'farmer';
    } else if (currentPortalRole === 'processor') {
        currentPortalRole = 'buyer';
    } else if (currentPortalRole !== 'farmer' && currentPortalRole !== 'buyer' && currentPortalRole !== 'admin') {
        currentPortalRole = 'farmer';
    }

    // 2. Render initial portal
    switchPortalView(currentPortalRole, false);

    // 3. Render dynamic data for this portal
    renderDynamicPortalData(currentPortalRole);

    // 4. Watch for theme changes to redraw charts with correct contrast
    setupThemeWatcher();
});

// Switches portal view between farmer, buyer, and admin
window.switchPortalView = function(role, saveToUser = true) {
    currentPortalRole = role;

    // 1. Update pill button states
    const pills = document.querySelectorAll('.persona-pill-btn');
    pills.forEach(p => p.classList.remove('active'));

    const activePill = document.getElementById(`btnSwitch${capitalize(role)}`);
    if (activePill) {
        activePill.classList.add('active');
    }

    // 2. Update portal view visibility
    const portals = document.querySelectorAll('.portal-view');
    portals.forEach(p => p.classList.remove('active-portal'));

    const targetPortal = document.getElementById(`${role}PortalView`);
    if (targetPortal) {
        targetPortal.classList.add('active-portal');
    }

    // 3. Update top switcher bar identity meta
    updateSwitcherIdentity(role);

    // 4. Save to AppState/localStorage if requested
    if (saveToUser) {
        const users = JSON.parse(localStorage.getItem('users') || '[]');
        const match = users.find(u => u.userType === role);
        if (match) {
            const { password, ...userNoPass } = match;
            if (window.AppState && typeof window.AppState.saveUser === 'function') {
                window.AppState.saveUser(userNoPass);
            } else {
                localStorage.setItem('currentUser', JSON.stringify(userNoPass));
            }
        }
    }

    // 5. Render dynamic data and charts
    renderDynamicPortalData(role);

    setTimeout(() => {
        initializeRoleCharts(role);
    }, 120);
};

window.renderActivePortal = function(role) {
    window.switchPortalView(role, false);
};

function capitalize(str) {
    if (!str) return '';
    return str.charAt(0).toUpperCase() + str.slice(1);
}

function updateSwitcherIdentity(role) {
    const avatar = document.getElementById('switcherAvatar');
    const name = document.getElementById('switcherName');
    const roleTitle = document.getElementById('switcherRoleTitle');
    const user = window.AppState?.currentUser || JSON.parse(localStorage.getItem('currentUser') || 'null');

    if (role === 'farmer') {
        if (avatar) avatar.src = 'https://ui-avatars.com/api/?name=Ramesh+Singh&background=1B6A45&color=fff';
        if (name) name.textContent = (user?.userType === 'farmer' && user?.name) ? user.name : 'Farmer Ramesh Singh';
        if (roleTitle) roleTitle.textContent = 'Verified Agricultural Producer (Punjab Agri Co-op)';
    } else if (role === 'buyer') {
        if (avatar) avatar.src = 'https://ui-avatars.com/api/?name=GreenGrid+BioPower&background=0284c7&color=fff';
        if (name) name.textContent = (user?.userType === 'buyer' && user?.name) ? user.name : 'GreenGrid Bio-Power Ltd';
        if (roleTitle) roleTitle.textContent = 'Tier-1 Industrial Off-Taker | GSTIN: 03AABCG1234F1Z9';
    } else if (role === 'admin') {
        if (avatar) avatar.src = 'https://ui-avatars.com/api/?name=Admin+Controller&background=7c3aed&color=fff';
        if (name) name.textContent = (user?.userType === 'admin' && user?.name) ? user.name : 'Platform Operations Admin';
        if (roleTitle) roleTitle.textContent = 'Master SuperAdmin Console | Security Clearance: Level-1';
    }
}

// ==============================================================================
// DYNAMIC PORTAL DATA RENDERING & LOCALSTORAGE SYNC
// ==============================================================================

function renderDynamicPortalData(role) {
    if (role === 'farmer') {
        renderFarmerListingsTable();
    } else if (role === 'buyer') {
        renderBuyerRfqsTable();
    } else if (role === 'admin') {
        renderAdminKycStatus();
    }
}

// 1. Farmer Dynamic Lots Table & Stats
function renderFarmerListingsTable() {
    const tbody = document.getElementById('farmerListingsTableBody');
    if (!tbody) return;

    let listings = [];
    try {
        const saved = localStorage.getItem('marketplaceListings');
        if (saved) {
            listings = JSON.parse(saved);
        }
    } catch (e) {
        listings = [];
    }

    // Default sample lots if none saved yet
    const defaultLots = [
        {
            id: 'LOT-881',
            name: 'Rice Paddy Straw (Basmati)',
            quantity: 80,
            price: 5200,
            moisture: '12.0%',
            calorific: '15.2 MJ/kg',
            status: 'Active / Listed',
            icon: 'fa-wheat-awn',
            color: 'text-amber'
        },
        {
            id: 'LOT-882',
            name: 'Wheat Straw Bundles (Turi)',
            quantity: 40,
            price: 4500,
            moisture: '13.5%',
            calorific: '16.0 MJ/kg',
            status: 'Active / Listed',
            icon: 'fa-seedling',
            color: 'text-green'
        },
        {
            id: 'LOT-883',
            name: 'Sugarcane Bagasse',
            quantity: 22,
            price: 3800,
            moisture: '35.0%',
            calorific: '9.8 MJ/kg',
            status: 'Reserved for Mill',
            icon: 'fa-candy-cane',
            color: 'text-purple'
        }
    ];

    let combinedLots = [];
    if (listings && listings.length > 0) {
        // Map user created or marketplace listings to table format
        const customLots = listings.map((item, idx) => ({
            id: item.id || `LOT-${900 + idx}`,
            name: item.name || 'Crop Residue Lot',
            quantity: item.quantity || 50,
            price: item.price || 4200,
            moisture: item.moisture || '13.0%',
            calorific: item.calorific || '15.0 MJ/kg',
            status: item.status || 'Active / Listed',
            isCustom: true,
            icon: getCropIcon(item.imageKey || item.name),
            color: 'text-emerald-600'
        }));
        combinedLots = customLots.slice(0, 8);
    } else {
        combinedLots = defaultLots;
    }

    // Calculate totals for Farmer stats cards
    let totalTons = 0;
    let totalEarnings = 0;
    combinedLots.forEach(lot => {
        totalTons += (parseFloat(lot.quantity) || 0);
        totalEarnings += ((parseFloat(lot.quantity) || 0) * (parseFloat(lot.price) || 0));
    });

    // Update stats cards
    const wasteSoldEl = document.getElementById('farmerWasteSold');
    if (wasteSoldEl) {
        wasteSoldEl.textContent = `${Math.round(totalTons)} Tons`;
    }

    const earningsEl = document.getElementById('farmerTotalEarnings');
    if (earningsEl) {
        earningsEl.textContent = `₹${Math.round(totalEarnings).toLocaleString('en-IN')}`;
    }

    // Render HTML table rows
    tbody.innerHTML = combinedLots.map(lot => `
        <tr>
            <td><strong>#${escapeHtml(lot.id)}</strong></td>
            <td><i class="fas ${lot.icon} ${lot.color}"></i> ${escapeHtml(lot.name)}</td>
            <td class="tabular">${lot.quantity} Tons</td>
            <td class="tabular">₹${Number(lot.price).toLocaleString('en-IN')}</td>
            <td><span class="badge-status status-verified">${escapeHtml(lot.moisture)}</span></td>
            <td>${escapeHtml(lot.calorific)}</td>
            <td><span class="badge-status status-approved"><i class="fas fa-check-circle"></i> ${escapeHtml(lot.status)}</span></td>
            <td>
                ${lot.isCustom ? `
                    <button type="button" class="btn-table-action btn-reject" onclick="deleteFarmerLot('${escapeHtml(lot.id)}')"><i class="fas fa-trash-alt"></i> Delete</button>
                ` : `
                    <button type="button" class="btn-table-action btn-details" onclick="alert('Viewing Lot #${escapeHtml(lot.id)} Lab Certificate')">View</button>
                `}
            </td>
        </tr>
    `).join('');
}

function getCropIcon(cropName) {
    const key = (cropName || '').toLowerCase();
    if (key.includes('rice') || key.includes('paddy')) return 'fa-wheat-awn';
    if (key.includes('wheat') || key.includes('stover')) return 'fa-seedling';
    if (key.includes('sugar') || key.includes('bagasse')) return 'fa-candy-cane';
    if (key.includes('cotton') || key.includes('stalk')) return 'fa-feather';
    if (key.includes('groundnut') || key.includes('husk')) return 'fa-shapes';
    return 'fa-leaf';
}

window.deleteFarmerLot = function(lotId) {
    if (!confirm(`Are you sure you want to withdraw Lot #${lotId} from the marketplace?`)) return;

    try {
        let listings = JSON.parse(localStorage.getItem('marketplaceListings') || '[]');
        listings = listings.filter(l => l.id !== lotId);
        localStorage.setItem('marketplaceListings', JSON.stringify(listings));
        renderFarmerListingsTable();
        if (window.showNotification) {
            window.showNotification(`Lot #${lotId} removed from marketplace.`, 'info');
        }
    } catch (e) {
        console.error('Error deleting lot', e);
    }
};

// 2. Buyer RFQ Table & Persistent State
function renderBuyerRfqsTable() {
    const rfqTable = document.querySelector('#buyerPortalView .portal-two-col .portal-table tbody');
    if (!rfqTable) return;

    let rfqs = [];
    try {
        rfqs = JSON.parse(localStorage.getItem('agriwaste_rfqs') || '[]');
    } catch(e) {
        rfqs = [];
    }

    const defaultRfqs = [
        { req: 'Sugarcane Bagasse (<18% moisture)', qty: '300 Tons', price: '₹3,900/T', bids: '4 Farmer Co-ops', status: 'Open' },
        { req: 'Rice Paddy Straw Bales', qty: '200 Tons', price: '₹5,300/T', bids: '7 Farmer Co-ops', status: 'Open' },
        { req: 'Groundnut Shells (Biofuel Grade)', qty: '100 Tons', price: '₹4,900/T', bids: '3 Farmer Co-ops', status: 'Evaluating' }
    ];

    const allRfqs = [...rfqs, ...defaultRfqs];

    rfqTable.innerHTML = allRfqs.map(rfq => `
        <tr>
            <td>${escapeHtml(rfq.req)}</td>
            <td class="tabular">${escapeHtml(rfq.qty)}</td>
            <td class="tabular">${escapeHtml(rfq.price)}</td>
            <td><strong>${escapeHtml(rfq.bids)}</strong></td>
            <td><span class="badge-status status-approved">${escapeHtml(rfq.status)}</span></td>
        </tr>
    `).join('');
}

window.openPostRfqModal = function() {
    const qty = prompt('Enter required biomass volume in Metric Tons (e.g. 250):', '250');
    if (!qty || isNaN(qty) || parseFloat(qty) <= 0) return;

    const material = prompt('Enter required crop residue (e.g. Sugarcane Bagasse / Rice Straw):', 'Sugarcane Bagasse');
    if (!material) return;

    const maxPrice = prompt('Enter maximum target price in ₹/Ton (e.g. 4200):', '4200');

    const newRfq = {
        req: `${material} (Moisture < 15%)`,
        qty: `${qty} Tons`,
        price: `₹${maxPrice || '4,200'}/T`,
        bids: 'Broadcast to 18 Mandis',
        status: 'Active RFQ'
    };

    try {
        const rfqs = JSON.parse(localStorage.getItem('agriwaste_rfqs') || '[]');
        rfqs.unshift(newRfq);
        localStorage.setItem('agriwaste_rfqs', JSON.stringify(rfqs));
        renderBuyerRfqsTable();
    } catch (e) {
        console.error('Error saving RFQ', e);
    }

    if (window.showNotification) {
        window.showNotification(`RFQ broadcasted for ${qty}T of ${material}! Nearby farmer cooperatives notified.`, 'success');
    } else {
        alert(`RFQ posted for ${qty}T of ${material}! Broadcast sent to farmer co-ops.`);
    }
};

// 3. Admin KYC Persistent Approvals
function renderAdminKycStatus() {
    let kycStatus = {};
    try {
        kycStatus = JSON.parse(localStorage.getItem('agriwaste_kyc_status') || '{}');
    } catch(e) {
        kycStatus = {};
    }

    Object.keys(kycStatus).forEach(rowId => {
        const row = document.getElementById(rowId);
        if (row) {
            const actionCell = row.cells[row.cells.length - 1];
            if (kycStatus[rowId] === 'approved') {
                actionCell.innerHTML = `<span class="badge-status status-approved"><i class="fas fa-check"></i> Approved</span>`;
            } else if (kycStatus[rowId] === 'rejected') {
                row.style.opacity = '0.4';
                actionCell.innerHTML = `<span class="badge-status status-danger"><i class="fas fa-times"></i> Rejected</span>`;
            }
        }
    });
}

window.approveKyc = function(rowId, name) {
    const row = document.getElementById(rowId);
    if (row) {
        const actionCell = row.cells[row.cells.length - 1];
        actionCell.innerHTML = `<span class="badge-status status-approved"><i class="fas fa-check"></i> Approved</span>`;

        try {
            const kycStatus = JSON.parse(localStorage.getItem('agriwaste_kyc_status') || '{}');
            kycStatus[rowId] = 'approved';
            localStorage.setItem('agriwaste_kyc_status', JSON.stringify(kycStatus));
        } catch (e) {}

        if (window.showNotification) {
            window.showNotification(`KYC Approved for ${name}. Verification badge issued.`, 'success');
        }
    }
};

window.rejectKyc = function(rowId) {
    const row = document.getElementById(rowId);
    if (row) {
        row.style.opacity = '0.4';
        const actionCell = row.cells[row.cells.length - 1];
        actionCell.innerHTML = `<span class="badge-status status-danger"><i class="fas fa-times"></i> Rejected</span>`;

        try {
            const kycStatus = JSON.parse(localStorage.getItem('agriwaste_kyc_status') || '{}');
            kycStatus[rowId] = 'rejected';
            localStorage.setItem('agriwaste_kyc_status', JSON.stringify(kycStatus));
        } catch (e) {}

        if (window.showNotification) {
            window.showNotification('Application rejected and archived.', 'info');
        }
    }
};

// ==============================================================================
// CHART INITIALIZERS FOR EACH ROLE (EDITORIAL AGRARIAN PALETTE)
// ==============================================================================

function destroyChart(key) {
    if (activeCharts[key]) {
        try { activeCharts[key].destroy(); } catch(e) {}
        activeCharts[key] = null;
    }
}

function initializeRoleCharts(role) {
    if (typeof Chart === 'undefined') return;

    if (role === 'farmer') {
        initFarmerCharts();
    } else if (role === 'buyer') {
        initBuyerCharts();
    } else if (role === 'admin') {
        initAdminCharts();
    }
}

function setupThemeWatcher() {
    const observer = new MutationObserver(() => {
        initializeRoleCharts(currentPortalRole);
    });
    observer.observe(document.body, { attributes: true, attributeFilter: ['class'] });
}

function isDarkMode() {
    return document.body.classList.contains('dark-theme');
}

// 1. Farmer Charts (Forest Green #1B6A45 & Harvest Gold #BA7612)
function initFarmerCharts() {
    const isDark = isDarkMode();
    const gridColor = isDark ? 'rgba(255, 255, 255, 0.08)' : 'rgba(0, 0, 0, 0.05)';
    const textColor = isDark ? '#E4DDD2' : '#2D3A30';

    // Farmer Revenue Trend
    const revCtx = document.getElementById('farmerRevenueChart')?.getContext('2d');
    if (revCtx) {
        destroyChart('farmerRevenue');
        activeCharts.farmerRevenue = new Chart(revCtx, {
            type: 'line',
            data: {
                labels: ['Nov', 'Dec', 'Jan', 'Feb', 'Mar (Current)'],
                datasets: [{
                    label: 'Residue Sales (₹)',
                    data: [35000, 62000, 98000, 142000, 184500],
                    borderColor: '#1B6A45',
                    backgroundColor: 'rgba(27, 106, 69, 0.12)',
                    tension: 0.35,
                    fill: true,
                    pointBackgroundColor: '#1B6A45',
                    pointRadius: 5
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: { legend: { display: false } },
                scales: {
                    y: {
                        ticks: { color: textColor, callback: v => '₹' + (v / 1000) + 'k' },
                        grid: { color: gridColor }
                    },
                    x: {
                        ticks: { color: textColor },
                        grid: { display: false }
                    }
                }
            }
        });
    }

    // Farmer Crop Residue Doughnut
    const cropCtx = document.getElementById('farmerCropChart')?.getContext('2d');
    if (cropCtx) {
        destroyChart('farmerCrop');
        activeCharts.farmerCrop = new Chart(cropCtx, {
            type: 'doughnut',
            data: {
                labels: ['Rice Straw', 'Wheat Stover', 'Sugarcane Bagasse', 'Cotton Stalks'],
                datasets: [{
                    data: [52, 28, 14, 6],
                    backgroundColor: ['#1B6A45', '#BA7612', '#0284c7', '#A63B20'],
                    borderWidth: 2,
                    borderColor: isDark ? '#1C2B22' : '#ffffff'
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        position: 'bottom',
                        labels: { color: textColor, boxWidth: 12, font: { size: 11 } }
                    }
                }
            }
        });
    }

    // Farmer Mandi Price Comparison Bar
    const mandiCtx = document.getElementById('farmerMandiChart')?.getContext('2d');
    if (mandiCtx) {
        destroyChart('farmerMandi');
        activeCharts.farmerMandi = new Chart(mandiCtx, {
            type: 'bar',
            data: {
                labels: ['Rice Straw', 'Wheat Bales', 'Bagasse', 'Cotton', 'Groundnut'],
                datasets: [{
                    label: 'Mandi Rate (₹/Ton)',
                    data: [5200, 4500, 3800, 2800, 4800],
                    backgroundColor: '#1B6A45',
                    borderRadius: 6
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: { legend: { display: false } },
                scales: {
                    y: {
                        ticks: { color: textColor, callback: v => '₹' + v },
                        grid: { color: gridColor }
                    },
                    x: {
                        ticks: { color: textColor },
                        grid: { display: false }
                    }
                }
            }
        });
    }
}

// 2. Buyer Charts (Steel Navy & Cyan)
function initBuyerCharts() {
    const isDark = isDarkMode();
    const gridColor = isDark ? 'rgba(255, 255, 255, 0.08)' : 'rgba(0, 0, 0, 0.05)';
    const textColor = isDark ? '#E4DDD2' : '#2D3A30';

    // Buyer Spend Trend
    const spendCtx = document.getElementById('buyerSpendChart')?.getContext('2d');
    if (spendCtx) {
        destroyChart('buyerSpend');
        activeCharts.buyerSpend = new Chart(spendCtx, {
            type: 'line',
            data: {
                labels: ['Q1 2025', 'Q2 2025', 'Q3 2025', 'Q4 2025', 'Q1 2026'],
                datasets: [{
                    label: 'Biomass Spend (₹)',
                    data: [210000, 390000, 540000, 710000, 845000],
                    borderColor: '#0284c7',
                    backgroundColor: 'rgba(2, 132, 199, 0.12)',
                    tension: 0.35,
                    fill: true,
                    pointBackgroundColor: '#0284c7',
                    pointRadius: 5
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: { legend: { display: false } },
                scales: {
                    y: {
                        ticks: { color: textColor, callback: v => '₹' + (v / 100000) + 'L' },
                        grid: { color: gridColor }
                    },
                    x: {
                        ticks: { color: textColor },
                        grid: { display: false }
                    }
                }
            }
        });
    }

    // Buyer Quality Matrix (Calorific vs Moisture)
    const qualCtx = document.getElementById('buyerQualityChart')?.getContext('2d');
    if (qualCtx) {
        destroyChart('buyerQuality');
        activeCharts.buyerQuality = new Chart(qualCtx, {
            type: 'bar',
            data: {
                labels: ['Rice Straw', 'Wheat Stover', 'Bagasse', 'Groundnut', 'Cotton Stalk'],
                datasets: [
                    {
                        label: 'Calorific Value (MJ/kg)',
                        data: [15.2, 16.0, 9.8, 17.5, 15.5],
                        backgroundColor: '#0284c7',
                        borderRadius: 4
                    },
                    {
                        label: 'Moisture Content (%)',
                        data: [12.0, 13.5, 35.0, 9.5, 11.5],
                        backgroundColor: '#38bdf8',
                        borderRadius: 4
                    }
                ]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: { position: 'bottom', labels: { color: textColor, boxWidth: 12, font: { size: 11 } } }
                },
                scales: {
                    y: {
                        ticks: { color: textColor },
                        grid: { color: gridColor }
                    },
                    x: {
                        ticks: { color: textColor },
                        grid: { display: false }
                    }
                }
            }
        });
    }

    // Buyer Carbon Offset
    const carbCtx = document.getElementById('buyerCarbonChart')?.getContext('2d');
    if (carbCtx) {
        destroyChart('buyerCarbon');
        activeCharts.buyerCarbon = new Chart(carbCtx, {
            type: 'line',
            data: {
                labels: ['Nov', 'Dec', 'Jan', 'Feb', 'Mar'],
                datasets: [{
                    label: 'CO₂e Offset (Tons)',
                    data: [42, 78, 115, 154, 185],
                    borderColor: '#1B6A45',
                    backgroundColor: 'rgba(27, 106, 69, 0.15)',
                    tension: 0.35,
                    fill: true,
                    pointBackgroundColor: '#1B6A45',
                    pointRadius: 5
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: { legend: { display: false } },
                scales: {
                    y: {
                        ticks: { color: textColor, callback: v => v + ' T' },
                        grid: { color: gridColor }
                    },
                    x: {
                        ticks: { color: textColor },
                        grid: { display: false }
                    }
                }
            }
        });
    }
}

// 3. Admin Charts (Dark Mode Violet & Amber)
function initAdminCharts() {
    const isDark = isDarkMode();
    const gridColor = isDark ? 'rgba(255, 255, 255, 0.08)' : 'rgba(0, 0, 0, 0.05)';
    const textColor = isDark ? '#E4DDD2' : '#2D3A30';

    // Admin GMV & Daily Volume
    const gmvCtx = document.getElementById('adminGmvChart')?.getContext('2d');
    if (gmvCtx) {
        destroyChart('adminGmv');
        activeCharts.adminGmv = new Chart(gmvCtx, {
            type: 'line',
            data: {
                labels: ['Oct', 'Nov', 'Dec', 'Jan', 'Feb', 'Mar'],
                datasets: [{
                    label: 'Platform GMV (₹ Lakhs)',
                    data: [8.5, 14.2, 22.0, 31.4, 38.0, 42.8],
                    borderColor: '#7c3aed',
                    backgroundColor: 'rgba(124, 58, 237, 0.15)',
                    tension: 0.35,
                    fill: true,
                    pointBackgroundColor: '#7c3aed',
                    pointRadius: 5
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: { legend: { display: false } },
                scales: {
                    y: {
                        ticks: { color: textColor, callback: v => '₹' + v + 'L' },
                        grid: { color: gridColor }
                    },
                    x: {
                        ticks: { color: textColor },
                        grid: { display: false }
                    }
                }
            }
        });
    }

    // Admin Stubble Incidents Prevented
    const burnCtx = document.getElementById('adminBurnChart')?.getContext('2d');
    if (burnCtx) {
        destroyChart('adminBurn');
        activeCharts.adminBurn = new Chart(burnCtx, {
            type: 'bar',
            data: {
                labels: ['Ludhiana', 'Karnal', 'Sangrur', 'Amritsar', 'Patiala'],
                datasets: [
                    {
                        label: 'Intercepted & Traded',
                        data: [48, 36, 29, 22, 18],
                        backgroundColor: '#1B6A45',
                        borderRadius: 4
                    },
                    {
                        label: 'Active Heat Hotspots',
                        data: [1, 2, 1, 0, 1],
                        backgroundColor: '#A63B20',
                        borderRadius: 4
                    }
                ]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        position: 'bottom',
                        labels: { color: textColor, boxWidth: 12, font: { size: 11 } }
                    }
                },
                scales: {
                    y: {
                        ticks: { color: textColor },
                        grid: { color: gridColor }
                    },
                    x: {
                        ticks: { color: textColor },
                        grid: { display: false }
                    }
                }
            }
        });
    }

    // Admin User Ecosystem Doughnut
    const userCtx = document.getElementById('adminUserChart')?.getContext('2d');
    if (userCtx) {
        destroyChart('adminUser');
        activeCharts.adminUser = new Chart(userCtx, {
            type: 'doughnut',
            data: {
                labels: ['Farmers & Co-ops', 'Industrial Buyers', 'Transporters & Logistics', 'Aggregators'],
                datasets: [{
                    data: [1240, 84, 28, 56],
                    backgroundColor: ['#1B6A45', '#0284c7', '#BA7612', '#7c3aed'],
                    borderWidth: 2,
                    borderColor: isDark ? '#131926' : '#ffffff'
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        position: 'bottom',
                        labels: { color: textColor, boxWidth: 12, font: { size: 11 } }
                    }
                }
            }
        });
    }
}

// ==============================================================================
// DEMO INTERACTIVE PORTAL ACTIONS
// ==============================================================================

window.requestStubblePickup = function() {
    const confirmation = confirm('Request automated stubble baler tractor dispatch to your farm coordinates?');
    if (confirmation) {
        if (window.showNotification) {
            window.showNotification('Pickup booked! Tractor Baler unit PB-10 dispatched for harvest collection.', 'success');
        } else {
            alert('Pickup booked! Tractor Baler unit dispatched to your location.');
        }
    }
};

window.exportBuyerEsgReport = function() {
    if (window.showNotification) {
        window.showNotification('Generating certified Scope 3 ESG Audit Ledger (PDF)...', 'info');
    }
    setTimeout(() => {
        alert('ESG Certificate Generated: 185 Metric Tons CO2e Avoidance Verified by Bureau of Energy Efficiency (BEE).');
    }, 800);
};

window.broadcastThermalAlert = function() {
    const confirmed = confirm('Broadcast Emergency Stubble Burning Warning via SMS to 420 registered farmers in Karnal and Sangrur sectors?');
    if (confirmed) {
        if (window.showNotification) {
            window.showNotification('Emergency satellite alert dispatched! Baler subsidies promoted via SMS.', 'success');
        } else {
            alert('SMS broadcast successfully sent to 420 farmers.');
        }
    }
};

window.dispatchSmsAlert = function(location) {
    if (window.showNotification) {
        window.showNotification(`Thermal warning & free baler pickup SMS dispatched to farmers in ${location}.`, 'success');
    } else {
        alert(`Warning SMS sent to farmers in ${location}.`);
    }
};

function escapeHtml(str) {
    if (!str) return '';
    return String(str).replace(/[&<>"']/g, function(m) {
        return {
            '&': '&amp;',
            '<': '&lt;',
            '>': '&gt;',
            '"': '&quot;',
            "'": '&#39;'
        }[m];
    });
}
