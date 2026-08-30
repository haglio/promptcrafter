import pytest

from promptcrafter.state import create_initial_state, submenu_state_key
from promptcrafter.types import Control, ControlState, Option, Schema, Section, Submenu


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


def _submenu_of_kind(kind):
    return Schema(sections=[Section(id="grove", text="grove", controls=[
        Control(id="bough", text="bough", kind="and-commas", options=[
            Option(id="knot", text="knot", submenu=Submenu(kind=kind, options=[
                Option(id="burl", text="burl"),
                Option(id="whorl", text="whorl"),
            ])),
        ]),
    ])])


class TestSubmenuStateShape:
    """Which submenus start with a string and which with a list.

    The question is asked with the *open* rival -- does the kind begin with
    `or` -- and not with a closed `{"or-adv", "or-adj"}` set. The two agree on
    all four declared submenu kinds, so a swap between them looks free and is
    not: nothing validates a submenu kind anywhere, and every other `or*`
    string flips shape. These pin the answer for both.
    """

    @pytest.mark.parametrize("kind", ["or-adv", "or-adj"])
    def test_a_single_select_submenu_starts_with_a_string(self, kind):
        state = create_initial_state(_submenu_of_kind(kind))

        assert state.controls[submenu_state_key("bough", "knot")].selected_options == ""

    @pytest.mark.parametrize("kind", ["and-adv", "and-adj"])
    def test_a_multi_select_submenu_starts_with_a_list(self, kind):
        state = create_initial_state(_submenu_of_kind(kind))

        assert state.controls[submenu_state_key("bough", "knot")].selected_options == []

    @pytest.mark.parametrize("kind", ["or", "or-prefix", "or-suffix"])
    def test_any_or_prefixed_kind_starts_with_a_string(self, kind):
        """Kinds outside the declared four, which nothing stops a schema using.

        `SubmenuKind` is a `Literal` erased at runtime, `Submenu` has no
        `__post_init__`, and there is no type checker in the gate -- so these
        reach the same code as the declared four and get the open rival's
        answer.
        """
        state = create_initial_state(_submenu_of_kind(kind))

        assert state.controls[submenu_state_key("bough", "knot")].selected_options == ""
