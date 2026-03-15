"""
Empathy Engine — FastAPI Application

REST API and web interface for emotion-aware text-to-speech synthesis.
"""

import os
import asyncio
from pathlib import Path

from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel

from emotion_detector import EmotionDetector
from voice_mapper import VoiceMapper
from tts_engine import TTSEngine

BASE_DIR = Path(__file__).parent
AUDIO_DIR = BASE_DIR / "static" / "audio"
AUDIO_DIR.mkdir(parents=True, exist_ok=True)

app = FastAPI(
    title="The Empathy Engine",
    description="AI-powered emotion-aware text-to-speech synthesis",
    version="1.0.0",
)

app.mount("/static", StaticFiles(directory=str(BASE_DIR / "static")), name="static")
templates = Jinja2Templates(directory=str(BASE_DIR / "templates"))

use_transformer = os.environ.get("USE_VADER", "").lower() not in ("1", "true", "yes")
detector = EmotionDetector(use_transformer=use_transformer)
mapper = VoiceMapper()
tts = TTSEngine()


class SpeakRequest(BaseModel):
    text: str


class AnalyzeRequest(BaseModel):
    text: str


@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    return templates.TemplateResponse("index.html", {
        "request": request,
        "emotion_backend": detector.backend,
        "tts_backend": tts.backend,
    })


@app.post("/speak")
async def speak(req: SpeakRequest):
    if not req.text or not req.text.strip():
        raise HTTPException(status_code=400, detail="Text input is required")

    if len(req.text) > 5000:
        raise HTTPException(status_code=400, detail="Text must be under 5000 characters")

    # Run blocking detection + TTS in a thread to keep the event loop responsive
    def _process():
        emotion_result = detector.detect(req.text)
        voice_params = mapper.map_emotion(emotion_result)
        audio_path = tts.synthesize(
            text=req.text,
            voice_params=voice_params,
            emotion=emotion_result.label,
        )
        return emotion_result, voice_params, audio_path

    emotion_result, voice_params, audio_path = await asyncio.to_thread(_process)

    audio_filename = os.path.basename(audio_path)

    return JSONResponse({
        "emotion": {
            "label": emotion_result.label,
            "score": emotion_result.score,
            "intensity": emotion_result.intensity,
            "all_scores": emotion_result.all_scores,
        },
        "voice_params": voice_params.to_dict(),
        "voice_description": mapper.get_description(emotion_result.label),
        "audio_url": f"/static/audio/{audio_filename}",
        "backends": {
            "emotion": detector.backend,
            "tts": tts.backend,
        },
    })


@app.post("/analyze")
async def analyze(req: AnalyzeRequest):
    if not req.text or not req.text.strip():
        raise HTTPException(status_code=400, detail="Text input is required")

    emotion_result = detector.detect(req.text)
    voice_params = mapper.map_emotion(emotion_result)

    return JSONResponse({
        "emotion": {
            "label": emotion_result.label,
            "score": emotion_result.score,
            "intensity": emotion_result.intensity,
            "all_scores": emotion_result.all_scores,
        },
        "voice_params": voice_params.to_dict(),
        "voice_description": mapper.get_description(emotion_result.label),
    })


@app.get("/mapping")
async def mapping():
    return JSONResponse(mapper.get_mapping_table())


@app.get("/health")
async def health():
    return JSONResponse({
        "status": "healthy",
        "backends": {
            "emotion": detector.backend,
            "tts": tts.backend,
        },
    })


if __name__ == "__main__":
    import uvicorn
    print("\n🎭 The Empathy Engine is starting...")
    print(f"   Emotion backend : {detector.backend}")
    print(f"   TTS backend     : {tts.backend}")
    print(f"   Server          : http://localhost:8000\n")
    uvicorn.run(app, host="0.0.0.0", port=8000)
