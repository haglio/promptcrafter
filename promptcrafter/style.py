"""The window's looks: the stylesheet, and the copy button's mark.

A 160-line Qt stylesheet and the two helpers that feed it were the first third
of `app.py`, ahead of the class that is what the module is for. Nothing here
knows about the schema, the state or a control kind; it is colours, geometry and
one icon.
"""

from __future__ import annotations

from PyQt6.QtCore import QSize
from PyQt6.QtGui import QIcon
from PyQt6.QtWidgets import QPushButton

from promptcrafter.paths import ensure_shared_ui_on_path

# shared_ui is imported via sys.path rather than installed; make it importable
# regardless of checkout depth (normal clone vs .claude/worktrees/<name>).
ensure_shared_ui_on_path()

from shared_ui.colors import (  # noqa: E402
    BG_BUTTON,
    BG_KEYCAP,
    BG_PRIMARY,
    BG_SECONDARY,
    BG_TERTIARY,
    BLUE,
    BORDER_SUBTLE,
    TEXT_MUTED,
    TEXT_PRIMARY,
    TEXT_SECONDARY,
    TOGGLE_OFF,
    TOGGLE_ON,
)
from shared_ui.fonts import FONT_UI, SIZE_BODY, SIZE_HEADING  # noqa: E402
from shared_ui.icons import glyph_pixmap  # noqa: E402


# The copy button's mark, at the size its 22px square leaves room for.
_COPY_ICON = 14


def copy_button(accessible_name: str) -> QPushButton:
    """A copy button wearing the family's two-overlapping-sheets mark.

    It was the clipboard emoji, which is a picture out of whatever font Windows
    resolves it to -- a different drawing at a different weight from the copy
    buttons in Origenerator and Fun Time, which the user has open beside this.

    Two renderings rather than one: Qt swaps to the Active pixmap while the
    cursor is over the button, which is how the stylesheet's hover brightening
    used to reach the glyph back when the glyph was text.
    """
    button = QPushButton()
    button.setObjectName("copy_button")
    button.setAccessibleName(accessible_name)
    icon = QIcon()
    icon.addPixmap(glyph_pixmap("copy", _COPY_ICON, TEXT_MUTED), QIcon.Mode.Normal)
    icon.addPixmap(glyph_pixmap("copy", _COPY_ICON, TEXT_SECONDARY), QIcon.Mode.Active)
    button.setIcon(icon)
    button.setIconSize(QSize(_COPY_ICON, _COPY_ICON))
    return button


def _qcolor_hex(c) -> str:
    return c.name()


def build_stylesheet() -> str:
    bg1 = _qcolor_hex(BG_PRIMARY)
    bg2 = _qcolor_hex(BG_SECONDARY)
    bg3 = _qcolor_hex(BG_TERTIARY)
    bg_btn = _qcolor_hex(BG_BUTTON)
    bg_key = _qcolor_hex(BG_KEYCAP)
    t1 = _qcolor_hex(TEXT_PRIMARY)
    t2 = _qcolor_hex(TEXT_SECONDARY)
    t_muted = _qcolor_hex(TEXT_MUTED)
    border = _qcolor_hex(BORDER_SUBTLE)
    blue = _qcolor_hex(BLUE)
    tog_on = _qcolor_hex(TOGGLE_ON)
    tog_off = _qcolor_hex(TOGGLE_OFF)
    font = FONT_UI
    sz = SIZE_BODY

    return f"""
    QMainWindow, QWidget#central {{
        background: {bg1};
        color: {t1};
        font-family: "{font}";
        font-size: {sz}pt;
    }}
    QScrollArea, QScrollArea > QWidget > QWidget {{
        background: {bg1};
        border: none;
    }}
    QGroupBox {{
        background: {bg3};
        border: 1px solid {bg_btn};
        border-radius: 16px;
        padding: 16px;
        padding-top: 36px;
        margin-top: 8px;
        font-weight: bold;
        font-size: {SIZE_HEADING}pt;
        color: {t1};
    }}
    QGroupBox::title {{
        subcontrol-origin: margin;
        subcontrol-position: top left;
        padding: 8px 16px;
        color: {t1};
    }}
    QPlainTextEdit {{
        background: {bg2};
        color: {t1};
        border: 1px solid {border};
        border-radius: 12px;
        padding: 12px;
        font-family: "{font}";
        font-size: {sz}pt;
    }}
    QPlainTextEdit:disabled {{
        color: {t2};
    }}
    QLabel {{
        color: {t1};
        background: transparent;
    }}
    QRadioButton, QCheckBox {{
        color: {t2};
        spacing: 6px;
        background: transparent;
    }}
    QRadioButton::indicator, QCheckBox::indicator {{
        width: 16px;
        height: 16px;
    }}
    QRadioButton:disabled, QCheckBox:disabled {{
        color: {t_muted};
    }}
    QPushButton {{
        background: {bg_key};
        color: {t2};
        border: none;
        border-radius: 6px;
        padding: 4px 8px;
        font-size: {sz}pt;
    }}
    QPushButton:hover {{
        background: {bg_btn};
    }}
    QPushButton#primary_button {{
        background: {blue};
        color: {t1};
        border-radius: 8px;
        padding: 8px 12px;
    }}
    QPushButton#copy_button {{
        background: transparent;
        color: {t_muted};
        padding: 2px;
        min-width: 22px;
        max-width: 22px;
        min-height: 22px;
        max-height: 22px;
    }}
    QPushButton#copy_button:hover {{
        background: {bg_btn};
        color: {t2};
    }}
    QPushButton#weight_reset {{
        background: {bg_key};
        color: {t2};
        font-size: 12px;
        padding: 2px 6px;
        border-radius: 4px;
    }}
    QPushButton#mode_toggle_auto {{
        background: {bg_key};
        color: {t2};
        border-radius: 6px;
        padding: 4px 8px;
    }}
    QPushButton#mode_toggle_manual {{
        background: #0f766e;
        color: {t1};
        border-radius: 6px;
        padding: 4px 8px;
    }}
    QWidget#prompt_area {{
        background: {bg3};
        border: 1px solid {bg_btn};
        border-radius: 16px;
    }}
    QWidget#control_divider {{
        background: {bg_btn};
        min-height: 1px;
        max-height: 1px;
    }}
    QWidget#submenu_indent {{
        border-left: 2px solid {border};
    }}
    QSlider::groove:horizontal {{
        height: 4px;
        background: {bg_btn};
        border-radius: 2px;
    }}
    QSlider::handle:horizontal {{
        width: 14px;
        height: 14px;
        margin: -5px 0;
        background: {blue};
        border-radius: 7px;
    }}
    QSlider::sub-page:horizontal {{
        background: {blue};
        border-radius: 2px;
    }}
    QCheckBox#toggle_switch {{
        spacing: 0px;
    }}
    QCheckBox#toggle_switch::indicator {{
        width: 44px;
        height: 24px;
        border-radius: 12px;
        background: {tog_off};
    }}
    QCheckBox#toggle_switch::indicator:checked {{
        background: {tog_on};
    }}
    """
