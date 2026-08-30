"""The two rival answers to "is this a radio kind?", kept side by side.

Three modules asked it with `kind.startswith("or")` and a fourth with an
explicit set of four. Nobody had written down whether that was a difference or
an accident, so this does: over every kind that exists they agree exactly, and
they part company only on a string that begins with `or` and is not one of the
four.

Which of the two the codebase should keep is the owner's call (flagged
2026-08-30). Until it is made, both keep a name and this file keeps the
evidence -- including a test that reds the day a thirteenth `or-*` kind is
declared without the question being answered.
"""

from typing import get_args

from promptcrafter.kinds import (
    ADVERB_SUBMENU_KINDS,
    RADIO_CONTROL_KINDS,
    RADIO_SUBMENU_KINDS,
    is_adverb_submenu_kind,
    is_or_prefixed_kind,
    is_radio_kind,
    is_radio_submenu_kind,
)
from promptcrafter.types import ControlKind, SubmenuKind

DECLARED_CONTROL_KINDS = get_args(ControlKind)
DECLARED_SUBMENU_KINDS = get_args(SubmenuKind)


class TestTheTwoRivals:
    def test_they_agree_on_every_declared_control_kind(self):
        disagreements = [
            kind for kind in DECLARED_CONTROL_KINDS
            if is_radio_kind(kind) != is_or_prefixed_kind(kind)
        ]

        assert disagreements == []

    def test_the_declared_kinds_are_still_the_twelve_the_owner_kept(self):
        """Membership is fixed by decision, not by convenience (Q15).

        A kind added or removed has to move this line, which is the point: the
        schema format is what the README points users at.
        """
        assert set(DECLARED_CONTROL_KINDS) == {
            "or", "or-adv", "or-adj", "or-prefix",
            "and-commas", "and-commas-adj", "and-commas-adv",
            "and-spaces-adj", "required", "hidden-opposite",
            "toggle", "global-selector",
        }

    def test_a_thirteenth_or_kind_would_have_to_settle_which_rival_is_right(self):
        """The alarm. It reds on the change that makes the difference matter.

        Declare `or-something` without adding it to `RADIO_CONTROL_KINDS` and
        the closed rival calls it a checkbox control while the open one calls it
        a radio -- so the state is a string, the widgets are radios, and the
        renderer falls through to the and-commas branch, which wants a list and
        finds none. A fully interactive control that renders nothing, with no
        error anywhere.
        """
        assert RADIO_CONTROL_KINDS <= set(DECLARED_CONTROL_KINDS)
        assert {k for k in DECLARED_CONTROL_KINDS if is_or_prefixed_kind(k)} == RADIO_CONTROL_KINDS

    def test_they_part_company_off_the_declared_kinds(self):
        for kind in ("or-suffix", "orange", "order", "or2", "or-"):
            assert is_or_prefixed_kind(kind)
            assert not is_radio_kind(kind)

    def test_a_kind_that_does_not_begin_with_or_is_neither(self):
        for kind in ("and-commas-x", "totally-new", "OR"):
            assert not is_or_prefixed_kind(kind)
            assert not is_radio_kind(kind)


class TestTheSubmenuPredicatesAreNotOneQuestion:
    """Arity and word order, which look alike and are not.

    `is_radio_submenu_kind` decides the state shape and the widget class;
    `is_adverb_submenu_kind` decides only whether the modifier goes before the
    option text or after. They agree on two of the four submenu kinds and
    differ on the other two, so a refactor that merged them would be wrong.
    """

    def test_they_disagree_on_half_the_declared_submenu_kinds(self):
        answers = {
            kind: (is_radio_submenu_kind(kind), is_adverb_submenu_kind(kind))
            for kind in DECLARED_SUBMENU_KINDS
        }

        assert answers == {
            "or-adv": (True, True),
            "or-adj": (True, False),
            "and-adv": (False, True),
            "and-adj": (False, False),
        }

    def test_both_sets_are_drawn_from_the_declared_submenu_kinds(self):
        assert RADIO_SUBMENU_KINDS <= set(DECLARED_SUBMENU_KINDS)
        assert ADVERB_SUBMENU_KINDS <= set(DECLARED_SUBMENU_KINDS)

    def test_the_prefix_rival_answers_the_arity_question_for_submenus_too(self):
        """Which is why one expression served both, and why it was hard to see.

        No submenu kind is `or` or `or-prefix`, so over the four that exist the
        prefix test and the submenu set give the same answer.
        """
        for kind in DECLARED_SUBMENU_KINDS:
            assert is_or_prefixed_kind(kind) == is_radio_submenu_kind(kind)
