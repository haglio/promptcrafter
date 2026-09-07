from promptcrafter.types import Control, ControlState, ManyOf, Selection, Switch


def toggle_holds_an_option_list(control_state: ControlState) -> bool:
    """A toggle whose control offers more than one option narrows to a list;
    one that does not is a plain on/off.

    The two shapes part company three times -- what a flip writes, what
    ``is_toggle_enabled`` reads, and which renderer the kind reaches -- and this
    is the one place that asks which it has.
    """
    return not isinstance(control_state.selected_options, Switch)


def create_initial_toggle_state(control: Control) -> ControlState:
    if control.kind != "toggle":
        raise ValueError("create_initial_toggle_state can only be used with toggle controls.")

    initial = control.initially_selected_options

    if isinstance(initial, list):
        return ControlState(
            selected_options=ManyOf(tuple(initial)),
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
        return ControlState(selected_options=ManyOf(), enabled=False, weight=1)
    return ControlState(selected_options=Switch(False), enabled=False, weight=1)


def is_toggle_enabled(control_state: ControlState) -> bool:
    if not toggle_holds_an_option_list(control_state):
        return control_state.selected_options.is_switched_on()
    return control_state.enabled or False


def get_toggle_selections_for_next_state(
    control: Control,
    control_state: ControlState,
    enabled: bool,
) -> Selection:
    if control.kind != "toggle":
        raise ValueError("get_toggle_selections_for_next_state can only be used with toggle controls.")

    if not toggle_holds_an_option_list(control_state):
        return Switch(enabled)

    if not enabled:
        return control_state.selected_options

    if control_state.selected_options.has_selection():
        return control_state.selected_options
    return _get_toggle_default_selections(control)


def _get_toggle_default_selections(control: Control) -> Selection:
    if isinstance(control.initially_selected_options, list):
        return ManyOf(tuple(control.initially_selected_options))
    if len(control.options) > 1:
        return ManyOf(tuple(opt.id for opt in control.options))
    return Switch(True)
