from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime
from typing import Protocol

from shared.home import DeviceState, DeviceType, HomeDevice


SENSITIVE_DEVICE_TYPES = frozenset({DeviceType.LOCK})


class HomeAdapter(Protocol):
    def send(self, device_id: str, capability: str, value: object) -> None: ...


class RecordingHomeAdapter:
    def __init__(self) -> None:
        self.commands: list[tuple[str, str, object]] = []

    def send(self, device_id: str, capability: str, value: object) -> None:
        self.commands.append((device_id, capability, value))


@dataclass(frozen=True)
class HomeCommandResult:
    status: str
    command_id: str


class HomeRuntime:
    def __init__(self, adapter: HomeAdapter, stale_after_seconds: int = 60) -> None:
        self.adapter = adapter
        self.stale_after_seconds = stale_after_seconds
        self.devices: dict[str, HomeDevice] = {}
        self.updated_at: dict[str, datetime] = {}
        self.command_results: dict[str, HomeCommandResult] = {}

    def register(self, device: HomeDevice, updated_at: datetime | None = None) -> None:
        self.devices[device.device_id] = device
        self.updated_at[device.device_id] = updated_at or datetime.now(UTC)

    def command(self, command_id: str, device_id: str, capability: str, value: object, *, confirmed: bool = False) -> HomeCommandResult:
        if command_id in self.command_results:
            return self.command_results[command_id]
        device = self.devices[device_id]
        age = (datetime.now(UTC) - self.updated_at[device_id]).total_seconds()
        if device.state is DeviceState.UNAVAILABLE or age > self.stale_after_seconds:
            raise RuntimeError("device state is unavailable or stale")
        allowed = {item.name for item in device.capabilities}
        if capability not in allowed:
            raise PermissionError("device capability not granted")
        if device.type in SENSITIVE_DEVICE_TYPES and not confirmed:
            raise PermissionError("sensitive home action requires confirmation")
        self.adapter.send(device_id, capability, value)
        result = HomeCommandResult("executed", command_id)
        self.command_results[command_id] = result
        return result
