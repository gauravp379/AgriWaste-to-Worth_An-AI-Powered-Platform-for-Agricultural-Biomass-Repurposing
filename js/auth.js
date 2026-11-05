
// Client-Side Web Crypto SHA-256 Password Hashing (Demo Security Enhancement)
async function hashPassword(plainText) {
    if (!plainText || !window.crypto || !window.crypto.subtle) return plainText;
    try {
        const msgBuffer = new TextEncoder().encode(plainText);
        const hashBuffer = await crypto.subtle.digest('SHA-256', msgBuffer);
        const hashArray = Array.from(new Uint8Array(hashBuffer));
        return hashArray.map(b => b.toString(16).padStart(2, '0')).join('');
    } catch(e) {
        return plainText;
    }
}

// Authentication Module with Distinct Role-Based Portals (Farmer, Buyer, Admin)
// ==============================================================================

const DEFAULT_USERS = [
    {
        id: 'USR_FARMER_101',
        name: 'Farmer Ramesh Singh',
        email: 'farmer@agriwaste.com',
        password: 'farmer123',
        userType: 'farmer',
        roleTitle: 'Verified Agricultural Producer',
        location: 'Ludhiana, Punjab',
        organization: 'Punjab Kisan Cooperative',
        avatar: 'https://ui-avatars.com/api/?name=Ramesh+Singh&background=059669&color=fff'
    },
    {
        id: 'USR_BUYER_201',
        name: 'GreenGrid Bio-Power Ltd',
        email: 'buyer@biocorp.com',
        password: 'buyer123',
        userType: 'buyer',
        roleTitle: 'Industrial Biomass Off-Taker',
        location: 'Gurugram, Haryana',
        organization: 'GreenGrid Energy Group',
        gstin: '03AABCG1234F1Z9',
        avatar: 'https://ui-avatars.com/api/?name=GreenGrid+BioPower&background=0284c7&color=fff'
    },
    {
        id: 'USR_ADMIN_301',
        name: 'Platform Operations Admin',
        email: 'admin@agriwaste.com',
        password: 'admin123',
        userType: 'admin',
        roleTitle: 'Master Platform Controller',
        location: 'HQ New Delhi',
        organization: 'AgriWaste Regulatory Council',
        accessLevel: 'SuperAdmin Tier-1',
        avatar: 'https://ui-avatars.com/api/?name=Admin+Controller&background=7c3aed&color=fff'
    }
];

// Active role in modal
let activeModalRole = 'farmer';

document.addEventListener('DOMContentLoaded', function() {
    seedDefaultUsers();
    initializeAuth();
    enhanceAuthModalUI();
});

function seedDefaultUsers() {
    let users = [];
    try {
        users = JSON.parse(localStorage.getItem('users')) || [];
    } catch(e) {
        users = [];
    }
    
    // Add default users if missing
    DEFAULT_USERS.forEach(defUser => {
        if (!users.some(u => u.email.toLowerCase() === defUser.email.toLowerCase())) {
            users.push(defUser);
        }
    });
    localStorage.setItem('users', JSON.stringify(users));

    // If no currentUser exists, default to farmer for immediate experience
    if (!localStorage.getItem('currentUser')) {
        const defaultFarmer = { ...DEFAULT_USERS[0] };
        delete defaultFarmer.password;
        if (window.AppState && typeof window.AppState.saveUser === 'function') {
            window.AppState.saveUser(defaultFarmer);
        } else {
            localStorage.setItem('currentUser', JSON.stringify(defaultFarmer));
        }
    }
}

