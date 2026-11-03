from __future__ import annotations

from promptcrafter.types import Control, ControlState, ManyOf, Selection, Switch


def switch_holds_an_option_list(control_state: ControlState) -> bool:
    return not isinstance(control_state.selected_options, Switch)


def create_initial_switch_state(control: Control) -> ControlState:
    if control.kind != "switch":
        raise ValueError("create_initial_switch_state can only be used with switch controls.")

    initial = control.initially_selected_options

    if isinstance(initial, list):
        return ControlState(
            selected_options=ManyOf(tuple(initial)),
            enabled=False,
            weight=1,
        )

    if initial is True:
        return ControlState(
            selected_options=_get_switch_default_selections(control),
            enabled=True,
            weight=1,
        )

    if len(control.options) > 1:
        return ControlState(selected_options=ManyOf(), enabled=False, weight=1)
    return ControlState(selected_options=Switch(False), enabled=False, weight=1)


def is_switch_on(control_state: ControlState) -> bool:
    if not switch_holds_an_option_list(control_state):
        return control_state.selected_options.is_switched_on()
    return control_state.enabled or False


def get_switch_selections_for_next_state(
    control: Control,
    control_state: ControlState,
    enabled: bool,
) -> Selection:
    if control.kind != "switch":
        raise ValueError("get_switch_selections_for_next_state can only be used with switch controls.")

    if not switch_holds_an_option_list(control_state):
        return Switch(enabled)

    if not enabled:
        return control_state.selected_options

    if control_state.selected_options.has_selection():
        return control_state.selected_options
    return _get_switch_default_selections(control)


def _get_switch_default_selections(control: Control) -> Selection:
    if isinstance(control.initially_selected_options, list):
        return ManyOf(tuple(control.initially_selected_options))
    if len(control.options) > 1:
        return ManyOf(tuple(opt.id for opt in control.options))
    return Switch(True)
