"""Cross-service lifecycle and health orchestration contracts."""

import inspect
from concurrent.futures import ThreadPoolExecutor
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

    @property
    def ready(self) -> bool:
        return self.status == "healthy" and all(service.status == "healthy" for service in self.services)

    def to_dict(self) -> dict[str, Any]:
        return {
            "status": self.status,
            "ready": self.ready,
            "services": [service.to_dict() for service in self.services],
            "checked_at": self.checked_at.isoformat(),
        }


HealthProbe = Callable[[str, dict[str, Any], float], None]
LifecycleHook = Callable[..., Any]


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
    startup_hook: LifecycleHook | None = None
    shutdown_hook: LifecycleHook | None = None


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
        startup_hook: LifecycleHook | None = None,
        shutdown_hook: LifecycleHook | None = None,
    ) -> None:
        if not name:
            raise ValueError("service name is required")
        if name in self._services:
            raise ValueError(f"service {name!r} is already registered")
        port = metadata.get("port")
        if port is None or not isinstance(port, int) or not 1 <= port <= 65535:
            raise ValueError(f"service {name!r} requires a valid port between 1 and 65535")

        resolved_start = startup_hook if startup_hook is not None else start_hook
        resolved_stop = shutdown_hook if shutdown_hook is not None else stop_hook

        self._services[name] = _ManagedService(
            name=name,
            metadata=dict(metadata),
            start_hook=resolved_start,
            stop_hook=resolved_stop,
            startup_hook=resolved_start,
            shutdown_hook=resolved_stop,
        )

    def start(self, name: str, timeout: float | None = None) -> LifecycleState:
        service = self._get(name)
        if service.state is LifecycleState.RUNNING:
            return service.state
        timeout_value = self._timeout if timeout is None else float(timeout)
        if timeout_value <= 0:
            raise ValueError("timeout must be positive")

        service.state = LifecycleState.STARTING
        try:
            self._invoke_hook(service, service.startup_hook or service.start_hook, "startup", timeout_value)
            service.state = LifecycleState.RUNNING
        except Exception:
            service.state = LifecycleState.FAILED
            raise
        return service.state

    def startup(self, name: str, timeout: float | None = None) -> LifecycleState:
        return self.start(name, timeout=timeout)

    def stop(self, name: str, timeout: float | None = None) -> LifecycleState:
        service = self._get(name)
        if service.state is LifecycleState.STOPPED:
            return service.state
        timeout_value = self._timeout if timeout is None else float(timeout)
        if timeout_value <= 0:
            raise ValueError("timeout must be positive")

        service.state = LifecycleState.STOPPING
        try:
            self._invoke_hook(service, service.shutdown_hook or service.stop_hook, "shutdown", timeout_value)
            service.state = LifecycleState.STOPPED
        except Exception:
            service.state = LifecycleState.FAILED
            raise
        return service.state

    def shutdown(self, name: str, timeout: float | None = None) -> LifecycleState:
        return self.stop(name, timeout=timeout)

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

    def _invoke_hook(
        self,
        service: _ManagedService,
        hook: LifecycleHook | None,
        phase: str,
        timeout: float,
    ) -> None:
        if hook is None:
            return

        params = list(inspect.signature(hook).parameters.values())
        has_timeout = any(parameter.name == "timeout" for parameter in params)
        has_metadata = any(parameter.name in {"metadata", "service_metadata", "config"} for parameter in params)

        def runner() -> Any:
            if has_timeout and has_metadata:
                return hook(service.name, service.metadata, timeout=timeout)
            if has_timeout:
                return hook(service.name, service.metadata, timeout)
            if has_metadata:
                return hook(service.name, service.metadata)
            if len(params) >= 2:
                return hook(service.name, service.metadata)
            return hook(service.name)

        with ThreadPoolExecutor(max_workers=1) as executor:
            future = executor.submit(runner)
            try:
                future.result(timeout=timeout)
            except TimeoutError as error:
                raise TimeoutError(f"{phase} hook for {service.name!r} exceeded {timeout} seconds") from error

    def _get(self, name: str) -> _ManagedService:
        try:
            return self._services[name]
        except KeyError as error:
            raise KeyError(f"unknown service {name!r}") from error
