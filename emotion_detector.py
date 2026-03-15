"""
Emotion Detection Module

Uses HuggingFace's emotion-english-distilroberta-base for granular 7-emotion
classification. Falls back to VADER sentiment analysis when the transformer
model is unavailable.
"""

from dataclasses import dataclass, field
from typing import Dict

EMOTIONS = ["anger", "disgust", "fear", "joy", "neutral", "sadness", "surprise"]

VADER_THRESHOLDS = {
    "strong_positive": 0.6,
    "positive": 0.2,
    "negative": -0.2,
    "strong_negative": -0.6,
}


@dataclass
class EmotionResult:
    label: str
    score: float
    all_scores: Dict[str, float] = field(default_factory=dict)
    intensity: str = "moderate"

    def __post_init__(self):
        self.intensity = self._compute_intensity()

    def _compute_intensity(self) -> str:
        if self.score >= 0.8:
            return "strong"
        elif self.score >= 0.5:
            return "moderate"
        return "mild"


class EmotionDetector:
    def __init__(self, use_transformer: bool = True):
        self._pipeline = None
        self._vader = None
        self._use_transformer = use_transformer

        if use_transformer:
            self._init_transformer()

        if self._pipeline is None:
            self._init_vader()

    def _init_transformer(self):
        try:
            from transformers import pipeline
            self._pipeline = pipeline(
                "text-classification",
                model="j-hartmann/emotion-english-distilroberta-base",
                top_k=None,
                truncation=True,
            )
        except Exception:
            self._pipeline = None

    def _init_vader(self):
        try:
            from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
            self._vader = SentimentIntensityAnalyzer()
        except ImportError:
            raise RuntimeError(
                "Neither HuggingFace transformers nor VADER is available. "
                "Install at least one: pip install transformers torch OR pip install vaderSentiment"
            )

    def detect(self, text: str) -> EmotionResult:
        if not text or not text.strip():
            return EmotionResult(label="neutral", score=1.0, all_scores={"neutral": 1.0})

        if self._pipeline is not None:
            return self._detect_transformer(text)
        return self._detect_vader(text)

    def _detect_transformer(self, text: str) -> EmotionResult:
        results = self._pipeline(text[:512])[0]
        all_scores = {r["label"]: round(r["score"], 4) for r in results}
        top = max(results, key=lambda r: r["score"])
        return EmotionResult(
            label=top["label"],
            score=round(top["score"], 4),
            all_scores=all_scores,
        )

    def _detect_vader(self, text: str) -> EmotionResult:
        scores = self._vader.polarity_scores(text)
        compound = scores["compound"]

        if compound >= VADER_THRESHOLDS["strong_positive"]:
            label, score = "joy", min(compound, 1.0)
        elif compound >= VADER_THRESHOLDS["positive"]:
            label, score = "joy", compound
        elif compound <= VADER_THRESHOLDS["strong_negative"]:
            label, score = "anger", abs(compound)
        elif compound <= VADER_THRESHOLDS["negative"]:
            label, score = "sadness", abs(compound)
        else:
            label, score = "neutral", 1.0 - abs(compound)

        all_scores = {
            "joy": max(scores["pos"], 0),
            "anger": max(scores["neg"] * 0.5, 0),
            "sadness": max(scores["neg"] * 0.5, 0),
            "neutral": max(scores["neu"], 0),
            "surprise": 0.0,
            "fear": 0.0,
            "disgust": 0.0,
        }

        return EmotionResult(label=label, score=round(score, 4), all_scores=all_scores)

    @property
    def backend(self) -> str:
        if self._pipeline is not None:
            return "HuggingFace Transformers"
        return "VADER Sentiment"
