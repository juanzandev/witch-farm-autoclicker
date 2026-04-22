from __future__ import annotations

import os
import sys
from pathlib import Path

APP_NAME = "WitchFarmAutoClicker"


def get_runtime_base_dir() -> Path:
    if getattr(sys, "frozen", False) and hasattr(sys, "_MEIPASS"):
        return Path(sys._MEIPASS)  # type: ignore[attr-defined]
    return Path(__file__).resolve().parents[2]


def get_assets_dir() -> Path:
    return get_runtime_base_dir() / "assets"


def get_icon_path() -> Path:
    return get_assets_dir() / "witch.ico"


def get_user_data_dir() -> Path:
    appdata = os.environ.get("APPDATA")
    if appdata:
        base = Path(appdata)
    else:
        base = Path.home() / "AppData" / "Roaming"

    data_dir = base / APP_NAME
    data_dir.mkdir(parents=True, exist_ok=True)
    return data_dir


def get_log_dir() -> Path:
    log_dir = get_user_data_dir() / "logs"
    log_dir.mkdir(parents=True, exist_ok=True)
    return log_dir


def get_config_path() -> Path:
    return get_user_data_dir() / "config.json"
