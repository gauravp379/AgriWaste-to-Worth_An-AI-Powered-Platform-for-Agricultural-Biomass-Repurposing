// Main JavaScript - Core Functionality
// =======================

// Initialize application
document.addEventListener('DOMContentLoaded', function() {
    initializeApp();
    initializeNavigation();
    initializeNotifications();
    updateCartBadge();
});

// Global state management
const AppState = {
    currentUser: null,
    cart: [],
    notifications: [],
    
    init() {
        // Load from localStorage
        this.currentUser = JSON.parse(localStorage.getItem('currentUser')) || null;
        this.cart = JSON.parse(localStorage.getItem('cart')) || [];
        this.notifications = JSON.parse(localStorage.getItem('notifications')) || [];
        this.logisticsQueue = JSON.parse(localStorage.getItem('logisticsQueue')) || [];
    },
    
    saveUser(user) {
        this.currentUser = user;
        localStorage.setItem('currentUser', JSON.stringify(user));
    },
    
    saveCart() {
        localStorage.setItem('cart', JSON.stringify(this.cart));
    },
    
    saveLogistics() {
        localStorage.setItem('logisticsQueue', JSON.stringify(this.logisticsQueue));
    },
    
    saveNotifications() {
        localStorage.setItem('notifications', JSON.stringify(this.notifications));
    }
};

// Initialize app
function initializeApp() {
    AppState.init();
    updateUserUI();
    initializeThemeToggles();
    
    // Animate stats on homepage
    animateStats();
}

// Theme & Sunlight Contrast Toggles
function initializeThemeToggles() {
    const themeToggleBtn = document.getElementById('themeToggleBtn');
    const themeIcon = document.getElementById('themeIcon');
    const savedTheme = localStorage.getItem('agriwaste_theme');
    
    if (savedTheme === 'dark') {
        document.body.classList.add('dark-mode');
        document.body.classList.add('dark-theme');
        if (themeIcon) {
            themeIcon.classList.remove('fa-moon');
            themeIcon.classList.add('fa-sun');
        }
    }

    themeToggleBtn?.addEventListener('click', () => {
        document.body.classList.toggle('dark-mode');
        document.body.classList.toggle('dark-theme');
        const isDark = document.body.classList.contains('dark-mode');
        localStorage.setItem('agriwaste_theme', isDark ? 'dark' : 'light');
        if (themeIcon) {
            if (isDark) {
                themeIcon.classList.remove('fa-moon');
                themeIcon.classList.add('fa-sun');
            } else {
                themeIcon.classList.remove('fa-sun');
                themeIcon.classList.add('fa-moon');
            }
        }
        if (window.showNotification) {
            window.showNotification(isDark ? 'Dark Theme activated' : 'Light Theme activated', 'info');
        }
    });

    const sunlightBtn = document.getElementById('sunlightContrastBtn');
    const savedSunlight = localStorage.getItem('agriwaste_sunlight');
    if (savedSunlight === 'active') {
        document.body.classList.add('theme-sunlight-contrast');
        document.body.classList.add('sunlight-contrast');
    }

    sunlightBtn?.addEventListener('click', () => {
        document.body.classList.toggle('theme-sunlight-contrast');
        document.body.classList.toggle('sunlight-contrast');
        const isActive = document.body.classList.contains('theme-sunlight-contrast');
        localStorage.setItem('agriwaste_sunlight', isActive ? 'active' : 'inactive');
        if (window.showNotification) {
            window.showNotification(isActive ? 'Outdoor Sunlight Mode Enabled' : 'Standard Contrast Mode Restored', 'info');
        }
    });
}

// Navigation functionality
function initializeNavigation() {
    const hamburger = document.getElementById('hamburger');
    const navMenu = document.querySelector('.nav-menu');
    
    if (hamburger) {
        hamburger.addEventListener('click', () => {
            navMenu.classList.toggle('active');
            hamburger.classList.toggle('active');
        });
    }
    
    // Close menu when clicking outside
    document.addEventListener('click', (e) => {
        if (!e.target.closest('.navbar')) {
            navMenu?.classList.remove('active');
        }
    });
}

