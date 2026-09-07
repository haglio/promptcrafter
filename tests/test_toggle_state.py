from __future__ import annotations

from promptcrafter.toggle_state import (
    create_initial_toggle_state,
    get_toggle_selections_for_next_state,
    is_toggle_enabled,
)
from promptcrafter.types import Control, ControlState, ManyOf, Option, Switch


def _build_toggle(**overrides):
    defaults = dict(
        id="texture pack",
        text="texture pack",
        kind="toggle",
        options=[
            Option(id="oak", text="oak"),
            Option(id="pine", text="pine"),
        ],
    )
    defaults.update(overrides)
    return Control(**defaults)


class TestCreateInitialToggleState:
    def test_keeps_multi_option_defaults_separate_from_enabled_flag(self):
        control = _build_toggle(initially_selected_options=["oak"])

        assert create_initial_toggle_state(control) == ControlState(
            selected_options=ManyOf(("oak",)),
            enabled=False,
            weight=1,
        )

    def test_enables_toggle_initialized_with_true_using_all_options(self):
        control = _build_toggle(initially_selected_options=True)

        assert create_initial_toggle_state(control) == ControlState(
            selected_options=ManyOf(("oak", "pine")),
            enabled=True,
            weight=1,
        )


class TestGetToggleSelectionsForNextState:
    def test_preserves_multi_option_selection_when_turned_off_and_back_on(self):
        control = _build_toggle()
        selected_options = ManyOf(("oak",))

        off_selection = get_toggle_selections_for_next_state(
            control, ControlState(selected_options=selected_options), False
        )
        on_selection = get_toggle_selections_for_next_state(
            control, ControlState(selected_options=off_selection), True
        )

        assert off_selection == ManyOf(("oak",))
        assert on_selection == ManyOf(("oak",))


class TestIsToggleEnabled:
    def test_a_toggle_with_no_option_list_says_for_itself_whether_it_is_on(self):
        assert is_toggle_enabled(ControlState(selected_options=Switch(True))) is True
        assert is_toggle_enabled(ControlState(selected_options=Switch(False), enabled=True)) is False
