from __future__ import annotations

import re
from collections.abc import Iterator

from promptcrafter.runtime import find_control
from promptcrafter.toggle_state import get_toggle_selections_for_next_state
from promptcrafter.types import Control, ControlState, ManyOf, OneOf, Schema, State, Switch


def choose_option(state: State, control_key: str, option_id: str) -> None:
    cs = state.controls.get(control_key)
    if not cs:
        return
    cs.selected_options = cs.selected_options.with_toggled(option_id)


def toggle_option(state: State, control_key: str, option_id: str) -> None:
    cs = state.controls.get(control_key)
    if not cs or not isinstance(cs.selected_options, ManyOf):
        return
    cs.selected_options = cs.selected_options.with_toggled(option_id)


def set_toggle_enabled(schema: Schema, state: State, control_id: str, enabled: bool) -> None:
    cs = state.controls.get(control_id)
    if not cs:
        return
    control = find_control(schema, control_id)
    if not control:
        return
    cs.selected_options = get_toggle_selections_for_next_state(control, cs, enabled)
    cs.enabled = enabled


def set_global_selector_enabled(
    schema: Schema, state: State, control_id: str, enabled: bool
) -> None:
    cs = state.controls.get(control_id)
    if not cs:
        return
    previous = cs.selected_options.single_choice()
    cs.selected_options = OneOf() if enabled else Switch(False)
    if not enabled and previous:
        _clear_matches(schema, state, control_id, previous)


def choose_global_selector_option(
    schema: Schema, state: State, control_id: str, option_id: str
) -> None:
    cs = state.controls.get(control_id)
    if not cs:
        return
    previous = cs.selected_options.single_choice()
    if previous and previous != option_id:
        _clear_matches(schema, state, control_id, previous)
    cs.selected_options = OneOf(option_id)
    if option_id:
        _apply_matches(schema, state, control_id, option_id)


def _names(option_id: str, candidate: str) -> bool:
    if candidate == option_id:
        return True
    return re.search(rf"(?<!\w){re.escape(option_id)}(?!\w)", candidate) is not None


def _every_other_control(
    schema: Schema, state: State, source_control_id: str
) -> Iterator[tuple[Control, ControlState]]:
    for section in schema.sections:
        for control in section.controls:
            if control.id == source_control_id:
                continue
            cs = state.controls.get(control.id)
            if cs:
                yield control, cs


def _clear_matches(
    schema: Schema, state: State, source_control_id: str, option_id: str
) -> None:
    for _control, cs in _every_other_control(schema, state, source_control_id):
        cs.selected_options = cs.selected_options.without(
            lambda candidate: _names(option_id, candidate)
        )


def _apply_matches(schema: Schema, state: State, source_control_id: str, option_id: str) -> None:
    for control, cs in _every_other_control(schema, state, source_control_id):
        offered = [o.id for o in control.options if _names(option_id, o.id)]
        cs.selected_options = cs.selected_options.with_reach_of(option_id, offered)


def set_section_weight(state: State, section_id: str, weight: float) -> None:
    state.sections[section_id].weight = weight


def set_control_weight(state: State, control_id: str, weight: float) -> None:
    cs = state.controls.get(control_id)
    if cs:
        cs.weight = weight
