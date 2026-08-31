import unittest
import json
import threading
from datetime import UTC, datetime
from urllib.error import HTTPError
from urllib.request import Request, urlopen

from services.task.main import create_server
from shared.task_runtime import TaskManager
from shared.tasks import TaskDefinition, TaskSchedule, TaskState, TaskType


def make_task(task_id="task-1", user_id="user-1"):
    return TaskDefinition(task_id, user_id, "Briefing", TaskType.REMINDER)


class TaskRuntimeTests(unittest.TestCase):
    def test_create_is_idempotent_and_listing_is_user_scoped(self) -> None:
        manager = TaskManager()
        task = make_task()
        self.assertEqual(manager.create(task), task)
        self.assertEqual(manager.create(task), task)
        manager.create(make_task("task-2", "user-2"))
        self.assertEqual([item.task_id for item in manager.list("user-1")], ["task-1"])
        with self.assertRaises(ValueError):
            manager.create(make_task("task-1", "different-user"))

    def test_execution_succeeds_and_cancellation_is_terminal(self) -> None:
        manager = TaskManager(executor=lambda task: "done")
        manager.create(make_task())
        execution = manager.execute("task-1")
        self.assertTrue(execution.result.success)
        self.assertEqual(execution.definition.state, TaskState.SUCCEEDED)
        cancelled = manager.cancel("task-1")
        self.assertEqual(cancelled.state, TaskState.SUCCEEDED)

    def test_failures_retry_then_enter_failed_state(self) -> None:
        def fail(task):
            raise RuntimeError("worker unavailable")

        manager = TaskManager(executor=fail)
        manager.create(TaskDefinition("task-1", "user-1", "Briefing", TaskType.REMINDER, max_retries=1))
        first = manager.execute("task-1")
        second = manager.execute("task-1")
        self.assertEqual(first.definition.state, TaskState.QUEUED)
        self.assertEqual(second.definition.state, TaskState.FAILED)
        self.assertEqual(second.definition.retries, 2)

    def test_schedules_validate_timezones_and_select_due_tasks(self) -> None:
        with self.assertRaises(ValueError):
            TaskSchedule(run_at="2026-08-28T12:00:00")
        with self.assertRaises(ValueError):
            TaskSchedule(cron="0 9 * * *")
        with self.assertRaises(ValueError):
            TaskSchedule(cron="0 9 * * *", recurring=True, timezone="Mars/Olympus")

        manager = TaskManager()
        manager.create(TaskDefinition(
            "due",
            "user-1",
            "DST reminder",
            TaskType.REMINDER,
            schedule=TaskSchedule(run_at="2026-11-01T01:30:00-04:00", timezone="America/New_York"),
        ))
        before = datetime(2026, 11, 1, 5, 29, tzinfo=UTC)
        after = datetime(2026, 11, 1, 5, 30, tzinfo=UTC)
        self.assertEqual(manager.due(before), [])
        self.assertEqual([task.task_id for task in manager.due(after)], ["due"])

        recurring = TaskSchedule(cron="30 1 * * *", recurring=True, timezone="America/New_York")
        self.assertTrue(recurring.is_due(after))

    def test_completed_task_execution_is_idempotent(self) -> None:
        manager = TaskManager(executor=lambda task: "done")
        manager.create(TaskDefinition("task-1", "user-1", "Briefing", TaskType.REMINDER))
        first = manager.execute("task-1")
        second = manager.execute("task-1")
        self.assertTrue(first.result.success)
        self.assertTrue(second.result.success)
        self.assertEqual(len(manager.history("task-1")), 1)

    def test_running_task_is_not_reentered(self) -> None:
        manager = TaskManager(executor=lambda task: (_ for _ in ()).throw(RuntimeError("should not execute")))
        task = TaskDefinition("task-1", "user-1", "Briefing", TaskType.REMINDER, state=TaskState.RUNNING)
        manager._tasks["task-1"] = task
        execution = manager.execute("task-1")
        self.assertEqual(execution.definition.state, TaskState.RUNNING)
        self.assertIn("already running", execution.result.error or "")

    def test_paused_tasks_can_resume_and_idempotent_keys_are_unique(self) -> None:
        manager = TaskManager(executor=lambda task: "ok")
        first = TaskDefinition(
            "task-1",
            "user-1",
            "Reminder",
            TaskType.REMINDER,
            payload={"idempotency_key": "alpha"},
        )
        second = TaskDefinition(
            "task-2",
            "user-1",
            "Reminder",
            TaskType.REMINDER,
            payload={"idempotency_key": "alpha"},
        )
        manager.create(first)
        self.assertRaises(ValueError, manager.create, second)

        paused = manager.pause("task-1")
        self.assertEqual(paused.state, TaskState.PAUSED)
        self.assertEqual(manager.resume("task-1").state, TaskState.QUEUED)
        self.assertTrue(manager.retry("task-1").state == TaskState.QUEUED)

    def test_scheduler_executes_due_tasks_and_skips_paused_ones(self) -> None:
        manager = TaskManager(executor=lambda task: "done")
        manager.create(TaskDefinition(
            "task-1",
            "user-1",
            "Due reminder",
            TaskType.REMINDER,
            schedule=TaskSchedule(run_at="2026-11-01T18:00:00-04:00", timezone="America/New_York"),
        ))
        manager.create(TaskDefinition(
            "task-2",
            "user-1",
            "Paused reminder",
            TaskType.REMINDER,
            state=TaskState.PAUSED,
            schedule=TaskSchedule(run_at="2026-11-01T18:00:00-04:00", timezone="America/New_York"),
        ))
        due = manager.due(datetime(2026, 11, 1, 22, 0, tzinfo=UTC))
        self.assertEqual([task.task_id for task in due], ["task-1"])

    def test_conflicts_are_detected_for_overlapping_user_tasks(self) -> None:
        manager = TaskManager()
        first = TaskDefinition(
            "task-1",
            "user-1",
            "Window blinds",
            TaskType.AUTOMATION,
            schedule=TaskSchedule(run_at="2026-11-01T18:00:00-04:00", timezone="America/New_York"),
            payload={"resource": "living-room-blinds"},
        )
        second = TaskDefinition(
            "task-2",
            "user-1",
            "Night mode",
            TaskType.AUTOMATION,
            schedule=TaskSchedule(run_at="2026-11-01T18:00:00-04:00", timezone="America/New_York"),
            payload={"resource": "living-room-blinds"},
        )
        manager.create(first)
        manager.create(second)
        conflicts = manager.find_conflicts()
        self.assertEqual({(pair[0].task_id, pair[1].task_id) for pair in conflicts}, {("task-1", "task-2")})

    def test_task_service_schedules_lists_and_cancels_over_http(self) -> None:
        server = create_server(port=0)
        thread = threading.Thread(target=server.serve_forever, daemon=True)
        thread.start()
        base_url = f"http://127.0.0.1:{server.server_port}"
        try:
            request = Request(
                f"{base_url}/tasks/schedule",
                data=json.dumps({
                    "task_id": "http-task",
                    "user_id": "http-user",
                    "name": "Briefing",
                    "type": "reminder",
                }).encode(),
                headers={"Content-Type": "application/json"},
                method="POST",
            )
            with urlopen(request) as response:
                self.assertEqual(response.status, 201)
                self.assertEqual(json.load(response)["state"], "queued")
            with urlopen(f"{base_url}/tasks?user_id=http-user") as response:
                self.assertEqual(len(json.load(response)["tasks"]), 1)
            with urlopen(Request(f"{base_url}/tasks/http-task", method="DELETE")) as response:
                self.assertEqual(json.load(response)["state"], "cancelled")
        finally:
            server.shutdown()
            server.server_close()
            thread.join(timeout=2)

    def test_task_service_rejects_non_object_json(self) -> None:
        server = create_server(port=0)
        thread = threading.Thread(target=server.serve_forever, daemon=True)
        thread.start()
        try:
            request = Request(
                f"http://127.0.0.1:{server.server_port}/tasks/schedule",
                data=b"[]",
                headers={"Content-Type": "application/json"},
                method="POST",
            )
            with self.assertRaises(HTTPError) as context:
                urlopen(request)
            self.assertEqual(context.exception.code, 400)
        finally:
            server.shutdown()
            server.server_close()
            thread.join(timeout=2)


if __name__ == "__main__":
    unittest.main()
