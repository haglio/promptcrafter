from __future__ import annotations

import os

import pytest
from PySide6.QtWidgets import QApplication
from shared_ui.gui_thread_collection import the_application

# Qt reads this when the first QApplication is created, so it goes in before pytest-qt's qapp.
os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")


@pytest.fixture(autouse=True, scope="session")
def _cycles_collected_on_the_gui_thread_as_promptcrafter_collects_them(qapp):
    the_application(QApplication, [])
