"""The launch smoke test: everything ``pythonw -m promptcrafter`` imports.

The suite can be entirely green while the shortcut does nothing, and the reason
is the setup around it. ``tests/conftest.py`` puts ``shared_ui`` on ``sys.path``
and renders Qt offscreen before the first test module is collected. The shortcut
does neither: it starts ``.venv\\Scripts\\pythonw.exe`` inside this checkout with
the repo root as its working directory and nothing else. A module that imports
cleanly under the suite's arrangements can therefore fail at launch, and the
window simply never appears; ``pythonw`` has no console, so nothing anywhere
records why.

So this replays the launch's import phase in a fresh process: the interpreter the
shortcut starts, that working directory, and no inherited ``PYTHONPATH``.

``__main__.py`` *is* the whole launch here -- it builds the QApplication and the
window at module level -- so its imports are the launch's imports.

The walk that reads them off the AST and the three assertions that replay them
are ``app_support.launch_smoke``: seven repos carried a copy of the same 200
lines, drifting. What stays here is the half that is this app's -- which files
the launch executes, and which interpreter the shortcut starts.
"""
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
SHORTCUT_SCRIPT = REPO_ROOT / "scripts" / "Update-PromptCrafterShortcut.ps1"

# ``pythonw -m promptcrafter`` runs exactly this file, and it holds the whole
# launch: no main(), just the QApplication and the window at module level.
LAUNCH_FILES = (REPO_ROOT / PACKAGE / "__main__.py",)

# What the launch is for. Asserted present, so a walk that silently found
# nothing -- a renamed file, a parse that returned an empty tree -- cannot pass
# as a clean launch.
_THE_LAUNCH_MUST_REACH = ("promptcrafter.app", "promptcrafter.schema", "PyQt6.QtWidgets")


def _the_launchs_interpreter(repo_root: Path = REPO_ROOT) -> Path:
    """The interpreter to replay the launch under.

    The shortcut's own, where this checkout has one: the ``.ps1`` targets
    ``.venv\\Scripts\\pythonw.exe`` beside the repo, this project's interpreter
    and never PATH's, and the named copy it prefers is a copy of that same file
    in that same directory -- so either way the site-packages are this venv's.
    ``pythonw`` has no stdout or stderr to capture, so its console twin next to
    it stands in and the traceback is readable.

    A checkout with no venv of its own -- CI installs into the runner's Python
    -- falls back to the interpreter running the suite, which is the one this
    package is installed into. What must never stand in is a third interpreter
    off PATH, whose site-packages belong to neither the launch nor the suite.
    """
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
    )


def test_the_replay_takes_the_venv_the_shortcut_starts(tmp_path):
    """Which interpreter the replay picks is the whole premise of this file, so
    it is pinned here rather than left for a reader to work out -- nothing else
    goes red when the helper and the shortcut script drift apart."""
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
    """A checkout with no venv of its own is CI's shape, and the two tests that
    replay the launch have to keep running there rather than skipping away."""
    assert _the_launchs_interpreter(tmp_path) == Path(sys.executable)


def test_the_launch_imports_everything_it_names():
    """Failing here means the shortcut does nothing at all: pythonw has no
    console, so the traceback goes nowhere and no window appears."""
    assert_every_import_resolves(
        _run_the_launchs_way, launch_imports(PACKAGE, LAUNCH_FILES))


def test_the_walk_reaches_what_the_launch_is_made_of():
    assert_the_walk_reached(
        launch_imports(PACKAGE, LAUNCH_FILES), _THE_LAUNCH_MUST_REACH)


def test_a_launch_import_that_cannot_resolve_fails_here():
    """A negative control: if the subprocess reported success regardless, every
    assertion above would pass vacuously and the guard would be decorative."""
    assert_an_unresolvable_import_is_caught(
        _run_the_launchs_way, launch_imports(PACKAGE, LAUNCH_FILES),
        "promptcrafter.app")


def test_the_shortcut_runs_the_package_from_the_repo_root():
    """The working directory is what makes the repo's own ``promptcrafter``
    package resolve rather than an installed or sibling one, and it is what this
    test's ``cwd`` mirrors -- a shortcut that stopped setting it would leave
    this checking a fiction."""
    text = SHORTCUT_SCRIPT.read_text(encoding="utf-8")

    assert "$LauncherArgs = '-m promptcrafter'" in text
    assert "SetWorkingDirectory" in text
    assert "$LauncherRoot" in text
