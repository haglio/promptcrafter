from promptcrafter.types import Control, ControlState


def create_initial_toggle_state(control: Control) -> ControlState:
    if control.kind != "toggle":
        raise ValueError("create_initial_toggle_state can only be used with toggle controls.")

    initial = control.initially_selected_options

    if isinstance(initial, list):
        return ControlState(
            selected_options=list(initial),
            enabled=False,
            weight=1,
        )

    if initial is True:
        return ControlState(
            selected_options=_get_toggle_default_selections(control),
            enabled=True,
            weight=1,
        )

    if len(control.options) > 1:
        return ControlState(selected_options=[], enabled=False, weight=1)
    return ControlState(selected_options=False, enabled=False, weight=1)


def is_toggle_enabled(control_state: ControlState) -> bool:
    if isinstance(control_state.selected_options, bool):
        return control_state.selected_options
    return control_state.enabled or False


def get_toggle_selections_for_next_state(
    control: Control,
    control_state: ControlState,
    enabled: bool,
) -> bool | list[str]:
    if control.kind != "toggle":
        raise ValueError("get_toggle_selections_for_next_state can only be used with toggle controls.")

    if isinstance(control_state.selected_options, bool):
        return enabled

    if not isinstance(control_state.selected_options, list):
        raise ValueError("Toggle controls must use boolean or list selectedOptions.")

    if not enabled:
        return control_state.selected_options

    return (
        control_state.selected_options
        if control_state.selected_options
        else _get_toggle_default_selections(control)
    )


def _get_toggle_default_selections(control: Control) -> bool | list[str]:
    if isinstance(control.initially_selected_options, list):
        return list(control.initially_selected_options)
    if len(control.options) > 1:
        return [opt.id for opt in control.options]
    return True
