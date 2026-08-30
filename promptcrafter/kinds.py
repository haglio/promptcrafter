"""What a control's kind means, gathered from the six places that asked.

Six sites ask whether a kind is single-select: the state builder twice (controls
and submenus), the widget builder twice the same way, the has-a-selection query,
and the render dispatch. Five of them spell it ``kind.startswith("or")``; the
sixth uses an explicit set of the four ``or`` kinds. **That is how the original
was written and it is kept that way deliberately** -- the two came across from
the TypeScript this was ported from (``src/lib/state.ts:24``, ``:38``,
``src/components/Control.tsx:298``, ``src/components/Submenu.tsx:113``,
``src/lib/runtime.ts:55``, against ``src/lib/runtime.ts:522``), and the owner
confirmed on 2026-08-30 that they should stand.

What this module changes is only where they live: six inline spellings across
three modules became two named functions here, each site still asking the one it
always asked. They give the same answer for every kind that exists -- all twelve
``ControlKind`` members and all four ``SubmenuKind`` members -- so the only way
to make them differ is to declare a thirteenth kind starting with ``or`` and not
add it to :data:`RADIO_CONTROL_KINDS`. ``tests/test_kinds.py`` reds if that
happens, because such a control gets a string state and radio buttons from the
five, falls past the radio branch in the sixth, and renders nothing at all.
"""

from __future__ import annotations

from promptcrafter.types import ControlKind, SubmenuKind

# The four kinds the render dispatch treats as single-select.
RADIO_CONTROL_KINDS: frozenset[ControlKind] = frozenset({"or", "or-adv", "or-adj", "or-prefix"})

# The submenu kinds whose modifier follows the option text instead of preceding
# it. A different question from single-select, though the two tests sit close
# enough to look alike: of the four submenu kinds these two answers match on
# `or-adv` and `and-adj` and differ on the other two.
ADVERB_SUBMENU_KINDS: frozenset[SubmenuKind] = frozenset({"or-adv", "and-adv"})


def is_or_prefixed_kind(kind: str) -> bool:
    """The kind is named `or`-something.

    Asked at five of the six sites -- the state shape for controls and for
    submenus, the widget class for both, and whether a control counts as having
    a selection. Reads the schema's naming convention directly: every
    single-select kind is `or`-something and no other kind is.
    """
    return kind.startswith("or")


def is_radio_kind(kind: str) -> bool:
    """The kind is one of the four enumerated single-select control kinds.

    Asked at the sixth site, the render dispatch. Gives the same answer as
    :func:`is_or_prefixed_kind` for every kind that exists; the two can only
    part company over a kind starting with `or` that is not in the set above.
    """
    return kind in RADIO_CONTROL_KINDS


def is_adverb_submenu_kind(kind: str) -> bool:
    """A submenu whose text goes after the option's -- a word-order question.

    Not the arity question the two above answer, though it looks like it where
    it sits: over the four submenu kinds these answers differ on half of them.
    """
    return kind in ADVERB_SUBMENU_KINDS
