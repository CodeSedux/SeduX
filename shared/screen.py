from __future__ import annotations

from dataclasses import dataclass, field
from datetime import UTC, datetime
from enum import StrEnum
from threading import RLock
from typing import Protocol
from uuid import uuid4


class ScreenCapability(StrEnum):
    CAPTURE = "capture"
    OCR = "ocr"
    CLICK = "click"
    TYPE = "type"
    SUBMIT = "submit"
    SYSTEM = "system"


SENSITIVE_CAPABILITIES = frozenset({ScreenCapability.SUBMIT, ScreenCapability.SYSTEM})


@dataclass(frozen=True)
class ScreenAction:
    capability: ScreenCapability
    target: str
    value: str | None = None
    confirmed: bool = False
    dry_run: bool = True

    def __post_init__(self) -> None:
        if not isinstance(self.capability, ScreenCapability):
            raise ValueError("capability must be a ScreenCapability")
        if not str(self.target or "").strip():
            raise ValueError("target must be a non-empty screen selector")


@dataclass(frozen=True)
class ScreenAuditEvent:
    event_id: str
    actor: str
    action: ScreenAction
    outcome: str
    timestamp: str = field(default_factory=lambda: datetime.now(UTC).isoformat())


class ScreenReader(Protocol):
    def capture(self) -> bytes: ...
    def ocr(self, image: bytes) -> str: ...


class StubScreenReader:
    def capture(self) -> bytes:
        return b"sedux-screen"

    def ocr(self, image: bytes) -> str:
        return image.decode(errors="replace")


class ScreenActionExecutor:
    def __init__(self, capabilities: set[ScreenCapability], max_actions: int = 20) -> None:
        self.capabilities = set(capabilities)
        self.max_actions = max_actions
        self.audit: list[ScreenAuditEvent] = []
        self._stopped = False
        self._lock = RLock()

    def emergency_stop(self) -> None:
        with self._lock:
            self._stopped = True

    def execute(self, actor: str, action: ScreenAction, visible_targets: set[str]) -> ScreenAuditEvent:
        with self._lock:
            if self._stopped:
                return self._record(actor, action, "blocked: emergency stop")
            if len(self.audit) >= self.max_actions:
                return self._record(actor, action, "blocked: rate limit")
            if action.capability not in self.capabilities:
                return self._record(actor, action, "blocked: capability")
            if not str(action.target).strip() or action.target not in visible_targets:
                return self._record(actor, action, "blocked: target not verified")
            if action.capability in SENSITIVE_CAPABILITIES and not action.confirmed:
                return self._record(actor, action, "blocked: confirmation required")
            if action.dry_run:
                return self._record(actor, action, "dry-run")
            return self._record(actor, action, "executed")

    def _record(self, actor: str, action: ScreenAction, outcome: str) -> ScreenAuditEvent:
        event = ScreenAuditEvent(uuid4().hex, actor, action, outcome)
        self.audit.append(event)
        return event