// Update user interface based on auth status
function updateUserUI() {
    const loginBtn = document.getElementById('loginBtn');
    const signupBtn = document.getElementById('signupBtn');
    const userMenu = document.getElementById('userMenu');
    const userRoleBadge = document.getElementById('userRoleBadge');
    const logoutBtn = document.getElementById('logoutBtn');
    
    if (AppState.currentUser) {
        // User is logged in
        if (loginBtn) loginBtn.style.display = 'none';
        if (signupBtn) signupBtn.style.display = 'none';
        if (userMenu) {
            userMenu.style.display = 'flex';
            const userName = userMenu.querySelector('.user-name');
            if (userName) userName.textContent = AppState.currentUser.name;
            if (userRoleBadge) userRoleBadge.textContent = (AppState.currentUser.userType || '').toUpperCase();
        }
        logoutBtn?.addEventListener('click', () => window.logout && window.logout());
    } else {
        // User is not logged in
        if (loginBtn) loginBtn.style.display = 'inline-block';
        if (signupBtn) signupBtn.style.display = 'inline-block';
        if (userMenu) userMenu.style.display = 'none';
    }
}

// Cart functionality
function updateCartBadge() {
    const cartBadge = document.getElementById('cartBadge');
    if (cartBadge) {
        const itemCount = AppState.cart.reduce((sum, item) => sum + (item.quantity || 1), 0);
        cartBadge.textContent = itemCount;
        cartBadge.style.display = itemCount > 0 ? 'block' : 'none';
    }
}

function addToCart(item) {
    const existingItem = AppState.cart.find(i => i.id === item.id);
    
    if (existingItem) {
        existingItem.quantity = (existingItem.quantity || 1) + 1;
    } else {
        AppState.cart.push({ ...item, quantity: 1 });
    }
    
    AppState.saveCart();
    updateCartBadge();
    showNotification('Item added to cart successfully!', 'success');
}

function removeFromCart(itemId) {
    AppState.cart = AppState.cart.filter(item => item.id !== itemId);
    AppState.saveCart();
    updateCartBadge();
    loadCartItems();
}

function loadCartItems() {
    const cartContent = document.getElementById('cartContent');
    const cartTotal = document.getElementById('cartTotal');

    if (!cartContent) return;

    if (AppState.cart.length === 0) {
        cartContent.innerHTML = `
            <div class="cart-empty-state">
                <div class="cart-empty-icon"><i class="fas fa-shopping-basket"></i></div>
                <p class="cart-empty-title">Your cart is empty</p>
                <p class="cart-empty-sub">Add items from the marketplace to get started</p>
            </div>`;
        if (cartTotal) cartTotal.textContent = '₹0';
        return;
    }

    let total = 0;
    cartContent.innerHTML = '';

    AppState.cart.forEach(item => {
        const itemTotal = item.price * (item.quantity || 1);
        total += itemTotal;
        const qty = item.quantity || 1;

        const cartItemHTML = `
            <div class="cart-item" data-id="${item.id}">
                <div class="cart-item-image">
                    <i class="fas fa-seedling"></i>
                </div>
                <div class="cart-item-details">
                    <div class="cart-item-title">${item.name}</div>
                    <div class="cart-item-seller"><i class="fas fa-store-alt"></i> ${item.seller || 'Verified Supplier'}</div>
                    <div class="cart-item-price">₹${item.price.toLocaleString()} <span class="per-unit">/ton</span></div>
                    <div class="cart-item-controls">
                        <button class="qty-btn" onclick="changeCartQty('${item.id}', -1)"><i class="fas fa-minus"></i></button>
                        <span class="qty-val">${qty} ton${qty>1?'s':''}</span>
                        <button class="qty-btn" onclick="changeCartQty('${item.id}', 1)"><i class="fas fa-plus"></i></button>
                        <button class="cart-item-remove" onclick="removeFromCart('${item.id}')"><i class="fas fa-trash-alt"></i> Remove</button>
                    </div>
                    <div class="cart-item-subtotal">Subtotal: <strong>₹${itemTotal.toLocaleString()}</strong></div>
                </div>
            </div>
        `;
        cartContent.innerHTML += cartItemHTML;
    });

    if (cartTotal) cartTotal.textContent = `₹${total.toLocaleString()}`;
}

