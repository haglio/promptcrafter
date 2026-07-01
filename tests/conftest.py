import os

# Render Qt offscreen for the whole suite. Agents run this suite on every commit
# (and across parallel worktrees), so without this each test that shows a widget
# throws a real window onto the screen for a few milliseconds — a run flashes a
# burst of windows. Must be set before any QApplication is created (i.e. before
# pytest-qt's qapp fixture); setdefault lets a developer override it to watch a
# test on a real display.
os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from promptcrafter.paths import ensure_shared_ui_on_path

# Make shared_ui importable for tests regardless of checkout depth, before any
# test module (some import shared_ui directly) is collected.
ensure_shared_ui_on_path()
