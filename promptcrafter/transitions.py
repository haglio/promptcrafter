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

import re

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
        _clear_matches(schema, state, control_id, previous)


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
        _clear_matches(schema, state, control_id, previous)
    cs.selected_options = option_id
    if option_id:
        _apply_matches(schema, state, control_id, option_id)


def _names(option_id: str, candidate: str) -> bool:
    """Whether ``candidate`` is ``option_id``, or has it in it as a word.

    A global selector's choice reaches every other control offering the same
    id, and the ids that carry it as a word -- ``green`` reaches ``green
    tinted``, which is the reach the schemas are written for.  It was a
    substring test, so ``green`` also reached ``evergreen``, and released it
    (bugs 20 and 58).
    """
    if candidate == option_id:
        return True
    return re.search(rf"(?<!\w){re.escape(option_id)}(?!\w)", candidate) is not None


def _clear_matches(
    schema: Schema, state: State, source_control_id: str, option_id: str
) -> None:
    """Release ``option_id`` from every control the selector could have set.

    Skips the control the choice came from and nothing else, which is what
    :func:`_apply_matches` does and what the TypeScript this was ported from did
    in both loops (``src/App.tsx:204`` and ``:226``, ``schemaCtrl.id ===
    controlId``).  The port turned this one into a test on the *kind*, so a
    second selector was written to like any other control and then never
    released; with one selector in the schema the two guards pick the same
    control and nothing showed.

    Releases what :func:`_names` reaches: ``green`` and ``green tinted``, never
    ``evergreen``.
    """
    for section in schema.sections:
        for control in section.controls:
            if control.id == source_control_id:
                continue
            cs = state.controls.get(control.id)
            if not cs:
                continue
            if isinstance(cs.selected_options, str):
                if _names(option_id, cs.selected_options):
                    cs.selected_options = ""
            elif isinstance(cs.selected_options, list):
                filtered = [s for s in cs.selected_options if not _names(option_id, s)]
                if len(filtered) != len(cs.selected_options):
                    cs.selected_options = filtered


def _apply_matches(schema: Schema, state: State, source_control_id: str, option_id: str) -> None:
    """Tick ``option_id`` in every other control that offers it.

    Offers it by :func:`_names`; a control that holds one choice takes the
    exact id where it lists one, whatever is listed ahead of it.
    """
    for section in schema.sections:
        for control in section.controls:
            if control.id == source_control_id:
                continue
            cs = state.controls.get(control.id)
            if not cs:
                continue
            if isinstance(cs.selected_options, str):
                match = next((o for o in control.options if o.id == option_id), None) or next(
                    (o for o in control.options if _names(option_id, o.id)), None,
                )
                if match:
                    cs.selected_options = match.id
            elif isinstance(cs.selected_options, list):
                matching = [o.id for o in control.options if _names(option_id, o.id)]
                if matching:
                    # `dict.fromkeys`, not `set`: the TypeScript merged these
                    # with `Array.from(new Set([...]))` (`src/App.tsx:239`) and a
                    # JS Set keeps insertion order, so the list was stable. A
                    # Python set is hash-ordered, and string hashing is salted
                    # per process -- the port made this list come out in a
                    # different order run to run. Nothing reads it in order
                    # today, because the renderer and the widget builder both
                    # walk `control.options`, so it never showed in a prompt.
                    cs.selected_options = list(
                        dict.fromkeys([*cs.selected_options, *matching])
                    )


def set_section_weight(state: State, section_id: str, weight: float) -> None:
    state.sections[section_id].weight = weight


def set_control_weight(state: State, control_id: str, weight: float) -> None:
    cs = state.controls.get(control_id)
    if cs:
        cs.weight = weight
