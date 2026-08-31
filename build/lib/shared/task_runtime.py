"""Dependency-free task lifecycle and execution runtime."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from threading import RLock
from typing import Callable

from shared.tasks import TaskDefinition, TaskResult, TaskState


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

    def create(self, task: TaskDefinition) -> TaskDefinition:
        with self._lock:
            if task.task_id in self._tasks:
                existing = self._tasks[task.task_id]
                if existing == task:
                    return existing
                raise ValueError(f"task {task.task_id!r} already exists")
            self._tasks[task.task_id] = task
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
            self._history.setdefault(task_id, []).append(execution)
            if state is TaskState.FAILED:
                self._dead_letters.append(execution)
            return execution

        with self._lock:
            completed = self._replace(running, state=TaskState.SUCCEEDED)
            self._tasks[task_id] = completed
        execution = TaskExecution(completed, TaskResult(task_id, True, output=output))
        self._history.setdefault(task_id, []).append(execution)
        return execution

    def history(self, task_id: str) -> tuple[TaskExecution, ...]:
        return tuple(self._history.get(task_id, ()))

    def dead_letters(self) -> tuple[TaskExecution, ...]:
        return tuple(self._dead_letters)

    @staticmethod
    def _default_executor(task: TaskDefinition) -> str:
        return f"Task {task.name} completed"

    @staticmethod
    def _replace(task: TaskDefinition, **changes: object) -> TaskDefinition:
        values = task.__dict__ | changes
        return TaskDefinition(**values)
