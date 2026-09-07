"""Every schema this checkout can load leans only on what the fixture declares.

`tests/fixtures/test_schema.py` is what the renderer, the rules and the window
are tested against, so a schema feature that reaches the app without reaching
that fixture is a feature no test has ever run. Two schemas can reach the app:
the shipped demo, and the private overlay beside the checkout where there is
one -- a public clone, CI and a worktree have none, and there the demo is the
whole of the comparison.

A feature here is a shape the types can carry, never a value: which control and
submenu kinds are declared, which optional fields are filled in, which form each
condition and supplement takes, which sort of text node each piece of text is.
No id, no text and no name out of a schema reaches this file or the message it
fails with, which is what lets it run against a private schema at all.
"""

from __future__ import annotations

import dataclasses

from promptcrafter.schema import schema as demo_schema
from promptcrafter.schema_overlay import load_schema, overlay_path
from promptcrafter.types import (
    Control,
    DisabledOrHiddenBy,
    GlobalSubstitution,
    Option,
    PluralText,
    Schema,
    Section,
    Submenu,
    SupplementedBy,
    TemplateText,
    TextRef,
    TextReference,
)
from tests.fixtures.test_schema import TEST_SCHEMA


def schema_features(schema: Schema) -> set[str]:
    found: set[str] = set()
    for section in schema.sections:
        found.add(f"section:promptTarget={section.prompt_target or 'positive'}")
        _text_features(section.text, found)
        _condition_features(section.hidden_bys, "section.hiddenBys", found)
        _condition_features(section.revealed_bys, "section.revealedBys", found)
        _condition_features(section.disabled_bys, "section.disabledBys", found)
        for control in section.controls:
            _control_features(control, found)
    return found


def _control_features(control: Control, found: set[str]) -> None:
    found.add(f"control:kind={control.kind}")
    _text_features(control.text, found)
    if control.custom_text is not None:
        found.add("control:customText")
        _text_features(control.custom_text, found)
    if control.initially_selected_options is not None:
        found.add(
            "control:initiallySelectedOptions="
            f"{type(control.initially_selected_options).__name__}"
        )
    for substitution in control.global_substitutions:
        _substitution_features(substitution, found)
    _condition_features(control.hidden_opposite_bys, "control.hiddenOppositeBys", found)
    _condition_features(control.hidden_bys, "control.hiddenBys", found)
    _condition_features(control.revealed_bys, "control.revealedBys", found)
    _condition_features(control.disabled_bys, "control.disabledBys", found)
    for supplement in control.supplemented_bys:
        found.add(f"control.supplementedBys:{_which_ids_name(supplement)}")
        found.add(f"control.supplementedBys:side={supplement.side or 'unset'}")
        _text_features(supplement.supplemental_text, found)
    for option in control.options:
        _option_features(option, found, inside_a_submenu=False)


def _option_features(option: Option, found: set[str], *, inside_a_submenu: bool) -> None:
    _text_features(option.text, found)
    if option.custom_control_text is not None:
        found.add("option:customControlText")
        _text_features(option.custom_control_text, found)
    _condition_features(option.hidden_bys, "option.hiddenBys", found)
    _condition_features(option.revealed_bys, "option.revealedBys", found)
    _condition_features(option.disabled_bys, "option.disabledBys", found)
    if option.submenu is not None:
        found.add(f"submenu:kind={option.submenu.kind}")
        if inside_a_submenu:
            found.add("submenu:nested")
        for child in option.submenu.options:
            _option_features(child, found, inside_a_submenu=True)


def _substitution_features(substitution: GlobalSubstitution, found: set[str]) -> None:
    found.add("control:globalSubstitutions")
    _text_features(substitution.from_text, found)
    _text_features(substitution.to_text, found)
    for plural in (substitution.from_plural, substitution.to_plural):
        if plural is not None:
            found.add("control:globalSubstitutions:plural")
            _text_features(plural, found)


def _condition_features(
    conditions: list[DisabledOrHiddenBy], name: str, found: set[str]
) -> None:
    for condition in conditions:
        found.add(f"{name}:{_which_ids_name(condition)}")


def _which_ids_name(rule: DisabledOrHiddenBy | SupplementedBy) -> str:
    """Which of the two ids a condition or supplement fills in.

    The three forms are three different searches, and the fourth -- neither id
    -- is a rule that can never fire.
    """
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
    covered = schema_features(TEST_SCHEMA)

    for name, schema in _schemas_this_checkout_can_load():
        beyond = sorted(schema_features(schema) - covered)
        assert not beyond, f"{name} uses {beyond}, which the test schema does not"


def _one_control_of(kind: str) -> Schema:
    return Schema(sections=[Section(id="glade", text="glade", controls=[
        Control(id="probe", text="probe", kind=kind,
                options=[Option(id="zeta", text="zeta")]),
    ])])


def test_the_walk_names_a_feature_one_schema_carries_and_another_does_not():
    """What the comparison above is worth, said without either real schema."""
    assert schema_features(_one_control_of("toggle")) - schema_features(
        _one_control_of("or")
    ) == {"control:kind=toggle"}


# Every field of every schema type, and the walk owes each one an answer --
# including "this is a name, and a name is not a feature".
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
    """A new field on any of these reds this until the walk decides about it.

    Without it the comparison quietly narrows: a feature nobody taught the walk
    about is a feature it reports as covered.
    """
    for schema_type, expected in _FIELDS_THE_WALK_HAS_AN_ANSWER_FOR.items():
        assert {f.name for f in dataclasses.fields(schema_type)} == expected, schema_type
