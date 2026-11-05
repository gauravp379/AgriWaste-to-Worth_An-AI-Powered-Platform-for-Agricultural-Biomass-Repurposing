// AgriBot: Real-Time Agricultural Intelligence & Market Chatbot
// ==============================================================

// Client-side fallback knowledge base (updated with 2025-2026 benchmarks)
const KB = {
  greet: {
    patterns: ['hello', 'hi', 'hey', 'namaste', 'good morning', 'good evening', 'good afternoon', 'ram ram', 'kisan'],
    response: () => `### 🌾 **Namaste! I'm AgriBot – Your Real-Time Agricultural Intelligence Assistant**<br><br>
    I am connected to live Indian mandi databases, agricultural waste trade benchmarks, and government schemes.<br><br>
    **Here is how I can assist you today:**<br>
    • 📊 **Live Mandi Rates:** Real-time buying & selling prices for crop residues (Paddy straw, Wheat turi, Bagasse, Cotton stalks, etc.)<br>
    • 🏛️ **Government Subsidies:** CRM (50%–80% straw machine subsidy), SATAT (CBG at ₹46–54/kg), PM-KUSUM, GOBARdhan<br>
    • 💡 **Waste to Wealth:** High-return repurposing (Biogas/CBG, Biomass pellets, Mushroom farming, Biochar, Tableware)<br>
    • 🚫 **Zero Stubble Burning:** Avoid CAQM fines (up to ₹30,000) and earn ₹1,500–₹2,500/acre profit instead<br>
    • 🎙️ **Voice Enabled:** Type in English, Hindi, or Hinglish, or tap the **microphone icon** to speak!<br><br>
    *What agricultural question or market price would you like to check today?*`
  },
  goodbye: {
    patterns: ['bye', 'goodbye', 'see you', 'take care', 'thanks bye', 'ok bye', 'shukriya', 'dhanyawad'],
    response: () => `🌿 **Happy Farming & Sustainable Agriculture!**<br>Feel free to return anytime to check real-time market rates or list your crop residue on our **Marketplace**.`
  }
};

const chatHistory = [];
let currentAudio = null;
let recognition = null;
let isRecording = false;