// ─── Change cart quantity ────────────────────────────────────────────
window.changeCartQty = function(itemId, delta) {
    const item = AppState.cart.find(i => i.id === itemId);
    if (!item) return;
    item.quantity = Math.max(1, (item.quantity || 1) + delta);
    AppState.saveCart();
    updateCartBadge();
    loadCartItems();
};

// ─── Open Checkout Modal ──────────────────────────────────────────────
window.openCheckoutModal = function() {
    if (AppState.cart.length === 0) {
        showNotification('Your cart is empty!', 'error');
        return;
    }
    if (!AppState.currentUser) {
        showNotification('Please login to continue', 'warning');
        document.getElementById('cartSidebar')?.classList.remove('active');
        setTimeout(() => document.getElementById('loginBtn')?.click(), 400);
        return;
    }
    const modal = document.getElementById('checkoutModal');
    if (modal) {
        // Populate order summary in modal
        const total = AppState.cart.reduce((s, i) => s + i.price * (i.quantity || 1), 0);
        const summaryEl = document.getElementById('checkoutOrderSummary');
        if (summaryEl) {
            summaryEl.innerHTML = AppState.cart.map(item => `
                <div class="co-item">
                    <span>${item.name} × ${item.quantity || 1} ton${(item.quantity||1)>1?'s':''}</span>
                    <strong>₹${(item.price*(item.quantity||1)).toLocaleString()}</strong>
                </div>
            `).join('') + `
                <div class="co-total">
                    <span>Total Amount</span>
                    <strong>₹${total.toLocaleString()}</strong>
                </div>`;
        }
        document.getElementById('checkoutTotalAmt').textContent = `₹${total.toLocaleString()}`;
        modal.classList.add('active');
    }
};

// ─── Razorpay Payment ────────────────────────────────────────────────
window.initiateRazorpayPayment = function() {
    const fullName = document.getElementById('co_fullname')?.value.trim();
    const phone    = document.getElementById('co_phone')?.value.trim();
    const email    = document.getElementById('co_email')?.value.trim();
    const addr1    = document.getElementById('co_address1')?.value.trim();
    const city     = document.getElementById('co_city')?.value.trim();
    const state    = document.getElementById('co_state')?.value.trim();
    const pincode  = document.getElementById('co_pincode')?.value.trim();

    if (!fullName || !phone || !email || !addr1 || !city || !state || !pincode) {
        showNotification('Please fill in all address fields.', 'error');
        return;
    }
    if (!/^[6-9]\d{9}$/.test(phone)) {
        showNotification('Enter a valid 10-digit Indian mobile number.', 'error');
        return;
    }
    if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email)) {
        showNotification('Enter a valid email address.', 'error');
        return;
    }
    if (!/^\d{6}$/.test(pincode)) {
        showNotification('Enter a valid 6-digit PIN code.', 'error');
        return;
    }

    const total = AppState.cart.reduce((s, i) => s + i.price * (i.quantity || 1), 0);
    const amountPaise = total * 100; // Razorpay uses paise

    const deliveryAddress = `${addr1}, ${city}, ${state} - ${pincode}`;

    const options = {
        key: 'rzp_test_Si2jYQPhVrCNhZ',
        amount: amountPaise,
        currency: 'INR',
        name: 'AgriWaste to Worth',
        description: `Order for ${AppState.cart.length} item(s)`,
        image: 'https://via.placeholder.com/60x60.png?text=AW',
        handler: function(response) {
            onPaymentSuccess(response, {
                name: fullName, phone, email,
                address: deliveryAddress
            });
        },
        prefill: {
            name: fullName,
            email: email,
            contact: phone
        },
        notes: {
            delivery_address: deliveryAddress
        },
        theme: {
            color: '#2ecc71'
        },
        modal: {
            ondismiss: function() {
                showNotification('Payment cancelled. Your cart is safe.', 'info');
            }
        }
    };

    if (typeof Razorpay === 'undefined') {
        showNotification('Payment gateway not loaded. Please check your internet connection.', 'error');
        return;
    }
    const rzp = new Razorpay(options);
    rzp.on('payment.failed', function(resp) {
        showNotification('Payment failed: ' + (resp.error?.description || 'Unknown error'), 'error');
    });
    rzp.open();
};

