"""The window's looks: the stylesheet, and the copy button's mark.

A 160-line Qt stylesheet and the two helpers that feed it were the first third
of `app.py`, ahead of the class that is what the module is for. Nothing here
knows about the schema, the state or a control kind; it is colors, geometry and
one icon.
"""

from __future__ import annotations

from PyQt6.QtCore import QSize
from PyQt6.QtGui import QIcon
from PyQt6.QtWidgets import QPushButton

# shared_ui is imported via sys.path rather than installed; make it importable
# regardless of checkout depth (normal clone vs .claude/worktrees/<name>).
from shared_ui.colors import (
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
)
from shared_ui.fonts import FONT_UI, SIZE_BODY, SIZE_HEADING
from shared_ui.icons import icon_pixmap
from shared_ui.spacing import (
    BUTTON_ICON_INSET,
    BUTTON_PAD_H,
    BUTTON_PAD_H_TIGHT,
    BUTTON_PAD_V,
    BUTTON_RADIUS,
    GAP_MEDIUM,
    MARGIN_DIALOG,
)
from shared_ui.type_scale import in_pixels

# The copy button's mark, at the size its 22px square leaves room for.
_COPY_ICON = 14

_GROOVE_H = 4
_HANDLE_SIDE = 14
_TITLE_ROOM = in_pixels(SIZE_HEADING) + 2 * GAP_MEDIUM


def copy_button(accessible_name: str) -> QPushButton:
    """A copy button wearing the family's two-overlapping-sheets mark.

    It was the clipboard emoji, which is a picture out of whatever font Windows
    resolves it to -- a different drawing at a different weight from the copy
    buttons in Origenerator and Fun Time, which the user has open beside this.

    Two renderings rather than one: Qt swaps to the Active pixmap while the
    cursor is over the button, and a stylesheet hover rule cannot reach into a
    drawn mark the way it reaches text.
    """
    button = QPushButton()
    button.setObjectName("copy_button")
    button.setAccessibleName(accessible_name)
    icon = QIcon()
    icon.addPixmap(icon_pixmap("copy", _COPY_ICON, TEXT_MUTED), QIcon.Mode.Normal)
    icon.addPixmap(icon_pixmap("copy", _COPY_ICON, TEXT_SECONDARY), QIcon.Mode.Active)
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
        border-radius: {BUTTON_RADIUS}px;
        padding: {MARGIN_DIALOG}px;
        padding-top: {_TITLE_ROOM}px;
        margin-top: {GAP_MEDIUM}px;
        font-weight: bold;
        font-size: {SIZE_HEADING}pt;
        color: {t1};
    }}
    QGroupBox::title {{
        subcontrol-origin: margin;
        subcontrol-position: top left;
        padding: {GAP_MEDIUM}px {MARGIN_DIALOG}px;
        color: {t1};
    }}
    QPlainTextEdit {{
        background: {bg2};
        color: {t1};
        border: 1px solid {border};
        border-radius: {BUTTON_RADIUS}px;
        padding: {MARGIN_DIALOG}px;
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
        spacing: {GAP_MEDIUM}px;
        background: transparent;
    }}
    QRadioButton::indicator, QCheckBox::indicator {{
        width: 16px;
        height: 16px;
    }}
    QRadioButton:disabled, QCheckBox:disabled {{
        color: {t_muted};
    }}
    /* A plain button is the family's, from the application's sheet.  The
       named ones below keep their own shapes, borderless as they were. */
    QPushButton#primary_button {{
        background: {blue};
        color: {t1};
        border: none;
        border-radius: {BUTTON_RADIUS}px;
        padding: {BUTTON_PAD_V}px {BUTTON_PAD_H}px;
    }}
    QPushButton#copy_button {{
        background: transparent;
        color: {t_muted};
        border: none;
        padding: {BUTTON_ICON_INSET}px;
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
        border: none;
        padding: {BUTTON_ICON_INSET}px {BUTTON_PAD_H_TIGHT}px;
        border-radius: {BUTTON_RADIUS}px;
    }}
    QPushButton#mode_toggle_auto {{
        background: {bg_key};
        color: {t2};
        border: none;
        border-radius: {BUTTON_RADIUS}px;
        padding: {BUTTON_PAD_V}px {BUTTON_PAD_H_TIGHT}px;
    }}
    /* Manual mode is a state that means more than "engaged", and the family
       spends its one blue on those; the teal it wore was a hue no other app
       has. */
    QPushButton#mode_toggle_manual {{
        background: {blue};
        color: {t1};
        border: none;
        border-radius: {BUTTON_RADIUS}px;
        padding: {BUTTON_PAD_V}px {BUTTON_PAD_H_TIGHT}px;
    }}
    QWidget#prompt_area {{
        background: {bg3};
        border: 1px solid {bg_btn};
        border-radius: {BUTTON_RADIUS}px;
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
        height: {_GROOVE_H}px;
        background: {bg_btn};
        border-radius: {_GROOVE_H // 2}px;
    }}
    QSlider::handle:horizontal {{
        width: {_HANDLE_SIDE}px;
        height: {_HANDLE_SIDE}px;
        margin: -{(_HANDLE_SIDE - _GROOVE_H) // 2}px 0;
        background: {blue};
        border-radius: {_HANDLE_SIDE // 2}px;
    }}
    QSlider::sub-page:horizontal {{
        background: {blue};
        border-radius: {_GROOVE_H // 2}px;
    }}
    """
