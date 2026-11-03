from __future__ import annotations

from collections.abc import Callable, Iterator
from dataclasses import dataclass, field
from typing import Literal


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


TextPart = str | TextRef


@dataclass
class TemplateText:
    singular: list[TextPart]
    plural: list[TextPart] | None = None


TextValue = str | PluralText | TemplateText



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



ControlKind = Literal[
    "or", "or-adv", "or-adj", "or-prefix",
    "and-commas", "and-commas-adj", "and-commas-adv",
    "and-spaces-adj", "required", "hidden-opposite",
    "switch", "global-selector",
]

SubmenuKind = Literal["or-adv", "or-adj", "and-adv", "and-adj"]

PromptTarget = Literal["positive", "negative"]
PromptMode = Literal["auto", "manual"]


@dataclass
class Submenu:
    kind: SubmenuKind
    options: list[Option]


def submenu_state_key(parent_control_id: str, option_id: str) -> str:
    return f"{parent_control_id}__{option_id}__submenu"


@dataclass
class Option:
    id: str
    text: TextValue
    custom_control_text: TextValue | None = None
    submenu: Submenu | None = None
    hidden_bys: list[DisabledOrHiddenBy] = field(default_factory=list)
    revealed_bys: list[DisabledOrHiddenBy] = field(default_factory=list)
    disabled_bys: list[DisabledOrHiddenBy] = field(default_factory=list)


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


@dataclass
class Schema:
    sections: list[Section]



@dataclass(frozen=True)
class Place:
    kind: Literal["section", "control", "option"]
    id: str

    def __str__(self) -> str:
        return f"{self.kind}:{self.id}"


Holder = Section | Control | Option


def every_holder(schema: Schema) -> Iterator[tuple[Place, Holder]]:
    for section in schema.sections:
        yield Place("section", section.id), section
        for control in section.controls:
            yield Place("control", control.id), control
            yield from _every_option(control.options)


def _every_option(options: list[Option]) -> Iterator[tuple[Place, Holder]]:
    for option in options:
        yield Place("option", option.id), option
        if option.submenu is not None:
            yield from _every_option(option.submenu.options)


def texts_of(holder: Holder) -> list[TextValue]:
    if isinstance(holder, Option):
        found = [holder.text, holder.custom_control_text]
    elif isinstance(holder, Control):
        found = [holder.text, holder.custom_text]
        for substitution in holder.global_substitutions:
            found += [substitution.from_text, substitution.to_text,
                      substitution.from_plural, substitution.to_plural]
        found += [supplement.supplemental_text for supplement in holder.supplemented_bys]
    else:
        found = [holder.text]
    return [text for text in found if text is not None]


def conditions_of(holder: Holder) -> dict[str, list[DisabledOrHiddenBy]]:
    conditions = {"hiddenBys": holder.hidden_bys, "revealedBys": holder.revealed_bys,
                  "disabledBys": holder.disabled_bys}
    if isinstance(holder, Control):
        conditions["hiddenOppositeBys"] = holder.hidden_opposite_bys
    return conditions





@dataclass(frozen=True)
class Switch:

    on: bool = False

    def has_selection(self) -> bool:
        return self.on

    def contains(self, option_id: str) -> bool:
        return False

    def single_choice(self) -> str:
        return ""

    def is_switched_on(self) -> bool:
        return self.on

    def is_engaged(self, enabled: bool | None) -> bool:
        return self.on

    def with_toggled(self, option_id: str) -> Selection:
        return self

    def without(self, reaches: Callable[[str], bool]) -> Selection:
        return self

    def with_reach_of(self, option_id: str, offered: list[str]) -> Selection:
        return self


@dataclass(frozen=True)
class OneOf:

    chosen: str = ""

    def has_selection(self) -> bool:
        return bool(self.chosen)

    def contains(self, option_id: str) -> bool:
        return self.chosen == option_id

    def single_choice(self) -> str:
        return self.chosen

    def is_switched_on(self) -> bool:
        return True

    def is_engaged(self, enabled: bool | None) -> bool:
        return self.has_selection() if enabled is None else enabled

    def with_toggled(self, option_id: str) -> Selection:
        return OneOf("" if self.chosen == option_id else option_id)

    def without(self, reaches: Callable[[str], bool]) -> Selection:
        return OneOf() if reaches(self.chosen) else self

    def with_reach_of(self, option_id: str, offered: list[str]) -> Selection:
        if not offered:
            return self
        return OneOf(option_id if option_id in offered else offered[0])


@dataclass(frozen=True)
class ManyOf:

    chosen: tuple[str, ...] = ()

    def has_selection(self) -> bool:
        return bool(self.chosen)

    def contains(self, option_id: str) -> bool:
        return option_id in self.chosen

    def single_choice(self) -> str:
        return ""

    def is_switched_on(self) -> bool:
        return True

    def is_engaged(self, enabled: bool | None) -> bool:
        return self.has_selection() if enabled is None else enabled

    def with_toggled(self, option_id: str) -> Selection:
        if option_id in self.chosen:
            return ManyOf(tuple(o for o in self.chosen if o != option_id))
        return ManyOf((*self.chosen, option_id))

    def without(self, reaches: Callable[[str], bool]) -> Selection:
        return ManyOf(tuple(o for o in self.chosen if not reaches(o)))

    def with_reach_of(self, option_id: str, offered: list[str]) -> Selection:
        return ManyOf(tuple(dict.fromkeys([*self.chosen, *offered])))


Selection = Switch | OneOf | ManyOf


@dataclass
class ControlState:
    selected_options: Selection
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
    modes: dict[PromptTarget, PromptMode] = field(default_factory=_both_prompts_on_auto)



@dataclass
class Segment:
    text: str
    weight: float


@dataclass
class SupplementalText:
    text: str
    side: Literal["adv", "adj"]
