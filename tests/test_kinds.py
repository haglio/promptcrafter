"""The two spellings of "is this kind single-select?", kept as the original had them.

Five sites ask `kind.startswith("or")` and the sixth, the render dispatch, uses
an explicit set of four. Both came across from the TypeScript and the owner
confirmed on 2026-08-30 that the split stands; this module gathers them into two
named functions without moving any site off the one it always asked.

They give the same answer for every kind that exists. The one way to make them
differ is to declare a thirteenth kind starting with `or` and not add it to
`RADIO_CONTROL_KINDS` — so that is what these tests watch, because such a
control gets a string state and radio buttons from the five, falls past the
radio branch in the sixth into one that wants a list, and renders nothing at
all with no error anywhere.
"""

from typing import get_args

import pytest

from promptcrafter.kinds import (
    ADVERB_SUBMENU_KINDS,
    RADIO_CONTROL_KINDS,
    is_adverb_submenu_kind,
    is_or_prefixed_kind,
    is_radio_kind,
)
from promptcrafter.runtime import build_prompt
from promptcrafter.state import create_initial_state
from promptcrafter.types import Control, ControlKind, Option, Schema, Section, SubmenuKind

DECLARED_CONTROL_KINDS = get_args(ControlKind)
DECLARED_SUBMENU_KINDS = get_args(SubmenuKind)


class TestTheDeclaredKinds:
    def test_the_twelve_are_the_ones_the_owner_kept(self):
        """Which kinds are declared is a decision, not a convenience (Q15).

        Adding or removing a kind has to move this line, which is the point:
        `ControlKind` is the schema format the README points users at.
        """
        assert set(DECLARED_CONTROL_KINDS) == {
            "or", "or-adv", "or-adj", "or-prefix",
            "and-commas", "and-commas-adj", "and-commas-adv",
            "and-spaces-adj", "required", "hidden-opposite",
            "toggle", "global-selector",
        }

    @pytest.mark.parametrize("kind", [*DECLARED_CONTROL_KINDS, *DECLARED_SUBMENU_KINDS])
    def test_the_two_spellings_answer_alike_for_every_kind_that_exists(self, kind):
        assert is_or_prefixed_kind(kind) == is_radio_kind(kind)

    def test_a_new_or_kind_has_to_be_added_to_the_set_as_well(self):
        """The one maintenance rule the split carries.

        Declare `or-something` in `ControlKind` and leave `RADIO_CONTROL_KINDS`
        alone, and the five prefix sites call it single-select while the render
        dispatch does not: the control gets a string state, builds radio
        buttons, takes clicks, and contributes nothing to the prompt. Adding the
        kind to the set is the whole fix, and this is the test that says so.
        """
        assert {k for k in DECLARED_CONTROL_KINDS if is_or_prefixed_kind(k)} == RADIO_CONTROL_KINDS

    def test_single_select_is_exactly_the_or_named_kinds(self):
        """The naming convention the schema already follows, stated once."""
        assert {"or", "or-adv", "or-adj", "or-prefix"} == RADIO_CONTROL_KINDS
        assert {k for k in DECLARED_SUBMENU_KINDS if is_or_prefixed_kind(k)} == {"or-adv", "or-adj"}


class TestTheStateShapeMatchesWhatTheRendererReads:
    """For every declared kind, the state the builder makes is the one the
    renderer expects — which is the property the two spellings agreeing buys."""

    @pytest.mark.parametrize("kind", DECLARED_CONTROL_KINDS)
    def test_the_builder_and_the_renderer_want_the_same_shape(self, kind):
        schema = Schema(sections=[Section(id="grove", text="grove", controls=[
            Control(id="bough", text="bough", kind=kind,
                    options=[Option(id="oak", text="oak"), Option(id="ash", text="ash")]),
        ])])
        state = create_initial_state(schema)
        selected = state.controls["bough"].selected_options

        # These two pick their own shape and never ask the radio question: a
        # toggle is a bool or a list depending on how many options it has
        # (`toggle_state.create_initial_toggle_state`) and a global selector is
        # `False` or a string (`state._create_control_state`). Both are covered
        # in test_state.py and test_prompt.py.
        if kind in ("toggle", "global-selector"):
            return
        assert isinstance(selected, str) == is_radio_kind(kind)

        # `hidden-opposite` renders only while its `hidden_opposite_bys` fires,
        # which this one-control schema has nothing to fire; it is rendered in
        # full in test_prompt.py.
        if kind == "hidden-opposite":
            return
        state.controls["bough"].selected_options = "oak" if is_radio_kind(kind) else ["oak"]
        assert "oak" in build_prompt(schema, state, "positive")


class TestTheSubmenuQuestionsAreNotOneQuestion:
    """Arity and word order look alike where they sit, and are not the same.

    Arity — radios or tick controls, a string state or a list — is
    `is_or_prefixed_kind`, the same spelling the control sites use. Word order is
    `is_adverb_submenu_kind`. They agree on two of the four submenu kinds and
    differ on the other two, so merging them would be wrong.
    """

    def test_they_disagree_on_half_the_declared_submenu_kinds(self):
        answers = {kind: (is_or_prefixed_kind(kind), is_adverb_submenu_kind(kind))
                   for kind in DECLARED_SUBMENU_KINDS}

        assert answers == {
            "or-adv": (True, True),
            "or-adj": (True, False),
            "and-adv": (False, True),
            "and-adj": (False, False),
        }

    def test_the_adverb_set_is_drawn_from_the_declared_submenu_kinds(self):
        assert set(DECLARED_SUBMENU_KINDS) >= ADVERB_SUBMENU_KINDS
