from __future__ import annotations

from collections import deque
from dataclasses import replace
from typing import Protocol

from shared.memory import MemoryEntry, MemoryOperation, MemoryScope


SENSITIVE_KEYS = frozenset({"password", "secret", "token", "api_key"})


class EmbeddingAdapter(Protocol):
    def embed(self, text: str) -> tuple[float, ...]: ...


class GraphAdapter(Protocol):
    def link(self, user_id: str, source: str, target: str) -> None: ...


class ShortTermContext:
    def __init__(self, max_messages: int = 20) -> None:
        self._messages: deque[str] = deque(maxlen=max_messages)

    def add(self, message: str) -> None:
        if message:
            self._messages.append(message)

    def snapshot(self) -> tuple[str, ...]:
        return tuple(self._messages)


class MemoryStore:
    def __init__(self) -> None:
        self._entries: dict[tuple[str, str], MemoryEntry] = {}

    def create(self, entry: MemoryEntry) -> MemoryEntry:
        if entry.scope is MemoryScope.SYSTEM:
            raise PermissionError("users cannot create system memory")
        if any(part in entry.key.lower() for part in SENSITIVE_KEYS):
            raise ValueError("sensitive values cannot be persisted")
        identity = (entry.user_id, entry.key)
        if identity in self._entries:
            raise ValueError("memory already exists")
        stored = replace(entry, operation=MemoryOperation.CREATE)
        self._entries[identity] = stored
        return stored

    def get(self, user_id: str, key: str) -> MemoryEntry:
        try:
            return self._entries[(user_id, key)]
        except KeyError as error:
            raise KeyError("memory not found") from error

    def correct(self, user_id: str, key: str, value: str) -> MemoryEntry:
        updated = replace(self.get(user_id, key), value=value, operation=MemoryOperation.UPDATE)
        self._entries[(user_id, key)] = updated
        return updated

    def export(self, user_id: str) -> list[dict[str, object]]:
        return [entry.to_dict() for (owner, _), entry in self._entries.items() if owner == user_id]

    def delete(self, user_id: str, key: str) -> None:
        del self._entries[(user_id, key)]
