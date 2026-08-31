import unittest

from shared.home import DeviceCapability, DeviceState, DeviceType, HomeDevice, HomeScene
from shared.tasks import TaskDefinition, TaskSchedule, TaskState, TaskType
from shared.voice import AudioPayload, TTSChunk, TranscriptResult, VisemeFrame


class DomainContractsTests(unittest.TestCase):
    def test_task_contract_tracks_schedule_and_state(self) -> None:
        schedule = TaskSchedule(cron="0 9 * * 1-5", timezone="UTC", recurring=True)
        task = TaskDefinition(
            task_id="task-1",
            user_id="user-1",
            name="Daily briefing",
            type=TaskType.RECURRING,
            state=TaskState.QUEUED,
            schedule=schedule,
            payload={"channel": "voice"},
        )
        self.assertEqual(task.type, TaskType.RECURRING)
        self.assertTrue(task.schedule.recurring)
        self.assertEqual(task.to_dict()["state"], "queued")

    def test_task_contract_rejects_invalid_identity_and_retry_configuration(self) -> None:
        with self.assertRaises(ValueError):
            TaskDefinition("", "user-1", "Task", TaskType.REMINDER)
        with self.assertRaises(ValueError):
            TaskDefinition("task-1", "user-1", "Task", TaskType.REMINDER, max_retries=-1)

    def test_home_device_and_scene_contracts_are_serializable(self) -> None:
        device = HomeDevice(
            device_id="light-1",
            name="Desk lamp",
            type=DeviceType.LIGHT,
            room="office",
            state=DeviceState.ONLINE,
            capabilities=[DeviceCapability("brightness", 42)],
        )
        scene = HomeScene(
            scene_id="scene-1",
            name="focus",
            room="office",
            device_targets={"light-1": {"state": "on", "brightness": 35}},
        )
        self.assertEqual(device.to_dict()["type"], "light")
        self.assertEqual(scene.to_dict()["name"], "focus")

    def test_voice_contracts_capture_audio_and_viseme_shapes(self) -> None:
        payload = AudioPayload(sample_rate=16000, format="pcm16", data=b"abc")
        transcript = TranscriptResult(text="hello there", confidence=0.94)
        chunk = TTSChunk(
            text="hello there",
            audio_b64="Zm9v",
            visemes=[VisemeFrame("aa", 0.8), VisemeFrame("sil", 0.2)],
        )
        self.assertEqual(payload.to_dict()["sample_rate"], 16000)
        self.assertEqual(transcript.to_dict()["confidence"], 0.94)
        self.assertEqual(chunk.to_dict()["visemes"][0]["name"], "aa")


if __name__ == "__main__":
    unittest.main()
