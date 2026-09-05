"""PromptCrafter says its own name in the Windows task list.

Why an app names its processes, and why its own is the one it can only name for
the run after, is :mod:`app_support.process_identity`'s to say.  What is left
here is what only this repo can be wrong about: that the app makes the copy its
shortcut starts it through, run against a throwaway venv rather than read off the
entry point.  The shortcut's side -- that the ``.ps1`` points at that copy -- is
``test_launcher_contract``'s.
"""
from __future__ import annotations

from pathlib import Path

from app_support.process_identity_check import assert_the_app_names_its_process

from promptcrafter.paths import icon_path
from promptcrafter.process_name import APP_NAME, ROLE, name_this_process


def test_the_app_prepares_the_copy_its_shortcut_starts_through(tmp_path: Path):
    """From the windowed interpreter, which is what the shortcut starts;
    described as the app's name alone -- one app with one window, so the row is
    its name, not its name twice; carrying the app's own mark; and never taking
    a launch down when there is nothing to copy from."""
    assert_the_app_names_its_process(
        name_this_process, tmp_path, app_name=APP_NAME, role=ROLE,
        interpreter="pythonw.exe", row=APP_NAME, icon=icon_path())
