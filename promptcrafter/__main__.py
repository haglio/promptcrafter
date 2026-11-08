from __future__ import annotations

import logging
import sys

from PyQt6.QtWidgets import QApplication
from shared_ui.colors import dress_application
from shared_ui.loading_window import Loading, LoadingCanceled
from shared_ui.preview_icon import app_icon

from promptcrafter.errors import log_errors_and_keep_running
from promptcrafter.opening import open_promptcrafter, open_the_loading_screen
from promptcrafter.paths import icon_path, project_root
from promptcrafter.process_name import name_the_next_run
from promptcrafter.win32 import claim_this_checkouts_identity

# Before the first window exists: Windows picks the taskbar button from the id, and Qt hands
# every later window the application icon set here.
preview = claim_this_checkouts_identity(project_root())

name_the_next_run()

log_errors_and_keep_running()

app = QApplication(sys.argv)
dress_application(app)
icon = icon_path()
if icon.is_file():
    app.setWindowIcon(app_icon(icon, preview))
loading = Loading.at_the_click(app, logging.getLogger("promptcrafter"), lambda: open_the_loading_screen(preview))
try:
    window = open_promptcrafter(loading, preview=preview)
except LoadingCanceled:
    sys.exit(0)
loading.done()
window.show()
sys.exit(app.exec())
