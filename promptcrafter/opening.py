from __future__ import annotations

import sys

from shared_ui.preview import Preview, taskbar_identity

from promptcrafter.app import PromptCrafterWindow
from promptcrafter.paths import icon_path
from promptcrafter.references import report_dangling_references
from promptcrafter.schema_overlay import load_schema
from promptcrafter.win32 import APP_USER_MODEL_ID

STEPS = (
    ("Loading PromptCrafter...", 1.0),
    ("Opening the window...", 1.0),
)


def open_promptcrafter(loading, *, preview: Preview | None) -> PromptCrafterWindow:
    loading_promptcrafter, opening_the_window = (step for step, _weight in STEPS)
    loading.say(loading_promptcrafter)
    schema = load_schema()
    # Say on the way up which ids this schema points at and does not hold. Each one
    # renders as nothing, so without this a typo is indistinguishable from a blank
    # someone meant; the launcher sends this stream to its log.
    report_dangling_references(schema)
    loading.say(opening_the_window)
    return PromptCrafterWindow(schema, preview=preview)


def open_the_loading_screen(preview: Preview | None):
    from shared_ui.loading_process import LoadingProcess  # noqa: PLC0415

    return LoadingProcess.open(
        caption="PromptCrafter Loading", wordmark="PromptCrafter", icon=icon_path(), preview=preview,
        steps=STEPS, cancel_hint="Press Esc to cancel opening PromptCrafter",
        app_id=taskbar_identity(APP_USER_MODEL_ID, preview) if sys.platform == "win32" else None,
    )
