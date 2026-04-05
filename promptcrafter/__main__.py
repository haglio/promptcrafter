import sys

from PyQt6.QtWidgets import QApplication

from promptcrafter.app import PromptCrafterWindow
from promptcrafter.schema import schema

app = QApplication(sys.argv)
window = PromptCrafterWindow(schema)
window.show()
sys.exit(app.exec())
