"""Which ids a schema points at, and which of them it does not hold.

Every failed lookup in the renderer answers with the empty string, so a mistyped
id reaches the prompt as silence: the text is shorter than it should be, nothing
says why, and there is no way to tell a typo from a deliberate blank. So the app
says so here, once, on the way up, for the schema it loaded -- the private one
beside the checkout included, which no suite sees.

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
    Schema,
    SupplementedBy,
    TemplateText,
    TextRef,
    TextValue,
    conditions_of,
    every_holder,
    texts_of,
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
    for place, _ in every_holder(schema):
        found[place.kind].add(place.id)
    return found


def dangling_references(schema: Schema) -> list[Dangling]:
    """Every reference in the schema that names something it does not hold."""
    known = known_ids(schema)
    found: list[Dangling] = []
    for place, holder in every_holder(schema):
        where = str(place)
        for text in texts_of(holder):
            _from_text(text, where, known, found)
        conditions = [condition for named in conditions_of(holder).values() for condition in named]
        if isinstance(holder, Control):
            conditions += holder.supplemented_bys
        _from_conditions(conditions, where, known, found)
    return found


def _from_text(text: TextValue, where: str, known: dict[str, set[str]],
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
