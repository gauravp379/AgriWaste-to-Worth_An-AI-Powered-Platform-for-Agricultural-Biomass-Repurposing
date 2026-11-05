/**
 * API Client Module
 * Handles all communication with backend APIs
 */

const API = {
    baseURL: '/api',
    timeout: 30000,

    // AI System Endpoints
    async analyzeWaste(imageFiles, quantity = 1000, wasteType = null) {
        const formData = new FormData();
        const files = Array.isArray(imageFiles) ? imageFiles : [imageFiles];
        files.forEach((f, idx) => {
            formData.append('images', f);
            if (idx === 0) formData.append('image', f); // backwards compatibility
        });
        formData.append('quantity', quantity);
        if (wasteType) formData.append('waste_type', wasteType);

        try {
            const response = await fetch(`${this.baseURL}/analyze`, {
                method: 'POST',
                body: formData,
                timeout: this.timeout
            });
            return await response.json();
        } catch (error) {
            console.error('Error analyzing waste:', error);
            throw error;
        }
    },

    async classifyImage(imageFile) {
        const formData = new FormData();
        formData.append('image', imageFile);

        try {
            const response = await fetch(`${this.baseURL}/classify`, {
                method: 'POST',
                body: formData,
                timeout: this.timeout
            });
            return await response.json();
        } catch (error) {
            console.error('Error classifying image:', error);
            throw error;
        }
    },

    async predictPrice(wasteType, quantity, season = 'kharif') {
        try {
            const response = await fetch(`${this.baseURL}/price-predict`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ waste_type: wasteType, quantity, season }),
                timeout: this.timeout
            });
            return await response.json();
        } catch (error) {
            console.error('Error predicting price:', error);
            throw error;
        }
    },

    async assessQuality(moisture, calorific, purity, carbon) {
        try {
            const response = await fetch(`${this.baseURL}/quality-assess`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ moisture, calorific, purity, carbon }),
                timeout: this.timeout
            });
            return await response.json();
        } catch (error) {
            console.error('Error assessing quality:', error);
            throw error;
        }
    },

    async getRecommendations(wasteType, qualityScore) {
        try {
            const response = await fetch(`${this.baseURL}/recommendations`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ waste_type: wasteType, quality_score: qualityScore }),
                timeout: this.timeout
            });
            return await response.json();
        } catch (error) {
            console.error('Error getting recommendations:', error);
            throw error;
        }
    },

    async calculateCarbon(wasteType, quantity) {
        try {
            const response = await fetch(`${this.baseURL}/carbon`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ waste_type: wasteType, quantity }),
                timeout: this.timeout
            });
            return await response.json();
        } catch (error) {
            console.error('Error calculating carbon:', error);
            throw error;
        }
    },

    async getPerformance() {
        try {
            const response = await fetch(`${this.baseURL}/performance`);
            return await response.json();
        } catch (error) {
            console.error('Error getting performance:', error);
            throw error;
        }
    },

    // Chatbot Endpoints
    async transcribeAudio(audioFile) {
        const formData = new FormData();
        formData.append('audio', audioFile);

        try {
            const response = await fetch(`${this.baseURL}/chat/transcribe`, {
                method: 'POST',
                body: formData,
                timeout: this.timeout
            });
            return await response.json();
        } catch (error) {
            console.error('Error transcribing audio:', error);
            throw error;
        }
    },

    async askQuestion(question, history = []) {
        try {
            const response = await fetch(`${this.baseURL}/chat/ask`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ question, history }),
                timeout: this.timeout
            });
            return await response.json();
        } catch (error) {
            console.error('Error asking question:', error);
            throw error;
        }
    },

    async textToSpeech(text) {
        try {
            const response = await fetch(`${this.baseURL}/chat/text-to-speech`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ text }),
                timeout: this.timeout
            });
            return await response.json();
        } catch (error) {
            console.error('Error converting text to speech:', error);
            throw error;
        }
    },

    // Marketplace Live Endpoints
    async getListings(params = {}) {
        try {
            const query = new URLSearchParams();
            if (params.search) query.append('search', params.search);
            if (params.category) query.append('category', params.category);
            if (params.location) query.append('location', params.location);
            if (params.minPrice) query.append('minPrice', params.minPrice);
            if (params.maxPrice) query.append('maxPrice', params.maxPrice);
            if (params.sort) query.append('sort', params.sort);
            
            const url = `${this.baseURL}/listings${query.toString() ? '?' + query.toString() : ''}`;
            const response = await fetch(url);
            return await response.json();
        } catch (error) {
            console.error('Error fetching listings:', error);
            throw error;
        }
    },

    async createListing(listingData) {
        try {
            const response = await fetch(`${this.baseURL}/listings`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(listingData),
                timeout: this.timeout
            });
            return await response.json();
        } catch (error) {
            console.error('Error creating listing:', error);
            throw error;
        }
    },

    async deleteListing(id) {
        try {
            const response = await fetch(`${this.baseURL}/listings/${id}`, {
                method: 'DELETE'
            });
            return await response.json();
        } catch (error) {
            console.error('Error deleting listing:', error);
            throw error;
        }
    },

    // Dashboard & Analytics Live Endpoints
    async getDashboardStats() {
        try {
            const response = await fetch(`${this.baseURL}/dashboard/stats`);
            return await response.json();
        } catch (error) {
            console.error('Error fetching dashboard stats:', error);
            throw error;
        }
    },

    async getTransactions() {
        try {
            const response = await fetch(`${this.baseURL}/transactions`);
            return await response.json();
        } catch (error) {
            console.error('Error fetching transactions:', error);
            throw error;
        }
    },

    async createTransaction(transactionData) {
        try {
            const response = await fetch(`${this.baseURL}/transactions`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(transactionData),
                timeout: this.timeout
            });
            return await response.json();
        } catch (error) {
            console.error('Error creating transaction:', error);
            throw error;
        }
    },

    // System Endpoints
    async checkHealth() {
        try {
            const response = await fetch(`${this.baseURL}/health`);
            return await response.json();
        } catch (error) {
            console.error('Error checking health:', error);
            return { status: 'error', message: 'Backend unavailable' };
        }
    },

    async getSystemStatus() {
        try {
            const response = await fetch(`${this.baseURL}/status`);
            return await response.json();
        } catch (error) {
            console.error('Error getting system status:', error);
            return { components: { ai_system: 'unavailable', chatbot: 'unavailable' } };
        }
    }
};

// Helper function to show notifications
function showNotification(message, type = 'info', duration = 3000) {
    const notification = document.createElement('div');
    notification.className = `notification notification-${type}`;
    notification.textContent = message;
    notification.style.cssText = `
        position: fixed;
        top: 20px;
        right: 20px;
        padding: 15px 20px;
        background: ${type === 'success' ? '#2ecc71' : type === 'error' ? '#e74c3c' : '#3498db'};
        color: white;
        border-radius: 5px;
        box-shadow: 0 2px 10px rgba(0,0,0,0.2);
        z-index: 10000;
        animation: slideIn 0.3s ease;
    `;
    document.body.appendChild(notification);
    setTimeout(() => notification.remove(), duration);
}

// Check backend connectivity on page load
document.addEventListener('DOMContentLoaded', async function() {
    try {
        const status = await API.getSystemStatus();
        console.log('System Status:', status);
        
        if (status.components) {
            console.log('✓ AI System:', status.components.ai_system);
            console.log('✓ Chatbot:', status.components.chatbot);
        }
    } catch (error) {
        console.error('Backend connection error:', error);
    }
});
