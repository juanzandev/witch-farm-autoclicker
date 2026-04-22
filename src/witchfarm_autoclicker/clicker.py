from __future__ import annotations

import logging
import threading
import time
from typing import Callable

from pynput.mouse import Button, Controller

from .config import ClickerConfig


class WitchFarmClicker:
    def __init__(self, log_callback: Callable[[str], None]):
        self.mouse = Controller()
        self.log_callback = log_callback
        self.config = ClickerConfig()

        self._lock = threading.Lock()
        self._running = False
        self._stop_event = threading.Event()
        self._worker: threading.Thread | None = None

    @property
    def running(self) -> bool:
        with self._lock:
            return self._running

    def update_config(self, new_config: ClickerConfig) -> None:
        with self._lock:
            self.config = new_config
        self._log(
            "Config updated: "
            f"attack {new_config.attack_interval:.2f}s, "
            f"eat every {new_config.eat_interval:.1f}s, "
            f"eat {new_config.eat_duration:.1f}s"
        )

    def start(self) -> bool:
        with self._lock:
            if self._running:
                return False
            self._running = True
            self._stop_event.clear()
            self._worker = threading.Thread(target=self._loop, daemon=True)
            self._worker.start()

        self._log("Autoclicker enabled")
        return True

    def stop(self) -> bool:
        with self._lock:
            if not self._running:
                return False
            self._running = False
            self._stop_event.set()

        self._log("Autoclicker disabled")
        return True

    def toggle(self) -> bool:
        if self.running:
            self.stop()
            return False
        self.start()
        return True

    def _sleep_interruptible(self, seconds: float) -> None:
        self._stop_event.wait(timeout=max(0.0, seconds))

    def _left_click_once(self) -> None:
        self.mouse.press(Button.left)
        self._sleep_interruptible(0.015)
        self.mouse.release(Button.left)

    def _eat_cycle(self, cfg: ClickerConfig) -> None:
        start_position = self.mouse.position
        look_position = (start_position[0] + cfg.look_away_pixels, start_position[1])

        self.mouse.position = look_position
        self._sleep_interruptible(cfg.look_away_settle_time)

        self._log("Eating...")
        self.mouse.press(Button.right)
        start = time.monotonic()
        try:
            while not self._stop_event.is_set():
                if time.monotonic() - start >= cfg.eat_duration:
                    break
                self._sleep_interruptible(0.02)
        finally:
            self.mouse.release(Button.right)

        self._sleep_interruptible(0.05)
        self.mouse.position = start_position
        self._log("Back to attack position")

    def _loop(self) -> None:
        next_eat = time.monotonic() + self.config.eat_interval

        while not self._stop_event.is_set():
            cfg = self.config
            now = time.monotonic()

            if now >= next_eat:
                self._eat_cycle(cfg)
                next_eat = time.monotonic() + cfg.eat_interval
                continue

            self._left_click_once()
            self._sleep_interruptible(cfg.attack_interval)

    def _log(self, message: str) -> None:
        logging.info(message)
        self.log_callback(message)