// ─── On Payment Success ───────────────────────────────────────────────
function onPaymentSuccess(razorpayResponse, userDetails) {
    const total = AppState.cart.reduce((s, i) => s + i.price * (i.quantity || 1), 0);
    const txnId = 'TXN' + Date.now();
    const orderId = 'ORD-' + Math.random().toString(36).substr(2,8).toUpperCase();

    // Save transaction
    const transaction = {
        id: txnId,
        orderId,
        razorpay_payment_id: razorpayResponse.razorpay_payment_id,
        items: [...AppState.cart],
        total,
        deliveryAddress: userDetails.address,
        customerName: userDetails.name,
        customerEmail: userDetails.email,
        customerPhone: userDetails.phone,
        date: new Date().toISOString(),
        status: 'paid'
    };
    const transactions = JSON.parse(localStorage.getItem('transactions')) || [];
    transactions.unshift(transaction);
    localStorage.setItem('transactions', JSON.stringify(transactions));

    // Sync with backend API
    try {
        if (window.API && typeof API.createTransaction === 'function') {
            API.createTransaction(transaction).catch(err => console.warn('Failed to sync transaction to backend:', err));
        }
    } catch(err) {
        console.warn('API transaction sync error:', err);
    }

    // Add to logistics queue
    const newPickups = AppState.cart.map(item => ({
        id: `PK-${Math.floor(Math.random() * 900) + 100}`,
        name: `${userDetails.name}'s ${item.name}`,
        lat: 30.85 + (Math.random() * 0.1),
        lng: 75.80 + (Math.random() * 0.1),
        volume: `${item.quantity} tons`,
        decay: Math.random() > 0.5 ? 'High' : 'Medium',
        price: item.price * item.quantity,
        color: Math.random() > 0.5 ? 'bg-red' : 'bg-yellow',
        riskClass: Math.random() > 0.5 ? 'high-risk' : 'medium-risk',
        timestamp: new Date().toISOString()
    }));
    AppState.logisticsQueue = [...(AppState.logisticsQueue || []), ...newPickups];
    AppState.saveLogistics();

    // Clear cart
    AppState.cart = [];
    AppState.saveCart();
    updateCartBadge();

    // Close modals
    document.getElementById('checkoutModal')?.classList.remove('active');
    document.getElementById('cartSidebar')?.classList.remove('active');

    // Show success screen
    showOrderSuccessModal(orderId, razorpayResponse.razorpay_payment_id, total, userDetails.address);
    addNotification('Payment Successful 🎉', `Order ${orderId} paid ₹${total.toLocaleString()} — delivery to ${userDetails.address}`, 'success');
}

