"""Dependency-free contracts for PostgreSQL and Redis persistence."""

from __future__ import annotations

from collections import defaultdict, deque
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import StrEnum
from threading import RLock
from time import monotonic
from typing import Any


class PostgresTable(StrEnum):
    USERS = "users"
    CONVERSATIONS = "conversations"
    MESSAGES = "messages"
    TASKS = "tasks"
    MEMORY_ENTRIES = "memory_entries"
    AUDIT_EVENTS = "audit_events"


@dataclass(frozen=True)
class TableDefinition:
    name: PostgresTable
    columns: tuple[str, ...]
    primary_key: str = "id"


POSTGRES_SCHEMA: tuple[TableDefinition, ...] = (
    TableDefinition(PostgresTable.USERS, ("id", "external_id", "created_at")),
    TableDefinition(
        PostgresTable.CONVERSATIONS,
        ("id", "user_id", "title", "created_at", "updated_at"),
    ),
    TableDefinition(
        PostgresTable.MESSAGES,
        ("id", "conversation_id", "role", "content", "created_at"),
    ),
    TableDefinition(
        PostgresTable.TASKS,
        ("id", "user_id", "task_type", "state", "payload", "created_at", "updated_at"),
    ),
    TableDefinition(
        PostgresTable.MEMORY_ENTRIES,
        ("id", "user_id", "scope", "content", "created_at", "expires_at"),
    ),
    TableDefinition(
        PostgresTable.AUDIT_EVENTS,
        ("id", "user_id", "action", "resource", "metadata", "created_at"),
    ),
)


class RedisNamespace(StrEnum):
    SESSION = "session"
    RATE_LIMIT = "rate-limit"
    TASK_QUEUE = "task-queue"
    TASK_RESULT = "task-result"


@dataclass(frozen=True)
class RedisKey:
    namespace: RedisNamespace
    identifier: str

    def render(self) -> str:
        if not self.identifier or ":" in self.identifier:
            raise ValueError("Redis key identifiers must be non-empty and cannot contain ':'")
        return f"sedux:{self.namespace}:{self.identifier}"


@dataclass(frozen=True)
class QueueEnvelope:
    queue: str
    task_id: str
    payload: dict[str, Any]
    attempt: int = 1
    enqueued_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    def __post_init__(self) -> None:
        if not self.queue or not self.task_id:
            raise ValueError("queue and task_id are required")
        if self.attempt < 1:
            raise ValueError("attempt must be positive")

    def to_dict(self) -> dict[str, Any]:
        return {
            "queue": self.queue,
            "task_id": self.task_id,
            "payload": self.payload,
            "attempt": self.attempt,
            "enqueued_at": self.enqueued_at.isoformat(),
        }


@dataclass(frozen=True)
class RateLimitDecision:
    allowed: bool
    retry_after: float = 0.0


class RedisQueue:
    def __init__(self, name: str) -> None:
        if not name:
            raise ValueError("queue name is required")
        self.name = name
        self._lock = RLock()
        self._queue: deque[QueueEnvelope] = deque()

    def enqueue(self, envelope: QueueEnvelope) -> QueueEnvelope:
        if envelope.queue != self.name:
            raise ValueError("queue envelope does not belong to this queue")
        with self._lock:
            self._queue.append(envelope)
            return envelope

    def dequeue(self, max_items: int = 1) -> list[QueueEnvelope]:
        if max_items < 1:
            raise ValueError("max_items must be positive")
        with self._lock:
            items = [self._queue.popleft() for _ in range(min(max_items, len(self._queue)))]
            return items

    def pending(self) -> int:
        with self._lock:
            return len(self._queue)


class RedisBackedRateLimiter:
    def __init__(self, limit: int, window_seconds: float = 60.0) -> None:
        if limit < 1 or window_seconds <= 0:
            raise ValueError("limit and window must be positive")
        self.limit = limit
        self.window_seconds = window_seconds
        self._lock = RLock()
        self._events: dict[str, deque[float]] = defaultdict(deque)

    def allow(self, key: str, now: float | None = None) -> RateLimitDecision:
        if not key:
            raise ValueError("rate limit key is required")
        current = monotonic() if now is None else float(now)
        with self._lock:
            events = self._events[key]
            while events and events[0] <= current - self.window_seconds:
                events.popleft()
            if len(events) >= self.limit:
                retry_after = max(0.0, (events[0] + self.window_seconds) - current)
                return RateLimitDecision(False, retry_after)
            events.append(current)
            return RateLimitDecision(True, 0.0)
