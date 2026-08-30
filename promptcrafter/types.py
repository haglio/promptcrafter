from __future__ import annotations

from dataclasses import dataclass, field
from typing import Literal, Union


# --- Text value types ---

@dataclass
class PluralText:
    singular: str
    plural: str


@dataclass
class TextReference:
    kind: Literal["section", "control", "option"]
    id: str


@dataclass
class TextRef:
    ref: TextReference


TextPart = Union[str, TextRef]


@dataclass
class TemplateText:
    singular: list[TextPart]
    plural: list[TextPart] | None = None


TextValue = Union[str, PluralText, TemplateText]


# --- Visibility / supplement condition types ---

@dataclass
class DisabledOrHiddenBy:
    control_id: str | None = None
    option_id: str | None = None


@dataclass
class SupplementedBy:
    supplemental_text: TextValue
    side: Literal["adv", "adj"] | None = None
    control_id: str | None = None
    option_id: str | None = None


@dataclass
class GlobalSubstitution:
    from_text: TextValue
    to_text: TextValue
    from_plural: TextValue | None = None
    to_plural: TextValue | None = None


# --- Schema types ---

ControlKind = Literal[
    "or", "or-adv", "or-adj", "or-prefix",
    "and-commas", "and-commas-adj", "and-commas-adv",
    "and-spaces-adj", "required", "hidden-opposite",
    "toggle", "global-selector",
]

SubmenuKind = Literal["or-adv", "or-adj", "and-adv", "and-adj"]

PromptTarget = Literal["positive", "negative"]
PromptMode = Literal["auto", "manual"]


@dataclass
class Submenu:
    kind: SubmenuKind
    options: list[Option]


@dataclass
class Option:
    id: str
    text: TextValue
    custom_control_text: TextValue | None = None
    submenu: Submenu | None = None
    hidden_bys: list[DisabledOrHiddenBy] = field(default_factory=list)
    revealed_bys: list[DisabledOrHiddenBy] = field(default_factory=list)
    disabled_bys: list[DisabledOrHiddenBy] = field(default_factory=list)
    supplemented_bys: list[SupplementedBy] = field(default_factory=list)


@dataclass
class Control:
    id: str
    text: TextValue
    kind: ControlKind
    custom_text: TextValue | None = None
    initially_selected_options: bool | str | list[str] | None = None
    global_substitutions: list[GlobalSubstitution] = field(default_factory=list)
    hidden_opposite_bys: list[DisabledOrHiddenBy] = field(default_factory=list)
    options: list[Option] = field(default_factory=list)
    hidden_bys: list[DisabledOrHiddenBy] = field(default_factory=list)
    revealed_bys: list[DisabledOrHiddenBy] = field(default_factory=list)
    disabled_bys: list[DisabledOrHiddenBy] = field(default_factory=list)
    supplemented_bys: list[SupplementedBy] = field(default_factory=list)


@dataclass
class Section:
    id: str
    text: TextValue
    controls: list[Control]
    prompt_target: PromptTarget | None = None
    hidden_bys: list[DisabledOrHiddenBy] = field(default_factory=list)
    revealed_bys: list[DisabledOrHiddenBy] = field(default_factory=list)
    disabled_bys: list[DisabledOrHiddenBy] = field(default_factory=list)
    supplemented_bys: list[SupplementedBy] = field(default_factory=list)


@dataclass
class Schema:
    sections: list[Section]


# --- State types ---

@dataclass
class ControlState:
    selected_options: bool | str | list[str]
    weight: float = 1.0
    enabled: bool | None = None


@dataclass
class SectionState:
    weight: float = 1.0


def _both_prompts_on_auto() -> dict[PromptTarget, PromptMode]:
    return {"positive": "auto", "negative": "auto"}


@dataclass
class State:
    controls: dict[str, ControlState]
    sections: dict[str, SectionState]
    # Keyed by target rather than two fields named after their targets: the
    # window reaches these by the same string it uses to build a prompt, and
    # it used to do that by assembling the attribute name.
    modes: dict[PromptTarget, PromptMode] = field(default_factory=_both_prompts_on_auto)


# --- Rendering types ---

@dataclass
class Segment:
    text: str
    weight: float


@dataclass
class SupplementalText:
    text: str
    side: Literal["adv", "adj"]