// ─── Order Success Modal ──────────────────────────────────────────────
function showOrderSuccessModal(orderId, paymentId, total, address) {
    const existing = document.getElementById('orderSuccessModal');
    if (existing) existing.remove();

    const m = document.createElement('div');
    m.id = 'orderSuccessModal';
    m.className = 'modal active';
    m.innerHTML = `
        <div class="modal-content order-success-modal">
            <div class="success-anim">
                <div class="success-circle"><i class="fas fa-check"></i></div>
            </div>
            <h2 class="success-title">Payment Successful! 🎉</h2>
            <p class="success-sub">Thank you for your order. Your items will be dispatched soon.</p>
            <div class="success-details">
                <div class="sdet-row"><span>Order ID</span><strong>${orderId}</strong></div>
                <div class="sdet-row"><span>Payment ID</span><strong>${paymentId}</strong></div>
                <div class="sdet-row"><span>Amount Paid</span><strong>₹${total.toLocaleString()}</strong></div>
                <div class="sdet-row"><span>Delivery To</span><strong>${address}</strong></div>
            </div>
            <div class="success-actions">
                <button class="btn-primary" onclick="document.getElementById('orderSuccessModal').remove(); window.location.href='dashboard.html'">
                    <i class="fas fa-chart-line"></i> View Dashboard
                </button>
                <button class="btn-secondary" onclick="document.getElementById('orderSuccessModal').remove()">
                    Continue Shopping
                </button>
            </div>
        </div>
    `;
    document.body.appendChild(m);
    m.addEventListener('click', e => { if (e.target === m) m.remove(); });
}

// Cart sidebar toggle
document.getElementById('cartBtn')?.addEventListener('click', () => {
    const cartSidebar = document.getElementById('cartSidebar');
    if (cartSidebar) {
        cartSidebar.classList.toggle('active');
        loadCartItems();
    }
});

document.querySelector('.close-sidebar')?.addEventListener('click', () => {
    document.getElementById('cartSidebar')?.classList.remove('active');
});

// Notification system
function initializeNotifications() {
    const notifBtn = document.getElementById('notificationBtn');
    const notifBadge = document.getElementById('notifBadge');
    
    // Load initial notifications
    if (AppState.notifications.length === 0) {
        AppState.notifications = [
            {
                id: Date.now(),
                title: 'Welcome!',
                message: 'Start exploring the marketplace',
                type: 'info',
                read: false,
                timestamp: new Date()
            }
        ];
        AppState.saveNotifications();
    }
    
    updateNotificationBadge();
    
    notifBtn?.addEventListener('click', showNotifications);
}

function updateNotificationBadge() {
    const notifBadge = document.getElementById('notifBadge');
    if (notifBadge) {
        const unreadCount = AppState.notifications.filter(n => !n.read).length;
        notifBadge.textContent = unreadCount;
        notifBadge.style.display = unreadCount > 0 ? 'block' : 'none';
    }
}

function addNotification(title, message, type = 'info') {
    const notification = {
        id: Date.now(),
        title,
        message,
        type,
        read: false,
        timestamp: new Date()
    };
    
    AppState.notifications.unshift(notification);
    AppState.saveNotifications();
    updateNotificationBadge();
}

function showNotifications() {
    // Create modal for notifications
    const modal = document.createElement('div');
    modal.className = 'modal active';
    modal.innerHTML = `
        <div class="modal-content">
            <span class="close">&times;</span>
            <h2>Notifications</h2>
            <div id="notificationsList" style="max-height:400px;overflow-y:auto;">
                ${AppState.notifications.map(n => `
                    <div class="notification-item" style="padding:1rem;border-bottom:1px solid #ddd;${n.read ? '' : 'background:#f0f8ff;'}">
                        <h4>${n.title}</h4>
                        <p>${n.message}</p>
                        <small>${new Date(n.timestamp).toLocaleString()}</small>
                    </div>
                `).join('')}
            </div>
        </div>
    `;
    
    document.body.appendChild(modal);
    
    modal.querySelector('.close').addEventListener('click', () => {
        modal.remove();
    });
    
    // Mark all as read
    AppState.notifications.forEach(n => n.read = true);
    AppState.saveNotifications();
    updateNotificationBadge();
}

