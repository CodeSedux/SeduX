from __future__ import annotations

from dataclasses import dataclass, field
from enum import StrEnum
from statistics import fmean


class AvatarState(StrEnum):
    IDLE = "idle"
    LISTENING = "listening"
    THINKING = "thinking"
    SPEAKING = "speaking"
    ERROR = "error"


ALLOWED_TRANSITIONS: dict[AvatarState, frozenset[AvatarState]] = {
    AvatarState.IDLE: frozenset({AvatarState.LISTENING, AvatarState.THINKING, AvatarState.SPEAKING, AvatarState.ERROR}),
    AvatarState.LISTENING: frozenset({AvatarState.IDLE, AvatarState.THINKING, AvatarState.ERROR}),
    AvatarState.THINKING: frozenset({AvatarState.IDLE, AvatarState.SPEAKING, AvatarState.ERROR}),
    AvatarState.SPEAKING: frozenset({AvatarState.IDLE, AvatarState.LISTENING, AvatarState.ERROR}),
    AvatarState.ERROR: frozenset({AvatarState.IDLE}),
}

VISEME_TO_BLEND_SHAPE = {
    "sil": "mouthClose",
    "aa": "jawOpen",
    "ee": "mouthSmile",
    "oh": "mouthFunnel",
    "ou": "mouthPucker",
}


@dataclass(frozen=True)
class AvatarFrame:
    sequence: int
    state: AvatarState
    blend_shapes: dict[str, float] = field(default_factory=dict)
    gesture: str | None = None

    def __post_init__(self) -> None:
        if self.sequence < 0 or any(not 0 <= value <= 1 for value in self.blend_shapes.values()):
            raise ValueError("sequence and blend shape weights must be valid")


class AvatarRuntime:
    def __init__(self, slow_frame_ms: float = 25.0) -> None:
        self.state = AvatarState.IDLE
        self.frames: list[AvatarFrame] = []
        self.frame_times: list[float] = []
        self.slow_frame_ms = slow_frame_ms

    def transition(self, state: AvatarState) -> AvatarState:
        if state is self.state:
            return state
        if state not in ALLOWED_TRANSITIONS[self.state]:
            raise ValueError(f"invalid avatar transition: {self.state} -> {state}")
        self.state = state
        return state

    def record(self, blend_shapes: dict[str, float], gesture: str | None = None) -> AvatarFrame:
        frame = AvatarFrame(len(self.frames), self.state, dict(blend_shapes), gesture)
        self.frames.append(frame)
        return frame

    def map_viseme(self, viseme: str, weight: float) -> dict[str, float]:
        if viseme not in VISEME_TO_BLEND_SHAPE:
            raise ValueError(f"unsupported viseme {viseme!r}")
        return {VISEME_TO_BLEND_SHAPE[viseme]: max(0.0, min(1.0, weight))}

    def replay(self) -> tuple[AvatarFrame, ...]:
        return tuple(self.frames)

    def observe_frame_time(self, milliseconds: float) -> None:
        if milliseconds < 0:
            raise ValueError("frame time cannot be negative")
        self.frame_times.append(milliseconds)

    @property
    def low_performance(self) -> bool:
        return bool(self.frame_times) and fmean(self.frame_times[-60:]) > self.slow_frame_ms
