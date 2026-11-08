from __future__ import annotations

from app_support.process_identity import ProcessNamer

from promptcrafter.paths import icon_path

APP_NAME = "PromptCrafter"
ROLE = "PromptCrafter"


def namer():
    return ProcessNamer(APP_NAME, icon=icon_path())


def ready_the_copy_windows_shows_the_next_run_as() -> None:
    namer().name_this_process(ROLE)
