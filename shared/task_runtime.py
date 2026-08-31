"""Dependency-free task lifecycle and execution runtime."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from threading import RLock
from typing import Callable

from shared.tasks import TaskDefinition, TaskResult, TaskState, _parse_datetime


TaskExecutor = Callable[[TaskDefinition], str]


@dataclass(frozen=True)
class TaskExecution:
    definition: TaskDefinition
    result: TaskResult


class TaskManager:
    def __init__(self, executor: TaskExecutor | None = None) -> None:
        self._tasks: dict[str, TaskDefinition] = {}
        self._lock = RLock()
        self._executor = executor or self._default_executor
        self._history: dict[str, list[TaskExecution]] = {}
        self._dead_letters: list[TaskExecution] = []
        self._idempotency_index: dict[str, str] = {}

    def create(self, task: TaskDefinition) -> TaskDefinition:
        with self._lock:
            if task.task_id in self._tasks:
                existing = self._tasks[task.task_id]
                if existing == task:
                    return existing
                raise ValueError(f"task {task.task_id!r} already exists")
            idempotency_key = self._extract_idempotency_key(task)
            if idempotency_key is not None:
                existing_task_id = self._idempotency_index.get(idempotency_key)
                if existing_task_id is not None and existing_task_id != task.task_id:
                    raise ValueError(f"idempotency key {idempotency_key!r} already exists")
            self._tasks[task.task_id] = task
            if idempotency_key is not None:
                self._idempotency_index[idempotency_key] = task.task_id
            return task

    def list(self, user_id: str | None = None) -> list[TaskDefinition]:
        with self._lock:
            tasks = list(self._tasks.values())
        if user_id is not None:
            tasks = [task for task in tasks if task.user_id == user_id]
        return tasks

    def get(self, task_id: str) -> TaskDefinition:
        with self._lock:
            try:
                return self._tasks[task_id]
            except KeyError as error:
                raise KeyError(f"unknown task {task_id!r}") from error

    def due(self, now: datetime) -> list[TaskDefinition]:
        with self._lock:
            tasks = tuple(self._tasks.values())
        return [task for task in tasks if task.state is TaskState.QUEUED and task.schedule.is_due(now)]

    def pause(self, task_id: str) -> TaskDefinition:
        with self._lock:
            task = self.get(task_id)
            if task.state in {TaskState.CANCELLED, TaskState.SUCCEEDED}:
                return task
            updated = self._replace(task, state=TaskState.PAUSED)
            self._tasks[task_id] = updated
            return updated

    def resume(self, task_id: str) -> TaskDefinition:
        with self._lock:
            task = self.get(task_id)
            if task.state not in {TaskState.PAUSED, TaskState.QUEUED}:
                return task
            updated = self._replace(task, state=TaskState.QUEUED)
            self._tasks[task_id] = updated
            return updated

    def retry(self, task_id: str) -> TaskDefinition:
        with self._lock:
            task = self.get(task_id)
            if task.state in {TaskState.CANCELLED, TaskState.SUCCEEDED}:
                return task
            updated = self._replace(task, state=TaskState.QUEUED, retries=0)
            self._tasks[task_id] = updated
            return updated

    def cancel(self, task_id: str) -> TaskDefinition:
        with self._lock:
            task = self.get(task_id)
            if task.state in {TaskState.SUCCEEDED, TaskState.CANCELLED}:
                return task
            updated = self._replace(task, state=TaskState.CANCELLED)
            self._tasks[task_id] = updated
            return updated

    def execute(self, task_id: str) -> TaskExecution:
        with self._lock:
            task = self.get(task_id)
            history = self._history.get(task_id, ())
            if task.state is TaskState.PAUSED:
                return TaskExecution(task, TaskResult(task_id, False, error="task paused"))
            if task.state is TaskState.RUNNING:
                return TaskExecution(task, TaskResult(task_id, False, error="task already running"))
            if task.state is TaskState.SUCCEEDED and history:
                return history[-1]
            if task.state in {TaskState.CANCELLED, TaskState.SUCCEEDED}:
                return TaskExecution(task, TaskResult(task_id, task.state is TaskState.SUCCEEDED))
            running = self._replace(task, state=TaskState.RUNNING)
            self._tasks[task_id] = running

        try:
            output = self._executor(running)
        except Exception as error:
            with self._lock:
                retries = running.retries + 1
                state = TaskState.QUEUED if retries <= running.max_retries else TaskState.FAILED
                failed = self._replace(running, state=state, retries=retries)
                self._tasks[task_id] = failed
            execution = TaskExecution(failed, TaskResult(task_id, False, error=str(error)))
            if not self._history.get(task_id):
                self._history.setdefault(task_id, []).append(execution)
            else:
                self._history[task_id].append(execution)
            if state is TaskState.FAILED:
                self._dead_letters.append(execution)
            return execution

        with self._lock:
            completed = self._replace(running, state=TaskState.SUCCEEDED)
            self._tasks[task_id] = completed
        execution = TaskExecution(completed, TaskResult(task_id, True, output=output))
        prior = self._history.setdefault(task_id, [])
        if not prior:
            prior.append(execution)
        elif prior[-1].result.success is not True or prior[-1].definition.task_id != task_id:
            prior.append(execution)
        return prior[-1]

    def history(self, task_id: str) -> tuple[TaskExecution, ...]:
        return tuple(self._history.get(task_id, ()))

    def dead_letters(self) -> tuple[TaskExecution, ...]:
        return tuple(self._dead_letters)

    def find_conflicts(self) -> list[tuple[TaskDefinition, TaskDefinition]]:
        tasks = tuple(self._tasks.values())
        conflicts: list[tuple[TaskDefinition, TaskDefinition]] = []
        for index, left in enumerate(tasks):
            for right in tasks[index + 1:]:
                if left.user_id != right.user_id:
                    continue
                if left.task_id == right.task_id:
                    continue
                if self._is_conflicting(left, right):
                    conflicts.append((left, right))
        return conflicts

    @staticmethod
    def _is_conflicting(left: TaskDefinition, right: TaskDefinition) -> bool:
        left_resource = left.payload.get("resource") if isinstance(left.payload, dict) else None
        right_resource = right.payload.get("resource") if isinstance(right.payload, dict) else None
        if left_resource is not None and right_resource is not None and left_resource != right_resource:
            return False

        left_time = TaskManager._schedule_time(left)
        right_time = TaskManager._schedule_time(right)
        if left_time is None or right_time is None:
            if left.schedule.recurring and right.schedule.recurring:
                return bool(left.schedule.cron and right.schedule.cron and left.schedule.timezone == right.schedule.timezone and left.schedule.cron == right.schedule.cron)
            return False
        return left_time == right_time

    @staticmethod
    def _schedule_time(task: TaskDefinition) -> datetime | None:
        if task.schedule.run_at is None:
            return None
        try:
            return _parse_datetime(task.schedule.run_at)
        except ValueError:
            return None

    @staticmethod
    def _default_executor(task: TaskDefinition) -> str:
        return f"Task {task.name} completed"

    @staticmethod
    def _extract_idempotency_key(task: TaskDefinition) -> str | None:
        payload = task.payload if isinstance(task.payload, dict) else {}
        key = payload.get("idempotency_key")
        if isinstance(key, str) and key:
            return key
        return None

    @staticmethod
    def _replace(task: TaskDefinition, **changes: object) -> TaskDefinition:
        values = task.__dict__ | changes
        return TaskDefinition(**values)


class TaskScheduler:
    def __init__(self, manager: TaskManager | None = None) -> None:
        self.manager = manager or TaskManager()

    def poll(self, now: datetime) -> list[TaskDefinition]:
        return self.manager.due(now)

    def dispatch_due(self, now: datetime) -> list[TaskExecution]:
        executions: list[TaskExecution] = []
        for task in self.poll(now):
            executions.append(self.manager.execute(task.task_id))
        return executions
