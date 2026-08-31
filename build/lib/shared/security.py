from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
import re


class AccessScope(str, Enum):
    VOICE = "voice"
    MEMORY = "memory"
    HOME = "home"
    SCREEN = "screen"
    TASKS = "tasks"


@dataclass(frozen=True)
class SecurityPrinciple:
    subject: str
    scopes: list[AccessScope]
    active: bool = True

    def to_dict(self) -> dict[str, object]:
        return {
            "subject": self.subject,
            "scopes": [scope.value for scope in self.scopes],
            "active": self.active,
        }


def redact_sensitive_text(text: str) -> str:
    redacted = re.sub(r"(?i)token\s+[A-Za-z0-9]+", "Token [REDACTED]", text)
    redacted = re.sub(r"(?i)\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b", "[EMAIL]", redacted)
    redacted = re.sub(r"(?i)api[_-]?key\s*[:=]\s*[A-Za-z0-9._-]+", "api_key=[REDACTED]", redacted)
    return redacted
