from __future__ import annotations

import ast
from pathlib import Path
from unittest.mock import patch

from shared_ui import loading_process

from promptcrafter import opening
from promptcrafter.paths import icon_path
from promptcrafter.win32 import APP_USER_MODEL_ID


class _Loading:
    def __init__(self):
        self.said: list[str] = []

    def say(self, step: str) -> None:
        self.said.append(step)


def test_the_launch_says_each_step_before_it_takes_it():
    loading = _Loading()
    with patch.object(opening, "load_schema") as loaded, \
         patch.object(opening, "report_dangling_references") as checked, \
         patch.object(opening, "PromptCrafterWindow") as window_class:
        window = opening.open_promptcrafter(loading, preview=None)

    assert loading.said == [step for step, _weight in opening.STEPS]
    checked.assert_called_once_with(loaded.return_value)
    window_class.assert_called_once_with(loaded.return_value, preview=None)
    assert window is window_class.return_value


def test_the_loading_screen_runs_in_a_process_of_its_own_wearing_promptcrafters_taskbar_button(
        monkeypatch):
    monkeypatch.setattr(opening.sys, "platform", "win32")

    with patch.object(loading_process.LoadingProcess, "open") as opened:
        opening.open_the_loading_screen(None)

    opened.assert_called_once_with(
        caption="PromptCrafter Loading", wordmark="PromptCrafter", icon=icon_path(), preview=None,
        steps=opening.STEPS, cancel_hint="Press Esc to cancel opening PromptCrafter",
        app_id=APP_USER_MODEL_ID)


def test_the_launch_opens_its_loading_screen_only_when_a_launcher_with_one_started_it():
    entry_point = ast.parse((Path(opening.__file__).parent / "__main__.py").read_text(encoding="utf-8"))
    opened = [ast.unparse(node) for node in ast.walk(entry_point)
              if isinstance(node, ast.Call) and ast.unparse(node.func) == "Loading.at_the_click"]

    expected = ("Loading.at_the_click(app, logging.getLogger('promptcrafter'), "
                "lambda: open_the_loading_screen(preview))")
    assert opened == [expected]


def test_off_windows_the_loading_screen_wears_no_taskbar_identity(monkeypatch):
    monkeypatch.setattr(opening.sys, "platform", "linux")

    with patch.object(loading_process.LoadingProcess, "open") as opened:
        opening.open_the_loading_screen(None)

    assert opened.call_args.kwargs["app_id"] is None
