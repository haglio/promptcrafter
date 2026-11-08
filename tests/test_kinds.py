from __future__ import annotations

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
from promptcrafter.types import (
    Control,
    ControlKind,
    ManyOf,
    OneOf,
    Option,
    Schema,
    Section,
    SubmenuKind,
)
from tests.kind_shapes import KINDS_WHOSE_CONTROL_PICKS_ITS_SHAPE

DECLARED_CONTROL_KINDS = get_args(ControlKind)
DECLARED_SUBMENU_KINDS = get_args(SubmenuKind)

_KINDS_TEST_PROMPT_RENDERS_WITH_THEIR_TRIGGER_FIRED = ("hidden-opposite",)


class TestTheDeclaredKinds:
    def test_the_twelve_are_the_ones_the_owner_kept(self):
        assert set(DECLARED_CONTROL_KINDS) == {
            "or", "or-adv", "or-adj", "or-prefix",
            "and-commas", "and-commas-adj", "and-commas-adv",
            "and-spaces-adj", "required", "hidden-opposite",
            "switch", "global-selector",
        }

    @pytest.mark.parametrize("kind", [*DECLARED_CONTROL_KINDS, *DECLARED_SUBMENU_KINDS])
    def test_the_two_spellings_the_owner_chose_to_keep_answer_alike_for_every_kind_that_exists(self, kind):
        assert is_or_prefixed_kind(kind) == is_radio_kind(kind)

    def test_a_new_or_kind_left_out_of_the_set_would_take_clicks_and_render_nothing_so_it_goes_in_as_well(self):
        assert {k for k in DECLARED_CONTROL_KINDS if is_or_prefixed_kind(k)} == RADIO_CONTROL_KINDS

    def test_single_select_is_exactly_the_or_named_kinds(self):
        assert {"or", "or-adv", "or-adj", "or-prefix"} == RADIO_CONTROL_KINDS
        assert {k for k in DECLARED_SUBMENU_KINDS if is_or_prefixed_kind(k)} == {"or-adv", "or-adj"}


class TestTheStateShapeMatchesWhatTheRendererReads:

    @pytest.mark.parametrize("kind", DECLARED_CONTROL_KINDS)
    def test_the_builder_and_the_renderer_want_the_same_shape(self, kind):
        schema = Schema(sections=[Section(id="grove", text="grove", controls=[
            Control(id="bough", text="bough", kind=kind,
                    options=[Option(id="oak", text="oak"), Option(id="ash", text="ash")]),
        ])])
        state = create_initial_state(schema)
        selected = state.controls["bough"].selected_options

        if kind in KINDS_WHOSE_CONTROL_PICKS_ITS_SHAPE:
            return
        assert isinstance(selected, OneOf) == is_radio_kind(kind)

        if kind in _KINDS_TEST_PROMPT_RENDERS_WITH_THEIR_TRIGGER_FIRED:
            return
        state.controls["bough"].selected_options = (
            OneOf("oak") if is_radio_kind(kind) else ManyOf(("oak",))
        )
        assert "oak" in build_prompt(schema, state, "positive")


class TestTheSubmenuQuestionsAreNotOneQuestion:

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
