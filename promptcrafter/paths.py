"""Where this app's own files are.
"""

from __future__ import annotations

from pathlib import Path


def project_root() -> Path:
    """The checkout this package lives in, where its assets sit."""
    return Path(__file__).resolve().parent.parent


def icon_path() -> Path:
    """PromptCrafter's mark, beside the checkout root.

    Named here rather than at the one call site so a worktree finds its own copy
    -- the same reason ``app_support.siblings`` walks instead of counting parents.
    """
    return project_root() / "icon.ico"
