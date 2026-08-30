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

import sys
from pathlib import Path


def shared_ui_checkout() -> Path:
    """The ``shared_ui`` checkout dir; its ``shared_ui/`` child is the package.

    It was ``projects_root``, eighteen lines above :func:`project_root`, which
    returns something else entirely -- and the docstring had to correct the name
    on its first line. Anyone who read the name and not the docstring got the
    wrong idea about both.
    """
    here = Path(__file__).resolve()
    for parent in here.parents:
        checkout = parent / "shared_ui"
        if (checkout / "shared_ui" / "__init__.py").exists():
            return checkout
    raise RuntimeError(f"Could not locate the shared_ui package above {here}")


def ensure_shared_ui_on_path() -> None:
    """Put the ``shared_ui`` checkout on ``sys.path`` so ``shared_ui`` is importable.

    Appended, not prepended: the checkout dir also holds shared_ui's own
    ``tests``/``tools`` packages, so inserting it at the front would shadow this
    app's ``tests`` package.  Appending lets the app's own packages win while
    still making ``shared_ui`` resolvable (nothing else provides it).
    """
    root = str(shared_ui_checkout())
    if root not in sys.path:
        sys.path.append(root)


def project_root() -> Path:
    """The checkout this package lives in, where its assets sit."""
    return Path(__file__).resolve().parent.parent


def icon_path() -> Path:
    """PromptCrafter's mark, beside the checkout root.

    Named here rather than at the one call site so a worktree finds its own copy
    -- the same reason :func:`shared_ui_checkout` walks instead of counting parents.
    """
    return project_root() / "icon.ico"
