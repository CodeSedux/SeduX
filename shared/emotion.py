"""CPU-safe text emotion analysis contracts and baseline implementation."""

from dataclasses import asdict, dataclass
from enum import StrEnum
import re
from typing import Iterable


class EmotionLabel(StrEnum):
    HAPPY = "happy"
    SAD = "sad"
    ANGRY = "angry"
    ANXIOUS = "anxious"
    NEUTRAL = "neutral"


POSITIVE_WORDS = frozenset({"happy", "great", "good", "love", "excited", "thanks", "thankful", "joy"})
SAD_WORDS = frozenset({"sad", "lonely", "hurt", "miss", "sorry", "upset", "tired", "down"})
ANGRY_WORDS = frozenset({"angry", "mad", "hate", "frustrated", "furious", "annoyed"})
ANXIOUS_WORDS = frozenset({"anxious", "worried", "worry", "afraid", "scared", "nervous", "panic"})


@dataclass(frozen=True)
class EmotionCapturePolicy:
    user_id: str
    allowed_modalities: tuple[str, ...] = ("text", "face", "voice", "gaze")
    consented: bool = False
    retention_days: int = 30

    def __post_init__(self) -> None:
        if not self.user_id or not str(self.user_id).strip():
            raise ValueError("user_id must be non-empty")
        if not isinstance(self.retention_days, int) or self.retention_days <= 0:
            raise ValueError("retention_days must be a positive integer")
        object.__setattr__(self, "allowed_modalities", tuple(self.allowed_modalities))
        if not self.allowed_modalities:
            raise ValueError("allowed_modalities cannot be empty")

    def can_collect(self, modality: str) -> bool:
        return bool(self.consented and modality in self.allowed_modalities)


@dataclass(frozen=True)
class TextEmotionResult:
    text: str
    dominant: EmotionLabel
    confidence: float
    intensity: float
    valence: float
    arousal: float

    def to_dict(self) -> dict[str, object]:
        payload = asdict(self)
        payload["dominant"] = self.dominant.value
        return payload


@dataclass(frozen=True)
class EmotionSignal:
    modality: str
    dominant: EmotionLabel
    confidence: float
    intensity: float
    consented: bool = True

    def __post_init__(self) -> None:
        if not self.modality or not 0 <= self.confidence <= 1 or not 0 <= self.intensity <= 1:
            raise ValueError("modality is required and scores must be between zero and one")


ModalityEmotionResult = EmotionSignal


@dataclass(frozen=True)
class FusedEmotionResult:
    dominant: EmotionLabel
    confidence: float
    intensity: float
    modalities: tuple[str, ...]


def fuse_emotions(
    results: Iterable[EmotionSignal | ModalityEmotionResult],
    policy: EmotionCapturePolicy | None = None,
) -> FusedEmotionResult:
    usable = []
    for result in results:
        if result.confidence <= 0:
            continue
        if policy is not None and not policy.can_collect(result.modality):
            continue
        if not getattr(result, "consented", True):
            continue
        usable.append(result)

    if not usable:
        return FusedEmotionResult(EmotionLabel.NEUTRAL, 0.0, 0.0, ())

    scores: dict[EmotionLabel, float] = {}
    for result in usable:
        scores[result.dominant] = scores.get(result.dominant, 0.0) + result.confidence * result.intensity
    dominant = max(scores, key=scores.get)
    matching = [result for result in usable if result.dominant is dominant]
    total_confidence = sum(result.confidence for result in usable)
    confidence = sum(result.confidence for result in matching) / total_confidence
    intensity = sum(result.intensity * result.confidence for result in matching) / sum(
        result.confidence for result in matching
    )
    return FusedEmotionResult(
        dominant,
        round(confidence, 3),
        round(intensity, 3),
        tuple(result.modality for result in usable),
    )


def analyze_text_emotion(text: str) -> TextEmotionResult:
    if not text or not text.strip():
        raise ValueError("text must be non-empty")

    tokens = re.findall(r"[a-z']+", text.lower())
    scores = {
        EmotionLabel.HAPPY: sum(token in POSITIVE_WORDS for token in tokens),
        EmotionLabel.SAD: sum(token in SAD_WORDS for token in tokens),
        EmotionLabel.ANGRY: sum(token in ANGRY_WORDS for token in tokens),
        EmotionLabel.ANXIOUS: sum(token in ANXIOUS_WORDS for token in tokens),
    }
    dominant = max(scores, key=scores.get)
    winning_score = scores[dominant]
    if winning_score == 0:
        dominant = EmotionLabel.NEUTRAL

    signed_score = (
        scores[EmotionLabel.HAPPY]
        - scores[EmotionLabel.SAD]
        - scores[EmotionLabel.ANGRY]
        - scores[EmotionLabel.ANXIOUS]
    )
    valence = max(-1.0, min(1.0, signed_score / 3))
    intensity = max(0.0, min(1.0, sum(scores.values()) / 4))
    arousal = max(0.0, min(1.0, (scores[EmotionLabel.ANGRY] + scores[EmotionLabel.ANXIOUS] + text.count("!")) / 4))
    confidence = 0.5 if dominant is EmotionLabel.NEUTRAL else min(0.98, 0.55 + winning_score / 10)

    return TextEmotionResult(
        text=text,
        dominant=dominant,
        confidence=round(confidence, 3),
        intensity=round(intensity, 3),
        valence=round(valence, 3),
        arousal=round(arousal, 3),
    )
