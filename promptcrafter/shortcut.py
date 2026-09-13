"""``python -m promptcrafter.shortcut``: write PromptCrafter.lnk, the shortcut to pin.

It starts the app from this checkout on its own windowed interpreter -- the copy
named for PromptCrafter when the app can make one -- and carries the
AppUserModelID the app claims, so the window opens in the pin rather than beside
it.
"""
from __future__ import annotations

import sys
from pathlib import Path

from app_support.win32 import write_shortcut

from promptcrafter.paths import icon_path, project_root
from promptcrafter.process_name import ROLE, namer
from promptcrafter.win32 import APP_USER_MODEL_ID

SHORTCUT_NAME = "PromptCrafter.lnk"
ARGUMENTS = "-m promptcrafter"


def write(root: Path | None = None, *, writer=write_shortcut) -> Path:
    """Write the shortcut into *root*, over whatever is there, and say where."""
    root = root or project_root()
    plain = root / ".venv" / "Scripts" / "pythonw.exe"
    if not plain.is_file():
        raise FileNotFoundError(f"No interpreter at {plain} -- create the project venv first")
    shortcut = root / SHORTCUT_NAME
    writer(str(shortcut), target=namer().named_exe(plain, ROLE), arguments=ARGUMENTS,
           working_directory=str(root), icon=str(icon_path()), app_id=APP_USER_MODEL_ID)
    return shortcut


def main(root: Path | None = None) -> int:
    try:
        shortcut = write(root)
    except FileNotFoundError as missing:
        print(missing, file=sys.stderr)
        return 1
    print(f"Updated shortcut: {shortcut}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
