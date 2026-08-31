import unittest
from datetime import UTC, datetime, timedelta

from shared.home import DeviceCapability, DeviceType, HomeDevice
from shared.home_runtime import HomeRuntime, RecordingHomeAdapter
from shared.memory import MemoryEntry, MemoryOperation, MemoryScope
from shared.memory_runtime import MemoryStore, ShortTermContext
from shared.screen import ScreenAction, ScreenActionExecutor, ScreenCapability
from shared.task_runtime import TaskManager
from shared.tasks import TaskDefinition, TaskType


class ActionRuntimeTests(unittest.TestCase):
    def test_screen_rejects_blank_targets_and_keeps_safety_checks(self) -> None:
        with self.assertRaises(ValueError):
            ScreenAction(ScreenCapability.CLICK, "   ")

        runtime = ScreenActionExecutor({ScreenCapability.CLICK, ScreenCapability.SUBMIT}, max_actions=5)
        action = ScreenAction(ScreenCapability.CLICK, "login-button", confirmed=True, dry_run=False)
        self.assertEqual(runtime.execute("user", action, {"login-button"}).outcome, "executed")

    def test_screen_requires_confirmation_and_honors_stop(self) -> None:
        runtime = ScreenActionExecutor({ScreenCapability.SUBMIT})
        action = ScreenAction(ScreenCapability.SUBMIT, "send-button")
        self.assertIn("confirmation", runtime.execute("user", action, {"send-button"}).outcome)
        runtime.emergency_stop()
        confirmed = ScreenAction(ScreenCapability.SUBMIT, "send-button", confirmed=True, dry_run=False)
        self.assertIn("emergency", runtime.execute("user", confirmed, {"send-button"}).outcome)

    def test_memory_is_bounded_isolated_and_excludes_secrets(self) -> None:
        context = ShortTermContext(2)
        for item in ("one", "two", "three"):
            context.add(item)
        self.assertEqual(context.snapshot(), ("two", "three"))

        store = MemoryStore()
        store.create(MemoryEntry("a", MemoryScope.USER, MemoryOperation.CREATE, "name", "Ada"))
        self.assertEqual(store.export("b"), [])
        with self.assertRaises(ValueError):
            store.create(MemoryEntry("a", MemoryScope.USER, MemoryOperation.CREATE, "api_key", "secret"))

    def test_home_checks_staleness_permissions_confirmation_and_duplicates(self) -> None:
        adapter = RecordingHomeAdapter()
        runtime = HomeRuntime(adapter)
        lock = HomeDevice("front", "Front door", DeviceType.LOCK, "hall", capabilities=[DeviceCapability("locked")])
        runtime.register(lock)
        with self.assertRaises(PermissionError):
            runtime.command("one", "front", "locked", True)
        first = runtime.command("one", "front", "locked", True, confirmed=True)
        self.assertIs(first, runtime.command("one", "front", "locked", True, confirmed=True))
        self.assertEqual(len(adapter.commands), 1)
        runtime.register(lock, datetime.now(UTC) - timedelta(minutes=2))
        with self.assertRaises(RuntimeError):
            runtime.command("two", "front", "locked", False, confirmed=True)

    def test_home_requires_explicit_confirmation_for_alarm_and_tracks_stale_state(self) -> None:
        adapter = RecordingHomeAdapter()
        runtime = HomeRuntime(adapter)
        alarm = HomeDevice("alarm-1", "Hall alarm", DeviceType.ALARM, "hall", capabilities=[DeviceCapability("armed")])
        runtime.register(alarm)

        with self.assertRaises(PermissionError):
            runtime.command("alarm-command", "alarm-1", "armed", True)

        self.assertEqual(
            runtime.command("alarm-command", "alarm-1", "armed", True, confirmed=True).status,
            "executed",
        )
        self.assertEqual(len(adapter.commands), 1)

        runtime.register(alarm, datetime.now(UTC) - timedelta(minutes=2))
        with self.assertRaises(RuntimeError):
            runtime.command("alarm-command-2", "alarm-1", "armed", False, confirmed=True)

    def test_failed_task_enters_history_and_dead_letters(self) -> None:
        manager = TaskManager(executor=lambda task: (_ for _ in ()).throw(RuntimeError("failed")))
        manager.create(TaskDefinition("task", "user", "Fail", TaskType.AI_TASK, max_retries=0))
        manager.execute("task")
        self.assertEqual(len(manager.history("task")), 1)
        self.assertEqual(len(manager.dead_letters()), 1)


if __name__ == "__main__":
    unittest.main()