"""Dead-code detection — fails if vulture finds unreferenced code.

Vulture is pointed at the production packages explicitly (``promptcrafter`` and
``scripts``) instead of scanning ``.`` with an ``--exclude`` list.  Agents run
from a ``.claude/worktrees/<name>`` checkout whose own root path contains
``.claude``; an ``--exclude .claude`` pattern then matches the worktree root and
silently excludes *everything*, turning the scan into a no-op that always
passes.  Naming the production directories keeps the scan honest in every
checkout, and makes the old ``.venv``/``tests``/``node_modules`` excludes
unnecessary since nothing else is ever scanned.
"""

import subprocess
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent


def test_no_dead_code():
    result = subprocess.run(
        [sys.executable, "-m", "vulture", "promptcrafter", "scripts"],
        capture_output=True,
        text=True,
        cwd=str(PROJECT_ROOT),
    )
    assert result.returncode == 0, f"Vulture found dead code:\n{result.stdout}"
