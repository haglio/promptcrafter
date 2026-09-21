"""Which ids a schema points at, and which of them it does not hold.

Every failed lookup in the renderer answers with the empty string, so a mistyped
id reaches the prompt as silence: the text is shorter than it should be, nothing
says why, and there is no way to tell a typo from a deliberate blank. This is the
half that can be checked before anything renders; runtime says so once per id
when it happens anyway, which is the only thing that can reach a schema the suite
never sees.

It walks the schema itself rather than borrowing the renderer's lookups: what it
needs is the whole set of ids, which is one pass, and taking it from here keeps
this under the renderer rather than beside it.
"""
from __future__ import annotations

import logging
from dataclasses import dataclass

from promptcrafter.types import (
    Control,
    DisabledOrHiddenBy,
    Option,
    Schema,
    SupplementedBy,
    TemplateText,
    TextRef,
    TextValue,
)

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class Dangling:
    """One reference that resolves to nothing, and where it was found."""

    kind: str
    id: str
    at: str


def report_dangling_references(schema: Schema) -> list[Dangling]:
    """Log every reference the schema does not hold, and hand them over.

    The app calls this on the way up, which is the only place a schema the suite
    never sees -- the private one beside the checkout -- can be checked at all.
    """
    found = dangling_references(schema)
    for dangling in found:
        logger.warning("%s names a %s that is not in this schema: %r", dangling.at,
                       dangling.kind, dangling.id)
    return found


def known_ids(schema: Schema) -> dict[str, set[str]]:
    """Every id the schema holds, by what kind of thing carries it."""
    found: dict[str, set[str]] = {"section": set(), "control": set(), "option": set()}
    for section in schema.sections:
        found["section"].add(section.id)
        for control in section.controls:
            found["control"].add(control.id)
            _option_ids(control.options, found["option"])
    return found


def dangling_references(schema: Schema) -> list[Dangling]:
    """Every reference in the schema that names something it does not hold."""
    known = known_ids(schema)
    found: list[Dangling] = []
    for section in schema.sections:
        where = f"section:{section.id}"
        _from_text(section.text, where, known, found)
        _from_conditions(_all_conditions(section), where, known, found)
        for control in section.controls:
            _from_control(control, known, found)
    return found


def _option_ids(options: list[Option], into: set[str]) -> None:
    for option in options:
        into.add(option.id)
        if option.submenu:
            _option_ids(option.submenu.options, into)


def _from_control(control: Control, known: dict[str, set[str]],
                  found: list[Dangling]) -> None:
    where = f"control:{control.id}"
    _from_text(control.text, where, known, found)
    _from_text(control.custom_text, where, known, found)
    _from_conditions(_all_conditions(control) + control.hidden_opposite_bys,
                     where, known, found)
    for substitution in control.global_substitutions:
        for text in (substitution.from_text, substitution.to_text,
                     substitution.from_plural, substitution.to_plural):
            _from_text(text, where, known, found)
    for supplement in control.supplemented_bys:
        _from_supplement(supplement, where, known, found)
    for option in control.options:
        _from_option(option, known, found)


def _from_option(option: Option, known: dict[str, set[str]],
                 found: list[Dangling]) -> None:
    where = f"option:{option.id}"
    _from_text(option.text, where, known, found)
    _from_text(option.custom_control_text, where, known, found)
    _from_conditions(_all_conditions(option), where, known, found)
    if option.submenu:
        for child in option.submenu.options:
            _from_option(child, known, found)


def _from_supplement(supplement: SupplementedBy, where: str,
                     known: dict[str, set[str]], found: list[Dangling]) -> None:
    _from_text(supplement.supplemental_text, where, known, found)
    _from_conditions([supplement], where, known, found)


def _all_conditions(holder) -> list:
    return [*holder.hidden_bys, *holder.revealed_bys, *holder.disabled_bys]


def _from_text(text: TextValue | None, where: str, known: dict[str, set[str]],
               found: list[Dangling]) -> None:
    if not isinstance(text, TemplateText):
        return
    found.extend(
        Dangling(kind=part.ref.kind, id=part.ref.id, at=where)
        for parts in (text.singular, text.plural or [])
        for part in parts
        if isinstance(part, TextRef) and part.ref.id not in known[part.ref.kind]
    )


def _from_conditions(conditions: list[DisabledOrHiddenBy | SupplementedBy], where: str,
                     known: dict[str, set[str]], found: list[Dangling]) -> None:
    found.extend(
        Dangling(kind=kind, id=named, at=where)
        for condition in conditions
        for kind in ("control", "option")
        if (named := getattr(condition, f"{kind}_id")) is not None
        and named not in known[kind]
    )
