"""Guard that the GUI suite renders offscreen.

If this fails, ``tests/conftest.py`` is no longer forcing the offscreen Qt
platform and running the suite will flash real windows onto the screen.
"""


def test_gui_suite_renders_offscreen(qapp):
    assert qapp.platformName() == "offscreen"
