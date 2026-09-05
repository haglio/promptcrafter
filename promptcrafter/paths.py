"""Locate the sibling ``shared_ui`` package without hardcoding directory depth.

``shared_ui`` lives next to this project under the shared ``projects`` root and
is imported via ``sys.path`` rather than installed.  It uses a src-style layout
-- its importable package sits one level down, at
``shared_ui/shared_ui/__init__.py`` -- so we walk up to the directory that holds
the ``shared_ui`` *checkout* and put that checkout on ``sys.path`` (importing
``shared_ui`` then finds the package inside it).  Walking, rather than counting
parents, keeps this working whether the app is a normal clone or a
``.claude/worktrees/<name>`` worktree.
"""

from __future__ import annotations

from pathlib import Path

from app_support.siblings import ensure_sibling_importable


def ensure_shared_ui_on_path() -> None:
    """Put the ``shared_ui`` checkout on ``sys.path`` so ``shared_ui`` is importable.

    Appended, not prepended: the checkout dir also holds shared_ui's own
    ``tests``/``tools`` packages, so inserting it at the front would shadow this
    app's ``tests`` package.  Appending lets the app's own packages win while
    still making ``shared_ui`` resolvable (nothing else provides it).
    """
    ensure_sibling_importable("shared_ui", near=Path(__file__))


def project_root() -> Path:
    """The checkout this package lives in, where its assets sit."""
    return Path(__file__).resolve().parent.parent


def icon_path() -> Path:
    """PromptCrafter's mark, beside the checkout root.

    Named here rather than at the one call site so a worktree finds its own copy
    -- the same reason ``app_support.siblings`` walks instead of counting parents.
    """
    return project_root() / "icon.ico"