function initializeAuth() {
    const loginBtn = document.getElementById('loginBtn');
    const signupBtn = document.getElementById('signupBtn');
    const logoutBtn = document.getElementById('logoutBtn');
    const authModal = document.getElementById('authModal');
    const showSignupLink = document.getElementById('showSignup');
    const showLoginLink = document.getElementById('showLogin');
    const loginForm = document.getElementById('loginForm');
    const signupForm = document.getElementById('signupForm');
    const closeBtn = authModal?.querySelector('.close');

    // Show login modal
    loginBtn?.addEventListener('click', (e) => {
        e.preventDefault();
        openAuthModal('login');
    });

    // Show signup modal
    signupBtn?.addEventListener('click', (e) => {
        e.preventDefault();
        openAuthModal('signup');
    });

    // Switch between forms
    showSignupLink?.addEventListener('click', (e) => {
        e.preventDefault();
        switchToSignup();
    });

    showLoginLink?.addEventListener('click', (e) => {
        e.preventDefault();
        switchToLogin();
    });

    // Close modal
    closeBtn?.addEventListener('click', () => {
        authModal.classList.remove('active');
    });

    window.addEventListener('click', (e) => {
        if (e.target === authModal) {
            authModal.classList.remove('active');
        }
    });

    // Handle form submit
    loginForm?.querySelector('form')?.addEventListener('submit', handleLogin);
    signupForm?.querySelector('form')?.addEventListener('submit', handleSignup);

    // Logout
    if (logoutBtn) {
        logoutBtn.addEventListener('click', logout);
    }
}

function openAuthModal(mode = 'login', initialRole = null) {
    const authModal = document.getElementById('authModal');
    if (!authModal) return;

    if (initialRole) {
        activeModalRole = initialRole;
    }
    enhanceAuthModalUI();
    setModalRole(activeModalRole);

    authModal.classList.add('active');
    if (mode === 'login') {
        switchToLogin();
    } else {
        switchToSignup();
    }
}

function switchToLogin() {
    const loginForm = document.getElementById('loginForm');
    const signupForm = document.getElementById('signupForm');
    loginForm?.classList.remove('hidden');
    signupForm?.classList.add('hidden');
}

function switchToSignup() {
    const loginForm = document.getElementById('loginForm');
    const signupForm = document.getElementById('signupForm');
    loginForm?.classList.add('hidden');
    signupForm?.classList.remove('hidden');
}

// Enhances modal DOM with role selector tabs, role custom styling, and 1-click test logins
function enhanceAuthModalUI() {
    const authContainer = document.querySelector('.auth-container');
    if (!authContainer) return;

    // Check if role tabs already injected
    if (!document.getElementById('authRoleTabs')) {
        const tabsHtml = `
            <div id="authRoleTabs" class="auth-role-tabs">
                <button type="button" class="role-tab active" data-role="farmer" onclick="setModalRole('farmer')">
                    <i class="fas fa-seedling"></i>
                    <span>Farmer (Kisan)</span>
                </button>
                <button type="button" class="role-tab" data-role="buyer" onclick="setModalRole('buyer')">
                    <i class="fas fa-industry"></i>
                    <span>Industrial Buyer</span>
                </button>
                <button type="button" class="role-tab" data-role="admin" onclick="setModalRole('admin')">
                    <i class="fas fa-shield-halved"></i>
                    <span>Admin</span>
                </button>
            </div>
            
            <div id="roleNoticeBanner" class="role-notice-banner farmer-banner">
                <i class="fas fa-leaf notice-icon"></i>
                <div class="notice-text">
                    <strong id="roleNoticeTitle">Kisan Portal Login</strong>
                    <p id="roleNoticeDesc">Sell paddy straw, sugarcane bagasse, and stubble at transparent market prices.</p>
                </div>
            </div>
        `;
        authContainer.insertAdjacentHTML('afterbegin', tabsHtml);
    }

    // Check if 1-click quick login box is already injected
    if (!document.getElementById('demoQuickLoginBox')) {
        const demoBoxHtml = `
            <div id="demoQuickLoginBox" class="demo-quick-login-box">
                <div class="demo-box-header">
                    <i class="fas fa-bolt text-amber"></i>
                    <span>Quick 1-Click Evaluation Login:</span>
                </div>
                <div class="demo-btn-row">
                    <button type="button" class="btn-demo-quick demo-farmer" onclick="quickLoginAs('farmer')">
                        <i class="fas fa-tractor"></i> As Farmer
                    </button>
                    <button type="button" class="btn-demo-quick demo-buyer" onclick="quickLoginAs('buyer')">
                        <i class="fas fa-building"></i> As Buyer
                    </button>
                    <button type="button" class="btn-demo-quick demo-admin" onclick="quickLoginAs('admin')">
                        <i class="fas fa-user-shield"></i> As Admin
                    </button>
                </div>
            </div>
        `;
        authContainer.insertAdjacentHTML('beforeend', demoBoxHtml);
    }

    // Role-specific signup extra fields
    const signupForm = document.getElementById('signupForm');
    if (signupForm && !document.getElementById('roleExtraFields')) {
        const extraFieldsHtml = `
            <div id="roleExtraFields" class="form-group" style="margin-top:0.5rem;">
                <label id="roleExtraLabel">Farm Location / District</label>
                <input type="text" id="signupExtraField" placeholder="e.g. Ludhiana, Punjab">
            </div>
        `;
        const submitBtn = signupForm.querySelector('button[type="submit"]');
        if (submitBtn) {
            submitBtn.insertAdjacentHTML('beforebegin', extraFieldsHtml);
        }
    }
}

