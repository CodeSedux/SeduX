"""Dependency-free contracts for the SeduX control plane."""

from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from typing import Any


@dataclass(frozen=True)
class ServiceStatus:
    name: str
    status: str
    version: str = "0.1.0"
    port: int | None = None
    kind: str = "internal"

    def to_dict(self) -> dict[str, Any]:
        payload = asdict(self)
        if payload["port"] is None:
            payload.pop("port")
        return payload


SERVICE_NAMES = (
    "gateway",
    "voice",
    "avatar",
    "llm",
    "emotion",
    "task",
    "home",
    "screen",
)

SERVICE_REGISTRY: dict[str, dict[str, Any]] = {
    "gateway": {"name": "gateway", "port": 8080, "kind": "control-plane"},
    "voice": {"name": "voice", "port": 8001, "kind": "service"},
    "avatar": {"name": "avatar", "port": 8002, "kind": "service"},
    "llm": {"name": "llm", "port": 8003, "kind": "service"},
    "emotion": {"name": "emotion", "port": 8004, "kind": "service"},
    "task": {"name": "task", "port": 8005, "kind": "service"},
    "home": {"name": "home", "port": 8006, "kind": "service"},
    "screen": {"name": "screen", "port": 8007, "kind": "service"},
}


def build_service_statuses(status: str = "planned") -> list[dict[str, Any]]:
    entries: list[dict[str, Any]] = []
    for name in SERVICE_NAMES:
        metadata = SERVICE_REGISTRY[name]
        entries.append(
            ServiceStatus(
                name=name,
                status="ok" if name == "gateway" else status,
                version="0.1.0",
                port=metadata["port"],
                kind=metadata["kind"],
            ).to_dict()
        )
    return entries


def health_payload(service: str) -> dict[str, Any]:
    return {
        "service": service,
        "status": "ok",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "version": "0.1.0",
    }