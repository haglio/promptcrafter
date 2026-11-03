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

LAUNCH_FILES = (REPO_ROOT / PACKAGE / "__main__.py", REPO_ROOT / PACKAGE / "opening.py")

_THE_LAUNCH_MUST_REACH = ("promptcrafter.app", "promptcrafter.schema", "PyQt6.QtWidgets")


def _the_launchs_interpreter(repo_root: Path = REPO_ROOT) -> Path:
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
        [str(_the_launchs_interpreter()), "-c", "\n".join(statements)],
        cwd=REPO_ROOT,
        env=env,
        capture_output=True,
        text=True,
        check=False,
    )


def test_the_replay_takes_the_venv_the_shortcut_starts(tmp_path):
    scripts = tmp_path / ".venv" / "Scripts"
    scripts.mkdir(parents=True)
    (scripts / "python.exe").touch()

    assert _the_launchs_interpreter(tmp_path) == scripts / "python.exe"


def test_the_replay_takes_a_posix_venv_the_same_way(tmp_path):
    bin_dir = tmp_path / ".venv" / "bin"
    bin_dir.mkdir(parents=True)
    (bin_dir / "python").touch()

    assert _the_launchs_interpreter(tmp_path) == bin_dir / "python"


def test_the_replay_falls_back_to_the_interpreter_running_the_suite(tmp_path):
    assert _the_launchs_interpreter(tmp_path) == Path(sys.executable)


def test_the_launch_imports_everything_it_names():
    assert_every_import_resolves(
        _run_the_launchs_way, launch_imports(PACKAGE, LAUNCH_FILES))


def test_the_walk_reaches_what_the_launch_is_made_of():
    assert_the_walk_reached(
        launch_imports(PACKAGE, LAUNCH_FILES), _THE_LAUNCH_MUST_REACH)


def test_a_launch_import_that_cannot_resolve_fails_here():
    assert_an_unresolvable_import_is_caught(
        _run_the_launchs_way, launch_imports(PACKAGE, LAUNCH_FILES),
        "promptcrafter.app")

