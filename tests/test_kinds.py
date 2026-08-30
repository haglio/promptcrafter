"""One question, one answer, at all six places that ask it.

Whether a kind is single-select decides four things: the state shape, the widget
class, whether the control counts as having a selection, and which renderer
builds its text. They used to be worked out separately -- five sites spelled the
test `kind.startswith("or")` and the sixth enumerated the four `or` kinds inside
the render function, both carried over from the TypeScript. They agreed on every
kind that has ever existed, so the split was invisible; what it could produce is
a control whose state is a string while its renderer wants a list, which renders
nothing at all.

These tests are about that shape being unreachable, not about which spelling
won. They run against kinds that do not exist as well as the ones that do,
because nothing validates a kind at any layer: `Literal` is erased at runtime,
the dataclasses have no `__post_init__`, and there is no type checker in the
gate.
"""

from typing import get_args

import pytest

from promptcrafter.kinds import ADVERB_SUBMENU_KINDS, is_adverb_submenu_kind, is_radio_kind
from promptcrafter.runtime import build_prompt, control_has_at_least_one_selected_option
from promptcrafter.state import create_initial_state
from promptcrafter.types import Control, ControlKind, Option, Schema, Section, SubmenuKind

DECLARED_CONTROL_KINDS = get_args(ControlKind)
DECLARED_SUBMENU_KINDS = get_args(SubmenuKind)

# Kinds no schema declares. The first group would once have been classed
# single-select by five sites and multi-select by the sixth.
UNDECLARED = ["or-suffix", "or-pair", "orange", "order", "origin", "or2",
              "pick-one", "single", "totally-new"]


def _one_control_of(kind):
    return Schema(sections=[Section(id="grove", text="grove", controls=[
        Control(id="bough", text="bough", kind=kind,
                options=[Option(id="oak", text="oak"), Option(id="ash", text="ash")]),
    ])])


class TestTheDeclaredKinds:
    def test_the_twelve_are_the_ones_the_owner_kept(self):
        """Membership is a decision, not a convenience (Q15).

        Adding or removing a kind has to move this line, which is the point:
        `ControlKind` is the schema format the README points users at.
        """
        assert set(DECLARED_CONTROL_KINDS) == {
            "or", "or-adv", "or-adj", "or-prefix",
            "and-commas", "and-commas-adj", "and-commas-adv",
            "and-spaces-adj", "required", "hidden-opposite",
            "toggle", "global-selector",
        }

    def test_single_select_is_exactly_the_or_named_kinds(self):
        """The naming convention the schema already follows, stated once."""
        assert {k for k in DECLARED_CONTROL_KINDS if is_radio_kind(k)} == {
            "or", "or-adv", "or-adj", "or-prefix"}
        assert {k for k in DECLARED_SUBMENU_KINDS if is_radio_kind(k)} == {"or-adv", "or-adj"}


class TestTheStateShapeAndTheRendererCannotDisagree:
    """The failure this file exists to make unreachable.

    A control whose state builder says "string" and whose renderer says "list"
    builds working widgets, accepts clicks, and contributes nothing to the
    prompt, with no error anywhere. It takes one kind classed two ways.
    """

    @pytest.mark.parametrize("kind", [*DECLARED_CONTROL_KINDS, *UNDECLARED])
    def test_the_state_shape_matches_what_the_renderer_reads(self, kind):
        schema = _one_control_of(kind)
        state = create_initial_state(schema)
        selected = state.controls["bough"].selected_options

        assert isinstance(selected, str) == is_radio_kind(kind)

        # `toggle` and `global-selector` do not render from an option list at
        # all, and `hidden-opposite` renders only while its `hidden_opposite_bys`
        # fires, which this one-control schema has nothing to fire. All three are
        # rendered in full in test_prompt.py; the shape assertion above still
        # covers them here.
        if kind in ("toggle", "global-selector", "hidden-opposite"):
            return
        state.controls["bough"].selected_options = "oak" if is_radio_kind(kind) else ["oak"]
        assert "oak" in build_prompt(schema, state, "positive")

    @pytest.mark.parametrize("kind", [*DECLARED_CONTROL_KINDS, *UNDECLARED])
    def test_has_a_selection_agrees_with_the_state_shape(self, kind):
        schema = _one_control_of(kind)
        state = create_initial_state(schema)
        control = schema.sections[0].controls[0]
        if kind in ("toggle", "global-selector", "required"):
            return  # these three answer from their own rule, not from the shape
        state.controls["bough"].selected_options = "oak" if is_radio_kind(kind) else ["oak"]

        assert control_has_at_least_one_selected_option(control, state) is True


class TestTheSubmenuQuestionsAreNotOneQuestion:
    """Arity and word order look alike where they sit, and are not the same.

    Arity — radios or checkboxes, a string state or a list — is `is_radio_kind`,
    the same question the control kinds ask. Word order is
    `is_adverb_submenu_kind`. They agree on two of the four submenu kinds and
    differ on the other two, so merging them would be wrong.
    """

    def test_they_disagree_on_half_the_declared_submenu_kinds(self):
        answers = {kind: (is_radio_kind(kind), is_adverb_submenu_kind(kind))
                   for kind in DECLARED_SUBMENU_KINDS}

        assert answers == {
            "or-adv": (True, True),
            "or-adj": (True, False),
            "and-adv": (False, True),
            "and-adj": (False, False),
        }

    def test_the_adverb_set_is_drawn_from_the_declared_submenu_kinds(self):
        assert ADVERB_SUBMENU_KINDS <= set(DECLARED_SUBMENU_KINDS)
