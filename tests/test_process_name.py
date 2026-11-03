from __future__ import annotations

from pathlib import Path

from app_support.launcher import launchers
from app_support.process_identity_check import ProcessName, assert_the_process_is_named

from promptcrafter.paths import icon_path
from promptcrafter.process_name import APP_NAME, ROLE, name_this_process, namer

REPO_ROOT = Path(__file__).resolve().parents[1]


def test_the_app_prepares_the_copy_its_shortcut_starts_through(tmp_path: Path):
    assert_the_process_is_named(
        name_this_process, tmp_path,
        ProcessName(
            app_name=APP_NAME,
            role=ROLE,
            interpreter="pythonw.exe",
            row=APP_NAME,
            icon=icon_path(),
        ),
    )


def test_it_starts_through_the_copy_the_app_names_for_itself():
    (launcher,) = [found for found in launchers(REPO_ROOT) if found.file == "launch_promptcrafter.vbs"]

    assert (launcher.interpreter, launcher.named_interpreter) == (
        "pythonw.exe", namer().exe_name("pythonw.exe", ROLE))
