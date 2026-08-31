"""Cross-service lifecycle and health orchestration contracts."""

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import StrEnum
from time import monotonic
from typing import Any, Callable
from urllib.request import urlopen

from shared.contracts import SERVICE_REGISTRY


class LifecycleState(StrEnum):
    REGISTERED = "registered"
    STARTING = "starting"
    RUNNING = "running"
    STOPPING = "stopping"
    STOPPED = "stopped"
    FAILED = "failed"


@dataclass(frozen=True)
class ServiceHealth:
    name: str
    state: LifecycleState
    status: str
    latency_ms: float | None = None
    error: str | None = None
    checked_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    def to_dict(self) -> dict[str, Any]:
        return {
            "name": self.name,
            "state": self.state.value,
            "status": self.status,
            "latency_ms": self.latency_ms,
            "error": self.error,
            "checked_at": self.checked_at.isoformat(),
        }


@dataclass(frozen=True)
class OrchestrationReport:
    status: str
    services: tuple[ServiceHealth, ...]
    checked_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    def to_dict(self) -> dict[str, Any]:
        return {
            "status": self.status,
            "services": [service.to_dict() for service in self.services],
            "checked_at": self.checked_at.isoformat(),
        }


HealthProbe = Callable[[str, dict[str, Any], float], None]
LifecycleHook = Callable[[str], None]


def http_health_probe(name: str, metadata: dict[str, Any], timeout: float) -> None:
    """Raise when a service does not return a successful health response."""
    port = metadata.get("port")
    if port is None:
        raise ValueError(f"Service {name!r} has no health port")
    with urlopen(f"http://127.0.0.1:{port}/health", timeout=timeout) as response:
        if response.status < 200 or response.status >= 300:
            raise RuntimeError(f"health endpoint returned HTTP {response.status}")


@dataclass
class _ManagedService:
    name: str
    metadata: dict[str, Any]
    state: LifecycleState = LifecycleState.REGISTERED
    start_hook: LifecycleHook | None = None
    stop_hook: LifecycleHook | None = None


class ServiceOrchestrator:
    """Track service lifecycle and aggregate health without owning process creation."""

    def __init__(
        self,
        registry: dict[str, dict[str, Any]] | None = None,
        probe: HealthProbe = http_health_probe,
        timeout: float = 1.0,
    ) -> None:
        self._registry = SERVICE_REGISTRY if registry is None else registry
        self._probe = probe
        self._timeout = timeout
        self._services = {
            name: _ManagedService(name=name, metadata=dict(metadata))
            for name, metadata in self._registry.items()
        }

    def register(
        self,
        name: str,
        metadata: dict[str, Any],
        *,
        start_hook: LifecycleHook | None = None,
        stop_hook: LifecycleHook | None = None,
    ) -> None:
        if not name:
            raise ValueError("service name is required")
        if name in self._services:
            raise ValueError(f"service {name!r} is already registered")
        self._services[name] = _ManagedService(
            name=name,
            metadata=dict(metadata),
            start_hook=start_hook,
            stop_hook=stop_hook,
        )

    def start(self, name: str) -> LifecycleState:
        service = self._get(name)
        if service.state is LifecycleState.RUNNING:
            return service.state
        service.state = LifecycleState.STARTING
        try:
            if service.start_hook:
                service.start_hook(name)
            service.state = LifecycleState.RUNNING
        except Exception:
            service.state = LifecycleState.FAILED
            raise
        return service.state

    def stop(self, name: str) -> LifecycleState:
        service = self._get(name)
        if service.state is LifecycleState.STOPPED:
            return service.state
        service.state = LifecycleState.STOPPING
        try:
            if service.stop_hook:
                service.stop_hook(name)
            service.state = LifecycleState.STOPPED
        except Exception:
            service.state = LifecycleState.FAILED
            raise
        return service.state

    def check(self, name: str) -> ServiceHealth:
        service = self._get(name)
        started = monotonic()
        try:
            self._probe(service.name, service.metadata, self._timeout)
        except Exception as error:
            service.state = LifecycleState.FAILED
            return ServiceHealth(
                name=service.name,
                state=service.state,
                status="unhealthy",
                latency_ms=round((monotonic() - started) * 1000, 2),
                error=str(error),
            )

        if service.state not in {LifecycleState.STOPPED, LifecycleState.STOPPING}:
            service.state = LifecycleState.RUNNING
        return ServiceHealth(
            name=service.name,
            state=service.state,
            status="healthy",
            latency_ms=round((monotonic() - started) * 1000, 2),
        )

    def check_all(self) -> OrchestrationReport:
        services = tuple(self.check(name) for name in self._services)
        healthy = sum(service.status == "healthy" for service in services)
        if healthy == len(services):
            status = "healthy"
        elif healthy == 0:
            status = "unavailable"
        else:
            status = "degraded"
        return OrchestrationReport(status=status, services=services)

    def _get(self, name: str) -> _ManagedService:
        try:
            return self._services[name]
        except KeyError as error:
            raise KeyError(f"unknown service {name!r}") from error
