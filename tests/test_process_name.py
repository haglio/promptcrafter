from __future__ import annotations

from pathlib import Path

from app_support.launcher import launchers
from app_support.process_identity_check import ProcessName, assert_the_process_is_named

from promptcrafter.paths import icon_path
from promptcrafter.process_name import (
    APP_NAME,
    ROLE,
    name_the_next_run,
    namer,
)

REPO_ROOT = Path(__file__).resolve().parents[1]

_THE_INTERPRETER_THE_SHORTCUT_STARTS = "pythonw.exe"
_THE_ROW_ONE_APP_WITH_ONE_WINDOW_SHOWS = APP_NAME


def test_the_app_readies_the_copy_its_shortcut_starts_through_and_one_it_cannot_make_never_takes_a_launch_down(tmp_path: Path):
    assert_the_process_is_named(
        name_the_next_run, tmp_path,
        ProcessName(
            app_name=APP_NAME,
            role=ROLE,
            interpreter=_THE_INTERPRETER_THE_SHORTCUT_STARTS,
            row=_THE_ROW_ONE_APP_WITH_ONE_WINDOW_SHOWS,
            icon=icon_path(),
        ),
    )


def test_it_starts_through_the_copy_the_app_names_for_itself():
    (launcher,) = [found for found in launchers(REPO_ROOT) if found.file == "launch_promptcrafter.vbs"]

    assert (launcher.interpreter, launcher.named_interpreter) == (
        _THE_INTERPRETER_THE_SHORTCUT_STARTS,
        namer().exe_name(_THE_INTERPRETER_THE_SHORTCUT_STARTS, ROLE))
