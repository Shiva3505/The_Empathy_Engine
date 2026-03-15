# 🎭 The Empathy Engine: Giving AI a Human Voice

An AI-powered service that detects the emotion of input text and dynamically modulates vocal characteristics to produce **emotionally expressive speech**.

Built with **HuggingFace Transformers**, **FastAPI**, and **pyttsx3** — designed to demonstrate NLP, AI model integration, and clean software architecture.

---

## 📋 Problem Statement

Traditional text-to-speech systems produce flat, monotone audio regardless of the emotional content of the text. The Empathy Engine bridges this gap by:

1. **Detecting emotion** from input text using state-of-the-art NLP models
2. **Mapping** each emotion to appropriate vocal parameters
3. **Generating speech** that sounds happy, sad, angry, or surprised — not just robotic

---

## 🏗️ Architecture

```
┌─────────────┐    ┌─────────────────┐    ┌──────────────┐    ┌─────────────┐
│  Text Input  │───▶│ Emotion Detector │───▶│ Voice Mapper  │───▶│  TTS Engine  │
│  (API/Web)   │    │ (HuggingFace /  │    │ (Intensity    │    │ (pyttsx3 /  │
│              │    │  VADER fallback) │    │  Scaling)     │    │  gTTS)      │
└─────────────┘    └─────────────────┘    └──────────────┘    └──────┬──────┘
                                                                       │
                                                                       ▼
                                                               ┌─────────────┐
                                                               │ Audio Output │
                                                               │  (.wav/.mp3) │
                                                               └─────────────┘
```

### Module Breakdown

| Module               | Responsibility                                    |
|----------------------|---------------------------------------------------|
| `emotion_detector.py`| Classifies text into 7 emotions with confidence   |
| `voice_mapper.py`    | Maps emotion → pitch, rate, volume with scaling   |
| `tts_engine.py`      | Generates speech audio with SSML-like processing  |
| `app.py`             | FastAPI server with REST API and web interface     |

---

## 🛠️ Tech Stack

| Category            | Technology                                          |
|---------------------|-----------------------------------------------------|
| **Language**        | Python 3.9+                                         |
| **NLP Model**       | `j-hartmann/emotion-english-distilroberta-base`     |
| **Fallback NLP**    | VADER Sentiment Analysis                            |
| **TTS Primary**     | pyttsx3 (offline, parameter control)                |
| **TTS Fallback**    | gTTS (Google Text-to-Speech)                        |
| **Web Framework**   | FastAPI + Uvicorn                                   |
| **Frontend**        | Vanilla HTML/CSS/JS with glassmorphism design       |

---

## ⚡ Installation

### 1. Clone the Repository

```bash
git clone https://github.com/<your-username>/empathy-engine.git
cd empathy-engine
```

### 2. Create a Virtual Environment (recommended)

```bash
python -m venv venv
source venv/bin/activate   # Linux/Mac
venv\Scripts\activate      # Windows
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

> **Note**: The HuggingFace model (~300MB) will be downloaded automatically on first run. If you prefer a lightweight setup, the system falls back to VADER sentiment analysis.

---

## 🚀 How to Run

### Start the Server (Full — with HuggingFace Transformer)

```bash
python app.py
```

> The HuggingFace model (~300MB) downloads automatically on first run. Startup may take a minute.

### Start the Server (Lightweight — with VADER)

For faster startup without downloading large models:

```bash
# Linux / macOS
USE_VADER=true python app.py

# Windows PowerShell
$env:USE_VADER="true"; python app.py
```

The server starts at **http://localhost:8000**.

### Web Interface

Open your browser and navigate to:

```
http://localhost:8000
```

You'll see a sleek dark-themed interface where you can:
1. Enter any text
2. Click **"Detect Emotion & Speak"**
3. View the detected emotion, confidence scores, and voice parameters
4. Listen to the emotionally expressive audio

### REST API

Use `curl` or any HTTP client:

```bash
curl -X POST http://localhost:8000/speak \
  -H "Content-Type: application/json" \
  -d '{"text": "I just got the best news of my life! This is incredible!"}'
