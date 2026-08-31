from __future__ import annotations

from collections import defaultdict, deque
from dataclasses import dataclass
from datetime import datetime, timezone
import os
from time import monotonic
from typing import Any, Callable, Mapping
from urllib.parse import urlparse
from urllib.request import urlopen


class SlidingWindowRateLimiter:
    def __init__(self, limit: int, window_seconds: float = 60) -> None:
        if limit < 1 or window_seconds <= 0:
            raise ValueError("limit and window must be positive")
        self.limit = limit
        self.window_seconds = window_seconds
        self._events: dict[str, deque[float]] = defaultdict(deque)

    def allow(self, key: str, now: float | None = None) -> bool:
        current = monotonic() if now is None else now
        events = self._events[key]
        while events and events[0] <= current - self.window_seconds:
            events.popleft()
        if len(events) >= self.limit:
            return False
        events.append(current)
        return True


class MetricsRegistry:
    def __init__(self) -> None:
        self.counters: dict[str, int] = defaultdict(int)
        self.observations: dict[str, list[float]] = defaultdict(list)

    def increment(self, name: str, amount: int = 1) -> None:
        self.counters[name] += amount

    def observe(self, name: str, value: float) -> None:
        self.observations[name].append(value)

    def snapshot(self) -> dict[str, object]:
        return {"counters": dict(self.counters), "observations": dict(self.observations)}


class StructuredLogger:
    def __init__(self, service: str) -> None:
        if not service:
            raise ValueError("service name is required")
        self.service = service
        self._events: list[dict[str, Any]] = []

    def emit(self, event: str, message: str, **fields: Any) -> dict[str, Any]:
        payload = {
            "service": self.service,
            "event": event,
            "message": message,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }
        payload.update(fields)
        self._events.append(payload)
        return payload

    def snapshot(self) -> list[dict[str, Any]]:
        return list(self._events)


@dataclass(frozen=True)
class DependencyStatus:
    name: str
    ready: bool
    detail: str


def tcp_like_readiness(name: str, url: str, timeout: float = 1.0, opener: Callable = urlopen) -> DependencyStatus:
    try:
        with opener(url, timeout=timeout):
            return DependencyStatus(name, True, "reachable")
    except Exception as error:
        return DependencyStatus(name, False, str(error))


def redis_readiness(
    name: str,
    url: str,
    timeout: float = 1.0,
    ping: Callable[[str], bool] | None = None,
) -> DependencyStatus:
    if not name or not url:
        raise ValueError("name and redis url are required")
    try:
        parsed = urlparse(url)
        if ping is not None:
            ready = bool(ping(url))
        else:
            ready = bool(parsed.scheme in {"redis", "rediss"} and parsed.netloc)
        if ready:
            return DependencyStatus(name, True, f"redis reachable at {url} (timeout={timeout})")
        return DependencyStatus(name, False, f"redis unreachable at {url}")
    except Exception as error:
        return DependencyStatus(name, False, str(error))


def validate_deployment_environment(env: Mapping[str, str] | None = None) -> bool:
    source = os.environ if env is None else env
    required = {
        "SEDUX_ENV": str(source.get("SEDUX_ENV", "")).strip(),
        "SEDUX_AUTH_SECRET": str(source.get("SEDUX_AUTH_SECRET", "")).strip(),
        "DATABASE_URL": str(source.get("DATABASE_URL", "")).strip(),
        "REDIS_URL": str(source.get("REDIS_URL", "")).strip(),
    }

    if not required["SEDUX_ENV"] or required["SEDUX_ENV"] not in {"development", "staging", "production"}:
        return False
    if len(required["SEDUX_AUTH_SECRET"]) < 32:
        return False

    database_url = urlparse(required["DATABASE_URL"])
    redis_url = urlparse(required["REDIS_URL"])
    if database_url.scheme not in {"postgresql", "postgres"} or not database_url.hostname:
        return False
    if redis_url.scheme not in {"redis", "rediss"} or not redis_url.hostname:
        return False

    return True


def build_backup_command(database_name: str, output_path: str, database_url: str | None = None) -> str:
    if not database_name or not output_path:
        raise ValueError("database_name and output_path are required")

    resolved_url = database_url or os.getenv("DATABASE_URL", "postgresql://sedux:sedux@postgres:5432/sedux")
    return (
        f"pg_dump --format=custom --dbname='{resolved_url}' --file='{output_path}' "
        f"--verbose --clean --if-exists"
    )


def build_restore_command(dump_path: str, target_database: str, source_database: str | None = None) -> str:
    if not dump_path or not target_database:
        raise ValueError("dump_path and target_database are required")

    source = source_database or target_database
    return (
        f"createdb {target_database} && "
        f"pg_restore --clean --if-exists --dbname={target_database} {dump_path} "
        f"&& psql -d {source} -c '\\dt'"
    )
