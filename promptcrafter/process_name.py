from __future__ import annotations

from app_support.process_identity import ProcessNamer

from promptcrafter.paths import icon_path

APP_NAME = "PromptCrafter"
ROLE = "PromptCrafter"


def namer():
    return ProcessNamer(APP_NAME, icon=icon_path())


def name_this_process() -> None:
    namer().name_this_process(ROLE)
