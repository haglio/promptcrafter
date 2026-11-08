from __future__ import annotations

import dataclasses
import re
from typing import get_args

from promptcrafter.schema import schema as demo_schema
from promptcrafter.schema_overlay import load_schema, overlay_path
from promptcrafter.state import create_initial_state
from promptcrafter.types import (
    Control,
    ControlKind,
    DisabledOrHiddenBy,
    GlobalSubstitution,
    Option,
    PluralText,
    Schema,
    Section,
    Submenu,
    SubmenuKind,
    SupplementedBy,
    TemplateText,
    TextRef,
    TextReference,
    conditions_of,
    every_holder,
    texts_of,
)
from tests.fixtures.sample_schema import SAMPLE_SCHEMA
from tests.kind_shapes import SHAPES_BY_KIND


def schema_features(schema: Schema) -> set[str]:
    found: set[str] = set()
    for place, holder in every_holder(schema):
        for name, conditions in conditions_of(holder).items():
            found.update(f"{place.kind}.{name}:{_which_ids_name(condition)}" for condition in conditions)
        for text in texts_of(holder):
            _text_features(text, found)
        _holder_features(holder, found)
    return found


def _holder_features(holder, found: set[str]) -> None:
    if isinstance(holder, Section):
        found.add(f"section:promptTarget={holder.prompt_target or 'positive'}")
    elif isinstance(holder, Control):
        _control_features(holder, found)
    else:
        _option_features(holder, found)


def _control_features(control: Control, found: set[str]) -> None:
    found.add(f"control:kind={control.kind}")
    if control.custom_text is not None:
        found.add("control:customText")
    if control.initially_selected_options is not None:
        found.add(
            "control:initiallySelectedOptions="
            f"{type(control.initially_selected_options).__name__}"
        )
    for substitution in control.global_substitutions:
        found.add("control:globalSubstitutions")
        if substitution.from_plural is not None or substitution.to_plural is not None:
            found.add("control:globalSubstitutions:plural")
    for supplement in control.supplemented_bys:
        found.add(f"control.supplementedBys:{_which_ids_name(supplement)}")
        found.add(f"control.supplementedBys:side={supplement.side or 'unset'}")


def _option_features(option: Option, found: set[str]) -> None:
    if option.custom_control_text is not None:
        found.add("option:customControlText")
    if option.submenu is not None:
        found.add(f"submenu:kind={option.submenu.kind}")
        if any(child.submenu is not None for child in option.submenu.options):
            found.add("submenu:nested")


def _which_ids_name(rule: DisabledOrHiddenBy | SupplementedBy) -> str:
    if rule.control_id and rule.option_id:
        return "by-control-and-option"
    if rule.control_id:
        return "by-control"
    if rule.option_id:
        return "by-option"
    return "by-nothing"


def _text_features(text, found: set[str]) -> None:
    if isinstance(text, PluralText):
        found.add("text:plural")
        return
    if not isinstance(text, TemplateText):
        found.add("text:plain")
        return
    found.add("text:template")
    if text.plural is not None:
        found.add("text:template:plural")
    for part in [*text.singular, *(text.plural or [])]:
        if isinstance(part, TextRef):
            found.add(f"text:template:ref={part.ref.kind}")


def _schemas_this_checkout_can_load():
    yield "the shipped demo schema", demo_schema
    if overlay_path().is_file():
        yield "this checkout's private schema", load_schema()


def test_no_schema_this_checkout_can_load_reaches_past_the_test_schema():
    covered = schema_features(SAMPLE_SCHEMA)

    for name, schema in _schemas_this_checkout_can_load():
        beyond = sorted(schema_features(schema) - covered)
        assert not beyond, f"{name} uses {beyond}, which the test schema does not"


def test_every_schema_this_checkout_can_load_opens_a_state_the_renderer_can_read():
    for name, schema in _schemas_this_checkout_can_load():
        state = create_initial_state(schema)
        wrong = sorted({
            control.kind
            for section in schema.sections
            for control in section.controls
            if not isinstance(
                getattr(state.controls.get(control.id), "selected_options", None),
                SHAPES_BY_KIND[control.kind],
            )
        })
        assert not wrong, f"{name} opens {wrong} controls holding a shape they cannot render"


def _one_control_of(kind: str) -> Schema:
    return Schema(sections=[Section(id="glade", text="glade", controls=[
        Control(id="probe", text="probe", kind=kind,
                options=[Option(id="zeta", text="zeta")]),
    ])])


def _every_string_of(text) -> list[str]:
    if isinstance(text, str):
        return [text]
    if isinstance(text, PluralText):
        return [text.singular, text.plural]
    return [part for part in [*text.singular, *(text.plural or [])] if isinstance(part, str)]


def test_a_schemas_features_carry_no_id_text_or_name_of_its_own_so_a_failure_over_his_private_schema_says_none():
    the_schemas_own_ids_and_texts = ({place.id for place, _ in every_holder(SAMPLE_SCHEMA)} | {
        word for _, holder in every_holder(SAMPLE_SCHEMA) for text in texts_of(holder) for word in _every_string_of(text)}
    ) - set(get_args(ControlKind)) - set(get_args(SubmenuKind))

    for feature in schema_features(SAMPLE_SCHEMA):
        assert set(re.split(r"[:=.]", feature)).isdisjoint(the_schemas_own_ids_and_texts), feature


def test_the_walk_names_a_feature_one_schema_carries_and_another_does_not():
    assert schema_features(_one_control_of("switch")) - schema_features(
        _one_control_of("or")
    ) == {"control:kind=switch"}


_FIELDS_THE_WALK_HAS_AN_ANSWER_FOR = {
    Schema: {"sections"},
    Section: {"id", "text", "controls", "prompt_target",
              "hidden_bys", "revealed_bys", "disabled_bys"},
    Control: {"id", "text", "kind", "custom_text", "initially_selected_options",
              "global_substitutions", "hidden_opposite_bys", "options",
              "hidden_bys", "revealed_bys", "disabled_bys", "supplemented_bys"},
    Option: {"id", "text", "custom_control_text", "submenu",
             "hidden_bys", "revealed_bys", "disabled_bys"},
    Submenu: {"kind", "options"},
    SupplementedBy: {"supplemental_text", "side", "control_id", "option_id"},
    GlobalSubstitution: {"from_text", "to_text", "from_plural", "to_plural"},
    DisabledOrHiddenBy: {"control_id", "option_id"},
    PluralText: {"singular", "plural"},
    TemplateText: {"singular", "plural"},
    TextRef: {"ref"},
    TextReference: {"kind", "id"},
}


def test_the_walk_has_an_answer_for_every_field_the_schema_types_declare():
    for schema_type, expected in _FIELDS_THE_WALK_HAS_AN_ANSWER_FOR.items():
        assert {f.name for f in dataclasses.fields(schema_type)} == expected, schema_type
