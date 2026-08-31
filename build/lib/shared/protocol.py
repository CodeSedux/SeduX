from __future__ import annotations

from dataclasses import dataclass, field
from datetime import UTC, datetime
from typing import Generic, TypeVar
from uuid import uuid4


API_VERSION = "v1"
PayloadT = TypeVar("PayloadT")


def new_request_id() -> str:
    return uuid4().hex


@dataclass(frozen=True)
class ApiEnvelope(Generic[PayloadT]):
    data: PayloadT
    request_id: str = field(default_factory=new_request_id)
    version: str = API_VERSION
    timestamp: str = field(default_factory=lambda: datetime.now(UTC).isoformat())

    def to_dict(self) -> dict[str, object]:
        return {
            "version": self.version,
            "request_id": self.request_id,
            "timestamp": self.timestamp,
            "data": self.data,
        }


@dataclass(frozen=True)
class StreamEvent:
    type: str
    payload: dict[str, object]
    sequence: int
    request_id: str
    version: str = API_VERSION

    def __post_init__(self) -> None:
        if not self.type or not self.request_id or self.sequence < 0:
            raise ValueError("type, request_id, and a non-negative sequence are required")

    def to_dict(self) -> dict[str, object]:
        return {
            "version": self.version,
            "type": self.type,
            "sequence": self.sequence,
            "request_id": self.request_id,
            "payload": self.payload,
        }