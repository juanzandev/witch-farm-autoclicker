from __future__ import annotations

import logging

from .config import ConfigManager
from .logging_setup import configure_logging
from .paths import get_config_path, get_log_dir
from .ui import App


def main() -> None:
    configure_logging(get_log_dir())
    logging.info("Starting Witch Farm Autoclicker")

    config_manager = ConfigManager(get_config_path())
    app = App(config_manager)
    app.run()


if __name__ == "__main__":
    main()
