from __future__ import annotations

import json
from pathlib import Path

from promptcrafter.paths import project_root
from promptcrafter.schema import schema as demo_schema
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
    TextPart,
    TextRef,
    TextReference,
    TextValue,
)

_KIND_THE_FILE_CALLS_TOGGLE = {"toggle": "switch"}


OVERLAY_NAME = "schema.local.json"


def overlay_path() -> Path:
    return project_root() / OVERLAY_NAME


def _text(value: object) -> TextValue:
    if isinstance(value, str):
        return value
    if not isinstance(value, dict):
        raise ValueError(f"A text value must be a string or an object, got {type(value).__name__}")
    singular = value.get("singular")
    if singular is None:
        raise ValueError("A text object needs a 'singular'")
    if isinstance(singular, list):
        plural = value.get("plural")
        return TemplateText(
            singular=[_text_part(p) for p in singular],
            plural=[_text_part(p) for p in plural] if isinstance(plural, list) else None,
        )
    return PluralText(singular=singular, plural=value.get("plural", singular))


def _text_part(part: object) -> TextPart:
    if isinstance(part, str):
        return part
    if isinstance(part, dict) and "ref" in part:
        ref = part["ref"]
        return TextRef(ref=TextReference(kind=ref["kind"], id=ref["id"]))
    raise ValueError(f"A template part must be a string or a {{'ref': ...}}, got {part!r}")


def _condition(entry: dict) -> DisabledOrHiddenBy:
    return DisabledOrHiddenBy(
        control_id=entry.get("controlId"),
        option_id=entry.get("optionId"),
    )


def _conditions(owner: dict, key: str) -> list[DisabledOrHiddenBy]:
    return [_condition(e) for e in owner.get(key, [])]


def _supplement(entry: dict) -> SupplementedBy:
    return SupplementedBy(
        supplemental_text=_text(entry["supplementalText"]),
        side=entry.get("side"),
        control_id=entry.get("controlId"),
        option_id=entry.get("optionId"),
    )


def _substitution(entry: dict) -> GlobalSubstitution:
    return GlobalSubstitution(
        from_text=_text(entry["from"]),
        to_text=_text(entry["to"]),
        from_plural=_text(entry["fromPlural"]) if "fromPlural" in entry else None,
        to_plural=_text(entry["toPlural"]) if "toPlural" in entry else None,
    )


def _option(doc: dict) -> Option:
    submenu = doc.get("submenu")
    return Option(
        id=doc["id"],
        text=_text(doc["text"]),
        custom_control_text=_text(doc["customControlText"]) if "customControlText" in doc else None,
        submenu=Submenu(
            kind=submenu["kind"],
            options=[_option(o) for o in submenu["options"]],
        ) if submenu else None,
        hidden_bys=_conditions(doc, "hiddenBys"),
        revealed_bys=_conditions(doc, "revealedBys"),
        disabled_bys=_conditions(doc, "disabledBys"),
    )


def _control(doc: dict) -> Control:
    return Control(
        id=doc["id"],
        text=_text(doc["text"]),
        kind=_KIND_THE_FILE_CALLS_TOGGLE.get(doc["kind"], doc["kind"]),
        custom_text=_text(doc["customText"]) if "customText" in doc else None,
        initially_selected_options=doc.get("initiallySelectedOptions"),
        global_substitutions=[_substitution(g) for g in doc.get("globalSubstitutions", [])],
        hidden_opposite_bys=_conditions(doc, "hiddenOppositeBys"),
        options=[_option(o) for o in doc.get("options", [])],
        hidden_bys=_conditions(doc, "hiddenBys"),
        revealed_bys=_conditions(doc, "revealedBys"),
        disabled_bys=_conditions(doc, "disabledBys"),
        supplemented_bys=[_supplement(s) for s in doc.get("supplementedBys", [])],
    )


def _section(doc: dict) -> Section:
    return Section(
        id=doc["id"],
        text=_text(doc["text"]),
        controls=[_control(c) for c in doc["controls"]],
        prompt_target=doc.get("promptTarget"),
        hidden_bys=_conditions(doc, "hiddenBys"),
        revealed_bys=_conditions(doc, "revealedBys"),
        disabled_bys=_conditions(doc, "disabledBys"),
    )


def schema_from_document(document: dict) -> Schema:
    return Schema(sections=[_section(s) for s in document["sections"]])


def load_schema() -> Schema:
    path = overlay_path()
    if not path.is_file():
        return demo_schema
    return schema_from_document(json.loads(path.read_text(encoding="utf-8")))
