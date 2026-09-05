import os
import subprocess
import sys
from pathlib import Path

from app_support.siblings import sibling_checkout

from promptcrafter import paths
from promptcrafter.paths import ensure_shared_ui_on_path


def test_ensure_shared_ui_on_path_makes_it_importable_and_is_idempotent():
    ensure_shared_ui_on_path()

    import shared_ui  # importable now, whichever checkout answered for it

    assert shared_ui.__file__ is not None
    before = list(sys.path)
    ensure_shared_ui_on_path()
    assert sys.path == before  # second call adds nothing


def test_the_checkout_the_walk_finds_holds_the_package():
    # The walk is app_support's; what is this repo's is that it is asked from
    # here, so a worktree of this repo lands on the same primary shared_ui.
    root = sibling_checkout("shared_ui", near=Path(paths.__file__))

    assert (root / "shared_ui" / "__init__.py").exists()


def test_app_module_imports_in_fresh_interpreter():
    """A fresh process (real app launch / worktree) must resolve shared_ui on
    its own, without a conftest or another test having patched sys.path."""
    pkg_root = Path(__file__).resolve().parents[1]
    code = (
        "import sys;"
        f"sys.path.insert(0, r'{pkg_root}');"
        "import promptcrafter.app as m;"
        "print(m.PromptCrafterWindow.__name__)"
    )
    result = subprocess.run(
        [sys.executable, "-c", code],
        capture_output=True,
        text=True,
        env={k: v for k, v in os.environ.items() if k != "PYTHONPATH"},
    )
    assert result.returncode == 0, result.stderr
    assert "PromptCrafterWindow" in result.stdout
