# Witch Farm Autoclicker

![Witch Spawn Egg](https://minecraft.wiki/images/Invicon_Witch_Spawn_Egg.png?060f4)

## Website

Live project page: https://juanzandev.github.io/witch-farm-autoclicker/

Windows desktop autoclicker for Minecraft AFK combat farms where the player must keep hitting an armor stand while periodically eating.

This is the initial public version and it will keep improving based on community support and feedback.

[![Platform](https://img.shields.io/badge/Platform-Windows%2010%2F11-3b82f6)](#)
[![Python](https://img.shields.io/badge/Python-3.10%2B-22c55e)](#)
[![Build](https://img.shields.io/badge/Build-PyInstaller-a855f7)](#)
[![Theme](https://img.shields.io/badge/UI-Minecraft%20Dark-0ea5e9)](#)

## Why This Project Exists

This project is built specifically for farms that rely on continuous armor-stand melee cycling.

If your setup requires:

- Constant left-click rhythm to keep farm logic active
- Long AFK sessions where hunger eventually interrupts your cycle
- A short right-click eat window before returning to your exact hit position

then this tool is exactly the style of autoclicker you want.

It attacks, periodically looks away, holds right click to eat, and then returns to the original aim point.

## Key Features

- User-configurable global trigger key (plus fallback emergency key)
- Adjustable attack interval and eat cycle timing
- Automatic look-away and right-click eating routine
- 3x3 direction grid (up/down/left/right + diagonals) for eat movement
- Configurable movement units (pixels) applied in selected direction
- Dark Minecraft-inspired desktop interface
- Custom title bar with minimize and close controls
- Taskbar-aware behavior for Windows
- Persistent config and logs in AppData

## Trigger Key Setting

Use the Toggle Key field in-app to choose your trigger key.

Supported values:

- Any single character key (example: `\\`, `q`, `7`)
- Special names: `f1` to `f12`, `esc`, `tab`, `space`, `enter`, `caps_lock`

Fallback key:

- `F8` remains available as a backup toggle.

## Required In-Game Setup

To use the autoclicker correctly:

- Put your sword in your main hand.
- Put your food in your off hand (second hand).

During each eat cycle, the app holds right click for the full Eat Duration and then returns your look movement back by the same amount.

## Fast Start

### Source Mode

1. Install source environment:

```bat
scripts\install_source.bat
```

2. Run app:

```bat
scripts\run_source.bat
```

### Build Portable EXE

```bat
build_exe.bat
```

Output appears in `dist`.

### Build Full Release (Portable + Setup Wizard + SHA)

```bat
build_release.bat
```

This generates and publishes all release artifacts to `docs/downloads`:

- `WitchFarmAutoClicker_latest.exe`
- `WitchFarmAutoClicker_latest.exe.sha256`
- `WitchFarmAutoClickerSetup_latest.exe`
- `WitchFarmAutoClickerSetup_latest.exe.sha256`

If you build manually, include the source path so the package is bundled correctly:

```bat
py -m PyInstaller --noconfirm --onefile --windowed --clean --paths src --name WitchFarmAutoClicker --icon assets\witch.ico --add-data "assets;assets" autoclicker.py
```

### Install EXE Locally

```bat
scripts\install_exe.bat
```

## Windows Security & Trusted Downloads

To reduce Windows SmartScreen warnings for downloaded executables, this project follows these practices:

- Publish SHA-256 checksum files for each downloadable build.
- Move toward installer-based distribution (wizard-style setup) for cleaner install/update behavior.
- Sign release binaries with an Authenticode code-signing certificate.

Important:

- Unsigned installers or EXEs can still trigger warning dialogs even when safe.
- A setup wizard improves installation UX, but does not by itself remove SmartScreen warnings.
- The strongest long-term fix is Authenticode code-signing + publisher reputation over time.

## Notes

- Borderless fullscreen is generally more reliable than exclusive fullscreen for global hotkeys.
- If hotkeys do not trigger, run Minecraft and this app at the same privilege level.
- Confirm farm/server rules before use.

## Attribution

Minecraft-related names and imagery belong to Mojang/Microsoft and their respective rights holders.
Minecraft Wiki content and assets are available under their published licensing terms.
