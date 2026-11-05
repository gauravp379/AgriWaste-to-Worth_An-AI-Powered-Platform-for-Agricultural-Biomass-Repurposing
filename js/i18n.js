// Multi-Language (EN / HI / MR) & Accessibility / Voice Assistant Engine
// ==============================================================================

const I18n = {
    currentLang: localStorage.getItem('appLang') || 'en',
    translations: {},

    async init() {
        try {
            const res = await fetch('data/translations.json');
            this.translations = await res.json();
        } catch (e) {
            console.warn('I18n: translations.json not loaded via fetch, using fallback', e);
            this.translations = {
                en: {
                    appName: "AgriWaste to Worth",
                    tagline: "Turn Crop Residue Into Guaranteed Profit",
                    searchPlaceholder: "Search rice straw, bagasse, wheat turi...",
                    listWasteBtn: "List Crop Waste",
                    scanPhotoBtn: "Take Photo / Scan",
                    heroFarmerBtn: "I'm a Farmer (Sell Waste)",
                    heroBuyerBtn: "I'm a Buyer (Buy Biomass)"
                },
                hi: {
                    appName: "एग्रीवेस्ट टू वर्थ (AgriWaste)",
                    tagline: "फसल अवशेष और पराली बेचें, सही दाम पाएं",
                    searchPlaceholder: "चावल की पराली, भूसा, खोई खोजें...",
                    listWasteBtn: "नई पराली बेचें",
                    scanPhotoBtn: "फोटो खींचें / स्कैन करें",
                    heroFarmerBtn: "मैं किसान हूं (पराली बेचें)",
                    heroBuyerBtn: "मैं खरीदार हूं (बायोमास खरीदें)"
                },
                mr: {
                    appName: "अॅग्रीवेस्ट टू वर्थ (AgriWaste)",
                    tagline: "शेती कचऱ्याचे रूपांतर करा हमखास नफ्यात",
                    searchPlaceholder: "भाताचा पेंढा, उसाची मळी, भुसा शोधा...",
                    listWasteBtn: "कचऱ्याची नोंदणी करा",
                    scanPhotoBtn: "फोटो काढा / तपासा",
                    heroFarmerBtn: "मी शेतकरी आहे (कचरा विका)",
                    heroBuyerBtn: "मी खरेदीदार आहे (बायोमास खरेदी करा)"
                }
            };
        }

        this.applyLanguage(this.currentLang);
        this.injectLanguageAndContrastControls();
        this.initializeVoiceSearch();
    },

    setLanguage(lang) {
        if (!['en', 'hi', 'mr'].includes(lang)) return;
        this.currentLang = lang;
        localStorage.setItem('appLang', lang);
        this.applyLanguage(lang);
    },

    t(key) {
        const dict = this.translations[this.currentLang] || this.translations['en'] || {};
        return dict[key] || key;
    },

    applyLanguage(lang) {
        const dict = this.translations[lang] || {};
        document.querySelectorAll('[data-i18n]').forEach(el => {
            const key = el.getAttribute('data-i18n');
            if (dict[key]) {
                if (el.tagName === 'INPUT' || el.tagName === 'TEXTAREA') {
                    el.placeholder = dict[key];
                } else {
                    el.textContent = dict[key];
                }
            }
        });

        // Update active class on selector buttons
        document.querySelectorAll('.btn-lang-toggle').forEach(btn => {
            if (btn.getAttribute('data-lang') === lang) {
                btn.classList.add('active');
            } else {
                btn.classList.remove('active');
            }
        });
    },

    injectLanguageAndContrastControls() {
        const navMenu = document.querySelector('.nav-actions');
        if (!navMenu || document.getElementById('langSwitcherBar')) return;

        const langBar = document.createElement('div');
        langBar.id = 'langSwitcherBar';
        langBar.className = 'lang-switcher-bar';
        langBar.innerHTML = `
            <div class="lang-pills">
                <button type="button" class="btn-lang-toggle ${this.currentLang === 'en' ? 'active' : ''}" data-lang="en" onclick="I18n.setLanguage('en')">EN</button>
                <button type="button" class="btn-lang-toggle ${this.currentLang === 'hi' ? 'active' : ''}" data-lang="hi" onclick="I18n.setLanguage('hi')">हिंदी</button>
                <button type="button" class="btn-lang-toggle ${this.currentLang === 'mr' ? 'active' : ''}" data-lang="mr" onclick="I18n.setLanguage('mr')">मराठी</button>
            </div>
            <button type="button" class="btn-contrast-toggle" title="Outdoor Sunlight High-Contrast Mode" onclick="I18n.toggleHighContrast()" aria-label="Toggle Outdoor Sunlight Contrast">
                <i class="fas fa-sun"></i>
            </button>
        `;
        navMenu.prepend(langBar);

        // Apply saved contrast mode
        if (localStorage.getItem('sunlightContrast') === 'true') {
            document.body.classList.add('theme-sunlight-contrast');
        }
    },

    toggleHighContrast() {
        const isContrast = document.body.classList.toggle('theme-sunlight-contrast');
        localStorage.setItem('sunlightContrast', isContrast ? 'true' : 'false');
        if (window.showNotification) {
            window.showNotification(isContrast ? 'High-Contrast Sunlight Mode Enabled' : 'Standard Mode Restored', 'info');
        }
    },

    initializeVoiceSearch() {
        const searchInputs = document.querySelectorAll('.search-box input, input[name="search"], #searchInput, #listingSearch');
        if (!('webkitSpeechRecognition' in window) && !('SpeechRecognition' in window)) {
            return; // Voice recognition not supported in this browser
        }

        const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;

        searchInputs.forEach(input => {
            if (input.parentElement && !input.parentElement.querySelector('.btn-voice-search')) {
                const voiceBtn = document.createElement('button');
                voiceBtn.type = 'button';
                voiceBtn.className = 'btn-voice-search';
                voiceBtn.title = 'Speak crop name (बोलकर खोजें)';
                voiceBtn.innerHTML = '<i class="fas fa-microphone"></i>';

                voiceBtn.addEventListener('click', (e) => {
                    e.preventDefault();
                    const recognition = new SpeechRecognition();
                    recognition.lang = this.currentLang === 'hi' ? 'hi-IN' : (this.currentLang === 'mr' ? 'mr-IN' : 'en-IN');
                    recognition.interimResults = false;

                    voiceBtn.classList.add('recording');
                    if (window.showNotification) {
                        window.showNotification('Listening... बोलिए (Crop name/location)', 'info');
                    }

                    recognition.onresult = (event) => {
                        const transcript = event.results[0][0].transcript;
                        input.value = transcript;
                        input.dispatchEvent(new Event('input', { bubbles: true }));
                        voiceBtn.classList.remove('recording');
                        if (window.showNotification) {
                            window.showNotification(`Recognized: "${transcript}"`, 'success');
                        }
                    };

                    recognition.onerror = () => {
                        voiceBtn.classList.remove('recording');
                    };

                    recognition.onend = () => {
                        voiceBtn.classList.remove('recording');
                    };

                    recognition.start();
                });

                input.parentElement.style.position = 'relative';
                input.parentElement.appendChild(voiceBtn);
            }
        });
    }
};

window.I18n = I18n;

document.addEventListener('DOMContentLoaded', () => {
    I18n.init();
});

