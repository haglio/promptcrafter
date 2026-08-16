"""Win32 identity for the PromptCrafter window.

Two different things decide what Windows shows for a running app, and neither
of them is the shortcut that started it:

  * the **window icon**, which is what Alt-Tab, the task list and the window's
    own corner draw.  Qt has none unless it is given one, so the window came up
    under a generic fallback -- not even Python's mark, just whatever Windows
    reaches for when an app supplies nothing.
  * the **AppUserModelID**, which decides which taskbar button the window
    belongs to.  ``Update-PromptCrafterShortcut.ps1`` already stamps the pinned
    shortcut with ``Local.PromptCrafter``; a process that does not claim the
    same id is treated as a different application and gets a second button
    beside the pin it was launched from.

Both have to be set before the first window exists, which is why this is called
from ``__main__`` rather than from the window's constructor.
"""
from __future__ import annotations

import ctypes
import logging
import sys

logger = logging.getLogger(__name__)

# The id the pinned shortcut carries.  One spelling in two places is one too
# many, but the shortcut is written by PowerShell and cannot read this -- so the
# script names it in a comment pointing here, and a mismatch shows up as the
# duplicate taskbar button this exists to prevent.
APP_USER_MODEL_ID = "Local.PromptCrafter"


def set_app_user_model_id(app_id: str = APP_USER_MODEL_ID) -> None:
    """Claim *app_id* for this process, so its window joins the pinned button.

    A no-op off Windows, and never fatal: an app that cannot group its taskbar
    button is still an app that runs.
    """
    if sys.platform != "win32":
        return
    try:
        result = ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(app_id)
    except (AttributeError, OSError):
        logger.warning("Could not set the AppUserModelID", exc_info=True)
        return
    if result < 0:
        logger.warning("SetCurrentProcessExplicitAppUserModelID failed: 0x%08x", result & 0xFFFFFFFF)
