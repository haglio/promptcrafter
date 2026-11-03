from __future__ import annotations

from promptcrafter.kinds import is_or_prefixed_kind
from promptcrafter.switch_state import create_initial_switch_state
from promptcrafter.types import (
    Control,
    ControlState,
    ManyOf,
    OneOf,
    Schema,
    SectionState,
    Selection,
    State,
    Switch,
    submenu_state_key,
)


def _every_option_of(control: Control) -> ManyOf:
    return ManyOf(tuple(opt.id for opt in control.options))


def _declared_list(control: Control) -> ManyOf | None:
    initial = control.initially_selected_options
    return ManyOf(tuple(initial)) if isinstance(initial, list) else None


def _initial_selection(control: Control) -> Selection:
    initial = control.initially_selected_options
    if control.kind == "global-selector" and initial is not True and not isinstance(initial, str):
        return Switch(False)
    if control.kind == "global-selector" or is_or_prefixed_kind(control.kind):
        return OneOf(initial) if isinstance(initial, str) else OneOf()
    if control.kind == "required":
        return _declared_list(control) or _every_option_of(control)
    return _declared_list(control) or ManyOf()


def _create_control_state(control: Control) -> ControlState:
    if control.kind == "switch":
        return create_initial_switch_state(control)
    return ControlState(selected_options=_initial_selection(control), weight=1)


def _walk_controls(controls: list[Control], bucket: dict[str, ControlState]) -> None:
    for control in controls:
        bucket[control.id] = _create_control_state(control)
        for option in control.options:
            if option.submenu:
                is_radio = is_or_prefixed_kind(option.submenu.kind)
                key = submenu_state_key(control.id, option.id)
                bucket[key] = ControlState(
                    selected_options=OneOf() if is_radio else ManyOf(),
                    weight=1,
                )


def create_initial_state(schema: Schema) -> State:
    controls: dict[str, ControlState] = {}
    for section in schema.sections:
        _walk_controls(section.controls, controls)
    return State(
        controls=controls,
        sections={s.id: SectionState(weight=1) for s in schema.sections},
    )
