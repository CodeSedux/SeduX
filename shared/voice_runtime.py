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


class VoiceSession:
    def __init__(
        self,
        stt_adapter: STTAdapter | None = None,
        tts_adapter: TTSAdapter | None = None,
        max_buffer_ms: int = 1000,
    ) -> None:
        self.stt_adapter = stt_adapter or StubSTTAdapter()
        self.tts_adapter = tts_adapter or StubTTSAdapter()
        self.max_buffer_ms = max_buffer_ms
        self.buffer = BoundedAudioBuffer(max_chunks=max(1, max_buffer_ms // 10))

    def push_audio(self, chunk: bytes) -> None:
        if self.buffer.cancelled:
            raise RuntimeError("audio stream is cancelled")
        self.buffer.push(chunk)

    def cancel(self) -> None:
        self.buffer.cancel()

    def transcribe(self) -> TranscriptResult:
        if self.buffer.cancelled:
            raise RuntimeError("audio stream is cancelled")
        return self.stt_adapter.transcribe(self.buffer.payload())

    def synthesize(self, text: str) -> TTSChunk:
        if not text:
            raise ValueError("text is required")
        return self.tts_adapter.synthesize(text)


class VoicePipeline:
    def __init__(self, stt_adapter: STTAdapter | None = None, tts_adapter: TTSAdapter | None = None) -> None:
        self.stt_adapter = stt_adapter or StubSTTAdapter()
        self.tts_adapter = tts_adapter or StubTTSAdapter()

    @dataclass(frozen=True)
    class Result:
        transcript: TranscriptResult
        audio: TTSChunk

    def run(self, audio_chunk: bytes, text: str) -> Result:
        session = VoiceSession(self.stt_adapter, self.tts_adapter)
        session.push_audio(audio_chunk)
        transcript = session.transcribe()
        audio = session.synthesize(text)
        return self.Result(transcript=transcript, audio=audio)


def has_speech(chunk: bytes, threshold: int = 8) -> bool:
    return any(abs(byte - 128) >= threshold for byte in chunk)


def timed_transcribe(adapter: STTAdapter, audio: AudioPayload) -> TimedResult:
    started = perf_counter()
    return TimedResult(adapter.transcribe(audio), round((perf_counter() - started) * 1000, 3))


def timed_synthesize(adapter: TTSAdapter, text: str) -> TimedResult:
    started = perf_counter()
    return TimedResult(adapter.synthesize(text), round((perf_counter() - started) * 1000, 3))