// Toast notifications
function showNotification(message, type = 'success') {
    const toast = document.createElement('div');
    toast.style.cssText = `
        position: fixed;
        top: 100px;
        right: 20px;
        background: ${type === 'success' ? '#27ae60' : type === 'error' ? '#e74c3c' : '#3498db'};
        color: white;
        padding: 1rem 1.5rem;
        border-radius: 8px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.15);
        z-index: 10000;
        animation: slideIn 0.3s ease;
    `;
    toast.textContent = message;
    
    document.body.appendChild(toast);
    
    setTimeout(() => {
        toast.style.animation = 'slideOut 0.3s ease';
        setTimeout(() => toast.remove(), 300);
    }, 3000);
}

// Animate stats on homepage
function animateStats() {
    // Derive from real data
    const transactions = JSON.parse(localStorage.getItem('transactions')) || [];
    const users = JSON.parse(localStorage.getItem('users')) || [];

    // Waste processed = sum of quantities in completed transactions
    let totalWasteTons = 0;
    transactions.forEach(t => {
        if (t.status === 'completed' && Array.isArray(t.items)) {
            totalWasteTons += t.items.reduce((s, i) => s + (i.quantity || 1), 0);
        }
    });

    const activeUsersCount = users.length;
    const co2FactorPerTon = 2.5; // conservative estimate tons CO2 avoided per ton biomass
    const co2SavedTons = Math.round(totalWasteTons * co2FactorPerTon);

    const statElements = [
        { id: 'wasteProcessed', target: Math.max(0, Math.floor(totalWasteTons)) },
        { id: 'activeUsers', target: Math.max(0, activeUsersCount) },
        { id: 'co2Saved', target: Math.max(0, co2SavedTons) }
    ];
    
    statElements.forEach(({ id, target }) => {
        const element = document.getElementById(id);
        if (!element) return;
        
        let current = 0;
        const increment = target / 50;
        const timer = setInterval(() => {
            current += increment;
            if (current >= target) {
                element.textContent = target.toLocaleString() + '+';
                clearInterval(timer);
            } else {
                element.textContent = Math.floor(current).toLocaleString() + '+';
            }
        }, 30);
    });
}

// Modal handlers
document.addEventListener('click', (e) => {
    if (e.target.classList.contains('modal')) {
        e.target.classList.remove('active');
    }
    
    if (e.target.classList.contains('close')) {
        e.target.closest('.modal')?.classList.remove('active');
    }
});

// Get started button
document.getElementById('getStartedBtn')?.addEventListener('click', () => {
    if (AppState.currentUser) {
        window.location.href = 'marketplace.html';
    } else {
        document.getElementById('loginBtn')?.click();
    }
});

// Checkout button → open address + payment modal
document.getElementById('checkoutBtn')?.addEventListener('click', () => {
    window.openCheckoutModal();
});

// Utility functions
function formatDate(date) {
    return new Date(date).toLocaleDateString('en-IN', {
        year: 'numeric',
        month: 'short',
        day: 'numeric'
    });
}

function formatCurrency(amount) {
    return new Intl.NumberFormat('en-IN', {
        style: 'currency',
        currency: 'INR',
        minimumFractionDigits: 0
    }).format(amount);
}

// Export for use in other modules
window.AppState = AppState;
window.addToCart = addToCart;
window.removeFromCart = removeFromCart;
window.showNotification = showNotification;
window.addNotification = addNotification;
window.formatDate = formatDate;
window.formatCurrency = formatCurrency;

// Add CSS animations
const style = document.createElement('style');
style.textContent = `
    @keyframes slideIn {
        from { transform: translateX(400px); opacity: 0; }
        to { transform: translateX(0); opacity: 1; }
    }
    @keyframes slideOut {
        from { transform: translateX(0); opacity: 1; }
        to { transform: translateX(400px); opacity: 0; }
    }
`;
document.head.appendChild(style);
