# 🎭 The Empathy Engine: Giving AI a Human Voice

An AI-powered system that detects the **emotion in text** and generates **emotionally expressive speech** by dynamically adjusting voice characteristics such as **pitch, rate, and volume**.

This project demonstrates the integration of **Natural Language Processing (NLP)** with **Text-to-Speech (TTS)** to create speech that reflects the emotional tone of the input.

🌐 **Live Demo**  
https://empathy-engine-sbrn.onrender.com

---

# 📋 Problem Statement

Most traditional **Text-to-Speech (TTS)** systems produce flat and robotic speech regardless of the emotional meaning of the text.

The **Empathy Engine** solves this by:

- Detecting the **emotion** of input text using an NLP model
- Mapping detected emotion to **voice characteristics**
- Generating **emotionally expressive speech**

This helps AI systems communicate in a **more human-like and engaging way**.

---

# 🏗️ System Architecture

```
Text Input
     │
     ▼
Emotion Detection
(HuggingFace Model / VADER)
     │
     ▼
Voice Mapping
(Emotion → Pitch, Rate, Volume)
     │
     ▼
Text-to-Speech Engine
(pyttsx3 / gTTS)
     │
     ▼
Audio Output
```

---

# 🧩 Project Modules

| Module | Description |
|------|-------------|
| `emotion_detector.py` | Detects emotion from text |
| `voice_mapper.py` | Maps emotions to voice parameters |
| `tts_engine.py` | Converts processed text into speech |
| `app.py` | FastAPI server and web interface |

---

# 🛠️ Tech Stack

### Programming Language
- Python 3.9+

### Machine Learning / NLP
- HuggingFace Transformers  
- DistilRoBERTa Emotion Model  
- VADER Sentiment Analysis (fallback)

### Speech Synthesis
- pyttsx3
- gTTS (fallback)

### Backend Framework
- FastAPI
- Uvicorn

### Frontend
- HTML
- CSS
- JavaScript

### Deployment
- Render

---

# 📁 Project Structure

```
The_Empathy_Engine/
│
├── app.py
├── emotion_detector.py
├── voice_mapper.py
├── tts_engine.py
├── requirements.txt
├── README.md
├── LICENSE
│
├── static/
│   └── audio/
│
└── templates/
    └── index.html
```

---

# ⚙️ Installation

### 1️⃣ Clone the Repository

```
git clone https://github.com/Shiva3504/The_Empathy_Engine.git
```

```
cd The_Empathy_Engine
```

---

### 2️⃣ Create Virtual Environment

Windows

```
python -m venv venv
venv\Scripts\activate
```

Linux / Mac

```
python3 -m venv venv
source venv/bin/activate
```

---

### 3️⃣ Install Dependencies

```
pip install -r requirements.txt
```

---

# 🚀 Run the Project

Start the FastAPI server:

```
python app.py
```

Open the browser:

```
http://localhost:8000
```

---

# 🌐 Live Demo

You can directly test the deployed application here:

https://empathy-engine-sbrn.onrender.com

---

# 🔌 API Endpoints

| Endpoint | Method | Description |
|--------|--------|-------------|
| `/` | GET | Web interface |
| `/speak` | POST | Detect emotion and generate speech |
| `/analyze` | POST | Emotion detection only |
| `/mapping` | GET | Emotion to voice mapping |
| `/health` | GET | Health check |

---

# 📝 Example API Request

POST /speak

Request

```json
{
"text": "I just got the best news of my life!"
}
```

Example Response

```json
{
  "emotion": "joy",
  "confidence": 0.98,
  "voice_params": {
    "rate": 228,
    "pitch": 60,
    "volume": 0.92
  },
  "audio_url": "/static/audio/output.wav"
}
```

---

# 🌟 Features

- Emotion Detection from text
- Emotion-based voice modulation
- Real-time speech generation
- Interactive web interface
- REST API support
- Dual fallback system (NLP + TTS)
- Deployable AI service

---

# 🔮 Future Improvements

- Multi-language emotion detection
- Voice cloning support
- Real-time streaming audio
- Custom voice profiles
- Conversation emotion tracking

---

# 📜 License

This project is licensed under the **MIT License**.

---

# 👨‍💻 Author

**Shiva Ram Reddy Gunnala**

GitHub  
https://github.com/Shiva3505

---

⭐ If you like this project, consider giving it a **star on GitHub**.
