from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum


class DeviceType(str, Enum):
    LIGHT = "light"
    CLIMATE = "climate"
    SENSOR = "sensor"
    COVER = "cover"
    LOCK = "lock"
    MEDIA = "media"
    SWITCH = "switch"


class DeviceState(str, Enum):
    ONLINE = "online"
    OFFLINE = "offline"
    UNAVAILABLE = "unavailable"
    ACTIVE = "active"
    INACTIVE = "inactive"


@dataclass(frozen=True)
class DeviceCapability:
    name: str
    value: str | float | bool | None = None

    def to_dict(self) -> dict[str, object]:
        return {"name": self.name, "value": self.value}


@dataclass(frozen=True)
class HomeDevice:
    device_id: str
    name: str
    type: DeviceType
    room: str
    state: DeviceState = DeviceState.ONLINE
    capabilities: list[DeviceCapability] = field(default_factory=list)
    metadata: dict[str, object] = field(default_factory=dict)

    def to_dict(self) -> dict[str, object]:
        return {
            "device_id": self.device_id,
            "name": self.name,
            "type": self.type.value,
            "room": self.room,
            "state": self.state.value,
            "capabilities": [cap.to_dict() for cap in self.capabilities],
            "metadata": self.metadata,
        }


@dataclass(frozen=True)
class HomeScene:
    scene_id: str
    name: str
    room: str | None = None
    device_targets: dict[str, dict[str, object]] = field(default_factory=dict)

    def to_dict(self) -> dict[str, object]:
        return {
            "scene_id": self.scene_id,
            "name": self.name,
            "room": self.room,
            "device_targets": self.device_targets,
        }
