import json
import threading
import unittest
from urllib.request import urlopen

from services.avatar.main import create_server as create_avatar_server
from services.emotion.main import create_server as create_emotion_server
from services.home.main import create_server as create_home_server
from services.llm.main import create_server as create_llm_server
from services.screen.main import create_server as create_screen_server
from services.task.main import create_server as create_task_server
from services.voice.main import create_server as create_voice_server

SERVICE_FACTORIES = (
    ("avatar", create_avatar_server),
    ("emotion", create_emotion_server),
    ("home", create_home_server),
    ("llm", create_llm_server),
    ("screen", create_screen_server),
    ("task", create_task_server),
    ("voice", create_voice_server),
)


class ServiceStubTests(unittest.TestCase):
    def test_all_planned_services_expose_a_health_endpoint(self) -> None:
        for name, factory in SERVICE_FACTORIES:
            server = factory(port=0)
            thread = threading.Thread(target=server.serve_forever, daemon=True)
            thread.start()
            try:
                with urlopen(f"http://127.0.0.1:{server.server_port}/health") as response:
                    self.assertEqual(response.status, 200)
                    payload = json.load(response)
                    self.assertEqual(payload["service"], name)
                    self.assertEqual(payload["status"], "ok")
            finally:
                server.shutdown()
                server.server_close()
                thread.join(timeout=2)


if __name__ == "__main__":
    unittest.main()
