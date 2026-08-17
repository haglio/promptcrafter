import sys

from PyQt6.QtGui import QIcon
from PyQt6.QtWidgets import QApplication

from promptcrafter.app import PromptCrafterWindow
from promptcrafter.paths import icon_path
from promptcrafter.process_name import name_this_process
from promptcrafter.schema import schema
from promptcrafter.win32 import set_app_user_model_id

# Both before the first window exists: the id decides which taskbar button the
# window joins, and Qt hands every later window the application icon set here.
# Without them PromptCrafter came up under a generic fallback mark and beside
# its own pinned shortcut rather than in it.  See promptcrafter.win32.
set_app_user_model_id()

# And leave the shortcut an interpreter that says so in the task list -- see
# promptcrafter.process_name.  One run behind, because writing the copy takes
# the very interpreter being named.
name_this_process()

app = QApplication(sys.argv)
icon = icon_path()
if icon.is_file():
    app.setWindowIcon(QIcon(str(icon)))
window = PromptCrafterWindow(schema)
window.show()
sys.exit(app.exec())
