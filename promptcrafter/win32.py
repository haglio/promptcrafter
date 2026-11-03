# Windows takes the taskbar button from the AppUserModelID, and Qt gives a window no icon
# unless it is handed one; both have to be set before the first window exists.
from __future__ import annotations

import logging
import sys
from pathlib import Path

from app_support.win32 import set_app_user_model_id as claim_taskbar_identity
from shared_ui.preview import Preview, preview_of, taskbar_identity

logger = logging.getLogger(__name__)

APP_USER_MODEL_ID = "Local.PromptCrafter"


def claim_this_checkouts_identity(checkout: Path) -> Preview | None:
    preview = preview_of(checkout)
    if sys.platform == "win32":
        try:
            claim_taskbar_identity(taskbar_identity(APP_USER_MODEL_ID, preview))
        except OSError:
            logger.warning("Could not set the AppUserModelID", exc_info=True)
    return preview
