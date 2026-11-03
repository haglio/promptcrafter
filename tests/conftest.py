from __future__ import annotations

import os

# Qt reads this when the first QApplication is created, so it goes in before pytest-qt's qapp.
os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")


