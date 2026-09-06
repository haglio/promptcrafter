import sys

from PyQt6.QtGui import QIcon
from PyQt6.QtWidgets import QApplication

from promptcrafter.app import PromptCrafterWindow
from promptcrafter.paths import ensure_shared_ui_on_path, icon_path
from promptcrafter.process_name import name_this_process
from promptcrafter.schema_overlay import load_schema
from promptcrafter.win32 import set_app_user_model_id

ensure_shared_ui_on_path()
from shared_ui.chrome import family_stylesheet  # noqa: E402

# Both before the first window exists: the id decides which taskbar button the
# window joins, and Qt hands every later window the application icon set here.
# Without them PromptCrafter came up under a generic fallback mark and beside
# its own pinned shortcut rather than in it.  See promptcrafter.win32.
set_app_user_model_id()

# And leave the shortcut an interpreter that says so in the task list -- see
# promptcrafter.process_name.  One run late, because writing the copy takes
# the very interpreter being named.
name_this_process()

app = QApplication(sys.argv)
# The family's chrome goes on the application, where the tooltip rule can
# reach a top-level popup; the window's own sheet sits over it.
app.setStyleSheet(family_stylesheet())
icon = icon_path()
if icon.is_file():
    app.setWindowIcon(QIcon(str(icon)))
window = PromptCrafterWindow(load_schema())
window.show()
sys.exit(app.exec())
