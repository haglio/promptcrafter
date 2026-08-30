"""What a control's kind means, asked in one place.

Six sites ask "is this kind single-select?" -- the state builder (twice, once
for controls and once for submenus), the widget builder (twice, the same way),
the has-a-selection query, and the renderer. Five of them spelled it
``kind.startswith('or')`` and the sixth built a set of the four ``or`` kinds
inside the render function; both came straight across from the TypeScript this
was ported from (``src/lib/state.ts:24``, ``:38``, ``src/components/Control.tsx:298``,
``src/components/Submenu.tsx:113``, ``src/lib/runtime.ts:55`` against
``src/lib/runtime.ts:522``).

They agreed on every kind that has ever existed, so the difference was invisible
-- and it could only ever show as the state shape and the renderer disagreeing
about one control, which is a shape no schema should be able to reach. It is the
majority spelling now, at all six, so they cannot disagree at all.
"""

from __future__ import annotations

from promptcrafter.types import SubmenuKind

# The submenu kinds whose modifier follows the option text instead of preceding
# it. A different question from single-select, though the two tests sit close
# enough to look alike: of the four submenu kinds these two answers match on
# `or-adv` and `and-adj` and differ on the other two.
ADVERB_SUBMENU_KINDS: frozenset[SubmenuKind] = frozenset({"or-adv", "and-adv"})


def is_radio_kind(kind: str) -> bool:
    """One selection rather than several -- a radio group, not checkboxes.

    Decides the state shape (a string, not a list), the widget class, whether
    the control counts as having a selection, and which renderer builds its
    text. All four answers come from here, so they cannot drift apart.

    The rule is the naming convention the schema already follows: every
    single-select kind is named `or`-something, and no other kind is. It holds
    over all twelve control kinds and all four submenu kinds.
    """
    return kind.startswith("or")


def is_adverb_submenu_kind(kind: str) -> bool:
    """A submenu whose text goes after the option's -- a word-order question.

    Not the same question as :func:`is_radio_kind`, though the two tests look
    alike where they sit: this one decides only whether the modifier precedes
    or follows the option text, and over the four submenu kinds the two answers
    differ on half of them.
    """
    return kind in ADVERB_SUBMENU_KINDS
