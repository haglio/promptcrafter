from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path


def test_app_module_imports_in_fresh_interpreter():
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
        check=False,
    )
    assert result.returncode == 0, result.stderr
    assert "PromptCrafterWindow" in result.stdout
