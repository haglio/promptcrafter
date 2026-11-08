from __future__ import annotations

import ast
from pathlib import Path

import pytest

from promptcrafter.state import create_initial_state, submenu_state_key
from promptcrafter.types import (
    Control,
    ControlState,
    ManyOf,
    OneOf,
    Option,
    Schema,
    Section,
    Submenu,
)


class TestCreateInitialState:
    def test_uses_switch_helper_semantics_for_multi_option_defaults(self):
        state = create_initial_state(Schema(sections=[
            Section(
                id="mods",
                text="mods",
                controls=[Control(
                    id="texture pack",
                    text="texture pack",
                    kind="switch",
                    options=[Option(id="oak", text="oak"), Option(id="pine", text="pine")],
                    initially_selected_options=["oak"],
                )],
            ),
        ]))

        assert state.controls["texture pack"] == ControlState(
            selected_options=ManyOf(("oak",)),
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


PACKAGE = Path(__file__).resolve().parents[1] / "promptcrafter"


def _calls_in(module: str) -> set[str]:
    return {ast.unparse(node.func) for node in ast.walk(ast.parse((PACKAGE / module).read_text(encoding="utf-8")))
            if isinstance(node, ast.Call)}


def test_only_submenu_state_key_spells_a_submenus_key_since_a_reader_spelling_it_otherwise_would_find_nothing_and_go_quiet():
    spelled_elsewhere = [path.name for path in PACKAGE.glob("*.py")
                         if path.name != "types.py" and "__submenu" in path.read_text(encoding="utf-8")]

    assert spelled_elsewhere == []
    for reader_or_writer in ("state.py", "runtime.py", "app.py"):
        assert "submenu_state_key" in _calls_in(reader_or_writer), reader_or_writer


class TestSubmenuStateShape:

    @pytest.mark.parametrize("kind", ["or-adv", "or-adj"])
    def test_a_single_select_submenu_starts_holding_one_choice(self, kind):
        state = create_initial_state(_submenu_of_kind(kind))

        assert state.controls[submenu_state_key("bough", "knot")].selected_options == OneOf()

    @pytest.mark.parametrize("kind", ["and-adv", "and-adj"])
    def test_a_multi_select_submenu_starts_with_a_list(self, kind):
        state = create_initial_state(_submenu_of_kind(kind))

        assert state.controls[submenu_state_key("bough", "knot")].selected_options == ManyOf()

    @pytest.mark.parametrize("kind", ["or", "or-prefix", "or-suffix"])
    def test_any_or_prefixed_kind_starts_holding_one_choice_since_nothing_validates_a_submenu_kind(self, kind):
        state = create_initial_state(_submenu_of_kind(kind))

        assert state.controls[submenu_state_key("bough", "knot")].selected_options == OneOf()
