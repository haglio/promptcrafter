"""The state machine, asked directly.

Until these rules left `PromptCrafterWindow` the only way to reach them was to
build a Qt window and send it a fake click, so the two that mattered most --
the global selector's reach across the other controls -- were pinned by four
window tests and nothing else. Here they are ordinary function calls.
"""

import copy

from promptcrafter.runtime import build_prompt
from promptcrafter.state import create_initial_state
from promptcrafter.transitions import (
    choose_global_selector_option,
    choose_option,
    set_control_weight,
    set_global_selector_enabled,
    set_section_weight,
    set_toggle_enabled,
    toggle_option,
)
from promptcrafter.types import Control, ControlState, Option, Schema, Section
from tests.fixtures.test_schema import TEST_SCHEMA


def a_state():
    return create_initial_state(TEST_SCHEMA)


def _evergreen_schema():
    """A selector offering ``green`` beside controls that list ``evergreen``
    ahead of it: the letters of the choice, but not the word."""
    return Schema(sections=[Section(id="garden", text="garden", controls=[
        Control(id="shade", text="shade", kind="global-selector",
                options=[Option(id="green", text="green"), Option(id="black", text="black")]),
        Control(id="foliage", text="foliage", kind="or",
                options=[Option(id="evergreen", text="evergreen"),
                         Option(id="green", text="green")]),
        Control(id="mulch", text="mulch", kind="and-spaces-adj",
                options=[Option(id="evergreen bark", text="evergreen bark"),
                         Option(id="green moss", text="green moss")]),
    ])])


def _two_selector_schema():
    """Two global selectors and one ordinary radio, all offering the same ids.

    `hue`'s option id contains the selector's as a word rather than equalling
    it, which is what the containment half of the match reaches.
    """
    return Schema(sections=[Section(id="palette", text="palette", controls=[
        Control(id="tint", text="tint", kind="global-selector",
                options=[Option(id="amber", text="amber"), Option(id="slate", text="slate")]),
        Control(id="mood", text="mood", kind="global-selector",
                options=[Option(id="amber", text="amber"), Option(id="slate", text="slate")]),
        Control(id="hue", text="hue", kind="or",
                options=[Option(id="amber glazed", text="amber glazed"),
                         Option(id="slate washed", text="slate washed")]),
    ])])


class TestChoosingOneOfMany:
    def test_choosing_an_option_selects_it(self):
        state = a_state()

        choose_option(state, "alignment", "hero")

        assert state.controls["alignment"].selected_options == "hero"

    def test_choosing_what_is_already_chosen_empties_the_control(self):
        state = a_state()
        choose_option(state, "alignment", "hero")

        choose_option(state, "alignment", "hero")

        assert state.controls["alignment"].selected_options == ""

    def test_choosing_a_second_option_replaces_the_first(self):
        state = a_state()
        choose_option(state, "alignment", "hero")

        choose_option(state, "alignment", "villain")

        assert state.controls["alignment"].selected_options == "villain"

    def test_a_submenu_is_chosen_by_its_composite_key(self):
        """Submenu state is in the same dict, so it needs no rule of its own."""
        state = a_state()
        toggle_option(state, "appendages", "wings")

        choose_option(state, "appendages__wings__submenu", "feathered")

        assert build_prompt(TEST_SCHEMA, state, "positive") == (
            "space robo dino demon monster, feathered wings"
        )

    def test_a_control_the_state_does_not_know_is_left_alone(self):
        state = a_state()

        choose_option(state, "no such control", "hero")

        assert "no such control" not in state.controls


class TestTickingSeveral:
    def test_an_option_outside_the_list_goes_in(self):
        state = a_state()

        toggle_option(state, "appendages", "wings")

        assert state.controls["appendages"].selected_options == ["wings"]

    def test_an_option_inside_the_list_comes_out(self):
        state = a_state()
        toggle_option(state, "appendages", "wings")
        toggle_option(state, "appendages", "horns")

        toggle_option(state, "appendages", "wings")

        assert state.controls["appendages"].selected_options == ["horns"]

    def test_a_control_holding_one_selection_is_left_alone(self):
        """A radio's state is a string, and this rule only edits lists."""
        state = a_state()
        choose_option(state, "alignment", "hero")

        toggle_option(state, "alignment", "villain")

        assert state.controls["alignment"].selected_options == "hero"