```

---

## 📝 Example Input & Output

### Example 1: Happy Text

**Input**:
```json
{"text": "I just got promoted! This is the best day ever!"}
```

**Output**:
```json
{
  "emotion": {
    "label": "joy",
    "score": 0.9841,
    "intensity": "strong",
    "all_scores": {
      "joy": 0.9841,
      "surprise": 0.0089,
      "neutral": 0.0035,
      "anger": 0.0012,
      "sadness": 0.0010,
      "fear": 0.0008,
      "disgust": 0.0005
    }
  },
  "voice_params": {
    "rate": 228,
    "pitch": 60,
    "volume": 0.92
  },
  "voice_description": "Faster speech, higher pitch, louder volume — upbeat and energetic",
  "audio_url": "/static/audio/output_a1b2c3d4.wav"
}
```

### Example 2: Sad Text

**Input**:
```json
{"text": "I feel so alone. Nobody understands what I'm going through."}
```

**Output**:
```json
{
  "emotion": {
    "label": "sadness",
    "score": 0.9523,
    "intensity": "strong"
  },
  "voice_params": {
    "rate": 131,
    "pitch": 40,
    "volume": 0.64
  },
  "voice_description": "Slower speech, lower pitch, softer volume — subdued and reflective"
}
```

---

## 🎯 Emotion-to-Voice Mapping Logic

The system uses **intensity-based interpolation** — voice parameters scale proportionally to the confidence score of the detected emotion.

| Emotion     | Rate (wpm) | Pitch | Volume | Style                    |
|-------------|------------|-------|--------|--------------------------|
| **Joy**     | 228 (+30%) | 60    | 0.92   | Upbeat, energetic        |
| **Anger**   | 201 (+15%) | 45    | 1.00   | Intense, forceful        |
| **Sadness** | 131 (-25%) | 40    | 0.64   | Subdued, reflective      |
| **Surprise**| 210 (+20%) | 65    | 0.96   | Animated, excited        |
| **Fear**    | 193 (+10%) | 58    | 0.68   | Tense, anxious           |
| **Disgust** | 158 (-10%) | 43    | 0.72   | Dismissive, withdrawn    |
| **Neutral** | 175 (base) | 50    | 0.80   | Calm, balanced           |

### Intensity Scaling

The confidence score determines how strongly the emotion affects voice parameters:

| Confidence | Intensity | Scaling Factor |
|------------|-----------|----------------|
| ≥ 0.8      | Strong    | 100%           |
| ≥ 0.5      | Moderate  | 70%            |
| ≥ 0.3      | Mild      | 40%            |
| < 0.3      | Minimal   | 20%            |

**Example**: *"This is good"* → mild joy (40% scaling) vs. *"This is the best news ever!"* → strong joy (100% scaling)

---

## 🔌 API Endpoints

| Endpoint       | Method | Description                    |
|----------------|--------|--------------------------------|
| `/`            | GET    | Web interface                  |
| `/speak`       | POST   | Detect emotion & generate audio|
| `/analyze`     | POST   | Emotion analysis only (no audio)|
| `/mapping`     | GET    | View emotion-to-voice mapping  |
| `/health`      | GET    | Service health check           |

---

## 🌟 Bonus Features Implemented

- ✅ **Granular Emotion Detection** — 7 emotions (joy, anger, sadness, surprise, fear, disgust, neutral)
- ✅ **Emotion Intensity Scaling** — Voice parameters scale with confidence score
- ✅ **Web Interface** — Premium dark-themed UI with glassmorphism design
- ✅ **SSML-like Support** — Automatic emphasis on emotional keywords and contextual pauses
- ✅ **Dual Backend Fallback** — HuggingFace → VADER for NLP; pyttsx3 → gTTS for TTS

---

## 🔮 Future Improvements

1. **Multi-language Support** — Extend emotion detection and TTS to additional languages
2. **Voice Cloning** — Use models like Coqui TTS for personalized voice synthesis
3. **Real-time Streaming** — WebSocket-based streaming for live emotional speech
4. **Prosody Control** — Fine-grained control over intonation contours
5. **Emotion History** — Track emotional arcs over conversation threads
6. **Custom Voice Profiles** — Allow users to define their own emotion-to-voice mappings
7. **Batch Processing** — Process multiple texts in a single API call

---

## 📁 Project Structure

```
empathy-engine/
├── app.py                  # FastAPI application & API endpoints
├── emotion_detector.py     # Emotion classification module
├── voice_mapper.py         # Emotion → voice parameter mapping
├── tts_engine.py           # Text-to-speech synthesis engine
├── requirements.txt        # Python dependencies
├── README.md               # This file
├── .gitignore              # Git ignore rules
├── static/
│   └── audio/              # Generated audio files
└── templates/
    └── index.html          # Web interface
```

---

## 📜 License

This project is open source and available under the [MIT License](LICENSE).

---

<p align="center">
  <strong>The Empathy Engine</strong> — Because AI should speak with feeling, not just words.
</p>
