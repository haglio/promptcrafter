from __future__ import annotations

import logging
import sys

from PyQt6.QtWidgets import QApplication
from shared_ui.chrome import family_stylesheet
from shared_ui.loading_window import Loading, LoadingCanceled
from shared_ui.preview_icon import app_icon

from promptcrafter.errors import log_errors_and_keep_running
from promptcrafter.opening import open_promptcrafter, open_the_loading_screen
from promptcrafter.paths import icon_path, project_root
from promptcrafter.process_name import name_this_process
from promptcrafter.win32 import claim_this_checkouts_identity

# Both before the first window exists: the id decides which taskbar button the
# window joins, and Qt hands every later window the application icon set here.
# Without them the window wears a generic fallback mark and sits beside its own
# pinned shortcut rather than in it.  See promptcrafter.win32.
preview = claim_this_checkouts_identity(project_root())

# And leave the shortcut an interpreter that says so in the task list -- see
# promptcrafter.process_name.  One run late, because writing the copy takes
# the very interpreter being named.
name_this_process()

log_errors_and_keep_running()

app = QApplication(sys.argv)
# The family's chrome goes on the application, where the tooltip rule can
# reach a top-level popup; the window's own sheet sits over it.
app.setStyleSheet(family_stylesheet())
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
