import os
import random

import pytest

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


def pytest_collection_modifyitems(items):
    """Collect in a different order when asked, so a test that leans on the ones
    beside it fails on the commit that introduces the lean.

    ``TEST_COLLECTION_ORDER=reverse`` collects back to front;
    ``TEST_COLLECTION_ORDER=shuffle`` shuffles with ``TEST_COLLECTION_SEED`` (0
    unless given), so a red run can be repeated exactly.  Unset leaves the order
    alone; anything else is a typo, and a typo that silently ran forward would
    make the gate's second leg a green that proves nothing.
    """
    order = os.environ.get("TEST_COLLECTION_ORDER")
    if order is None:
        return
    if order == "reverse":
        items.reverse()
    elif order == "shuffle":
        random.Random(int(os.environ.get("TEST_COLLECTION_SEED", "0"))).shuffle(items)
    else:
        raise pytest.UsageError(
            f"TEST_COLLECTION_ORDER={order!r}: expected 'reverse' or 'shuffle'"
        )
