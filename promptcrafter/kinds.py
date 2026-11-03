from __future__ import annotations

from promptcrafter.types import ControlKind, SubmenuKind

RADIO_CONTROL_KINDS: frozenset[ControlKind] = frozenset({"or", "or-adv", "or-adj", "or-prefix"})

ADVERB_SUBMENU_KINDS: frozenset[SubmenuKind] = frozenset({"or-adv", "and-adv"})


def is_or_prefixed_kind(kind: str) -> bool:
    return kind.startswith("or")


def is_radio_kind(kind: str) -> bool:
    return kind in RADIO_CONTROL_KINDS


def is_adverb_submenu_kind(kind: str) -> bool:
    return kind in ADVERB_SUBMENU_KINDS
