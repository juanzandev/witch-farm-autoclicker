from __future__ import annotations

import logging
import sys
import time

from pynput import keyboard
from PySide6.QtCore import QObject, QPoint, Qt, QPropertyAnimation, Signal, QEasingCurve
from PySide6.QtGui import QAction, QIcon
from PySide6.QtWidgets import (
    QApplication,
    QButtonGroup,
    QCheckBox,
    QComboBox,
    QFormLayout,
    QFrame,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMainWindow,
    QMenu,
    QMessageBox,
    QPushButton,
    QTabWidget,
    QTextEdit,
    QVBoxLayout,
    QWidget,
    QSystemTrayIcon,
    QSizeGrip,
    QGraphicsDropShadowEffect,
    QGraphicsOpacityEffect,
)

from .clicker import WitchFarmClicker
from .config import ClickerConfig, ConfigManager
from .paths import get_icon_path


class _Bridge(QObject):
    log_message = Signal(str)
    toggle_request = Signal()


class App(QMainWindow):
    FALLBACK_HOTKEY = keyboard.Key.f8
    APP_TITLE = "Farm Control"
    DEVELOPER_TAG = "@juanzandev"
    SPECIAL_HOTKEYS = {
        "f1": keyboard.Key.f1, "f2": keyboard.Key.f2, "f3": keyboard.Key.f3, "f4": keyboard.Key.f4,
        "f5": keyboard.Key.f5, "f6": keyboard.Key.f6, "f7": keyboard.Key.f7, "f8": keyboard.Key.f8,
        "f9": keyboard.Key.f9, "f10": keyboard.Key.f10, "f11": keyboard.Key.f11, "f12": keyboard.Key.f12,
        "esc": keyboard.Key.esc, "tab": keyboard.Key.tab, "space": keyboard.Key.space,
        "enter": keyboard.Key.enter, "caps_lock": keyboard.Key.caps_lock,
    }
    MODIFIER_KEYS = {
        keyboard.Key.ctrl: "ctrl", keyboard.Key.ctrl_l: "ctrl", keyboard.Key.ctrl_r: "ctrl",
        keyboard.Key.alt: "alt", keyboard.Key.alt_l: "alt", keyboard.Key.alt_r: "alt",
        keyboard.Key.shift: "shift", keyboard.Key.shift_l: "shift", keyboard.Key.shift_r: "shift",
    }
    VK_MAIN_KEYS = {
        220: "\\",   # OEM_5 (backslash/pipe on many layouts)
        191: "/",
        192: "`",
        186: ";",
        222: "'",
        219: "[",
        221: "]",
        188: ",",
        190: ".",
        189: "-",
        187: "=",
    }
    DIRECTION_GRID = [["up-left", "up", "up-right"], ["left", "center", "right"], ["down-left", "down", "down-right"]]
    DIRECTION_LABELS = {
        "up-left": "↖", "up": "↑", "up-right": "↗",
        "left": "←", "center": "•", "right": "→",
        "down-left": "↙", "down": "↓", "down-right": "↘",
    }

    DARK_STYLE = """
    QMainWindow, QWidget { background: transparent; color: #EAF0FF; font-family: "Segoe UI", "Inter", sans-serif; }
    QFrame#TitleBar { background: #0B0D12; border-bottom: 1px solid #273046; }
    QFrame#OuterShell { background: #101116; border: 1px solid #2C3348; border-radius: 16px; }
    QFrame#Panel { background: #171A24; border: 1px solid #2C3348; border-radius: 10px; }
    QPushButton { background: #2A334A; color: #EAF0FF; border: none; padding: 8px 12px; border-radius: 8px; }
    QPushButton:hover { background: #3A4768; }
    QPushButton:checked { background: #2B6E3E; color: #F3FFF4; border: 1px solid #74D98E; }
    QLineEdit, QTextEdit, QComboBox { background: #1F2433; color: #EAF0FF; border: 1px solid #313C56; border-radius: 7px; padding: 6px; }
    QTabWidget::pane { border: 1px solid #2C3348; border-radius: 10px; background: #171A24; top: -1px; }
    QTabBar::tab { background: #1D2333; color: #AEB8D9; padding: 8px 14px; border-top-left-radius: 6px; border-top-right-radius: 6px; margin-right: 4px; }
    QTabBar::tab:selected { background: #2B6E3E; color: #F3FFF4; }
    """
    LIGHT_STYLE = """
    QMainWindow, QWidget { background: transparent; color: #1A2236; font-family: "Segoe UI", "Inter", sans-serif; }
    QFrame#TitleBar { background: #E8EDF6; border-bottom: 1px solid #C7D2E8; }
    QFrame#OuterShell { background: #F0F3F8; border: 1px solid #CED7EA; border-radius: 16px; }
    QFrame#Panel { background: #FFFFFF; border: 1px solid #CED7EA; border-radius: 10px; }
    QPushButton { background: #D6E0F2; color: #1A2236; border: none; padding: 8px 12px; border-radius: 8px; }
    QPushButton:hover { background: #C3D0E8; }
    QPushButton:checked { background: #4B86D8; color: #FFFFFF; border: 1px solid #2E68B8; }
    QLineEdit, QTextEdit, QComboBox { background: #EEF3FC; color: #1A2236; border: 1px solid #CED7EA; border-radius: 7px; padding: 6px; }
    QTabWidget::pane { border: 1px solid #CED7EA; border-radius: 10px; background: #FFFFFF; top: -1px; }
    QTabBar::tab { background: #E5ECF8; color: #3C4A68; padding: 8px 14px; border-top-left-radius: 6px; border-top-right-radius: 6px; margin-right: 4px; }
    QTabBar::tab:selected { background: #4B86D8; color: #FFFFFF; }
    """

    def __init__(self, config_manager: ConfigManager):
        self.qt_app = QApplication.instance() or QApplication(sys.argv)
        super().__init__()
        self.config_manager = config_manager
        self.config = self.config_manager.load()
        self.first_run = not self.config_manager.config_path.exists()
        self.clicker = WitchFarmClicker(self._queue_log)
        self.bridge = _Bridge()
        self.bridge.log_message.connect(self._append_log_ui)
        self.bridge.toggle_request.connect(self.toggle)
        self.last_hotkey_time = 0.0
        self.capture_mode = False
        self.pressed_modifiers: set[str] = set()
        self.drag_origin: QPoint | None = None
        self.startup_animation = bool(getattr(self.config, "startup_animation", True))
        self.theme_name = getattr(self.config, "theme", "dark")
        self.listener = None
        self.tray_icon = None
        self._tab_fade_anim = None
        self._settings_flash_anim = None

        self.setWindowTitle(self.APP_TITLE)
        self.setWindowFlags(Qt.Window | Qt.FramelessWindowHint)
        self.setAttribute(Qt.WA_TranslucentBackground, True)
        self.setMinimumSize(640, 540)
        self.resize(760, 620)
        self._set_icon()
        self._build_ui()
        self._apply_theme(self.theme_name)
        self._start_hotkey_listener()
        self.apply_settings(show_error=False, write_log=False)
        self._apply_status_ui(False)
        self.show()
        if self.startup_animation:
            self._play_startup_animation()
        if self.first_run:
            self._show_onboarding()

    def _set_icon(self) -> None:
        icon_path = get_icon_path()
        if icon_path.exists():
            self.setWindowIcon(QIcon(str(icon_path)))

    def _build_ui(self) -> None:
        root = QWidget()
        self.setCentralWidget(root)
        main = QVBoxLayout(root)
        main.setContentsMargins(8, 8, 8, 8)
        main.setSpacing(6)

        self.outer_shell = QFrame()
        self.outer_shell.setObjectName("OuterShell")
        shell_layout = QVBoxLayout(self.outer_shell)
        shell_layout.setContentsMargins(10, 10, 10, 10)
        shell_layout.setSpacing(6)
        main.addWidget(self.outer_shell)

        title_bar = QFrame()
        title_bar.setObjectName("TitleBar")
        title_layout = QHBoxLayout(title_bar)
        title_layout.setContentsMargins(10, 8, 10, 8)
        self.title_label = QLabel(self.APP_TITLE)
        self.dev_label = QLabel(f"Built by {self.DEVELOPER_TAG}")
        self.dev_label.setStyleSheet("color:#9EF59E; background:#16201D; padding:2px 8px; border-radius:4px;")
        title_layout.addWidget(self.title_label)
        title_layout.addWidget(self.dev_label)
        title_layout.addStretch()
        min_btn = QPushButton("-")
        min_btn.setFixedWidth(34)
        min_btn.clicked.connect(self._minimize_to_tray)
        close_btn = QPushButton("X")
        close_btn.setFixedWidth(34)
        close_btn.clicked.connect(self._on_close)
        title_layout.addWidget(min_btn)
        title_layout.addWidget(close_btn)
        shell_layout.addWidget(title_bar)
        title_bar.mousePressEvent = self._title_mouse_press
        title_bar.mouseMoveEvent = self._title_mouse_move

        status_row = QFrame()
        status_layout = QHBoxLayout(status_row)
        status_layout.setContentsMargins(6, 4, 6, 4)
        self.status_dot = QLabel("●")
        self.status_dot.setStyleSheet("font-size:16px; color:#F8D26A;")
        self.status_text = QLabel("Status: OFF")
        self.status_mode = QLabel("Idle")
        self.status_mode.setStyleSheet("background:#1D2333; padding:2px 8px; border-radius:4px;")
        status_layout.addWidget(self.status_dot)
        status_layout.addWidget(self.status_text)
        status_layout.addStretch()
        status_layout.addWidget(self.status_mode)
        shell_layout.addWidget(status_row)

        self.tabs = QTabWidget()
        self.controls_tab = QWidget()
        self.logs_tab = QWidget()
        self.settings_tab = QWidget()
        self.tabs.addTab(self.controls_tab, "Controls")
        self.tabs.addTab(self.logs_tab, "Debug Log")
        self.tabs.addTab(self.settings_tab, "Settings")
        shell_layout.addWidget(self.tabs, 1)
        self.tabs.currentChanged.connect(self._animate_current_tab)
        grip_row = QHBoxLayout()
        grip_row.addStretch()
        self.resize_grip = QSizeGrip(root)
        grip_row.addWidget(self.resize_grip)
        shell_layout.addLayout(grip_row)

        shadow = QGraphicsDropShadowEffect(self.outer_shell)
        shadow.setBlurRadius(26)
        shadow.setColor(Qt.black)
        shadow.setOffset(0, 6)
        self.outer_shell.setGraphicsEffect(shadow)

        self._build_controls_tab()
        self._build_logs_tab()
        self._build_settings_tab()

    def _build_controls_tab(self) -> None:
        panel = QFrame()
        panel.setObjectName("Panel")
        wrap = QVBoxLayout(self.controls_tab)
        wrap.setContentsMargins(0, 0, 0, 0)
        wrap.addWidget(panel)
        layout = QVBoxLayout(panel)

        form = QFormLayout()
        self.attack_edit = QLineEdit(str(self.config.attack_interval))
        self.eat_interval_edit = QLineEdit(str(self.config.eat_interval))
        self.eat_duration_edit = QLineEdit(str(self.config.eat_duration))
        self.look_away_edit = QLineEdit(str(self.config.look_away_pixels))
        form.addRow("Attack Interval (sec)", self.attack_edit)
        form.addRow("Eat Every (sec)", self.eat_interval_edit)
        form.addRow("Eat Duration (sec)", self.eat_duration_edit)
        form.addRow("Look Move Units (px)", self.look_away_edit)
        layout.addLayout(form)

        self.err_form = QLabel("")
        self.err_form.setStyleSheet("color:#ff9ca1;")

        layout.addWidget(QLabel("Look Direction"))
        grid = QGridLayout()
        self.direction_group = QButtonGroup(self)
        self.direction_group.setExclusive(True)
        self.direction_buttons = {}
        for r, row_values in enumerate(self.DIRECTION_GRID):
            for c, direction in enumerate(row_values):
                btn = QPushButton(self.DIRECTION_LABELS[direction])
                btn.setCheckable(True)
                self.direction_group.addButton(btn)
                self.direction_buttons[direction] = btn
                grid.addWidget(btn, r, c)
        layout.addLayout(grid)
        self._set_direction(self.config.look_direction)

        hk_row = QHBoxLayout()
        self.hotkey_edit = QLineEdit(self.config.hotkey)
        self.hotkey_edit.setReadOnly(True)
        self.hotkey_capture_btn = QPushButton("Press a key now")
        self.hotkey_capture_btn.clicked.connect(self._toggle_hotkey_capture)
        hk_row.addWidget(self.hotkey_edit, 1)
        hk_row.addWidget(self.hotkey_capture_btn)
        layout.addWidget(QLabel("Hotkey (supports combos)"))
        layout.addLayout(hk_row)
        self.err_hotkey = QLabel("")
        self.err_hotkey.setStyleSheet("color:#ff9ca1;")
        layout.addWidget(self.err_hotkey)
        layout.addWidget(QLabel("Fallback hotkey: F8"))

        self.apply_btn = QPushButton("Apply Settings")
        self.apply_btn.clicked.connect(self.apply_settings)
        self.toggle_btn = QPushButton(self._toggle_button_text(False))
        self.toggle_btn.setStyleSheet("background:#2B6E3E; color:#F3FFF4;")
        self.toggle_btn.clicked.connect(self.toggle)
        layout.addWidget(self.apply_btn)
        layout.addWidget(self.toggle_btn)
        layout.addStretch()

    def _build_logs_tab(self) -> None:
        panel = QFrame()
        panel.setObjectName("Panel")
        wrap = QVBoxLayout(self.logs_tab)
        wrap.setContentsMargins(0, 0, 0, 0)
        wrap.addWidget(panel)
        layout = QVBoxLayout(panel)
        top = QHBoxLayout()
        top.addWidget(QLabel("Runtime Debug Log"))
        top.addStretch()
        clear_btn = QPushButton("Clear")
        clear_btn.clicked.connect(self._clear_log)
        top.addWidget(clear_btn)
        layout.addLayout(top)
        self.log_box = QTextEdit()
        self.log_box.setReadOnly(True)
        layout.addWidget(self.log_box, 1)

    def _build_settings_tab(self) -> None:
        panel = QFrame()
        panel.setObjectName("Panel")
        wrap = QVBoxLayout(self.settings_tab)
        wrap.setContentsMargins(0, 0, 0, 0)
        wrap.addWidget(panel)
        layout = QFormLayout(panel)
        self.theme_combo = QComboBox()
        self.theme_combo.addItems(["dark", "light"])
        self.theme_combo.setCurrentText(self.theme_name if self.theme_name in ("dark", "light") else "dark")
        self.theme_combo.currentTextChanged.connect(self._apply_theme)
        self.theme_combo.currentTextChanged.connect(lambda _v: self._animate_settings_feedback())
        self.startup_anim_check = QCheckBox("Enable startup animation")
        self.startup_anim_check.setChecked(self.startup_animation)
        self.startup_anim_check.stateChanged.connect(lambda _v: self._animate_settings_feedback())
        layout.addRow("Theme", self.theme_combo)
        layout.addRow("", self.startup_anim_check)
        layout.addRow("", QLabel("Minimize sends app to tray.\nClose stops clicker immediately."))

    def _apply_theme(self, theme_name: str) -> None:
        self.theme_name = "light" if theme_name == "light" else "dark"
        self.qt_app.setStyleSheet(self.LIGHT_STYLE if self.theme_name == "light" else self.DARK_STYLE)

    def _title_mouse_press(self, event) -> None:
        if event.button() == Qt.LeftButton:
            self.drag_origin = event.globalPosition().toPoint() - self.frameGeometry().topLeft()

    def _title_mouse_move(self, event) -> None:
        if self.drag_origin and event.buttons() & Qt.LeftButton:
            self.move(event.globalPosition().toPoint() - self.drag_origin)

    def _animate_current_tab(self, _index: int) -> None:
        page = self.tabs.currentWidget()
        if page is None:
            return
        effect = QGraphicsOpacityEffect(page)
        page.setGraphicsEffect(effect)
        anim = QPropertyAnimation(effect, b"opacity", self)
        anim.setDuration(220)
        anim.setStartValue(0.15)
        anim.setEndValue(1.0)
        anim.setEasingCurve(QEasingCurve.OutCubic)
        anim.finished.connect(lambda: page.setGraphicsEffect(None))
        anim.start()
        self._tab_fade_anim = anim

    def _animate_settings_feedback(self) -> None:
        effect = QGraphicsOpacityEffect(self.settings_tab)
        self.settings_tab.setGraphicsEffect(effect)
        anim = QPropertyAnimation(effect, b"opacity", self)
        anim.setDuration(180)
        anim.setStartValue(0.8)
        anim.setEndValue(1.0)
        anim.setEasingCurve(QEasingCurve.OutQuad)
        anim.finished.connect(lambda: self.settings_tab.setGraphicsEffect(None))
        anim.start()
        self._settings_flash_anim = anim

    def _set_direction(self, direction: str) -> None:
        if direction not in self.direction_buttons:
            direction = "right"
        self.direction_buttons[direction].setChecked(True)

    def _get_direction(self) -> str:
        for direction, button in self.direction_buttons.items():
            if button.isChecked():
                return direction
        return "right"

    def _toggle_hotkey_capture(self) -> None:
        self.capture_mode = not self.capture_mode
        self.hotkey_capture_btn.setText("Listening..." if self.capture_mode else "Press a key now")
        self.err_hotkey.setText("Press desired key/combo" if self.capture_mode else "")

    def _start_hotkey_listener(self) -> None:
        def on_press(key):
            try:
                mod = self.MODIFIER_KEYS.get(key)
                if mod:
                    self.pressed_modifiers.add(mod)
                    return
                if self.capture_mode:
                    combo = self._format_combo(key)
                    if combo:
                        self.hotkey_edit.setText(combo)
                        self.capture_mode = False
                        self.hotkey_capture_btn.setText("Press a key now")
                        self.err_hotkey.setText("")
                    return
                now = time.monotonic()
                if now - self.last_hotkey_time < 0.25:
                    return
                if key == self.FALLBACK_HOTKEY or self._matches_configured_hotkey(key):
                    self.last_hotkey_time = now
                    self.bridge.toggle_request.emit()
            except Exception:
                logging.exception("Hotkey listener error")

        def on_release(key):
            mod = self.MODIFIER_KEYS.get(key)
            if mod and mod in self.pressed_modifiers:
                self.pressed_modifiers.remove(mod)

        self.listener = keyboard.Listener(on_press=on_press, on_release=on_release)
        self.listener.start()

    def _format_combo(self, key) -> str:
        mods = [m for m in ("ctrl", "alt", "shift") if m in self.pressed_modifiers]
        main = self._extract_main_key_name(key)
        if not main:
            return ""
        return "+".join(mods + [main]) if mods else main

    def _extract_main_key_name(self, key) -> str:
        if hasattr(key, "char") and key.char:
            ch = key.char
            # Ctrl+letter combos often arrive as control characters (1..26).
            if len(ch) == 1 and ord(ch) < 32:
                letter_index = ord(ch)
                if 1 <= letter_index <= 26:
                    return chr(ord("a") + letter_index - 1)
            return ch.lower()
        special_name = next((name for name, special in self.SPECIAL_HOTKEYS.items() if key == special), "")
        if special_name:
            return special_name
        vk = getattr(key, "vk", None)
        if vk in self.VK_MAIN_KEYS:
            return self.VK_MAIN_KEYS[vk]
        return ""

    def _matches_configured_hotkey(self, key) -> bool:
        text = self.hotkey_edit.text().strip().lower()
        if not text:
            return False
        tokens = [token for token in text.split("+") if token]
        main = tokens[-1]
        mods = set(tokens[:-1])
        if not mods.issubset(self.pressed_modifiers):
            return False
        if main in self.SPECIAL_HOTKEYS:
            return key == self.SPECIAL_HOTKEYS[main]
        resolved = self._extract_main_key_name(key)
        return bool(resolved) and resolved == main

    def _validate_hotkey(self, text: str) -> str:
        value = text.strip().lower()
        if not value:
            raise ValueError("Hotkey cannot be empty")
        tokens = [t for t in value.split("+") if t]
        if not tokens:
            raise ValueError("Hotkey is invalid")
        for mod in tokens[:-1]:
            if mod not in ("ctrl", "alt", "shift"):
                raise ValueError("Modifiers must be ctrl/alt/shift")
        main = tokens[-1]
        if len(main) == 1 or main in self.SPECIAL_HOTKEYS:
            return value
        raise ValueError("Main key is invalid")

    def _validate_float(self, widget: QLineEdit, name: str, min_value: float) -> float:
        try:
            value = float(widget.text().strip())
        except Exception:
            raise ValueError(f"{name} must be numeric")
        if value <= min_value:
            raise ValueError(f"{name} must be greater than {min_value}")
        return value

    def _validate_non_negative_int(self, widget: QLineEdit, name: str) -> int:
        try:
            value = int(float(widget.text().strip()))
        except Exception:
            raise ValueError(f"{name} must be numeric")
        if value < 0:
            raise ValueError(f"{name} must be >= 0")
        return value

    def _clear_validation_errors(self) -> None:
        self.err_form.setText("")
        self.err_hotkey.setText("")

    def _parse_config_from_ui(self) -> ClickerConfig:
        self._clear_validation_errors()
        has_error = False
        try:
            attack = self._validate_float(self.attack_edit, "Attack interval", 0.0)
        except ValueError as exc:
            self.err_form.setText(str(exc))
            has_error = True
            attack = self.config.attack_interval
        try:
            eat_interval = self._validate_float(self.eat_interval_edit, "Eat interval", 0.0)
        except ValueError as exc:
            self.err_form.setText(str(exc))
            has_error = True
            eat_interval = self.config.eat_interval
        try:
            eat_duration = self._validate_float(self.eat_duration_edit, "Eat duration", 0.0)
        except ValueError as exc:
            self.err_form.setText(str(exc))
            has_error = True
            eat_duration = self.config.eat_duration
        try:
            look_away = self._validate_non_negative_int(self.look_away_edit, "Look move units")
        except ValueError as exc:
            self.err_form.setText(str(exc))
            has_error = True
            look_away = self.config.look_away_pixels
        try:
            hotkey = self._validate_hotkey(self.hotkey_edit.text())
        except ValueError as exc:
            self.err_hotkey.setText(str(exc))
            has_error = True
            hotkey = self.config.hotkey
        if has_error:
            raise ValueError("Please fix highlighted fields")

        cfg = ClickerConfig(
            attack_interval=attack,
            eat_interval=eat_interval,
            eat_duration=eat_duration,
            look_away_pixels=look_away,
            look_away_settle_time=self.config.look_away_settle_time,
            look_direction=self._get_direction(),
            hotkey=hotkey,
            theme=self.theme_name,
            startup_animation=self.startup_anim_check.isChecked(),
        )
        return cfg

    def apply_settings(self, show_error: bool = True, write_log: bool = True) -> bool:
        try:
            self.config = self._parse_config_from_ui()
            self.clicker.update_config(self.config)
            self.config_manager.save(self.config)
            self.toggle_btn.setText(self._toggle_button_text(self.clicker.running))
            self._animate_settings_feedback()
            if write_log:
                self._queue_log("Settings applied")
            return True
        except ValueError as exc:
            if show_error:
                QMessageBox.warning(self, "Invalid Input", str(exc))
            return False
        except Exception as exc:
            logging.exception("Failed to apply settings")
            if show_error:
                QMessageBox.critical(self, "Apply Settings Failed", str(exc))
            return False

    def _toggle_button_text(self, running: bool) -> str:
        base = f"Start / Stop  [{self.hotkey_edit.text()} or F8]"
        return f"{base}  (ON)" if running else base

    def toggle(self) -> None:
        if not self.apply_settings(show_error=True, write_log=False):
            return
        is_on = self.clicker.toggle()
        self.toggle_btn.setText(self._toggle_button_text(is_on))
        self.toggle_btn.setStyleSheet("background:#7A2B2B; color:#F3FFF4;" if is_on else "background:#2B6E3E; color:#F3FFF4;")
        self._apply_status_ui(is_on)

    def _apply_status_ui(self, running: bool) -> None:
        if running:
            self.status_text.setText("Status: ON")
            self.status_dot.setStyleSheet("font-size:16px; color:#89F28B;")
            self.status_mode.setText("Active")
            self.status_mode.setStyleSheet("background:#23402A; color:#A7FFAD; padding:2px 8px; border-radius:4px;")
        else:
            self.status_text.setText("Status: OFF")
            self.status_dot.setStyleSheet("font-size:16px; color:#F8D26A;")
            self.status_mode.setText("Idle")
            self.status_mode.setStyleSheet("background:#1D2333; color:#B4BCD8; padding:2px 8px; border-radius:4px;")

    def _play_startup_animation(self) -> None:
        self.setWindowOpacity(0.0)
        self.anim = QPropertyAnimation(self, b"windowOpacity")
        self.anim.setDuration(320)
        self.anim.setStartValue(0.0)
        self.anim.setEndValue(1.0)
        self.anim.start()

    def _show_onboarding(self) -> None:
        QMessageBox.information(
            self,
            "Welcome",
            "Quick setup:\n"
            "1) Put sword in main hand.\n"
            "2) Put food in off hand.\n"
            "3) Configure intervals and hotkey.\n"
            "4) Press Start / Stop.",
        )

    def _queue_log(self, text: str) -> None:
        self.bridge.log_message.emit(text)

    def _append_log_ui(self, text: str) -> None:
        stamp = time.strftime("%H:%M:%S")
        self.log_box.append(f"[{stamp}] {text}")

    def _clear_log(self) -> None:
        self.log_box.clear()
        self._queue_log("Log cleared")

    def _create_tray_icon(self) -> None:
        if self.tray_icon is not None:
            return
        icon = self.windowIcon()
        self.tray_icon = QSystemTrayIcon(icon, self)
        menu = QMenu()
        restore_action = QAction("Restore", self)
        restore_action.triggered.connect(self._restore_from_tray)
        quit_action = QAction("Quit", self)
        quit_action.triggered.connect(self._on_close)
        menu.addAction(restore_action)
        menu.addAction(quit_action)
        self.tray_icon.setContextMenu(menu)
        self.tray_icon.activated.connect(lambda reason: self._restore_from_tray() if reason == QSystemTrayIcon.Trigger else None)
        self.tray_icon.show()

    def _minimize_to_tray(self) -> None:
        self._create_tray_icon()
        self.hide()

    def _restore_from_tray(self) -> None:
        self.showNormal()
        self.raise_()
        self.activateWindow()

    def _on_close(self) -> None:
        self.clicker.stop()
        if self.listener is not None:
            self.listener.stop()
        if self.tray_icon is not None:
            self.tray_icon.hide()
        self.close()

    def closeEvent(self, event) -> None:
        self.clicker.stop()
        if self.listener is not None:
            self.listener.stop()
        if self.tray_icon is not None:
            self.tray_icon.hide()
        event.accept()

    def run(self) -> None:
        self.qt_app.exec()
