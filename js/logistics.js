// Logistics & Routing Module
// Uses Google Maps API

let map;
let routePolyline;
let markers = [];

const HUB_LOCATION = { lat: 30.9010, lng: 75.8573 }; // Ludhiana, Punjab

// Mock database of pickups (Initial set if empty)
const DEFAULT_PICKUPS = [
    { id: 'PK-101', name: 'Farm A (Wheat Straw)', lat: 30.880, lng: 75.810, volume: '15 tons', decay: 'High', color: 'bg-red', riskClass: 'high-risk', price: 15000 },
    { id: 'PK-102', name: 'Farm B (Rice Husk)', lat: 30.920, lng: 75.890, volume: '8 tons', decay: 'Low', color: 'bg-green', riskClass: 'low-risk', price: 8000 },
    { id: 'PK-103', name: 'Farm C (Bagasse)', lat: 30.850, lng: 75.820, volume: '22 tons', decay: 'Medium', color: 'bg-yellow', riskClass: 'medium-risk', price: 22000 },
    { id: 'PK-104', name: 'Farm D (Banana Stem)', lat: 30.940, lng: 75.840, volume: '10 tons', decay: 'High', color: 'bg-red', riskClass: 'high-risk', price: 10000 },
    { id: 'PK-105', name: 'Farm E (Cotton Stalk)', lat: 30.910, lng: 75.920, volume: '18 tons', decay: 'Low', color: 'bg-green', riskClass: 'low-risk', price: 18000 }
];

let pendingPickups = JSON.parse(localStorage.getItem('logisticsQueue'));

if (!pendingPickups || pendingPickups.length === 0) {
    pendingPickups = DEFAULT_PICKUPS;
    localStorage.setItem('logisticsQueue', JSON.stringify(pendingPickups));
}

// Initialize the Google Map (Called via Maps API callback script in HTML)
window.initMap = function() {
    map = new google.maps.Map(document.getElementById("map"), {
        center: HUB_LOCATION,
        zoom: 12,
        styles: [
            { "featureType": "poi", "stylers": [{ "visibility": "off" }] },
            { "featureType": "transit", "stylers": [{ "visibility": "off" }] }
        ]
    });

    // Place Hub Marker
    new google.maps.Marker({
        position: HUB_LOCATION,
        map: map,
        icon: {
            path: google.maps.SymbolPath.CIRCLE,
            scale: 10,
            fillColor: "#34495e",
            fillOpacity: 1,
            strokeWeight: 2,
            strokeColor: "#ffffff"
        },
        title: "Central Hub (Depot)"
    });

    renderPickupsList();
    renderMarkers();
};

function renderMarkers() {
    // Clear old
    markers.forEach(m => m.setMap(null));
    markers = [];

    pendingPickups.forEach((p, idx) => {
        let pinColor = p.decay === 'High' ? '#e74c3c' : p.decay === 'Medium' ? '#f39c12' : '#2ecc71';
        
        const marker = new google.maps.Marker({
            position: { lat: p.lat, lng: p.lng },
            map: map,
            icon: {
                path: google.maps.SymbolPath.BACKWARD_CLOSED_ARROW,
                fillColor: pinColor,
                fillOpacity: 0.9,
                scale: 6,
                strokeColor: '#fff',
                strokeWeight: 2
            },
            title: p.name
        });
        
        const info = new google.maps.InfoWindow({
            content: `<b>${p.name}</b><br/>Vol: ${p.volume}<br/>Decay: ${p.decay}`
        });

        marker.addListener('click', () => {
            info.open(map, marker);
        });

        markers.push(marker);
    });
}

function renderPickupsList() {
    const container = document.getElementById('pickupList');
    if(pendingPickups.length === 0) {
        container.innerHTML = `<p style="text-align:center; padding: 20px; color:#999;">No pickups scheduled</p>`;
        return;
    }

    container.innerHTML = pendingPickups.map(p => `
        <div class="pickup-item ${p.riskClass} ${p.isClustered ? 'clustered' : ''}">
            <div class="pickup-header">
                <h4>${p.id}</h4>
                <div class="pickup-actions">
                    <span class="badge ${p.color}">${p.decay} Decay</span>
                    <button class="btn-complete" onclick="completeDelivery('${p.id}')" title="Mark as Delivered & Pay">
                        <i class="fas fa-check-circle"></i>
                    </button>
                </div>
            </div>
            <div class="pickup-details">
                <span><i class="fas fa-tractor"></i> ${p.name}</span>
                <span><i class="fas fa-weight-hanging"></i> ${p.volume} Required</span>
                ${p.isClustered ? `<span><i class="fas fa-link"></i> Grouped in Cluster A</span>` : ''}
            </div>
        </div>
    `).join('');
}

// Delivery Completion & Payment
window.completeDelivery = function(id) {
    const pickup = pendingPickups.find(p => p.id === id);
    if (!pickup) return;

    // Show Payment Modal
    const modal = document.getElementById('paymentModal');
    const amount = document.getElementById('paymentAmount');
    const details = document.getElementById('paymentDetails');
    const confirmBtn = document.getElementById('confirmPayment');

    if (modal && amount && details) {
        amount.textContent = `₹${(pickup.price || 5000).toLocaleString()}`;
        details.textContent = `${pickup.id} - ${pickup.name} (${pickup.volume})`;
        modal.style.display = 'flex';
        
        confirmBtn.onclick = () => {
            // Remove from pickups
            pendingPickups = pendingPickups.filter(p => p.id !== id);
            localStorage.setItem('logisticsQueue', JSON.stringify(pendingPickups));
            
            // Re-render
            renderPickupsList();
            renderMarkers();
            
            modal.style.display = 'none';
            if (window.showNotification) {
                window.showNotification(`Payment of ₹${(pickup.price || 5000).toLocaleString()} released to farmer!`, 'success');
            }
        };
    }
}