class TestFlippingAToggle:
    def test_turning_a_toggle_on_selects_its_defaults(self):
        state = a_state()

        set_toggle_enabled(TEST_SCHEMA, state, "is portrait", True)

        assert state.controls["is portrait"].enabled is True
        assert state.controls["is portrait"].selected_options is True

    def test_turning_a_toggle_off_keeps_the_narrowed_selection(self):
        schema = copy.deepcopy(TEST_SCHEMA)
        schema.sections[1].controls.insert(0, Control(
            id="texture pack", text="texture pack", kind="toggle",
            options=[Option(id="oak", text="oak"), Option(id="pine", text="pine")],
        ))
        state = create_initial_state(schema)
        set_toggle_enabled(schema, state, "texture pack", True)
        toggle_option(state, "texture pack", "pine")

        set_toggle_enabled(schema, state, "texture pack", False)

        assert state.controls["texture pack"].enabled is False
        assert state.controls["texture pack"].selected_options == ["oak"]

    def test_a_state_key_the_schema_has_no_control_for_is_left_alone(self):
        """The guard that stops a stale key reaching the toggle rules.

        `get_toggle_selections_for_next_state` raises on a control that is not a
        toggle, and it would have nothing to raise about here -- there is no
        control at all.
        """
        state = a_state()
        state.controls["orphaned"] = ControlState(selected_options=False)

        set_toggle_enabled(TEST_SCHEMA, state, "orphaned", True)

        assert state.controls["orphaned"].selected_options is False
        assert state.controls["orphaned"].enabled is None


class TestTheGlobalSelector:
    def test_switching_it_on_leaves_it_with_nothing_chosen(self):
        """Off is False and on-with-nothing-chosen is "" -- not the same value."""
        state = a_state()
        assert state.controls["colorize"].selected_options is False

        set_global_selector_enabled(TEST_SCHEMA, state, "colorize", True)

        assert state.controls["colorize"].selected_options == ""

    def test_choosing_an_option_ticks_it_in_the_other_controls(self):
        state = a_state()
        set_global_selector_enabled(TEST_SCHEMA, state, "colorize", True)

        choose_global_selector_option(TEST_SCHEMA, state, "colorize", "green")

        assert state.controls["eye color"].selected_options == "green"

    def test_choosing_reaches_options_that_contain_the_id_as_a_word(self):
        """`render style` offers `green tinted`, which has `green` in it as a
        word, so it is ticked too -- the reach the schemas are written for. The
        window test of the same name pins the widget side; this one pins the
        rule.
        """
        state = a_state()
        set_global_selector_enabled(TEST_SCHEMA, state, "colorize", True)

        choose_global_selector_option(TEST_SCHEMA, state, "colorize", "green")

        assert "green tinted" in state.controls["render style"].selected_options

    def test_choosing_does_not_reach_an_id_that_merely_contains_the_letters(self):
        """The match was a substring test, so `green` reached `evergreen`; and
        where `evergreen` was listed first it was the one picked, and the exact
        `green` beside it was skipped (bug 20)."""
        schema = _evergreen_schema()
        state = create_initial_state(schema)
        set_global_selector_enabled(schema, state, "shade", True)

        choose_global_selector_option(schema, state, "shade", "green")

        assert state.controls["foliage"].selected_options == "green"
        assert state.controls["mulch"].selected_options == ["green moss"]

    def test_releasing_does_not_reach_an_id_that_merely_contains_the_letters(self):
        """The release side of the same rule (bug 58): what the selector never
        set, it does not take back."""
        schema = _evergreen_schema()
        state = create_initial_state(schema)
        choose_option(state, "foliage", "evergreen")
        state.controls["mulch"].selected_options = ["evergreen bark"]
        set_global_selector_enabled(schema, state, "shade", True)
        choose_global_selector_option(schema, state, "shade", "green")

        set_global_selector_enabled(schema, state, "shade", False)

        assert state.controls["foliage"].selected_options == ""
        assert state.controls["mulch"].selected_options == ["evergreen bark"]

    def test_choosing_a_second_option_releases_the_first(self):
        state = a_state()
        set_global_selector_enabled(TEST_SCHEMA, state, "colorize", True)
        choose_global_selector_option(TEST_SCHEMA, state, "colorize", "green")

        choose_global_selector_option(TEST_SCHEMA, state, "colorize", "black")

        assert state.controls["eye color"].selected_options == "black"
        assert state.controls["render style"].selected_options == ["black and white"]

    def test_switching_it_off_releases_everything_it_had_set(self):
        state = a_state()
        set_global_selector_enabled(TEST_SCHEMA, state, "colorize", True)
        choose_global_selector_option(TEST_SCHEMA, state, "colorize", "green")

        set_global_selector_enabled(TEST_SCHEMA, state, "colorize", False)

        assert state.controls["colorize"].selected_options is False
        assert state.controls["eye color"].selected_options == ""
        assert state.controls["render style"].selected_options == []

    def test_switching_it_off_before_anything_was_chosen_releases_nothing(self):
        state = a_state()
        choose_option(state, "eye color", "green")
        set_global_selector_enabled(TEST_SCHEMA, state, "colorize", True)

        set_global_selector_enabled(TEST_SCHEMA, state, "colorize", False)

        assert state.controls["eye color"].selected_options == "green"

    def test_the_selector_holds_the_option_it_was_given(self):
        state = a_state()
        set_global_selector_enabled(TEST_SCHEMA, state, "colorize", True)

        choose_global_selector_option(TEST_SCHEMA, state, "colorize", "green")

        assert state.controls["colorize"].selected_options == "green"

    def test_releasing_also_reaches_ids_that_contain_the_choice_as_a_word(self):
        """The release side of the word match.

        `hue` was never set to `amber`; it was set to `amber glazed`, which has
        it as a word -- and switching the selector off takes that back out.
        """
        schema = _two_selector_schema()
        state = create_initial_state(schema)
        set_global_selector_enabled(schema, state, "tint", True)
        choose_global_selector_option(schema, state, "tint", "amber")
        assert state.controls["hue"].selected_options == "amber glazed"

        set_global_selector_enabled(schema, state, "tint", False)

        assert state.controls["hue"].selected_options == ""

    def test_a_second_selector_is_released_like_any_other_control(self):
        """Both loops skip the control the choice came from, and only that one.

        The TypeScript this was ported from wrote the same guard in both --
        `schemaCtrl.id === controlId`, `src/App.tsx:204` and `:226`. The port
        turned the releasing one into a test on the *kind*, so a second selector
        was written to like any ordinary control and then never released: it
        kept a choice its own switch never made, and would push it onward. One
        selector is all any schema here has, so the two guards picked the same
        control and nothing showed.
        """
        schema = _two_selector_schema()
        state = create_initial_state(schema)
        set_global_selector_enabled(schema, state, "tint", True)
        set_global_selector_enabled(schema, state, "mood", True)

        choose_global_selector_option(schema, state, "tint", "amber")
        assert state.controls["mood"].selected_options == "amber"

        set_global_selector_enabled(schema, state, "tint", False)

        assert state.controls["mood"].selected_options == ""
        assert state.controls["hue"].selected_options == ""


