import os
import sys
from pathlib import Path

# Add project root to path for shared knowledge engine
ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from flask import Flask, render_template, request, jsonify, url_for
from werkzeug.utils import secure_filename
from gtts import gTTS
import random
import string
import re

# Load environment variables
try:
    from dotenv import load_dotenv
    load_dotenv(ROOT_DIR / '.env')
except ImportError:
    pass

from groq import Groq

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['ALLOWED_EXTENSIONS'] = {'webm', 'wav', 'mp3', 'm4a'}

# Initialize Groq & Knowledge Engine
groq_api_key = os.getenv('GROQ_API_KEY')
groq_client = Groq(api_key=groq_api_key) if groq_api_key else None

try:
    from agri_market_knowledge import AgriMarketKnowledge, agri_knowledge
    HAS_KNOWLEDGE = True
except Exception as e:
    HAS_KNOWLEDGE = False
    print(f"Warning: Could not import AgriMarketKnowledge: {e}")


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']


def transcribe_audio_groq(filepath):
    if not groq_client:
        return "Audio transcription unavailable: Groq API key not set"
    with open(filepath, "rb") as f:
        response = groq_client.audio.transcriptions.create(
            model="whisper-large-v3-turbo",
            file=f,
        )
        return response.text


def get_answer_groq(question):
    if HAS_KNOWLEDGE:
        res = agri_knowledge.generate_expert_response(question)
        return res.get("answer", "")
    elif groq_client:
        response = groq_client.chat.completions.create(
            model="qwen/qwen3.8-27b",
            messages=[
                {"role": "system", "content": "You are a helpful agriculture expert chatbot for Indian farmers. Answer questions about farming, agricultural waste, prices, and sustainability with exact facts."},
                {"role": "user", "content": question}
            ],
        )
        return response.choices[0].message.content
    return "Agriculture knowledge engine is currently unavailable."


def text_to_audio(text, filename):
    clean = re.sub(r'#+|\*+|_+|`+|\[.*?\]\(.*?\)|\|.*\|', '', text)
    clean = re.sub(r'\s+', ' ', clean).strip()
    words = clean.split()
    if len(words) > 120:
        clean = ' '.join(words[:120]) + '... For full details, please refer to the text on screen.'

    tts = gTTS(clean, lang='en')
    audio_path = os.path.join("static/audio", f"{filename}.mp3")
    os.makedirs("static/audio", exist_ok=True)
    tts.save(audio_path)
    return audio_path


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/chat', methods=['POST'])
def chat():
    if 'audio' in request.files:
        audio = request.files['audio']
        if audio and allowed_file(audio.filename):
            filename = secure_filename(audio.filename)
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            audio.save(filepath)
            transcription = transcribe_audio_groq(filepath)
            answer = get_answer_groq(transcription)
            voice_filename = ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))
            text_to_audio(answer, voice_filename)
            return jsonify({
                'text': f"🎤 Transcribed: {transcription}\n\n🤖 Answer: {answer}",
                'voice': url_for('static', filename='audio/' + voice_filename + '.mp3')
            })

    elif 'text' in request.form:
        question = request.form['text']
        answer = get_answer_groq(question)
        voice_filename = ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))
        text_to_audio(answer, voice_filename)
        return jsonify({
            'text': answer,
            'voice': url_for('static', filename='audio/' + voice_filename + '.mp3')
        })

    return jsonify({'text': 'No valid input found'}), 400


if __name__ == '__main__':
    os.makedirs("uploads", exist_ok=True)
    os.makedirs("static/audio", exist_ok=True)
    app.run(debug=True)