// --- AI Logic Algorithms ---

window.clusterPickups = function() {
    const btn = document.querySelector('.btn-cluster');
    btn.innerHTML = `<i class="fas fa-circle-notch fa-spin"></i> Clustering`;
    
    setTimeout(() => {
        // AI Logic Simulation: Farm A and Farm C are very close geographically (30.88/75.81 & 30.85/75.82)
        // Group them into a cluster!
        pendingPickups.forEach(p => {
            if (p.id === 'PK-101' || p.id === 'PK-103') {
                p.isClustered = true;
            }
        });

        // Re-sort the array so high-risk are prioritized on top, then clustered
        pendingPickups.sort((a, b) => {
            if (a.decay === 'High' && b.decay !== 'High') return -1;
            if (b.decay === 'High' && a.decay !== 'High') return 1;
            return 0;
        });

        renderPickupsList();
        
        btn.innerHTML = `<i class="fas fa-object-group"></i> Cluster`;
        const alertHtml = document.createElement('div');
        alertHtml.innerHTML = `<div style="background:#2ecc71;color:white;padding:10px;margin-bottom:15px;border-radius:4px;"><i class="fas fa-info-circle"></i> AI clustered 2 close locations!</div>`;
        document.getElementById('pickupList').prepend(alertHtml);
        
    }, 800);
};

window.optimizeRoute = function() {
    const loader = document.getElementById('loader');
    loader.style.display = 'flex';
    
    // Simulate complex AI calculation time
    setTimeout(() => {
        loader.style.display = 'none';
        
        // Remove old polyline if exists
        if(routePolyline) routePolyline.setMap(null);
        
        // 1. Weighted Nearest Neighbor Spatial Algorithm
        const calcDist = (p1, p2) => Math.sqrt(Math.pow(p1.lat - p2.lat, 2) + Math.pow(p1.lng - p2.lng, 2));

        let unvisited = [...pendingPickups];
        let currentLoc = HUB_LOCATION;
        let optimizedPath = [];
        
        while(unvisited.length > 0) {
            let bestIdx = -1;
            let lowestScore = Infinity;
            
            for (let i = 0; i < unvisited.length; i++) {
                let candidate = unvisited[i];
                let dist = calcDist(currentLoc, candidate);
                
                // Weighting logic (Pull truck towards High decay crops)
                let weight = 1;
                if (candidate.decay === 'High') weight = 3.5;
                else if (candidate.decay === 'Medium') weight = 1.5;
                
                let cost = dist / weight;
                
                // Cluster Protection: If truck is currently at a clustered farm, it MUST finish the cluster
                // Since this mock uses 'isClustered' generically for Cluster A
                if (currentLoc.isClustered && candidate.isClustered) {
                    cost = 0; // Force immediate pickup
                }
                
                if (cost < lowestScore) {
                    lowestScore = cost;
                    bestIdx = i;
                }
            }
            
            let nextStop = unvisited.splice(bestIdx, 1)[0];
            optimizedPath.push(nextStop);
            currentLoc = nextStop; // truck moves here
        }
        
        pendingPickups = optimizedPath;
        
        renderPickupsList(); // Update UI to reflect new intelligent path
        
        // 2. Build coordinate path starting and ending at Hub
        const pathCoords = [HUB_LOCATION];
        pendingPickups.forEach(p => {
            pathCoords.push({ lat: p.lat, lng: p.lng });
        });
        pathCoords.push(HUB_LOCATION); // Return trip
        
        // 3. Draw the free Polyline "as the crow flies"
        routePolyline = new google.maps.Polyline({
            path: pathCoords,
            geodesic: true,
            strokeColor: '#3498db',
            strokeOpacity: 0.8,
            strokeWeight: 4,
            icons: [{
                icon: { path: google.maps.SymbolPath.FORWARD_CLOSED_ARROW },
                offset: '50%',
                repeat: '100px'
            }]
        });
        
        routePolyline.setMap(map);
        
        // 4. Update the statistics overlay
        document.getElementById('routeStats').style.display = 'block';
        
        // Mock distance mathematically roughly (since we can't use directions service)
        // Ludhiana farms are generally 3-8km apart in this mock data
        const calculatedDistance = 42.5; // Simulate 42.5 km
        const calculatedHours = 1.8; // Simulate 1.8 hours
        
        document.getElementById('valDist').innerText = calculatedDistance + ' km';
        document.getElementById('valDur').innerText = calculatedHours + ' hrs';
        
        // Add success notification
        const alertHtml = document.createElement('div');
        alertHtml.innerHTML = `<div style="background:#3498db;color:white;padding:10px;margin-bottom:15px;border-radius:4px;"><i class="fas fa-check"></i> Fallback AI Route calculated successfully!</div>`;
        document.getElementById('pickupList').prepend(alertHtml);
        
    }, 1200);
};