class TestWeights:
    def test_a_section_takes_the_weight_it_is_given(self):
        state = a_state()

        set_section_weight(state, "details", 1.7)

        assert state.sections["details"].weight == 1.7

    def test_a_control_takes_the_weight_it_is_given(self):
        state = a_state()

        set_control_weight(state, "armor", 0.6)

        assert state.controls["armor"].weight == 0.6

    def test_a_control_the_state_does_not_know_is_left_alone(self):
        state = a_state()

        set_control_weight(state, "no such control", 0.6)

        assert "no such control" not in state.controls


class TestTheStateObjectsSurviveEveryRule:
    """The aliasing the window depends on.

    `_rebuild()` re-reads `self.state`, so a rule that replaced a dict entry
    instead of editing the object in it would leave the window drawing the
    state from before the click. Every rule edits in place; this is the test
    that says so.
    """

    def _ids(self, state):
        return (
            {k: id(v) for k, v in state.controls.items()},
            {k: id(v) for k, v in state.sections.items()},
        )

    def test_no_rule_replaces_a_control_or_section_state(self):
        schema = copy.deepcopy(TEST_SCHEMA)
        schema.sections.append(Section(
            id="spare", text="spare",
            controls=[Control(id="spare", text="spare", kind="and-commas",
                              options=[Option(id="green", text="green")])],
        ))
        state = create_initial_state(schema)
        before = self._ids(state)

        choose_option(state, "alignment", "hero")
        toggle_option(state, "appendages", "wings")
        set_toggle_enabled(schema, state, "is portrait", True)
        set_global_selector_enabled(schema, state, "colorize", True)
        choose_global_selector_option(schema, state, "colorize", "green")
        set_global_selector_enabled(schema, state, "colorize", False)
        set_section_weight(state, "details", 1.7)
        set_control_weight(state, "armor", 0.6)

        assert self._ids(state) == before


class TestTheSelectorsMergeIsStable:
    """The merged list comes out the same on every run.

    The TypeScript merged with `Array.from(new Set([...a, ...b]))`
    (`src/App.tsx:239`), and a JS Set keeps insertion order. The port used
    `list(set(a) | set(b))`, which is hash-ordered -- and Python salts string
    hashing per process, so the same clicks left the list in a different order
    from one run to the next. Nothing renders from that order, so it never
    reached a prompt; it is still a state that changes when nothing did.
    """

    def test_the_merged_selection_keeps_the_order_it_was_built_in(self):
        schema = _two_selector_schema()
        schema.sections[0].controls.append(
            Control(id="wash", text="wash", kind="and-commas",
                    initially_selected_options=["slate washed"],
                    options=[Option(id="amber glazed", text="amber glazed"),
                             Option(id="slate washed", text="slate washed")]))
        state = create_initial_state(schema)
        set_global_selector_enabled(schema, state, "tint", True)

        choose_global_selector_option(schema, state, "tint", "amber")

        assert state.controls["wash"].selected_options == ["slate washed", "amber glazed"]
