"""What a click does to the state, with no window around it.

Every rule here used to be a method on ``PromptCrafterWindow``, which meant the
app's whole state machine could only be exercised by building a Qt window and
sending it fake clicks -- and the two hardest rules in it, the global selector's
reach across the other controls, were the two least reachable that way.  They
are ordinary functions now: they take the schema and the state, and the window's
handlers are the wiring that reads two ids off a widget and rebuilds afterwards.

Every one of them mutates the ``ControlState`` (or ``SectionState``) that is
already in the dict rather than putting a new one there.  The window keeps no
copy of the state and re-reads it on each rebuild, so that aliasing is what
makes a click show up on screen; replacing a dict entry instead would leave the
UI showing the state from before the click.
"""

from __future__ import annotations

from promptcrafter.runtime import find_control
from promptcrafter.toggle_state import get_toggle_selections_for_next_state
from promptcrafter.types import Schema, State


def choose_option(state: State, control_key: str, option_id: str) -> None:
    """Pick ``option_id`` in a control that holds one selection.

    Choosing what is already chosen clears the control instead, which is the
    only way to put a radio group back to nothing -- Qt radios have no such
    gesture of their own.
    """
    cs = state.controls.get(control_key)
    if not cs:
        return
    if cs.selected_options == option_id:
        cs.selected_options = ""
    else:
        cs.selected_options = option_id


def toggle_option(state: State, control_key: str, option_id: str) -> None:
    """Add ``option_id`` to a control that holds a list, or take it back out."""
    cs = state.controls.get(control_key)
    if not cs or not isinstance(cs.selected_options, list):
        return
    if option_id in cs.selected_options:
        cs.selected_options = [o for o in cs.selected_options if o != option_id]
    else:
        cs.selected_options = [*cs.selected_options, option_id]


def set_toggle_enabled(schema: Schema, state: State, control_id: str, enabled: bool) -> None:
    """Switch a toggle control on or off.

    What its options become on the way is ``toggle_state``'s rule, not this
    one's: turning a multi-option toggle off keeps the narrowed selection so
    that turning it back on restores it.
    """
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
    """Switch the global selector on (no option chosen yet) or off.

    Off is ``False`` rather than ``""`` -- the two are what the renderer and the
    widget builder read to tell "off" from "on with nothing picked".  Switching
    it off also releases whatever it had reached out and selected elsewhere.
    """
    cs = state.controls.get(control_id)
    if not cs:
        return
    previous = cs.selected_options if isinstance(cs.selected_options, str) else ""
    cs.selected_options = "" if enabled else False
    if not enabled and previous:
        _clear_matches(schema, state, previous)


def choose_global_selector_option(
    schema: Schema, state: State, control_id: str, option_id: str
) -> None:
    """Pick an option in the global selector and push it across the window.

    The previous choice is released from the other controls before the new one
    is applied, so the two cannot both be showing at once.
    """
    cs = state.controls.get(control_id)
    if not cs:
        return
    previous = cs.selected_options if isinstance(cs.selected_options, str) else ""
    if previous and previous != option_id:
        _clear_matches(schema, state, previous)
    cs.selected_options = option_id
    if option_id:
        _apply_matches(schema, state, control_id, option_id)


def _clear_matches(schema: Schema, state: State, option_id: str) -> None:
    """Release ``option_id`` from every control the selector could have set.

    Held as found (2026-08-25, bug 20): the match is a substring test, so
    releasing ``green`` also releases ``green tinted``.  Note also that this
    skips every control of kind ``global-selector`` while :func:`_apply_matches`
    skips only the one control the choice came from -- an asymmetry recorded
    rather than fixed, since one selector is all any schema here has.
    """
    for section in schema.sections:
        for control in section.controls:
            if control.kind == "global-selector":
                continue
            cs = state.controls.get(control.id)
            if not cs:
                continue
            if isinstance(cs.selected_options, str):
                if cs.selected_options == option_id or option_id in cs.selected_options:
                    cs.selected_options = ""
            elif isinstance(cs.selected_options, list):
                filtered = [s for s in cs.selected_options if s != option_id and option_id not in s]
                if len(filtered) != len(cs.selected_options):
                    cs.selected_options = filtered


def _apply_matches(schema: Schema, state: State, source_control_id: str, option_id: str) -> None:
    """Tick ``option_id`` in every other control that offers it.

    Held as found (2026-08-25, bug 20): ``option_id in o.id`` is a substring
    test, so choosing ``green`` also ticks ``green tinted``.
    """
    for section in schema.sections:
        for control in section.controls:
            if control.id == source_control_id:
                continue
            cs = state.controls.get(control.id)
            if not cs:
                continue
            if isinstance(cs.selected_options, str):
                match = next(
                    (o for o in control.options if o.id == option_id or option_id in o.id),
                    None,
                )
                if match:
                    cs.selected_options = match.id
            elif isinstance(cs.selected_options, list):
                matching = [o.id for o in control.options if o.id == option_id or option_id in o.id]
                if matching:
                    cs.selected_options = list(set(cs.selected_options) | set(matching))


def set_section_weight(state: State, section_id: str, weight: float) -> None:
    state.sections[section_id].weight = weight


def set_control_weight(state: State, control_id: str, weight: float) -> None:
    cs = state.controls.get(control_id)
    if cs:
        cs.weight = weight
