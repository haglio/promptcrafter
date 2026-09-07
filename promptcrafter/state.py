from promptcrafter.kinds import is_or_prefixed_kind
from promptcrafter.toggle_state import create_initial_toggle_state
from promptcrafter.types import (
    Control,
    ControlState,
    ManyOf,
    OneOf,
    Schema,
    SectionState,
    State,
    Switch,
    submenu_state_key,
)


def _every_option_of(control: Control) -> ManyOf:
    return ManyOf(tuple(opt.id for opt in control.options))


def _declared_list(control: Control) -> ManyOf | None:
    initial = control.initially_selected_options
    return ManyOf(tuple(initial)) if isinstance(initial, list) else None


def _create_control_state(control: Control) -> ControlState:
    if control.kind == "toggle":
        return create_initial_toggle_state(control)

    if control.kind == "global-selector":
        initial = control.initially_selected_options
        if initial is True:
            return ControlState(selected_options=OneOf(), weight=1)
        if isinstance(initial, str):
            return ControlState(selected_options=OneOf(initial), weight=1)
        return ControlState(selected_options=Switch(False), weight=1)

    if control.kind == "required":
        return ControlState(
            selected_options=_declared_list(control) or _every_option_of(control),
            weight=1,
        )

    if control.kind == "hidden-opposite":
        return ControlState(selected_options=_declared_list(control) or ManyOf(), weight=1)

    if is_or_prefixed_kind(control.kind):
        initial = control.initially_selected_options
        return ControlState(
            selected_options=OneOf(initial) if isinstance(initial, str) else OneOf(),
            weight=1,
        )
    return ControlState(selected_options=_declared_list(control) or ManyOf(), weight=1)


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
