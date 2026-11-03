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
    assert copy_button("Copy prompt").text() == ""


def test_it_brightens_while_the_cursor_is_over_it(qapp):
    button = copy_button("Copy prompt")
    icon = button.icon()

    assert icon.pixmap(_size(), QIcon.Mode.Active).toImage() == \
        icon_pixmap("copy", _MARK, TEXT_SECONDARY).toImage()
    assert icon.pixmap(_size(), QIcon.Mode.Active).toImage() != \
        icon.pixmap(_size(), QIcon.Mode.Normal).toImage()


def test_it_keeps_the_name_a_screen_reader_reads(qapp):
    assert copy_button("Copy section").accessibleName() == "Copy section"
    assert copy_button("Copy section").objectName() == "copy_button"


def test_it_is_the_familys_square_button(qapp):
    button = copy_button("Copy prompt")

    assert button.property(ICON_BUTTON_PROPERTY) is True
    assert (button.width(), button.height()) == (BUTTON_SIZE, BUTTON_SIZE)
