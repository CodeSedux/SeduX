from __future__ import annotations

from collections import defaultdict, deque
from dataclasses import dataclass
from time import monotonic
from typing import Callable
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
