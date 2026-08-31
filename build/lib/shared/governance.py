from __future__ import annotations

from dataclasses import dataclass, field

from shared.security import AccessScope


@dataclass(frozen=True)
class ConsentRecord:
    user_id: str
    purpose: str
    granted: bool
    scopes: list[AccessScope] = field(default_factory=list)
    created_at: str | None = None

    def to_dict(self) -> dict[str, object]:
        return {
            "user_id": self.user_id,
            "purpose": self.purpose,
            "granted": self.granted,
            "scopes": [scope.value for scope in self.scopes],
            "created_at": self.created_at,
        }


@dataclass(frozen=True)
class AuditEvent:
    actor: str
    action: str
    entity: str
    details: dict[str, object] = field(default_factory=dict)
    timestamp: str | None = None

    def to_dict(self) -> dict[str, object]:
        return {
            "actor": self.actor,
            "action": self.action,
            "entity": self.entity,
            "details": self.details,
            "timestamp": self.timestamp,
        }


@dataclass(frozen=True)
class RetentionPolicy:
    purpose: str
    ttl_days: int
    mode: str = "delete_after"

    def to_dict(self) -> dict[str, object]:
        return {
            "purpose": self.purpose,
            "ttl_days": self.ttl_days,
            "mode": self.mode,
        }
