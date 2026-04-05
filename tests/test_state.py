from promptcrafter.state import create_initial_state
from promptcrafter.types import Control, ControlState, Option, Schema, Section


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


class TestCreateInitialState:
    def test_uses_toggle_helper_semantics_for_multi_option_defaults(self):
        state = create_initial_state(Schema(sections=[
            Section(
                id="mods",
                text="mods",
                controls=[_build_toggle(initially_selected_options=["oak"])],
            ),
        ]))

        assert state.controls["texture pack"] == ControlState(
            selected_options=["oak"],
            enabled=False,
            weight=1,
        )
