import unittest

from shared.config import EnvironmentSettings, get_settings


class ConfigTests(unittest.TestCase):
    def test_default_settings_are_valid(self) -> None:
        settings = get_settings()
        self.assertEqual(settings.app_name, "sedux")
        self.assertTrue(settings.host)
        self.assertTrue(settings.port > 0)

    def test_explicit_settings_override(self) -> None:
        settings = EnvironmentSettings(
            app_name="sedux-test",
            env="test",
            host="0.0.0.0",
            port=9000,
            debug=True,
        )
        self.assertEqual(settings.app_name, "sedux-test")
        self.assertEqual(settings.env, "test")
        self.assertEqual(settings.port, 9000)
        self.assertTrue(settings.debug)

    def test_invalid_settings_are_rejected(self) -> None:
        with self.assertRaises(ValueError):
            EnvironmentSettings(port=0)
        with self.assertRaises(ValueError):
            EnvironmentSettings(host="")


if __name__ == "__main__":
    unittest.main()