// Switches role state in modal and updates styling
window.setModalRole = function(role) {
    activeModalRole = role;

    // Update active tab buttons
    const tabs = document.querySelectorAll('.auth-role-tabs .role-tab');
    tabs.forEach(tab => {
        if (tab.getAttribute('data-role') === role) {
            tab.classList.add('active');
        } else {
            tab.classList.remove('active');
        }
    });

    const modalContent = document.querySelector('.modal-content');
    if (modalContent) {
        modalContent.classList.remove('theme-farmer-modal', 'theme-buyer-modal', 'theme-admin-modal');
        modalContent.classList.add(`theme-${role}-modal`);
    }

    // Update banner text
    const banner = document.getElementById('roleNoticeBanner');
    const title = document.getElementById('roleNoticeTitle');
    const desc = document.getElementById('roleNoticeDesc');
    const icon = banner?.querySelector('.notice-icon');
    const extraLabel = document.getElementById('roleExtraLabel');
    const extraInput = document.getElementById('signupExtraField');

    if (banner) {
        banner.className = `role-notice-banner ${role}-banner`;
    }

    if (role === 'farmer') {
        if (title) title.textContent = 'Kisan Portal Login | किसान लॉगिन';
        if (desc) desc.textContent = 'Sell crop stubble & biomass directly to verified industrial processors at zero commission.';
        if (icon) icon.className = 'fas fa-leaf notice-icon';
        if (extraLabel) extraLabel.textContent = 'Farm Location & Primary Crop';
        if (extraInput) extraInput.placeholder = 'e.g. Ludhiana, Punjab (Paddy / Wheat)';
    } else if (role === 'buyer') {
        if (title) title.textContent = 'Industrial Buyer Procurement Terminal';
        if (desc) desc.textContent = 'Procure bulk agricultural residues with calorific & moisture lab certification.';
        if (icon) icon.className = 'fas fa-industry notice-icon';
        if (extraLabel) extraLabel.textContent = 'Company Name & GSTIN';
        if (extraInput) extraInput.placeholder = 'e.g. GreenGrid Bio-Power (03AABCG1234F1Z9)';
    } else if (role === 'admin') {
        if (title) title.textContent = 'Platform Command & Governance Center';
        if (desc) desc.textContent = 'Master administration, KYC verification queue, satellite burn monitoring, and dispute escrow.';
        if (icon) icon.className = 'fas fa-shield-halved notice-icon';
        if (extraLabel) extraLabel.textContent = 'Admin Staff Clearance Code';
        if (extraInput) extraInput.placeholder = 'e.g. AGRI-SEC-MASTER-2026';
    }

    // Suggest default credentials into login inputs for ease of testing
    const emailInput = document.getElementById('loginEmail');
    const passwordInput = document.getElementById('loginPassword');
    const def = DEFAULT_USERS.find(u => u.userType === role);
    if (def && emailInput && passwordInput) {
        emailInput.value = def.email;
        passwordInput.value = def.password;
    }
};

// 1-Click login execution for quick persona switching
window.quickLoginAs = function(role) {
    const def = DEFAULT_USERS.find(u => u.userType === role);
    if (!def) return;

    const { password, ...userWithoutPassword } = def;
    
    // Save to AppState and LocalStorage
    if (window.AppState && typeof window.AppState.saveUser === 'function') {
        window.AppState.saveUser(userWithoutPassword);
    } else {
        localStorage.setItem('currentUser', JSON.stringify(userWithoutPassword));
    }

    // Close modal
    const modal = document.getElementById('authModal');
    if (modal) modal.classList.remove('active');

    // Notify
    if (window.showNotification) {
        window.showNotification(`Logged in as ${userWithoutPassword.name} (${role.toUpperCase()})`, 'success');
    }

    // If not on dashboard, navigate to dashboard
    if (!window.location.pathname.endsWith('dashboard.html')) {
        window.location.href = 'dashboard.html';
    } else {
        // Reload dashboard view to active role
        if (window.renderActivePortal) {
            window.renderActivePortal(role);
        } else {
            window.location.reload();
        }
    }
};

