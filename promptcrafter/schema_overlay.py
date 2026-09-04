"""Load the schema the user actually authored, or fall back to the shipped demo.

``promptcrafter/schema.py`` is a small fabricated schema -- heroes, villains,
pigeons -- and it is the only one this repo may ever contain. A real schema is
the user's own prompt vocabulary: private, and full of exactly the terms
``app_support.sanitize`` refuses to let near a commit. So the real one lives in
a git-ignored ``schema.local.json`` beside the checkout, read at runtime, in the
same shape as every other private overlay in this family.

The JSON keeps the **camelCase** spelling the schema was authored in, not the
snake_case of the dataclasses it becomes. That is deliberate: the overlay is a
document a person edits by hand, and its keys should read the way the schema
they wrote reads. :func:`schema_from_document` is the one place the two
vocabularies meet.

Absence is not an error. A public clone has no overlay, CI has none, and a
worktree has none either -- each of those gets the demo schema, which is what
makes the suite deterministic wherever it runs. Only the checkout holding the
file sees the real thing.
"""
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

OVERLAY_NAME = "schema.local.json"


def overlay_path() -> Path:
    """Where this checkout's private schema would be.

    The checkout's own root, deliberately not the primary's the way
    ``app_support.sanitize`` borrows a blocklist across worktrees. The blocklist
    describes the machine and must be found from anywhere; a schema is content,
    and a worktree that silently loaded the user's real one would run its tests
    against 444 options that are not in the tree under test.
    """
    return project_root() / OVERLAY_NAME


def _text(value: object) -> TextValue:
    """A text node: a bare string, a singular/plural pair, or a template."""
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
    """One piece of a template: literal text, or a reference to another node."""
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
        supplemented_bys=[_supplement(s) for s in doc.get("supplementedBys", [])],
    )


def _control(doc: dict) -> Control:
    return Control(
        id=doc["id"],
        text=_text(doc["text"]),
        kind=doc["kind"],
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
        supplemented_bys=[_supplement(s) for s in doc.get("supplementedBys", [])],
    )


def schema_from_document(document: dict) -> Schema:
    """Build a :class:`Schema` from the overlay's camelCase document."""
    return Schema(sections=[_section(s) for s in document["sections"]])


def load_schema() -> Schema:
    """The private schema if this checkout has one, else the shipped demo."""
    path = overlay_path()
    if not path.is_file():
        return demo_schema
    return schema_from_document(json.loads(path.read_text(encoding="utf-8")))
