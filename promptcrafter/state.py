from promptcrafter.kinds import is_radio_kind
from promptcrafter.toggle_state import create_initial_toggle_state
from promptcrafter.types import (
    Control,
    ControlState,
    Schema,
    SectionState,
    State,
    submenu_state_key,
)


def _create_control_state(control: Control) -> ControlState:
    if control.kind == "toggle":
        return create_initial_toggle_state(control)

    if control.kind == "global-selector":
        initial = control.initially_selected_options
        if initial is True:
            return ControlState(selected_options="", weight=1)
        if isinstance(initial, str):
            return ControlState(selected_options=initial, weight=1)
        return ControlState(selected_options=False, weight=1)

    if control.kind == "required":
        if isinstance(control.initially_selected_options, list):
            return ControlState(selected_options=list(control.initially_selected_options), weight=1)
        return ControlState(selected_options=[opt.id for opt in control.options], weight=1)

    if control.kind == "hidden-opposite":
        if isinstance(control.initially_selected_options, list):
            return ControlState(selected_options=list(control.initially_selected_options), weight=1)
        return ControlState(selected_options=[], weight=1)

    is_radio = is_radio_kind(control.kind)
    if is_radio:
        return ControlState(
            selected_options=control.initially_selected_options if isinstance(control.initially_selected_options, str) else "",
            weight=1,
        )
    return ControlState(
        selected_options=list(control.initially_selected_options) if isinstance(control.initially_selected_options, list) else [],
        weight=1,
    )


def _walk_controls(controls: list[Control], bucket: dict[str, ControlState]) -> None:
    for control in controls:
        bucket[control.id] = _create_control_state(control)
        for option in control.options:
            if option.submenu:
                is_radio = is_radio_kind(option.submenu.kind)
                key = submenu_state_key(control.id, option.id)
                bucket[key] = ControlState(
                    selected_options="" if is_radio else [],
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
