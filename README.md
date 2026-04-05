# PromptCrafter

A config-driven prompt crafting desktop app built with PyQt6, using `shared_ui` for shared design tokens.

## Stack

- PyQt6 desktop app
- pytest + pytest-qt for testing
- Config-driven prompt schema in `promptcrafter/schema.py`

## Run

```bash
python -m promptcrafter
```

## Desktop Launcher

PromptCrafter launches from a Windows Taskbar shortcut:

- `PromptCrafter.lnk` - shortcut to pin to Taskbar
- `scripts/Update-PromptCrafterShortcut.ps1` - creates/updates the shortcut

The shortcut runs `pythonw.exe -m promptcrafter` so no console window appears.

## Refresh The Icon

```powershell
py -3 ".\scripts\Generate-PromptCrafterIcon.py"
```

## Rebuild The Shortcut

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File ".\scripts\Update-PromptCrafterShortcut.ps1"
```

## Test

```bash
python -m pytest tests/ -v
```

## Repo Notes

- There is no separate nested source repo here. PromptCrafter is this repo.
- The pinned Taskbar shortcut is the development desktop app, not a packaged production build.
