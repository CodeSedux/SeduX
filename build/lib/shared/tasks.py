from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError


class TaskState(str, Enum):
    QUEUED = "queued"
    RUNNING = "running"
    SUCCEEDED = "succeeded"
    FAILED = "failed"
    CANCELLED = "cancelled"


class TaskType(str, Enum):
    REMINDER = "reminder"
    RECURRING = "recurring"
    AUTOMATION = "automation"
    API_CALL = "api_call"
    AI_TASK = "ai_task"


@dataclass(frozen=True)
class TaskSchedule:
    cron: str | None = None
    timezone: str = "UTC"
    run_at: str | None = None
    recurring: bool = False

    def __post_init__(self) -> None:
        try:
            ZoneInfo(self.timezone)
        except ZoneInfoNotFoundError as error:
            raise ValueError(f"unknown timezone {self.timezone!r}") from error
        if self.recurring:
            if self.run_at is not None or self.cron is None:
                raise ValueError("recurring schedules require cron and cannot define run_at")
            _validate_cron(self.cron)
        elif self.cron is not None:
            raise ValueError("cron schedules must be recurring")
        if self.run_at is not None:
            run_at = _parse_datetime(self.run_at)
            if run_at.tzinfo is None or run_at.utcoffset() is None:
                raise ValueError("run_at must include a UTC offset")

    def is_due(self, now: datetime) -> bool:
        if now.tzinfo is None or now.utcoffset() is None:
            raise ValueError("now must be timezone-aware")
        if self.run_at is not None:
            return _parse_datetime(self.run_at) <= now
        if self.cron is None:
            return True
        localized = now.astimezone(ZoneInfo(self.timezone))
        return _cron_matches(self.cron, localized)

    def to_dict(self) -> dict[str, object]:
        return {
            "cron": self.cron,
            "timezone": self.timezone,
            "run_at": self.run_at,
            "recurring": self.recurring,
        }


def _parse_datetime(value: str) -> datetime:
    try:
        return datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError as error:
        raise ValueError("run_at must be an ISO 8601 timestamp") from error


def _validate_cron(expression: str) -> None:
    fields = expression.split()
    if len(fields) != 5:
        raise ValueError("cron must contain five fields")
    limits = ((0, 59), (0, 23), (1, 31), (1, 12), (0, 6))
    for field_value, (minimum, maximum) in zip(fields, limits, strict=True):
        _cron_values(field_value, minimum, maximum)


def _cron_matches(expression: str, moment: datetime) -> bool:
    values = (moment.minute, moment.hour, moment.day, moment.month, (moment.weekday() + 1) % 7)
    limits = ((0, 59), (0, 23), (1, 31), (1, 12), (0, 6))
    return all(
        value in _cron_values(field_value, minimum, maximum)
        for field_value, value, (minimum, maximum) in zip(expression.split(), values, limits, strict=True)
    )


def _cron_values(field_value: str, minimum: int, maximum: int) -> set[int]:
    values: set[int] = set()
    for part in field_value.split(","):
        base, separator, step_text = part.partition("/")
        try:
            step = int(step_text) if separator else 1
        except ValueError as error:
            raise ValueError(f"invalid cron step {step_text!r}") from error
        if step <= 0:
            raise ValueError("cron step must be positive")
        if base == "*":
            start, end = minimum, maximum
        elif "-" in base:
            start_text, end_text = base.split("-", 1)
            try:
                start, end = int(start_text), int(end_text)
            except ValueError as error:
                raise ValueError(f"invalid cron range {base!r}") from error
        else:
            try:
                start = end = int(base)
            except ValueError as error:
                raise ValueError(f"invalid cron value {base!r}") from error
        if not minimum <= start <= end <= maximum:
            raise ValueError(f"cron field {part!r} is out of range")
        values.update(range(start, end + 1, step))
    return values


@dataclass(frozen=True)
class TaskDefinition:
    task_id: str
    user_id: str
    name: str
    type: TaskType
    state: TaskState = TaskState.QUEUED
    schedule: TaskSchedule = field(default_factory=TaskSchedule)
    payload: dict[str, object] = field(default_factory=dict)
    retries: int = 0
    max_retries: int = 3

    def __post_init__(self) -> None:
        if not self.task_id or not self.user_id or not self.name:
            raise ValueError("task_id, user_id, and name are required")
        if self.retries < 0 or self.max_retries < 0:
            raise ValueError("retries cannot be negative")

    def to_dict(self) -> dict[str, object]:
        return {
            "task_id": self.task_id,
            "user_id": self.user_id,
            "name": self.name,
            "type": self.type.value,
            "state": self.state.value,
            "schedule": self.schedule.to_dict(),
            "payload": self.payload,
            "retries": self.retries,
            "max_retries": self.max_retries,
        }


@dataclass(frozen=True)
class TaskResult:
    task_id: str
    success: bool
    output: str = ""
    error: str | None = None

    def to_dict(self) -> dict[str, object]:
        return {
            "task_id": self.task_id,
            "success": self.success,
            "output": self.output,
            "error": self.error,
        }
