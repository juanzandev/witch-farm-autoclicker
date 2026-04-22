from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from pathlib import Path


@dataclass
class ClickerConfig:
    attack_interval: float = 0.75
    eat_interval: float = 120.0
    eat_duration: float = 3.0
    look_away_pixels: int = 450
    look_away_settle_time: float = 0.15
    hotkey: str = "\\"


class ConfigManager:
    def __init__(self, config_path: Path):
        self.config_path = config_path

    def load(self) -> ClickerConfig:
        if not self.config_path.exists():
            return ClickerConfig()

        try:
            data = json.loads(self.config_path.read_text(encoding="utf-8"))
        except (OSError, ValueError, json.JSONDecodeError):
            return ClickerConfig()

        cfg = ClickerConfig()
        cfg.attack_interval = self._coerce_float(data.get("attack_interval"), cfg.attack_interval)
        cfg.eat_interval = self._coerce_float(data.get("eat_interval"), cfg.eat_interval)
        cfg.eat_duration = self._coerce_float(data.get("eat_duration"), cfg.eat_duration)
        cfg.look_away_pixels = int(self._coerce_float(data.get("look_away_pixels"), cfg.look_away_pixels))
        cfg.look_away_settle_time = self._coerce_float(data.get("look_away_settle_time"), cfg.look_away_settle_time)
        cfg.hotkey = self._coerce_str(data.get("hotkey"), cfg.hotkey)
        return cfg

    def save(self, cfg: ClickerConfig) -> None:
        self.config_path.parent.mkdir(parents=True, exist_ok=True)
        self.config_path.write_text(json.dumps(asdict(cfg), indent=2), encoding="utf-8")

    @staticmethod
    def _coerce_float(value, fallback: float) -> float:
        try:
            return float(value)
        except (TypeError, ValueError):
            return fallback

    @staticmethod
    def _coerce_str(value, fallback: str) -> str:
        if isinstance(value, str):
            value = value.strip()
            if value:
                return value
        return fallback
