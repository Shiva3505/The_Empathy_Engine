"""
Voice Mapper Module

Maps detected emotions to vocal parameters (rate, pitch, volume) with
intensity-based scaling. Parameters are interpolated between neutral
and full-emotion values based on the detection confidence score.
"""

from dataclasses import dataclass
from typing import Dict
from emotion_detector import EmotionResult


@dataclass
class VoiceParams:
    rate: int = 175
    pitch: int = 50
    volume: float = 0.8

    def to_dict(self) -> Dict:
        return {"rate": self.rate, "pitch": self.pitch, "volume": round(self.volume, 2)}


NEUTRAL_PARAMS = VoiceParams(rate=175, pitch=50, volume=0.8)

EMOTION_PROFILES: Dict[str, VoiceParams] = {
    "joy":      VoiceParams(rate=228, pitch=60, volume=0.92),
    "anger":    VoiceParams(rate=201, pitch=45, volume=1.0),
    "sadness":  VoiceParams(rate=131, pitch=40, volume=0.64),
    "surprise": VoiceParams(rate=210, pitch=65, volume=0.96),
    "fear":     VoiceParams(rate=193, pitch=58, volume=0.68),
    "disgust":  VoiceParams(rate=158, pitch=43, volume=0.72),
    "neutral":  VoiceParams(rate=175, pitch=50, volume=0.8),
}

EMOTION_DESCRIPTIONS: Dict[str, str] = {
    "joy":      "Faster speech, higher pitch, louder volume — upbeat and energetic",
    "anger":    "Slightly faster speech, lower pitch, maximum volume — intense and forceful",
    "sadness":  "Slower speech, lower pitch, softer volume — subdued and reflective",
    "surprise": "Faster speech, highest pitch, louder volume — animated and excited",
    "fear":     "Slightly faster speech, higher pitch, softer volume — tense and anxious",
    "disgust":  "Slower speech, lower pitch, softer volume — dismissive and withdrawn",
    "neutral":  "Normal speech rate, default pitch, moderate volume — calm and balanced",
}


def _lerp(a: float, b: float, t: float) -> float:
    return a + (b - a) * t


class VoiceMapper:
    def __init__(self, profiles: Dict[str, VoiceParams] = None):
        self.profiles = profiles or EMOTION_PROFILES

    def map_emotion(self, emotion_result: EmotionResult) -> VoiceParams:
        label = emotion_result.label.lower()
        target = self.profiles.get(label, NEUTRAL_PARAMS)
        t = self._scale_intensity(emotion_result.score)

        return VoiceParams(
            rate=int(_lerp(NEUTRAL_PARAMS.rate, target.rate, t)),
            pitch=int(_lerp(NEUTRAL_PARAMS.pitch, target.pitch, t)),
            volume=round(_lerp(NEUTRAL_PARAMS.volume, target.volume, t), 2),
        )

    @staticmethod
    def _scale_intensity(score: float) -> float:
        if score >= 0.8:
            return 1.0
        elif score >= 0.5:
            return 0.7
        elif score >= 0.3:
            return 0.4
        return 0.2

    @staticmethod
    def get_description(label: str) -> str:
        return EMOTION_DESCRIPTIONS.get(label.lower(), EMOTION_DESCRIPTIONS["neutral"])

    def get_mapping_table(self) -> Dict[str, Dict]:
        return {
            emotion: {
                "params": params.to_dict(),
                "description": self.get_description(emotion),
            }
            for emotion, params in self.profiles.items()
        }
