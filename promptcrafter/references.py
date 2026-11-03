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

    kind: str
    id: str
    at: str


def report_dangling_references(schema: Schema) -> list[Dangling]:
    found = dangling_references(schema)
    for dangling in found:
        logger.warning("%s names a %s that is not in this schema: %r", dangling.at,
                       dangling.kind, dangling.id)
    return found


def known_ids(schema: Schema) -> dict[str, set[str]]:
    found: dict[str, set[str]] = {"section": set(), "control": set(), "option": set()}
    for place, _ in every_holder(schema):
        found[place.kind].add(place.id)
    return found


def dangling_references(schema: Schema) -> list[Dangling]:
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
