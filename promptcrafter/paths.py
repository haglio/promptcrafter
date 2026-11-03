from __future__ import annotations

from pathlib import Path


def project_root() -> Path:
    return Path(__file__).resolve().parent.parent


def icon_path() -> Path:
    return project_root() / "icon.ico"