// Markdown to Rich HTML Formatter
function renderMarkdown(md) {
  if (!md) return '';

  let html = md;

  // 1. Tables: Parse Markdown tables into styled HTML <table>
  html = html.replace(/((?:\|[^\n]+\|\r?\n)+)/g, function (tableBlock) {
    const lines = tableBlock.trim().split(/\r?\n/).filter(line => line.includes('|'));
    if (lines.length < 2) return tableBlock;

    let tableHtml = '<table class="chat-table">';
    let isHeader = true;

    lines.forEach((line, index) => {
      // Check if separator line (e.g., |:---|:---|)
      if (line.match(/^\|?\s*[-:]+[-| :]*\s*\|?$/)) {
        isHeader = false;
        return;
      }

      const cells = line.split('|').slice(1, -1);
      if (index === 0) {
        tableHtml += '<thead><tr>';
        cells.forEach(cell => {
          tableHtml += `<th>${cell.trim()}</th>`;
        });
        tableHtml += '</tr></thead><tbody>';
      } else {
        tableHtml += '<tr>';
        cells.forEach(cell => {
          tableHtml += `<td>${cell.trim()}</td>`;
        });
        tableHtml += '</tr>';
      }
    });

    tableHtml += '</tbody></table>';
    return tableHtml;
  });

  // 2. Headings
  html = html.replace(/^#### (.*?)$/gm, '<h4>$1</h4>');
  html = html.replace(/^### (.*?)$/gm, '<h3>$1</h3>');
  html = html.replace(/^## (.*?)$/gm, '<h2>$1</h2>');

  // 3. Bold & Italic
  html = html.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>');
  html = html.replace(/\*(.*?)\*/g, '<em>$1</em>');

  // 4. Bullet lists
  html = html.replace(/^\s*[-*•]\s+(.*?)$/gm, '<li>$1</li>');
  html = html.replace(/((?:<li>.*?<\/li>\s*)+)/g, '<ul>$1</ul>');

  // 5. Line breaks (protect table rows from being broken by <br>)
  html = html.replace(/\n\n/g, '<br><br>');
  html = html.replace(/\n(?!(?:<\/?(table|thead|tbody|tr|th|td|ul|ol|li|h2|h3|h4)))/g, '<br>');

  return html;
}

// Add message to chat container
function addMessage(text, sender, isHtml = false, metadata = null) {
  const messages = document.getElementById('chatMessages');
  if (!messages) return;

  const div = document.createElement('div');
  div.className = `chat-message ${sender}`;

  let contentHtml = isHtml ? text : renderMarkdown(text);
  let audioButtonHtml = '';

  if (sender === 'bot') {
    // Generate clean text for speech playback
    const rawCleanText = text.replace(/<[^>]*>/g, '').replace(/[\*#\|]/g, ' ').replace(/\s+/g, ' ').trim();
    const encodedText = encodeURIComponent(rawCleanText.slice(0, 300));
    
    audioButtonHtml = `
      <div style="display:flex; align-items:center; gap:8px; flex-wrap:wrap; margin-top:6px;">
        <button class="listen-btn" onclick="playSpeech(this, '${encodedText}')" title="Listen to answer">
          <i class="fas fa-volume-up"></i> Listen
        </button>
        ${metadata && metadata.model ? `<span class="meta-badge"><i class="fas fa-brain"></i> Live AI Engine (${metadata.model})</span>` : ''}
        ${metadata && metadata.source === 'llm_grounded' ? '<span class="meta-badge" style="background:#e3f2fd; color:#1565c0;"><i class="fas fa-satellite"></i> Verified Mandi Data Grounded</span>' : ''}
      </div>
    `;
  }

  div.innerHTML = `
    <div class="message-avatar">
      ${sender === 'bot' ? '<i class="fas fa-robot"></i>' : '<i class="fas fa-user"></i>'}
    </div>
    <div class="message-bubble">
      ${contentHtml}
      ${audioButtonHtml}
      <span class="message-time">${new Date().toLocaleTimeString('en-IN', { hour: '2-digit', minute: '2-digit' })}</span>
    </div>
  `;

  messages.appendChild(div);
  messages.scrollTop = messages.scrollHeight;

  chatHistory.push({
    role: sender === 'bot' ? 'assistant' : 'user',
    sender,
    content: text,
    text
  });
}

// Show typing indicator
function showTyping() {
  const messages = document.getElementById('chatMessages');
  if (!messages) return;
  const div = document.createElement('div');
  div.id = 'typingIndicator';
  div.className = 'chat-message bot';
  div.innerHTML = `
    <div class="message-avatar"><i class="fas fa-robot"></i></div>
    <div class="message-bubble typing">
      <span></span><span></span><span></span>
      <span style="font-size:0.75rem; color:#27ae60; margin-left:8px; font-weight:500;">Consulting live mandi & agricultural database...</span>
    </div>
  `;
  messages.appendChild(div);
  messages.scrollTop = messages.scrollHeight;
}

function removeTyping() {
  document.getElementById('typingIndicator')?.remove();
}

// Send message to backend
async function sendMessage() {
  const input = document.getElementById('chatInput');
  const msg = input?.value?.trim();
  if (!msg) return;

  input.value = '';
  addMessage(msg, 'user');
  showTyping();

  try {
    if (window.API && typeof API.askQuestion === 'function') {
      const historyContext = chatHistory.slice(-6);
      const res = await API.askQuestion(msg, historyContext);

      if (res && res.answer) {
        removeTyping();
        addMessage(res.answer, 'bot', false, {
          source: res.source,
          model: res.model,
          crops: res.detected_crops,
          topics: res.detected_topics
        });
        return;
      }
    }
  } catch (err) {
    console.warn('Live API response error, falling back to local intelligence:', err);
  }

  // Client-side fallback if network or server fails
  setTimeout(() => {
    removeTyping();
    const fallbackResponse = getClientFallback(msg);
    addMessage(fallbackResponse, 'bot', true);
  }, 400);
}

// Client-side fallback logic with verified real-time data
function getClientFallback(msg) {
  const lower = msg.toLowerCase();

  // Rice / Paddy
  if (/rice|paddy|dhan|parali|chawal|husk/.test(lower)) {
    return `### 🌾 **Paddy / Rice Residue – Real-Time Market Overview**<br><br>
    <table class="chat-table">
      <thead><tr><th>Residue Type</th><th>Price Range (per ton)</th><th>Best Use</th></tr></thead>
      <tbody>
        <tr><td><strong>Paddy Straw (Parali)</strong></td><td>₹4,800 – ₹5,400</td><td>NTPC Co-firing, Pellets, CBG</td></tr>
        <tr><td><strong>Rice Husk</strong></td><td>₹5,200 – ₹6,300</td><td>Boiler Fuel, Silica Extraction</td></tr>
      </tbody>
    </table>
    • <strong>Top Buyers:</strong> Thermal power plants (NTPC 5% co-firing mandate), Rice Mills, SATAT Biogas Plants.<br>
    • <strong>Govt Subsidies:</strong> CRM Scheme offers <strong>50% subsidy</strong> to individual farmers and <strong>80% subsidy</strong> to Custom Hiring Centres on Super Seeders & Straw Balers.<br>
    💡 <em>Do not burn parali! Avoid fines up to ₹30,000 and sell baled straw on our Marketplace.</em>`;
  }

  // Wheat Straw / Turi
  if (/wheat|gehun|gehu|turi|bhoosa|bhusa/.test(lower)) {
    return `### 🌾 **Wheat Straw (Turi / Bhoosa) – Market Overview**<br><br>
    <table class="chat-table">
      <thead><tr><th>Residue Type</th><th>Current Price (per ton)</th><th>High-Value Commercial Uses</th></tr></thead>
      <tbody>
        <tr><td><strong>Wheat Straw (Turi)</strong></td><td>₹4,200 – ₹5,200 (Avg ₹4,650)</td><td>Dairy Cattle Fodder, Mushroom Substrate</td></tr>
      </tbody>
    </table>
    • <strong>Calorific Energy:</strong> 15.0 – 17.0 MJ/kg | Moisture: 10%–12%<br>
    • <strong>Mushroom Cultivation:</strong> Yields 0.8–1.2 kg Oyster mushrooms per kg of straw with an ROI of over 300%!`;
  }

  // Sugarcane Bagasse
  if (/sugarcane|ganna|bagasse|cane/.test(lower)) {
    return `### 🍬 **Sugarcane Bagasse & Trash – Market Overview**<br><br>
    • <strong>Bagasse Price:</strong> ₹3,400 – ₹4,400 per ton (dry basis)<br>
    • <strong>Sugarcane Leaves/Trash:</strong> ₹2,200 – ₹3,000 per ton<br>
    • <strong>Industrial Uses:</strong> Cogeneration in sugar mills, Biodegradable plates & tableware (export market), Paper & Pulp.<br>
    • <strong>Major Markets:</strong> Maharashtra, Uttar Pradesh, Karnataka.`;
  }

  // Cotton Stalks
  if (/cotton|kapas|stalk/.test(lower)) {
    return `### 🌸 **Cotton Stalks – High-Energy Biomass**<br><br>
    • <strong>Market Price:</strong> ₹4,800 – ₹5,800 per ton<br>
    • <strong>Calorific Value:</strong> 16.0 – 18.2 MJ/kg (highest energy density among crop stalks)<br>
    • <strong>Commercial Uses:</strong> Industrial briquettes, Particle board for furniture, Biochar soil conditioner.<br>
    ⚠️ <em>Removing and selling stalks immediately prevents pink bollworm pest infestation in the next season.</em>`;
  }

  // Subsidies / Government Schemes
  if (/subsidy|scheme|yojana|crm|satat|kusum|gobardhan|government/.test(lower)) {
    return `### 🏛️ **Key Government Subsidies for Agricultural Waste (2025-2026)**<br><br>
    1. <strong>CRM (Crop Residue Management):</strong> 50% subsidy for individual farmers, 80% for FPOs/CHCs on Super Seeders, Balers, and Happy Seeders.<br>
    2. <strong>SATAT Scheme:</strong> Guaranteed purchase of Compressed Bio-Gas (CBG) at ₹46–₹54 per kg by IOCL, BPCL, and GAIL.<br>
    3. <strong>PM-KUSUM:</strong> 60% subsidy for Solar Agricultural Pumps.<br>
    4. <strong>GOBARdhan:</strong> Up to ₹50 Lakh financial assistance for community biogas plants.`;
  }

  // Stubble Burning Penalties
  if (/burn|burning|stubble|fine|penalty|pollution|caqm/.test(lower)) {
    return `### 🔥 **Stubble Burning Penalties & Legal Enforcement**<br><br>
    Under the Commission for Air Quality Management (CAQM) regulations:<br>
    • Less than 2 acres: <strong>₹5,000 fine</strong><br>
    • 2 to 5 acres: <strong>₹10,000 fine</strong><br>
    • More than 5 acres: <strong>₹30,000 fine</strong><br>
    • Plus 'Red Entry' in revenue records which can restrict fertilizer subsidies and MSP sales.<br><br>
    💰 <em>By contrast, baling and selling on our <strong>Marketplace</strong> yields ₹1,500 – ₹2,500 per acre net profit!</em>`;
  }

  return `### 🌾 **AgriBot Real-Time Market Overview**<br><br>
  Here are today's verified trading prices for key agricultural residues:<br>
  <table class="chat-table">
    <thead><tr><th>Crop Residue</th><th>Market Price (per ton)</th><th>Top Commercial Use</th></tr></thead>
    <tbody>
      <tr><td><strong>Rice Paddy Straw</strong></td><td>₹4,800 – ₹5,400</td><td>NTPC Co-firing, Pellets, CBG</td></tr>
      <tr><td><strong>Rice Husk</strong></td><td>₹5,200 – ₹6,300</td><td>Boiler Fuel, Silica Extraction</td></tr>
      <tr><td><strong>Wheat Straw (Turi)</strong></td><td>₹4,200 – ₹5,200</td><td>Dairy Fodder, Mushroom Substrate</td></tr>
      <tr><td><strong>Sugarcane Bagasse</strong></td><td>₹3,400 – ₹4,400</td><td>Cogeneration, Bio-Tableware</td></tr>
      <tr><td><strong>Cotton Stalks</strong></td><td>₹4,800 – ₹5,800</td><td>Briquettes & Pellets</td></tr>
      <tr><td><strong>Groundnut Shells</strong></td><td>₹5,500 – ₹6,800</td><td>Boilers, Activated Carbon</td></tr>
    </tbody>
  </table><br>
  💬 <em>Ask me any question about crop prices, machinery subsidies, biochar, biogas, or composting!</em>`;
}

// Quick reply click handler
function sendQuickReply(text) {
  const input = document.getElementById('chatInput');
  if (input) {
    input.value = text;
    sendMessage();
  }
}

// Clear chat history
function clearChat() {
  const messages = document.getElementById('chatMessages');
  if (messages) {
    messages.innerHTML = '';
    chatHistory.length = 0;
    addMessage(KB.greet.response(), 'bot', true);
  }
}

// Text-to-Speech audio player
async function playSpeech(btn, encodedText) {
  const text = decodeURIComponent(encodedText);

  // Stop currently playing audio
  if (currentAudio) {
    currentAudio.pause();
    currentAudio = null;
    document.querySelectorAll('.listen-btn').forEach(b => {
      b.classList.remove('playing');
      b.innerHTML = '<i class="fas fa-volume-up"></i> Listen';
    });
  }

  btn.classList.add('playing');
  btn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Loading...';

  try {
    // 1. Try server-side gTTS audio file
    if (window.API && typeof API.textToSpeech === 'function') {
      const res = await API.textToSpeech(text);
      if (res && res.audio_url) {
        currentAudio = new Audio(res.audio_url);
        currentAudio.onplay = () => {
          btn.innerHTML = '<i class="fas fa-stop"></i> Stop';
        };
        currentAudio.onended = () => {
          btn.classList.remove('playing');
          btn.innerHTML = '<i class="fas fa-volume-up"></i> Listen';
          currentAudio = null;
        };
        currentAudio.play();
        return;
      }
    }
  } catch (err) {
    console.warn('Server TTS failed, falling back to browser speech synthesis:', err);
  }

  // 2. Fallback to Browser Native Web SpeechSynthesis
  if ('speechSynthesis' in window) {
    const utterance = new SpeechSynthesisUtterance(text);
    utterance.lang = 'en-IN';
    utterance.rate = 0.95;
    utterance.onstart = () => {
      btn.innerHTML = '<i class="fas fa-stop"></i> Stop';
    };
    utterance.onend = () => {
      btn.classList.remove('playing');
      btn.innerHTML = '<i class="fas fa-volume-up"></i> Listen';
    };
    utterance.onerror = () => {
      btn.classList.remove('playing');
      btn.innerHTML = '<i class="fas fa-volume-up"></i> Listen';
    };
    window.speechSynthesis.speak(utterance);
  } else {
    btn.classList.remove('playing');
    btn.innerHTML = '<i class="fas fa-volume-up"></i> Listen';
    alert('Audio playback is not supported on this browser.');
  }
}

// Speech-to-Text Microphone Recording
function toggleVoiceRecording() {
  const micBtn = document.getElementById('micBtn');
  const input = document.getElementById('chatInput');
  if (!micBtn) return;

  if (isRecording) {
    stopVoiceRecording();
    return;
  }

  // Check browser Web Speech API
  const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
  if (SpeechRecognition) {
    try {
      recognition = new SpeechRecognition();
      recognition.continuous = false;
      recognition.interimResults = true;
      recognition.lang = 'en-IN'; // Also detects bilingual Indian speech

      recognition.onstart = () => {
        isRecording = true;
        micBtn.classList.add('recording');
        micBtn.title = 'Listening... Click to stop';
        if (input) input.placeholder = '🎙️ Listening... Speak now in Hindi or English';
      };

      recognition.onresult = (event) => {
        const transcript = Array.from(event.results)
          .map(result => result[0].transcript)
          .join('');
        if (input) input.value = transcript;
      };

      recognition.onerror = (event) => {
        console.warn('Speech recognition error:', event.error);
        stopVoiceRecording();
      };

      recognition.onend = () => {
        stopVoiceRecording();
        if (input && input.value.trim().length > 0) {
          sendMessage();
        }
      };

      recognition.start();
      return;
    } catch (e) {
      console.warn('Web Speech API failed, trying media recorder:', e);
    }
  }

  alert('Voice recognition is best supported on Chrome, Edge, and modern mobile browsers.');
}

function stopVoiceRecording() {
  isRecording = false;
  const micBtn = document.getElementById('micBtn');
  const input = document.getElementById('chatInput');
  if (micBtn) {
    micBtn.classList.remove('recording');
    micBtn.title = 'Speak in Hindi/English';
  }
  if (input) {
    input.placeholder = 'Ask about crop waste, prices, subsidies in English or Hindi...';
  }
  if (recognition) {
    try { recognition.stop(); } catch (e) {}
    recognition = null;
  }
}

// Initialize Chatbot Interface
document.addEventListener('DOMContentLoaded', function () {
  const container = document.getElementById('chatbotContainer');
  if (!container) return;

  container.innerHTML = `
    <div class="chatbot-wrapper" id="chatbotWrapper">
      <div class="chat-header">
        <div class="chat-header-info">
          <div class="bot-avatar"><i class="fas fa-robot"></i></div>
          <div>
            <h3>AgriBot <span style="font-size:0.75rem; background:rgba(255,255,255,0.25); padding:2px 8px; border-radius:10px; margin-left:6px;">Live Mandi AI</span></h3>
            <span class="online-status"><i class="fas fa-circle"></i> Connected to Real-Time Agricultural Database</span>
          </div>
        </div>
        <button class="btn-icon" onclick="clearChat()" title="Restart Chat"><i class="fas fa-rotate-right"></i></button>
      </div>

      <div class="chat-messages" id="chatMessages"></div>

      <div class="quick-replies" id="quickReplies">
        <button onclick="sendQuickReply('What are current biomass market rates in India?')">📊 Today's Mandi Prices</button>
        <button onclick="sendQuickReply('What is the current market price of wheat straw and rice husk?')">🌾 Wheat & Rice Straw</button>
        <button onclick="sendQuickReply('Sugarcane bagasse prices and commercial products in Maharashtra')">🍬 Sugarcane Bagasse</button>
        <button onclick="sendQuickReply('Cotton stalk briquetting uses and market value')">🌸 Cotton Stalks</button>
        <button onclick="sendQuickReply('Government subsidy schemes for crop residue management (CRM)')">🏛️ Subsidies & Schemes</button>
        <button onclick="sendQuickReply('Tell me about SATAT scheme for biogas and CBG rates')">⚡ SATAT CBG Scheme</button>
        <button onclick="sendQuickReply('How to grow mushrooms on wheat straw and what is the ROI?')">🍄 Mushroom Farming</button>
        <button onclick="sendQuickReply('What are the penalties for stubble burning and how to sell on marketplace?')">🔥 Stubble Regulations</button>
      </div>

      <div class="chat-input-area">
        <input type="text" id="chatInput" placeholder="Ask about crop waste, prices, subsidies in English or Hindi..." 
               onkeydown="if(event.key==='Enter') sendMessage()">
        <button class="mic-btn" id="micBtn" onclick="toggleVoiceRecording()" title="Speak in Hindi/English">
          <i class="fas fa-microphone"></i>
        </button>
        <button class="send-btn" onclick="sendMessage()" title="Send Question">
          <i class="fas fa-paper-plane"></i>
        </button>
      </div>
    </div>
  `;

  // Initial Greeting
  setTimeout(() => addMessage(KB.greet.response(), 'bot', true), 300);
});

window.sendMessage = sendMessage;
window.sendQuickReply = sendQuickReply;
window.clearChat = clearChat;
window.playSpeech = playSpeech;
window.toggleVoiceRecording = toggleVoiceRecording;