async function handleLogin(e) {
    e.preventDefault();
    const email = document.getElementById('loginEmail')?.value.trim();
    const password = document.getElementById('loginPassword')?.value;
    const hashedPassword = await hashPassword(password);
    
    const users = JSON.parse(localStorage.getItem('users')) || [];
    
    let user = users.find(u => u.email.toLowerCase() === email.toLowerCase() && (u.password === password || u.password === hashedPassword));
    if (!user) {
        user = DEFAULT_USERS.find(u => u.email.toLowerCase() === email.toLowerCase() && (u.password === password || u.password === hashedPassword));
    }

    if (user) {
        const { password, ...userWithoutPassword } = user;
        
        if (window.AppState && typeof window.AppState.saveUser === 'function') {
            window.AppState.saveUser(userWithoutPassword);
        } else {
            localStorage.setItem('currentUser', JSON.stringify(userWithoutPassword));
        }
        
        document.getElementById('authModal')?.classList.remove('active');
        
        if (window.showNotification) {
            window.showNotification(`Welcome back, ${user.name}!`, 'success');
        }

        // Navigate to dashboard if on another page
        if (!window.location.pathname.endsWith('dashboard.html')) {
            window.location.href = 'dashboard.html';
        } else {
            if (window.renderActivePortal) {
                window.renderActivePortal(user.userType || activeModalRole);
            } else {
                window.location.reload();
            }
        }
    } else {
        if (window.showNotification) {
            window.showNotification('Invalid email or password. Use demo buttons or credentials.', 'error');
        } else {
            alert('Invalid email or password. You can use the Quick 1-Click buttons below!');
        }
    }
}

async function handleSignup(e) {
    e.preventDefault();
    const name = document.getElementById('signupName')?.value.trim();
    const email = document.getElementById('signupEmail')?.value.trim();
    const password = document.getElementById('signupPassword')?.value;
    const hashedPassword = await hashPassword(password);
    const extra = document.getElementById('signupExtraField')?.value.trim();
    const userType = activeModalRole || 'farmer';
    
    const users = JSON.parse(localStorage.getItem('users')) || [];
    if (users.some(u => u.email.toLowerCase() === email.toLowerCase())) {
        if (window.showNotification) window.showNotification('Email already registered', 'error');
        return;
    }
    
    const newUser = {
        id: 'USR_' + Date.now(),
        name,
        email,
        password: hashedPassword, // Stored as SHA-256 hash
        userType,
        extraInfo: extra,
        location: extra || 'India',
        createdAt: new Date().toISOString(),
        avatar: `https://ui-avatars.com/api/?name=${encodeURIComponent(name)}&background=random`
    };

    users.push(newUser);
    localStorage.setItem('users', JSON.stringify(users));
    
    const { password: _, ...userWithoutPassword } = newUser;
    if (window.AppState && typeof window.AppState.saveUser === 'function') {
        window.AppState.saveUser(userWithoutPassword);
    } else {
        localStorage.setItem('currentUser', JSON.stringify(userWithoutPassword));
    }
    
    document.getElementById('authModal')?.classList.remove('active');
    
    if (window.showNotification) {
        window.showNotification(`Account created! Welcome to the ${userType.toUpperCase()} portal.`, 'success');
    }

    if (!window.location.pathname.endsWith('dashboard.html')) {
        window.location.href = 'dashboard.html';
    } else {
        if (window.renderActivePortal) {
            window.renderActivePortal(userType);
        } else {
            window.location.reload();
        }
    }
}

function logout() {
    if (window.AppState) {
        window.AppState.currentUser = null;
    }
    localStorage.removeItem('currentUser');
    
    if (window.showNotification) {
        window.showNotification('Logged out successfully', 'info');
    }
    window.location.reload();
}

window.logout = logout;
window.openAuthModal = openAuthModal;
