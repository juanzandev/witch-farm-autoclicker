from __future__ import annotations

import ctypes
import logging
import time
import tkinter as tk
from tkinter import messagebox

from pynput import keyboard

from .clicker import WitchFarmClicker
from .config import ClickerConfig, ConfigManager
from .paths import get_icon_path


class App:
    FALLBACK_HOTKEY = keyboard.Key.f8

    GWL_EXSTYLE = -20
    WS_EX_APPWINDOW = 0x00040000
    WS_EX_TOOLWINDOW = 0x00000080
    SWP_NOMOVE = 0x0002
    SWP_NOSIZE = 0x0001
    SWP_NOZORDER = 0x0004
    SWP_FRAMECHANGED = 0x0020
    SPECIAL_HOTKEYS = {
        "f1": keyboard.Key.f1,
        "f2": keyboard.Key.f2,
        "f3": keyboard.Key.f3,
        "f4": keyboard.Key.f4,
        "f5": keyboard.Key.f5,
        "f6": keyboard.Key.f6,
        "f7": keyboard.Key.f7,
        "f8": keyboard.Key.f8,
        "f9": keyboard.Key.f9,
        "f10": keyboard.Key.f10,
        "f11": keyboard.Key.f11,
        "f12": keyboard.Key.f12,
        "esc": keyboard.Key.esc,
        "tab": keyboard.Key.tab,
        "space": keyboard.Key.space,
        "enter": keyboard.Key.enter,
        "caps_lock": keyboard.Key.caps_lock,
    }
    DIRECTION_GRID = [
        ["up-left", "up", "up-right"],
        ["left", "center", "right"],
        ["down-left", "down", "down-right"],
    ]
    DIRECTION_LABELS = {
        "up-left": "↖",
        "up": "↑",
        "up-right": "↗",
        "left": "←",
        "center": "•",
        "right": "→",
        "down-left": "↙",
        "down": "↓",
        "down-right": "↘",
    }

    def __init__(self, config_manager: ConfigManager):
        self.root = tk.Tk()
        self.root.title("Witch Farm Autoclicker")
        self.root.geometry("640x760")
        self.root.minsize(620, 700)
        self.root.configure(bg="#101116")

        self._set_icon()

        self.last_hotkey_time = 0.0
        self.drag_offset_x = 0
        self.drag_offset_y = 0
        self._taskbar_style_initialized = False

        self.config_manager = config_manager
        self.clicker = WitchFarmClicker(self._append_log)
        self.config = self.config_manager.load()

        self.status_var = tk.StringVar(value="Status: OFF")
        self.attack_var = tk.StringVar(value=str(self.config.attack_interval))
        self.eat_interval_var = tk.StringVar(
            value=str(int(self.config.eat_interval)))
        self.eat_duration_var = tk.StringVar(
            value=str(self.config.eat_duration))
        self.look_away_var = tk.StringVar(
            value=str(self.config.look_away_pixels))
        self.look_direction_var = tk.StringVar(value=self.config.look_direction)
        self.hotkey_var = tk.StringVar(value=self.config.hotkey)

        self._build_ui()
        self._start_hotkey_listener()

        self.root.overrideredirect(True)
        self.root.after(0, self._ensure_taskbar_presence)
        self.root.bind("<Map>", self._on_map)
        self.root.bind("<FocusIn>", self._on_focus_in)
        self.root.protocol("WM_DELETE_WINDOW", self._on_close)

        self.apply_settings(show_error=True, write_log=False)

    def _set_icon(self) -> None:
        icon_path = get_icon_path()
        if icon_path.exists():
            try:
                self.root.iconbitmap(default=str(icon_path))
            except Exception:
                logging.exception("Failed to set window icon")

    def _build_ui(self) -> None:
        titlebar = tk.Frame(
            self.root,
            bg="#0C0E14",
            height=34,
            highlightthickness=1,
            highlightbackground="#2C3348",
        )
        titlebar.pack(fill="x", side="top")
        titlebar.pack_propagate(False)

        title_text = tk.Label(
            titlebar,
            text="Witch Farm Autoclicker",
            fg="#9EF59E",
            bg="#0C0E14",
            font=("Consolas", 10, "bold"),
            padx=10,
        )
        title_text.pack(side="left")

        close_btn = tk.Button(
            titlebar,
            text="X",
            command=self._on_close,
            font=("Consolas", 10, "bold"),
            bg="#6F2530",
            fg="#FFECEF",
            activebackground="#A33446",
            activeforeground="#FFFFFF",
            relief="flat",
            bd=0,
            width=3,
            cursor="hand2",
        )
        close_btn.pack(side="right", padx=(0, 2), pady=3)

        min_btn = tk.Button(
            titlebar,
            text="-",
            command=self._minimize_window,
            font=("Consolas", 10, "bold"),
            bg="#22324B",
            fg="#D8E4FF",
            activebackground="#345074",
            activeforeground="#FFFFFF",
            relief="flat",
            bd=0,
            width=3,
            cursor="hand2",
        )
        min_btn.pack(side="right", padx=(0, 6), pady=3)

        titlebar.bind("<ButtonPress-1>", self._start_window_drag)
        titlebar.bind("<B1-Motion>", self._on_window_drag)
        title_text.bind("<ButtonPress-1>", self._start_window_drag)
        title_text.bind("<B1-Motion>", self._on_window_drag)

        top = tk.Frame(self.root, bg="#101116", padx=20, pady=18)
        top.pack(fill="x")

        banner = tk.Frame(top, bg="#1B1F2A", height=120,
                          highlightthickness=2, highlightbackground="#5CD65C")
        banner.pack(fill="x")
        banner.pack_propagate(False)

        tk.Label(
            banner,
            text="WITCH FARM CONTROL",
            fg="#9EF59E",
            bg="#1B1F2A",
            font=("Consolas", 20, "bold"),
        ).pack(pady=(18, 6))

        tk.Label(
            banner,
            text="Minecraft-themed macro panel",
            fg="#A7AED1",
            bg="#1B1F2A",
            font=("Consolas", 11),
        ).pack()

        tk.Label(
            self.root,
            textvariable=self.status_var,
            fg="#F8D26A",
            bg="#101116",
            font=("Consolas", 13, "bold"),
        ).pack(anchor="w", padx=22, pady=(8, 6))

        card = tk.Frame(
            self.root,
            bg="#171A24",
            padx=16,
            pady=14,
            highlightthickness=1,
            highlightbackground="#2C3348",
        )
        card.pack(fill="x", padx=20)

        self._build_input_row(card, "Attack Interval (sec)", self.attack_var)
        self._build_input_row(card, "Eat Every (sec)", self.eat_interval_var)
        self._build_input_row(card, "Eat Duration (sec)",
                              self.eat_duration_var)
        self._build_input_row(card, "Look Move Units (px)", self.look_away_var)
        self._build_direction_picker(card)
        self._build_input_row(card, "Toggle Key", self.hotkey_var)

        hotkey_row = tk.Frame(card, bg="#171A24")
        hotkey_row.pack(fill="x", pady=(7, 4))
        tk.Label(
            hotkey_row,
            text="Fallback Hotkey",
            fg="#C8CCDD",
            bg="#171A24",
            font=("Consolas", 11, "bold"),
        ).pack(side="left")
        tk.Label(
            hotkey_row,
            text="F8",
            fg="#9EF59E",
            bg="#252A39",
            font=("Consolas", 12, "bold"),
            padx=10,
            pady=3,
        ).pack(side="right")

        actions = tk.Frame(self.root, bg="#101116", pady=12)
        actions.pack(fill="x", padx=20)

        self.apply_btn = self._pixel_button(
            actions, "Apply Settings", self.apply_settings, "#3A4260")
        self.apply_btn.pack(side="left", padx=(0, 10))

        self.toggle_btn = self._pixel_button(
            actions, self._toggle_button_text(False), self.toggle, "#2B6E3E")
        self.toggle_btn.pack(side="left")

        log_wrap = tk.Frame(
            self.root,
            bg="#151823",
            highlightthickness=1,
            highlightbackground="#2C3348",
        )
        log_wrap.pack(fill="both", expand=True, padx=20, pady=(2, 18))

        tk.Label(
            log_wrap,
            text="Runtime Log",
            fg="#B4BADE",
            bg="#151823",
            anchor="w",
            padx=10,
            pady=6,
            font=("Consolas", 11, "bold"),
        ).pack(fill="x")

        self.log_box = tk.Text(
            log_wrap,
            height=10,
            bg="#0D0F15",
            fg="#9BEA9B",
            insertbackground="#9BEA9B",
            font=("Consolas", 10),
            bd=0,
            padx=10,
            pady=8,
        )
        self.log_box.pack(fill="both", expand=True)
        self.log_box.configure(state="disabled")

        footer_row = tk.Frame(self.root, bg="#101116")
        footer_row.pack(fill="x", padx=20, pady=(0, 10))
        tk.Label(
            footer_row,
            text="@juanzandev",
            fg="#7D85A8",
            bg="#101116",
            font=("Consolas", 10, "bold"),
        ).pack(side="right")

        self._append_log(f"Press {self._hotkey_hint()} to start/stop")

    def _build_input_row(self, parent, label: str, var: tk.StringVar) -> None:
        row = tk.Frame(parent, bg="#171A24")
        row.pack(fill="x", pady=5)

        tk.Label(
            row,
            text=label,
            fg="#C8CCDD",
            bg="#171A24",
            font=("Consolas", 11, "bold"),
        ).pack(side="left")

        entry = tk.Entry(
            row,
            textvariable=var,
            width=10,
            bg="#252A39",
            fg="#E8EAF2",
            insertbackground="#E8EAF2",
            relief="flat",
            font=("Consolas", 11),
            justify="center",
        )
        entry.pack(side="right")

    def _build_direction_picker(self, parent) -> None:
        outer = tk.Frame(parent, bg="#171A24")
        outer.pack(fill="x", pady=(8, 6))

        tk.Label(
            outer,
            text="Look Direction While Eating",
            fg="#C8CCDD",
            bg="#171A24",
            font=("Consolas", 11, "bold"),
        ).pack(anchor="w", pady=(0, 6))

        grid = tk.Frame(
            outer,
            bg="#1A1E2A",
            padx=8,
            pady=8,
            highlightthickness=1,
            highlightbackground="#2C3348",
        )
        grid.pack(anchor="w")

        for row_index, row_values in enumerate(self.DIRECTION_GRID):
            for col_index, direction in enumerate(row_values):
                rb = tk.Radiobutton(
                    grid,
                    text=self.DIRECTION_LABELS[direction],
                    value=direction,
                    variable=self.look_direction_var,
                    indicatoron=False,
                    width=4,
                    height=1,
                    command=self._on_direction_selected,
                    bg="#252A39",
                    fg="#E8EAF2",
                    selectcolor="#2B6E3E",
                    activebackground="#3A4260",
                    activeforeground="#FFFFFF",
                    relief="flat",
                    bd=0,
                    font=("Consolas", 11, "bold"),
                    cursor="hand2",
                )
                rb.grid(row=row_index, column=col_index, padx=4, pady=4)

        if self.look_direction_var.get() not in self.DIRECTION_LABELS:
            self.look_direction_var.set("right")

    def _on_direction_selected(self) -> None:
        direction = self.look_direction_var.get()
        self._append_log(f"Look direction: {direction}")

    def _validate_direction(self, raw_value: str) -> str:
        value = raw_value.strip().lower()
        if value in self.DIRECTION_LABELS:
            return value
        raise ValueError("Invalid look direction selected")

    def _pixel_button(self, parent, text, command, bg_color):
        return tk.Button(
            parent,
            text=text,
            command=command,
            font=("Consolas", 11, "bold"),
            bg=bg_color,
            fg="#EAF0FF",
            activebackground="#4C5A84",
            activeforeground="#FFFFFF",
            relief="flat",
            bd=0,
            padx=16,
            pady=9,
            cursor="hand2",
        )

    def _start_hotkey_listener(self) -> None:
        def on_press(key):
            try:
                is_main_hotkey = self._matches_configured_hotkey(key)
                is_fallback_hotkey = key == self.FALLBACK_HOTKEY
                if is_main_hotkey or is_fallback_hotkey:
                    now = time.monotonic()
                    if now - self.last_hotkey_time < 0.3:
                        return
                    self.last_hotkey_time = now
                    self.root.after(0, self.toggle)
            except Exception:
                logging.exception("Hotkey listener error")

        self.listener = keyboard.Listener(on_press=on_press)
        self.listener.start()

    def _matches_configured_hotkey(self, key) -> bool:
        hotkey = self.config.hotkey.strip()
        if not hotkey:
            return False

        normalized = hotkey.lower()
        if normalized in self.SPECIAL_HOTKEYS:
            return key == self.SPECIAL_HOTKEYS[normalized]

        return hasattr(key, "char") and key.char is not None and key.char.lower() == hotkey.lower()

    def _validate_hotkey(self, raw_value: str) -> str:
        value = raw_value.strip()
        if not value:
            raise ValueError("Toggle key cannot be empty")

        if len(value) == 1:
            return value

        normalized = value.lower()
        if normalized in self.SPECIAL_HOTKEYS:
            return normalized

        allowed = "single character or one of: f1-f12, esc, tab, space, enter, caps_lock"
        raise ValueError(f"Invalid toggle key. Use {allowed}")

    def _hotkey_hint(self) -> str:
        key_text = self.config.hotkey
        return f"{key_text} or F8"

    def _toggle_button_text(self, running: bool) -> str:
        base = f"Toggle  [{self._hotkey_hint()}]"
        if running:
            return f"{base}  (ON)"
        return base

    def _start_window_drag(self, event) -> None:
        self.drag_offset_x = event.x_root - self.root.winfo_x()
        self.drag_offset_y = event.y_root - self.root.winfo_y()

    def _on_window_drag(self, event) -> None:
        x = event.x_root - self.drag_offset_x
        y = event.y_root - self.drag_offset_y
        self.root.geometry(f"+{x}+{y}")

    def _minimize_window(self) -> None:
        self.root.overrideredirect(False)
        self.root.after_idle(self.root.iconify)

    def _ensure_taskbar_presence(self) -> None:
        if self._taskbar_style_initialized:
            return

        if hasattr(ctypes, "windll"):
            try:
                hwnd = ctypes.windll.user32.GetParent(self.root.winfo_id())
                ex_style = ctypes.windll.user32.GetWindowLongW(
                    hwnd, self.GWL_EXSTYLE)
                ex_style = (
                    ex_style & ~self.WS_EX_TOOLWINDOW) | self.WS_EX_APPWINDOW
                ctypes.windll.user32.SetWindowLongW(
                    hwnd, self.GWL_EXSTYLE, ex_style)
                ctypes.windll.user32.SetWindowPos(
                    hwnd,
                    0,
                    0,
                    0,
                    0,
                    0,
                    self.SWP_NOMOVE | self.SWP_NOSIZE | self.SWP_NOZORDER | self.SWP_FRAMECHANGED,
                )

                self.root.withdraw()
                self.root.after(20, self.root.deiconify)
            except Exception:
                logging.exception("Taskbar style setup failed")

        self._taskbar_style_initialized = True

    def _on_map(self, _event) -> None:
        if self.root.state() != "iconic":
            self.root.after(10, lambda: self.root.overrideredirect(True))
            self.root.after(20, self._ensure_taskbar_presence)

    def _on_focus_in(self, _event) -> None:
        if self.root.state() != "iconic" and not self.root.overrideredirect():
            self.root.overrideredirect(True)

    def _append_log(self, text: str) -> None:
        stamp = time.strftime("%H:%M:%S")
        line = f"[{stamp}] {text}\n"

        def write_line():
            self.log_box.configure(state="normal")
            self.log_box.insert("end", line)
            self.log_box.see("end")
            self.log_box.configure(state="disabled")

        self.root.after(0, write_line)

    def _parse_config_from_ui(self) -> ClickerConfig:
        cfg = ClickerConfig(
            attack_interval=float(self.attack_var.get().strip()),
            eat_interval=float(self.eat_interval_var.get().strip()),
            eat_duration=float(self.eat_duration_var.get().strip()),
            look_away_pixels=int(float(self.look_away_var.get().strip())),
            look_away_settle_time=self.config.look_away_settle_time,
            look_direction=self._validate_direction(self.look_direction_var.get()),
            hotkey=self._validate_hotkey(self.hotkey_var.get()),
        )

        if cfg.attack_interval <= 0:
            raise ValueError("Attack interval must be greater than 0")
        if cfg.eat_interval <= 0:
            raise ValueError("Eat interval must be greater than 0")
        if cfg.eat_duration <= 0:
            raise ValueError("Eat duration must be greater than 0")
        if cfg.look_away_pixels < 0:
            raise ValueError("Look move units must be 0 or greater")

        return cfg

    def apply_settings(self, show_error: bool = True, write_log: bool = True) -> bool:
        try:
            self.config = self._parse_config_from_ui()
            self.hotkey_var.set(self.config.hotkey)
            self.clicker.update_config(self.config)
            self.config_manager.save(self.config)
            self.toggle_btn.configure(
                text=self._toggle_button_text(self.clicker.running))
            if write_log:
                self._append_log("Settings applied")
            return True
        except ValueError as exc:
            if show_error:
                messagebox.showerror("Invalid Input", str(exc))
            return False

    def toggle(self) -> None:
        if not self.apply_settings(show_error=True, write_log=False):
            return

        is_on = self.clicker.toggle()
        if is_on:
            self.status_var.set("Status: ON")
            self.toggle_btn.configure(
                bg="#7A2B2B", text=self._toggle_button_text(True))
        else:
            self.status_var.set("Status: OFF")
            self.toggle_btn.configure(
                bg="#2B6E3E", text=self._toggle_button_text(False))

    def _on_close(self) -> None:
        self.clicker.stop()
        if hasattr(self, "listener"):
            self.listener.stop()
        self.root.destroy()

    def run(self) -> None:
        self.root.mainloop()
