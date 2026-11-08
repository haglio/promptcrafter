from __future__ import annotations

import ast
from pathlib import Path

CONFTEST = Path(__file__).with_name("conftest.py")


def test_the_suite_renders_offscreen_so_no_test_flashes_a_window_onto_his_screen(qapp):
    assert qapp.platformName() == "offscreen"


def test_a_developer_who_sets_qt_qpa_platform_himself_watches_a_test_on_a_real_display():
    settings = [ast.unparse(node.func) for node in ast.walk(ast.parse(CONFTEST.read_text(encoding="utf-8")))
                if isinstance(node, ast.Call) and node.args
                and isinstance(node.args[0], ast.Constant) and node.args[0].value == "QT_QPA_PLATFORM"]

    assert settings == ["os.environ.setdefault"]
