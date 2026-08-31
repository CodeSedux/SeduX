from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(frozen=True)
class AudioPayload:
    sample_rate: int = 16000
    channels: int = 1
    format: str = "pcm16"
    data: bytes = b""

    def to_dict(self) -> dict[str, object]:
        return {
            "sample_rate": self.sample_rate,
            "channels": self.channels,
            "format": self.format,
            "data_length": len(self.data),
        }


@dataclass(frozen=True)
class TranscriptResult:
    text: str
    is_final: bool = True
    confidence: float = 0.0
    language: str = "en"

    def to_dict(self) -> dict[str, object]:
        return {
            "text": self.text,
            "is_final": self.is_final,
            "confidence": self.confidence,
            "language": self.language,
        }


@dataclass(frozen=True)
class VisemeFrame:
    name: str
    weight: float = 0.0

    def to_dict(self) -> dict[str, object]:
        return {"name": self.name, "weight": self.weight}


@dataclass(frozen=True)
class TTSChunk:
    text: str
    audio_b64: str = ""
    visemes: list[VisemeFrame] = field(default_factory=list)

    def to_dict(self) -> dict[str, object]:
        return {
            "text": self.text,
            "audio_b64": self.audio_b64,
            "visemes": [frame.to_dict() for frame in self.visemes],
        }
