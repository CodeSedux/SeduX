from __future__ import annotations

from collections import deque
from dataclasses import dataclass
from time import perf_counter
from typing import Protocol

from shared.voice import AudioPayload, TTSChunk, TranscriptResult, VisemeFrame


class STTAdapter(Protocol):
    def transcribe(self, audio: AudioPayload) -> TranscriptResult: ...


class TTSAdapter(Protocol):
    def synthesize(self, text: str) -> TTSChunk: ...


class StubSTTAdapter:
    def transcribe(self, audio: AudioPayload) -> TranscriptResult:
        text = audio.data.decode("utf-8", errors="ignore").strip() or "audio received"
        return TranscriptResult(text=text, confidence=1.0)


class StubTTSAdapter:
    def synthesize(self, text: str) -> TTSChunk:
        visemes = [VisemeFrame("aa", min(1.0, len(word) / 10)) for word in text.split()]
        return TTSChunk(text=text, audio_b64=text.encode().hex(), visemes=visemes)


@dataclass(frozen=True)
class TimedResult:
    value: TranscriptResult | TTSChunk
    latency_ms: float


class BoundedAudioBuffer:
    def __init__(self, max_chunks: int = 32) -> None:
        if max_chunks < 1:
            raise ValueError("max_chunks must be positive")
        self._chunks: deque[bytes] = deque(maxlen=max_chunks)
        self.cancelled = False

    def push(self, chunk: bytes) -> None:
        if self.cancelled:
            raise RuntimeError("audio stream is cancelled")
        if chunk:
            self._chunks.append(bytes(chunk))

    def cancel(self) -> None:
        self.cancelled = True
        self._chunks.clear()

    def payload(self, sample_rate: int = 16000) -> AudioPayload:
        return AudioPayload(sample_rate=sample_rate, data=b"".join(self._chunks))

    @property
    def size(self) -> int:
        return len(self._chunks)


def has_speech(chunk: bytes, threshold: int = 8) -> bool:
    return any(abs(byte - 128) >= threshold for byte in chunk)


def timed_transcribe(adapter: STTAdapter, audio: AudioPayload) -> TimedResult:
    started = perf_counter()
    return TimedResult(adapter.transcribe(audio), round((perf_counter() - started) * 1000, 3))


def timed_synthesize(adapter: TTSAdapter, text: str) -> TimedResult:
    started = perf_counter()
    return TimedResult(adapter.synthesize(text), round((perf_counter() - started) * 1000, 3))
