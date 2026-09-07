from __future__ import annotations

from collections.abc import Callable
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


def submenu_state_key(parent_control_id: str, option_id: str) -> str:
    """Where a submenu's own selections live.

    Submenu state sits in the same flat dict as control state, under a
    composite key. Three modules build that key -- the one that writes the dict
    and the two that read it -- so it lives with the `Submenu` it addresses
    rather than with any of them: a reader that disagreed with the writer would
    find no key, and every consumer treats a missing key as "there is no
    submenu" and returns early, so the app would go quiet rather than fail.
    """
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


# --- State types ---

# What one control has picked. Three shapes, one set of questions: readers ask
# rather than test which of the three they were handed, which is what the field
# below used to make every one of them do.


@dataclass(frozen=True)
class Switch:
    """A control that is only ever on or off.

    A ``toggle`` whose control offers at most one option of its own, and a
    ``global-selector`` that is switched off. The selector is the one control
    that changes which of these three it holds, because "off" and "on with
    nothing picked" have to stay tellable apart.
    """

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
    """One option id, or nothing: every ``or`` kind, an ``or`` submenu, and a
    ``global-selector`` that is switched on."""

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
        """Choosing what is already chosen empties the control, which is the
        only way to put a radio group back to nothing."""
        return OneOf("" if self.chosen == option_id else option_id)

    def without(self, reaches: Callable[[str], bool]) -> Selection:
        return OneOf() if reaches(self.chosen) else self

    def with_reach_of(self, option_id: str, offered: list[str]) -> Selection:
        if not offered:
            return self
        return OneOf(option_id if option_id in offered else offered[0])


@dataclass(frozen=True)
class ManyOf:
    """Every option ticked in a control that holds a list."""

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
        # `dict.fromkeys`, not `set`: the TypeScript merged these with
        # `Array.from(new Set([...]))` (`src/App.tsx:239`) and a JS Set keeps
        # insertion order, so the list was stable. A Python set is hash-ordered
        # and string hashing is salted per process, so the port made this come
        # out differently run to run.
        return ManyOf(tuple(dict.fromkeys([*self.chosen, *offered])))


Selection = Union[Switch, OneOf, ManyOf]


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
