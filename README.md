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
- Dark Minecraft-inspired desktop interface
- Custom title bar with minimize and close controls
- Taskbar-aware behavior for Windows
- Persistent config and logs in AppData

## Recommended Farm Setups

These presets are based on common farm families discussed in Minecraft Wiki tutorials and community build patterns. Start with these values, then fine-tune based on your TPS, ping, and armor/food setup.

| Farm Type | Suggested Attack Interval | Eat Every | Eat Duration | Look Away Pixels | Recommended Notes |
| --- | --- | --- | --- | --- | --- |
| Witch Hut Farm (manual kill bay) | `0.72s` to `0.80s` | `120s` | `3.0s` | `420` to `520` | Balanced default. Good for long sessions and stable drop processing. |
| Raid Farm Manual Chamber (JE sword finish) | `0.60s` to `0.75s` | `90s` | `3.0s` to `3.5s` | `500` to `650` | Faster click profile for wave pressure and cleanup cadence. |
| Guardian Manual Finisher Area | `0.65s` to `0.78s` | `75s` to `90s` | `3.0s` to `4.0s` | `550` to `700` | More frequent eating helps sustain long fights and chip damage scenarios. |
| General Mob Tower XP Finisher | `0.75s` to `0.90s` | `120s` to `150s` | `2.5s` to `3.0s` | `350` to `500` | Safer, relaxed profile for mixed-mob funnels. |
| Zombified Piglin or Zombie Melee Chute | `0.68s` to `0.80s` | `90s` to `120s` | `3.0s` | `450` to `600` | Strong baseline where constant melee cadence is preferred for kill credit. |

### Quick Preset Rule

- If mobs pile up: lower attack interval.
- If food still runs out: decrease eat interval and/or increase eat duration.
- If camera returns incorrectly: increase look-away pixels slightly.

## Trigger Key Setting

Use the Toggle Key field in-app to choose your trigger key.

Supported values:

- Any single character key (example: `\\`, `q`, `7`)
- Special names: `f1` to `f12`, `esc`, `tab`, `space`, `enter`, `caps_lock`

Fallback key:

- `F8` remains available as a backup toggle.

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

### Install EXE Locally

```bat
scripts\install_exe.bat
```

## Reference Farm Sources (Internet)

Preset recommendations were informed by farm categories and mechanics from:

- https://minecraft.wiki/w/Tutorial:Witch_farming
- https://minecraft.wiki/w/Tutorial:Mob_farm
- https://minecraft.wiki/w/Tutorial:Raid_farming
- https://minecraft.wiki/w/Tutorial:Guardian_farming
- https://minecraft.wiki/w/Witch

## Make This Repo Shine On GitHub

Suggested repository metadata for your push:

- Repo description: Minecraft armor-stand AFK autoclicker with auto-eat timing and Windows desktop UI.
- Topics: `minecraft`, `autoclicker`, `python`, `windows`, `pyinstaller`, `gaming-tools`, `afk-farm`, `desktop-app`

Recommended release structure:

1. Tag first release as `v1.0.0`.
2. Attach portable EXE built from this repo.
3. Include one screenshot of the app UI in the release notes.

## Notes

- Borderless fullscreen is generally more reliable than exclusive fullscreen for global hotkeys.
- If hotkeys do not trigger, run Minecraft and this app at the same privilege level.
- Confirm farm/server rules before use.

## Attribution

Minecraft-related names and imagery belong to Mojang/Microsoft and their respective rights holders.
Minecraft Wiki content and assets are available under their published licensing terms.
