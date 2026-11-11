from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

from app_support.launch_smoke import (
    assert_an_unresolvable_import_is_caught,
    assert_every_import_resolves,
    assert_the_walk_reached,
    launch_imports,
)

REPO_ROOT = Path(__file__).resolve().parents[1]
PACKAGE = "promptcrafter"

_WHAT_PYTHONW_M_PROMPTCRAFTER_RUNS = REPO_ROOT / PACKAGE / "__main__.py"
_WHAT_IT_OPENS_THE_WINDOW_THROUGH = REPO_ROOT / PACKAGE / "opening.py"
LAUNCH_FILES = (_WHAT_PYTHONW_M_PROMPTCRAFTER_RUNS, _WHAT_IT_OPENS_THE_WINDOW_THROUGH)

_THE_LAUNCH_MUST_REACH = ("promptcrafter.app", "promptcrafter.schema", "PySide6.QtWidgets")


def _the_launchs_console_interpreter(repo_root: Path = REPO_ROOT) -> Path:
    for console in (
        repo_root / ".venv" / "Scripts" / "python.exe",
        repo_root / ".venv" / "bin" / "python",
    ):
        if console.exists():
            return console
    return Path(sys.executable)


def _run_the_launchs_way(statements: list[str]) -> subprocess.CompletedProcess:
    env = {k: v for k, v in os.environ.items() if k != "PYTHONPATH"}
    env["QT_QPA_PLATFORM"] = "offscreen"

    return subprocess.run(
        [str(_the_launchs_console_interpreter()), "-c", "\n".join(statements)],
        cwd=REPO_ROOT,
        env=env,
        capture_output=True,
        text=True,
        check=False,
    )


def test_the_replay_takes_the_venv_the_shortcut_starts_whose_renamed_copy_shares_its_site_packages(tmp_path):
    scripts = tmp_path / ".venv" / "Scripts"
    scripts.mkdir(parents=True)
    (scripts / "python.exe").touch()

    assert _the_launchs_console_interpreter(tmp_path) == scripts / "python.exe"


def test_the_replay_takes_the_console_twin_since_pythonw_has_no_output_to_read(tmp_path):
    scripts = tmp_path / ".venv" / "Scripts"
    scripts.mkdir(parents=True)
    (scripts / "pythonw.exe").touch()
    (scripts / "python.exe").touch()

    assert _the_launchs_console_interpreter(tmp_path) == scripts / "python.exe"


def test_the_replay_takes_a_posix_venv_the_same_way(tmp_path):
    bin_dir = tmp_path / ".venv" / "bin"
    bin_dir.mkdir(parents=True)
    (bin_dir / "python").touch()

    assert _the_launchs_console_interpreter(tmp_path) == bin_dir / "python"


def test_the_replay_falls_back_to_the_interpreter_running_the_suite_never_one_off_path_whose_packages_are_neither_the_launchs_nor_the_suites(tmp_path):
    assert _the_launchs_console_interpreter(tmp_path) == Path(sys.executable)


def test_the_launch_imports_everything_it_names_since_under_pythonw_a_failed_import_shows_only_in_the_launchers_log():
    assert_every_import_resolves(
        _run_the_launchs_way, launch_imports(PACKAGE, LAUNCH_FILES))


def test_the_walk_reaches_what_the_launch_is_made_of():
    assert_the_walk_reached(
        launch_imports(PACKAGE, LAUNCH_FILES), _THE_LAUNCH_MUST_REACH)


def test_this_file_keeps_only_the_apps_half_which_files_and_which_interpreter_since_the_walk_is_app_supports_one_copy():
    helpers = {name for name, value in globals().items()
               if callable(value) and value.__module__ == __name__ and not name.startswith("test_")}

    assert helpers == {
        "_the_launchs_console_interpreter",
        "_run_the_launchs_way",
    }


def test_a_launch_import_that_cannot_resolve_fails_here():
    assert_an_unresolvable_import_is_caught(
        _run_the_launchs_way, launch_imports(PACKAGE, LAUNCH_FILES),
        "promptcrafter.app")

