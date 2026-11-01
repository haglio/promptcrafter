"""The copy buttons wear the family's mark, not an emoji.

They were U+1F4CB, the clipboard emoji -- a picture out of whatever font Windows
resolves it to, at a weight nothing else here shares.  Origenerator and Fun Time
both draw a two-overlapping-sheets copy glyph, and all three apps are open on one
screen, so this one draws it too.
"""

from __future__ import annotations

from PyQt6.QtCore import QSize
from PyQt6.QtGui import QIcon
from shared_ui.chrome import ICON_BUTTON_PROPERTY
from shared_ui.colors import TEXT_MUTED, TEXT_SECONDARY
from shared_ui.icons import icon_pixmap
from shared_ui.spacing import BUTTON_ICON_INSET, BUTTON_SIZE

from promptcrafter.style import copy_button

_MARK = BUTTON_SIZE - 2 * BUTTON_ICON_INSET


def _size() -> QSize:
    return QSize(_MARK, _MARK)


def test_it_wears_the_familys_copy_mark(qapp):
    button = copy_button("Copy prompt")

    assert button.icon().pixmap(_size(), QIcon.Mode.Normal).toImage() == \
        icon_pixmap("copy", _MARK, TEXT_MUTED).toImage()


def test_it_carries_no_text_of_its_own(qapp):
    # An emoji left as the label would sit beside the icon rather than instead
    # of it, which is worse than either on its own.
    assert copy_button("Copy prompt").text() == ""


def test_it_brightens_while_the_cursor_is_over_it(qapp):
    # The stylesheet's hover rule used to brighten the glyph because the glyph
    # was text. Qt swaps to the Active pixmap for a hovered button, so the mark
    # keeps that feedback now that it is drawn.
    button = copy_button("Copy prompt")
    icon = button.icon()

    assert icon.pixmap(_size(), QIcon.Mode.Active).toImage() == \
        icon_pixmap("copy", _MARK, TEXT_SECONDARY).toImage()
    assert icon.pixmap(_size(), QIcon.Mode.Active).toImage() != \
        icon.pixmap(_size(), QIcon.Mode.Normal).toImage()


def test_it_keeps_the_name_a_screen_reader_reads(qapp):
    # The emoji was the only thing naming the control; dropping it for an icon
    # would have left the button anonymous.
    assert copy_button("Copy section").accessibleName() == "Copy section"
    assert copy_button("Copy section").objectName() == "copy_button"


def test_it_is_the_familys_square_button(qapp):
    button = copy_button("Copy prompt")

    assert button.property(ICON_BUTTON_PROPERTY) is True
    assert (button.width(), button.height()) == (BUTTON_SIZE, BUTTON_SIZE)
