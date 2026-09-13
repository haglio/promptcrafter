"""The shortcut to pin, written by ``python -m promptcrafter.shortcut``.

Windows works out what a running process is by matching it against a pinned
shortcut with the same target, and reads its name, description and icon off the
file it was started from.  Aimed at the shared system interpreter this shortcut
lent PromptCrafter's mark to every Python process on the machine; aimed at a bare
venv interpreter it left PromptCrafter one more anonymous "Python" row.
"""
from __future__ import annotations

import ctypes
from pathlib import Path
from types import SimpleNamespace

import pytest
from app_support.win32 import read_shortcut_app_user_model_id

from promptcrafter import shortcut
from promptcrafter.paths import icon_path
from promptcrafter.process_name import ROLE, namer
from promptcrafter.win32 import APP_USER_MODEL_ID


def _venv(root: Path) -> Path:
    scripts = root / ".venv" / "Scripts"
    scripts.mkdir(parents=True)
    (scripts / "pythonw.exe").write_bytes(b"")
    return scripts / "pythonw.exe"


def _writes_into(written: dict):
    return lambda lnk, **fields: written.update(lnk=lnk, **fields)


def test_it_starts_the_app_from_this_checkout_through_the_copy_named_for_it(
    tmp_path: Path, monkeypatch,
):
    plain = _venv(tmp_path)
    named = plain.with_name(namer().exe_name("pythonw.exe", ROLE))
    monkeypatch.setattr(shortcut, "namer",
                        lambda: SimpleNamespace(named_exe=lambda source, role: str(named)))
    written: dict = {}

    path = shortcut.write(tmp_path, writer=_writes_into(written))

    assert path == tmp_path / "PromptCrafter.lnk"
    assert written == {
        "lnk": str(path),
        "target": str(named),
        "arguments": "-m promptcrafter",
        "working_directory": str(tmp_path),
        "icon": str(icon_path()),
        "app_id": APP_USER_MODEL_ID,
    }


def test_the_copy_is_asked_of_this_checkouts_own_windowed_interpreter(
    tmp_path: Path, monkeypatch,
):
    plain = _venv(tmp_path)
    asked: list[tuple[Path, str]] = []
    monkeypatch.setattr(shortcut, "namer", lambda: SimpleNamespace(
        named_exe=lambda source, role: asked.append((source, role)) or str(source)))

    shortcut.write(tmp_path, writer=_writes_into({}))

    assert asked == [(plain, ROLE)]


def test_a_venv_that_will_not_take_the_copy_costs_the_name_and_nothing_else(
    tmp_path: Path, monkeypatch,
):
    plain = _venv(tmp_path)
    monkeypatch.setattr(shortcut, "namer",
                        lambda: SimpleNamespace(named_exe=lambda source, role: str(source)))
    written: dict = {}

    shortcut.write(tmp_path, writer=_writes_into(written))

    assert written["target"] == str(plain)


def test_without_the_project_venv_it_says_so_and_writes_nothing(tmp_path: Path, capsys):
    assert shortcut.main(tmp_path) == 1

    assert "create the project venv first" in capsys.readouterr().err
    assert not (tmp_path / "PromptCrafter.lnk").exists()


@pytest.mark.skipif(not hasattr(ctypes, "windll"), reason="COM: only Windows can say")
def test_the_shortcut_on_disk_carries_the_identity_the_app_claims(tmp_path: Path, capsys):
    _venv(tmp_path)

    assert shortcut.main(tmp_path) == 0

    assert read_shortcut_app_user_model_id(str(tmp_path / "PromptCrafter.lnk")) == APP_USER_MODEL_ID
    assert "Updated shortcut" in capsys.readouterr().out
