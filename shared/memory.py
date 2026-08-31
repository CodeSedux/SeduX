from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum


class MemoryScope(str, Enum):
    USER = "user"
    SESSION = "session"
    SYSTEM = "system"


class MemoryOperation(str, Enum):
    CREATE = "create"
    READ = "read"
    UPDATE = "update"
    DELETE = "delete"
    EXPORT = "export"


@dataclass(frozen=True)
class MemoryEntry:
    user_id: str
    scope: MemoryScope
    operation: MemoryOperation
    key: str
    value: str
    summary: str = ""
    metadata: dict[str, str] = field(default_factory=dict)
    expires_at: str | None = None

    def __post_init__(self) -> None:
        if not self.user_id or not self.key:
            raise ValueError("user_id and key are required")
        if self.expires_at is not None and not isinstance(self.expires_at, str):
            raise TypeError("expires_at must be an ISO timestamp string or None")

    def to_dict(self) -> dict[str, object]:
        return {
            "user_id": self.user_id,
            "scope": self.scope.value,
            "operation": self.operation.value,
            "key": self.key,
            "value": self.value,
            "summary": self.summary,
            "metadata": self.metadata,
            "expires_at": self.expires_at,
        }
