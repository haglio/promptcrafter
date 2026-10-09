from __future__ import annotations

import ast
import sys
import threading
from pathlib import Path

from PyQt6.QtCore import QTimer

from promptcrafter.errors import log_errors_and_keep_running

ENTRY_POINT = Path(__file__).resolve().parents[1] / "promptcrafter" / "__main__.py"


def test_an_error_nothing_catches_is_logged_and_the_app_keeps_running(qtbot, monkeypatch, caplog):
    monkeypatch.setattr(sys, "excepthook", sys.excepthook)
    monkeypatch.setattr(threading, "excepthook", threading.excepthook)
    log_errors_and_keep_running()
    went_on = []

    def go_wrong():
        raise RuntimeError("an invented error no handler expects")

    QTimer.singleShot(0, go_wrong)
    QTimer.singleShot(20, lambda: went_on.append(True))
    qtbot.waitUntil(lambda: went_on == [True])

    (logged,) = [record for record in caplog.records if record.name == "promptcrafter"]
    assert "an invented error no handler expects" in str(logged.exc_info[1])


def test_the_launch_does_so_before_the_app_exists():
    tree = ast.parse(ENTRY_POINT.read_text(encoding="utf-8"))
    first_call = {}
    for node in ast.walk(tree):
        if isinstance(node, ast.Call):
            name = ast.unparse(node.func)
            first_call[name] = min(node.lineno, first_call.get(name, node.lineno))

    assert first_call["log_errors_and_keep_running"] < first_call["QApplication"]
