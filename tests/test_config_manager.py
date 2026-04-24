import json
import tempfile
import unittest
from pathlib import Path

from witchfarm_autoclicker.config import ClickerConfig, ConfigManager


class ConfigManagerTests(unittest.TestCase):
    def test_load_returns_defaults_for_missing_file(self):
        with tempfile.TemporaryDirectory() as td:
            cfg_path = Path(td) / "config.json"
            manager = ConfigManager(cfg_path)

            cfg = manager.load()

            self.assertEqual(cfg, ClickerConfig())

    def test_load_coerces_values_and_falls_back(self):
        with tempfile.TemporaryDirectory() as td:
            cfg_path = Path(td) / "config.json"
            cfg_path.write_text(
                json.dumps(
                    {
                        "attack_interval": "0.5",
                        "eat_interval": 90,
                        "eat_duration": "bad-value",
                        "look_away_pixels": "300",
                        "look_away_settle_time": "0.2",
                        "look_direction": "down-left",
                        "hotkey": "f9",
                    }
                ),
                encoding="utf-8",
            )
            manager = ConfigManager(cfg_path)

            cfg = manager.load()

            self.assertEqual(cfg.attack_interval, 0.5)
            self.assertEqual(cfg.eat_interval, 90.0)
            self.assertEqual(cfg.eat_duration, 3.0)
            self.assertEqual(cfg.look_away_pixels, 300)
            self.assertEqual(cfg.look_away_settle_time, 0.2)
            self.assertEqual(cfg.look_direction, "down-left")
            self.assertEqual(cfg.hotkey, "f9")

    def test_save_writes_config_file(self):
        with tempfile.TemporaryDirectory() as td:
            cfg_path = Path(td) / "config.json"
            manager = ConfigManager(cfg_path)
            cfg = ClickerConfig(attack_interval=0.42, look_direction="up")

            manager.save(cfg)

            self.assertTrue(cfg_path.exists())
            saved = json.loads(cfg_path.read_text(encoding="utf-8"))
            self.assertEqual(saved["attack_interval"], 0.42)
            self.assertEqual(saved["look_direction"], "up")


if __name__ == "__main__":
    unittest.main()
