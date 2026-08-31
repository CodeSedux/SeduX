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

    def to_dict(self) -> dict[str, object]:
        return {
            "user_id": self.user_id,
            "scope": self.scope.value,
            "operation": self.operation.value,
            "key": self.key,
            "value": self.value,
            "summary": self.summary,
            "metadata": self.metadata,
        }
