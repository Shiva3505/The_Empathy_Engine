"""
Text-to-Speech Engine Module

Generates emotionally modulated speech audio. Uses pyttsx3 for offline
synthesis with rate/volume control. Falls back to gTTS when pyttsx3
is unavailable. Includes SSML-like text preprocessing for emphasis.

Note: pyttsx3 engine is created fresh for each synthesis call to avoid
the deadlock caused by its internal event loop conflicting with asyncio.
"""

import re
import uuid
import threading
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from typing import Optional

from voice_mapper import VoiceParams

AUDIO_DIR = Path(__file__).parent / "static" / "audio"
AUDIO_DIR.mkdir(parents=True, exist_ok=True)

# Thread pool for running blocking TTS operations
_tts_executor = ThreadPoolExecutor(max_workers=1)
# Lock to prevent concurrent pyttsx3 usage (it is not thread-safe)
_tts_lock = threading.Lock()

EMPHASIS_WORDS = {
    "joy": ["amazing", "wonderful", "fantastic", "love", "great", "awesome", "happy", "excited", "best"],
    "anger": ["hate", "terrible", "awful", "worst", "furious", "angry", "annoying", "stupid"],
    "sadness": ["sorry", "miss", "lost", "alone", "cry", "sad", "depressed", "hopeless"],
    "surprise": ["wow", "unbelievable", "incredible", "shocking", "unexpected", "suddenly"],
    "fear": ["scared", "afraid", "terrified", "danger", "horror", "panic", "worry"],
    "disgust": ["gross", "disgusting", "revolting", "nasty", "vile", "repulsive"],
}

EMOTION_PAUSES = {
    "joy": 0.1,
    "anger": 0.05,
    "sadness": 0.3,
    "surprise": 0.15,
    "fear": 0.2,
    "disgust": 0.2,
    "neutral": 0.15,
}


class SSMLProcessor:
    @staticmethod
    def add_emphasis(text: str, emotion: str) -> str:
        words = EMPHASIS_WORDS.get(emotion, [])
        for word in words:
            pattern = re.compile(rf'\b({word})\b', re.IGNORECASE)
            text = pattern.sub(rf' ... \1 ... ', text)
        return text

    @staticmethod
    def add_pauses(text: str, emotion: str) -> str:
        pause_duration = EMOTION_PAUSES.get(emotion, 0.15)
        if pause_duration >= 0.25:
            text = text.replace(". ", "... ")
            text = text.replace("! ", "!.. ")
            text = text.replace("? ", "?.. ")
        return text


class TTSEngine:
    def __init__(self):
        self._backend = None
        self._check_backend()

    def _check_backend(self):
        """Check which TTS backend is available (without keeping an engine alive)."""
        try:
            import pyttsx3
            # Quick init/stop test to verify pyttsx3 works
            engine = pyttsx3.init()
            engine.stop()
            del engine
            self._backend = "pyttsx3"
        except Exception:
            self._backend = "gTTS"

    def synthesize(
        self,
        text: str,
        voice_params: VoiceParams,
        emotion: str = "neutral",
        filename: Optional[str] = None,
    ) -> str:
        processed_text = SSMLProcessor.add_emphasis(text, emotion)
        processed_text = SSMLProcessor.add_pauses(processed_text, emotion)

        if filename is None:
            filename = f"output_{uuid.uuid4().hex[:8]}.wav"

        output_path = AUDIO_DIR / filename

        if self._backend == "pyttsx3":
            return self._synthesize_pyttsx3(processed_text, voice_params, str(output_path))
        return self._synthesize_gtts(processed_text, str(output_path))

    def _synthesize_pyttsx3(self, text: str, params: VoiceParams, output_path: str) -> str:
        """Synthesize using pyttsx3 — creates a fresh engine each time to avoid deadlocks."""
        wav_path = output_path
        if not wav_path.endswith(".wav"):
            wav_path = output_path.rsplit(".", 1)[0] + ".wav"

        def _do_synthesis():
            with _tts_lock:
                import pyttsx3
                engine = pyttsx3.init()
                try:
                    engine.setProperty("rate", params.rate)
                    engine.setProperty("volume", params.volume)

                    voices = engine.getProperty("voices")
                    if voices:
                        engine.setProperty("voice", voices[0].id)

                    engine.save_to_file(text, wav_path)
                    engine.runAndWait()
                finally:
                    engine.stop()
                    del engine

        # Run in a separate thread so it doesn't block FastAPI's event loop
        future = _tts_executor.submit(_do_synthesis)
        future.result(timeout=30)  # Wait up to 30 seconds

        return wav_path

    def _synthesize_gtts(self, text: str, output_path: str) -> str:
        try:
            from gtts import gTTS

            mp3_path = output_path.rsplit(".", 1)[0] + ".mp3"
            tts = gTTS(text=text, lang="en", slow=False)
            tts.save(mp3_path)
            return mp3_path
        except ImportError:
            raise RuntimeError(
                "No TTS engine available. Install pyttsx3 or gTTS: "
                "pip install pyttsx3 OR pip install gTTS"
            )

    @property
    def backend(self) -> str:
        return self._backend
