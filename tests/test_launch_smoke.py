"""The launch smoke test: everything ``pythonw -m promptcrafter`` imports.

The suite can be entirely green while the shortcut does nothing, and the reason
is the interpreter. ``tests/conftest.py`` puts ``shared_ui`` on ``sys.path`` and
renders Qt offscreen before the first test module is collected, and pytest runs
on this repo's ``.venv``. The shortcut does neither and uses neither: it targets
whichever ``pythonw`` is first on PATH -- ``Update-PromptCrafterShortcut.ps1``
resolves it with ``Get-Command pythonw`` -- with the repo root as its working
directory and nothing else. A module that imports cleanly under the venv the
suite happens to use can therefore fail under the interpreter that actually
launches, and the window simply never appears; ``pythonw`` has no console, so
nothing anywhere records why.

So this drives the launch's import phase under that interpreter, from that
working directory, with no inherited ``PYTHONPATH``.

``__main__.py`` *is* the whole launch here -- it builds the QApplication and the
window at module level -- so its imports are the launch's imports. They come off
its AST rather than a list maintained here, and are replayed whole (``from X
import a, b``, not ``import X``), so a symbol the launch names but the module no
longer defines fails here too.
"""
from __future__ import annotations

import ast
import os
import subprocess
import shutil
import sys

import pytest

from pathlib import Path

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

# Only these two. A broad ``except Exception`` around a launch body is an error
# *reporter* -- it puts a dialog on screen or writes a crash log -- so an import
# inside it is required, not optional: it failing is exactly the launch failure
# this file exists to catch.
_TOLERATED_BY = {"ImportError", "ModuleNotFoundError"}


# --------------------------------------------------------------------------
# What the launch imports
# --------------------------------------------------------------------------

def _is_type_checking(test: ast.expr) -> bool:
    """``if TYPE_CHECKING:`` bodies are never executed, at launch or anywhere."""
    if isinstance(test, ast.Name):
        return test.id == "TYPE_CHECKING"
    return isinstance(test, ast.Attribute) and test.attr == "TYPE_CHECKING"


def _tolerates_a_missing_module(handlers: list[ast.ExceptHandler]) -> bool:
    for handler in handlers:
        if handler.type is None:  # bare except -- catches everything, promises nothing
            return False
        caught = (
            handler.type.elts if isinstance(handler.type, ast.Tuple) else [handler.type]
        )
        if any(isinstance(n, ast.Name) and n.id in _TOLERATED_BY for n in caught):
            return True
    return False


def _optional_imports(tree: ast.Module) -> set[int]:
    """Imports whose absence the module already handles, so the launch survives
    them and this test must not insist on them."""
    optional: set[int] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.If) and _is_type_checking(node.test):
            body = node.body
        elif isinstance(node, ast.Try) and _tolerates_a_missing_module(node.handlers):
            body = node.body
        else:
            continue
        for statement in body:
            for inner in ast.walk(statement):
                optional.add(id(inner))
    return optional


def _render(node: ast.Import | ast.ImportFrom, package: str) -> str:
    """The import statement as the launch executes it, relative made absolute.

    Every launch file here sits at the top of its package, so a relative import
    is never deeper than one level.
    """
    names = ", ".join(
        alias.name + (f" as {alias.asname}" if alias.asname else "")
        for alias in node.names
    )
    if isinstance(node, ast.Import):
        return f"import {names}"
    assert node.level <= 1, f"unexpected relative import depth in {package}"
    module = node.module or ""
    if node.level:
        module = f"{package}.{module}" if module else package
    return f"from {module} import {names}"


def _is_a_compiler_directive(node: ast.Import | ast.ImportFrom) -> bool:
    """``from __future__ import ...`` loads no module -- it is a flag to the
    compiler, and it is only legal at the top of a file, so replaying it among
    the others is a SyntaxError rather than a check of anything."""
    return isinstance(node, ast.ImportFrom) and node.module == "__future__"


def _launch_imports(package: str, launch_files) -> list[str]:
    statements: list[str] = []
    for path in launch_files:
        tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
        optional = _optional_imports(tree)
        for node in ast.walk(tree):
            if not isinstance(node, (ast.Import, ast.ImportFrom)):
                continue
            if id(node) in optional or _is_a_compiler_directive(node):
                continue
            statements.append(_render(node, package))
    return statements


def _the_shortcuts_interpreter() -> str | None:
    """``Get-Command pythonw`` is how the shortcut script picks its target, so
    the first ``pythonw`` on PATH is what the icon really runs -- not this
    repo's venv, and not the ``python.exe`` running pytest."""
    return shutil.which("pythonw")


def _run_the_launchs_way(statements: list[str]) -> subprocess.CompletedProcess:
    env = {k: v for k, v in os.environ.items() if k != "PYTHONPATH"}
    env["QT_QPA_PLATFORM"] = "offscreen"

    # pythonw has no stdout or stderr to capture, so the console build of the
    # same interpreter stands in -- same install, same site-packages, and a
    # traceback we can actually read.
    interpreter = Path(_the_shortcuts_interpreter()).with_name("python.exe")

    return subprocess.run(
        [str(interpreter), "-c", "\n".join(statements)],
        cwd=REPO_ROOT,
        env=env,
        capture_output=True,
        text=True,
    )


needs_the_shortcuts_interpreter = pytest.mark.skipif(
    _the_shortcuts_interpreter() is None, reason="no pythonw on PATH for the shortcut"
)


@needs_the_shortcuts_interpreter
def test_the_launch_imports_everything_it_names():
    """Failing here means the shortcut does nothing at all: pythonw has no
    console, so the traceback goes nowhere and no window appears."""
    result = _run_the_launchs_way(_launch_imports(PACKAGE, LAUNCH_FILES))

    assert result.returncode == 0, result.stderr


def test_the_walk_reaches_what_the_launch_is_made_of():
    found = "\n".join(_launch_imports(PACKAGE, LAUNCH_FILES))

    for module in _THE_LAUNCH_MUST_REACH:
        assert module in found, f"the launch imports {module}; the walk missed it"


@needs_the_shortcuts_interpreter
def test_a_launch_import_that_cannot_resolve_fails_here():
    """A negative control: if the subprocess reported success regardless, every
    assertion above would pass vacuously and the guard would be decorative."""
    result = _run_the_launchs_way(
        [*_launch_imports(PACKAGE, LAUNCH_FILES), "from promptcrafter.app import NoSuchSymbol"]
    )

    assert result.returncode != 0
    assert "NoSuchSymbol" in result.stderr


def test_the_shortcut_runs_the_package_from_the_repo_root():
    """The working directory is what makes the repo's own ``promptcrafter``
    package resolve rather than an installed or sibling one, and it is what this
    test's ``cwd`` mirrors -- a shortcut that stopped setting it would leave
    this checking a fiction."""
    text = SHORTCUT_SCRIPT.read_text(encoding="utf-8")

    assert "$LauncherArgs = '-m promptcrafter'" in text
    assert "SetWorkingDirectory" in text
    assert "$LauncherRoot" in text
