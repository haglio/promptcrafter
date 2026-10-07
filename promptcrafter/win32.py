"""Win32 identity for the PromptCrafter window.

Two different things decide what Windows shows for a running app, and neither
of them is the shortcut that started it:

  * the **window icon**, which is what Alt-Tab, the task list and the window's
    own corner draw.  Qt has none unless it is given one, so the window came up
    under a generic fallback -- not even Python's mark, just whatever Windows
    reaches for when an app supplies nothing.
  * the **AppUserModelID**, which decides which taskbar button the window
    belongs to.  The shortcut to pin, listed in ``pyproject.toml``, carries
    ``Local.PromptCrafter``; a process that does not claim the same id is
    treated as a different application and gets a second button beside the pin
    it was launched from.

Both have to be set before the first window exists, which is why this is called
from ``__main__`` rather than from the window's constructor.
"""
from __future__ import annotations

import logging
import sys
from pathlib import Path

from app_support.win32 import set_app_user_model_id as claim_taskbar_identity
from shared_ui.preview import Preview, preview_of, taskbar_identity

logger = logging.getLogger(__name__)

APP_USER_MODEL_ID = "Local.PromptCrafter"


def claim_this_checkouts_identity(checkout: Path) -> Preview | None:
    """Claim the taskbar identity of what *checkout* runs as, and say what that is.

    A no-op off Windows, and never fatal: an app that cannot group its taskbar
    button is still an app that runs.
    """
    preview = preview_of(checkout)
    if sys.platform == "win32":
        try:
            claim_taskbar_identity(taskbar_identity(APP_USER_MODEL_ID, preview))
        except OSError:
            logger.warning("Could not set the AppUserModelID", exc_info=True)
    return preview
