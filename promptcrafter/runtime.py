from __future__ import annotations

import re

from promptcrafter.toggle_state import is_toggle_enabled
from promptcrafter.types import (
    Control,
    DisabledOrHiddenBy,
    GlobalSubstitution,
    Option,
    PluralText,
    PromptTarget,
    Schema,
    Section,
    Segment,
    State,
    SupplementalText,
    SupplementedBy,
    TemplateText,
    TextRef,
    TextValue,
)

ResolutionStack = set[str]


def _is_template_text(text: TextValue) -> bool:
    return isinstance(text, TemplateText)


def _normalize_resolved_text(text: str) -> str:
    return re.sub(r"\s+", " ", text).strip()


def _escape_regex(source: str) -> str:
    return re.escape(source)


def _replace_whole_word(input_text: str, from_text: str, to_text: str) -> str:
    trimmed = from_text.strip()
    if not trimmed:
        return input_text
    return re.sub(rf"\b{_escape_regex(trimmed)}\b", to_text, input_text, flags=re.IGNORECASE)


def is_subject_plural(state: State) -> bool:
    count = state.controls.get("count")
    return count is not None and count.selected_options == "two"


def control_has_at_least_one_selected_option(control: Control, state: State) -> bool:
    cs = state.controls.get(control.id)
    if not cs:
        return False
    if control.kind == "required":
        return True
    if control.kind == "toggle":
        return is_toggle_enabled(cs)
    if control.kind == "global-selector":
        return cs.selected_options is not False
    if control.kind.startswith("or"):
        return bool(cs.selected_options) if isinstance(cs.selected_options, str) else False
    return isinstance(cs.selected_options, list) and len(cs.selected_options) > 0


def _has_any_selection(selected_options: bool | str | list[str]) -> bool:
    if isinstance(selected_options, bool):
        return selected_options
    if isinstance(selected_options, str):
        return bool(selected_options)
    return len(selected_options) > 0


def _is_option_id_selected(state: State, option_id: str) -> bool:
    for cs in state.controls.values():
        if isinstance(cs.selected_options, str) and cs.selected_options == option_id:
            return True
        if isinstance(cs.selected_options, list) and option_id in cs.selected_options:
            return True
    return False


def _is_by_condition_matched(state: State, by: DisabledOrHiddenBy) -> bool:
    if not by.control_id:
        return _is_option_id_selected(state, by.option_id) if by.option_id else False

    control_state = state.controls.get(by.control_id)
    if not control_state:
        return False

    selected = control_state.selected_options

    if not by.option_id:
        if isinstance(selected, bool):
            return is_toggle_enabled(control_state)
        return control_state.enabled if control_state.enabled is not None else _has_any_selection(selected)

    if isinstance(selected, str):
        return selected == by.option_id
    if isinstance(selected, list):
        return by.option_id in selected
    return False


def is_triggered_by(state: State, conditions: list[DisabledOrHiddenBy] | None) -> bool:
    if not conditions:
        return False
    return any(_is_by_condition_matched(state, c) for c in conditions)


def is_disabled(state: State, disabled_bys: list[DisabledOrHiddenBy]) -> bool:
    return is_triggered_by(state, disabled_bys)


def is_hidden(
    state: State,
    hidden_bys: list[DisabledOrHiddenBy],
    revealed_bys: list[DisabledOrHiddenBy],
) -> bool:
    if is_triggered_by(state, hidden_bys):
        return True
    if not revealed_bys:
        return False
    return not is_triggered_by(state, revealed_bys)


def _find_control(schema: Schema, control_id: str) -> Control | None:
    for section in schema.sections:
        for control in section.controls:
            if control.id == control_id:
                return control
    return None


def _find_section(schema: Schema, section_id: str) -> Section | None:
    for section in schema.sections:
        if section.id == section_id:
            return section
    return None


def _find_option(schema: Schema, option_id: str) -> Option | None:
    for section in schema.sections:
        for control in section.controls:
            for option in control.options:
                if option.id == option_id:
                    return option
                if option.submenu:
                    for child in option.submenu.options:
                        if child.id == option_id:
                            return child
    return None


def _resolve_reference_value(
    ref_kind: str,
    ref_id: str,
    is_plural: bool,
    schema: Schema,
    state: State,
    stack: ResolutionStack,
) -> str:
    key = f"{ref_kind}:{ref_id}:{'plural' if is_plural else 'singular'}"
    if key in stack:
        return ""
    next_stack = stack | {key}

    if ref_kind == "option":
        option = _find_option(schema, ref_id)
        return get_option_text(option, is_plural, schema, state, next_stack) if option else ""
    if ref_kind == "control":
        control = _find_control(schema, ref_id)
        return _render_control_value(control, schema, state, next_stack) if control else ""
    section = _find_section(schema, ref_id)
    return _render_section_value(section, schema, state, next_stack) if section else ""


def get_text_value(
    text: TextValue,
    is_plural: bool,
    schema: Schema | None = None,
    state: State | None = None,
    stack: ResolutionStack | None = None,
) -> str:
    if stack is None:
        stack = set()
    if isinstance(text, str):
        return text
    if isinstance(text, TemplateText):
        if not schema or not state:
            return ""
        parts = text.plural if (is_plural and text.plural is not None) else text.singular
        resolved = []
        for part in parts:
            if isinstance(part, str):
                resolved.append(part)
            elif isinstance(part, TextRef):
                resolved.append(
                    _resolve_reference_value(
                        part.ref.kind, part.ref.id, is_plural, schema, state, stack
                    )
                )
        return _normalize_resolved_text("".join(resolved))
    if isinstance(text, PluralText):
        return text.plural if is_plural else text.singular
    return ""


def get_item_text(
    item_text: TextValue,
    is_plural: bool,
    schema: Schema | None = None,
    state: State | None = None,
    stack: ResolutionStack | None = None,
) -> str:
    return get_text_value(item_text, is_plural, schema, state, stack)


def get_option_text(
    option: Option,
    is_plural: bool,
    schema: Schema | None = None,
    state: State | None = None,
    stack: ResolutionStack | None = None,
) -> str:
    return get_item_text(option.text, is_plural, schema, state, stack)


def get_active_substitutions(schema: Schema, state: State) -> list[GlobalSubstitution]:
    substitutions: list[GlobalSubstitution] = []
    for section in schema.sections:
        if is_hidden(state, section.hidden_bys, section.revealed_bys) or is_disabled(state, section.disabled_bys):
            continue
        for control in section.controls:
            if control.kind != "toggle":
                continue
            if is_hidden(state, control.hidden_bys, control.revealed_bys) or is_disabled(state, control.disabled_bys):
                continue
            cs = state.controls.get(control.id)
            if not cs or not is_toggle_enabled(cs):
                continue
            substitutions.extend(control.global_substitutions)
    return substitutions


def apply_substitutions(
    text: str,
    substitutions: list[GlobalSubstitution],
    schema: Schema,
    state: State,
) -> str:
    result = text
    for sub in substitutions:
        from_plural = get_text_value(sub.from_plural or sub.from_text, True, schema, state).strip()
        to_plural = get_text_value(sub.to_plural or sub.to_text, True, schema, state).strip()
        from_text = get_text_value(sub.from_text, False, schema, state).strip()
        to_text = get_text_value(sub.to_text, False, schema, state).strip()
        if from_plural and to_plural:
            result = _replace_whole_word(result, from_plural, to_plural)
        if from_text and to_text:
            result = _replace_whole_word(result, from_text, to_text)
    return result


def submenu_state_key(parent_control_id: str, option_id: str) -> str:
    return f"{parent_control_id}__{option_id}__submenu"


def join_parts(parts: list[str]) -> str:
    filtered = [p for p in parts if p]
    joined = ", ".join(filtered)
    joined = re.sub(r"\s+,", ",", joined)
    joined = re.sub(r",\s*,", ", ", joined)
    joined = joined.strip().rstrip(",")
    return joined


def get_supplemental_texts(
    schema: Schema,
    state: State,
    supplemented_bys: list[SupplementedBy],
    stack: ResolutionStack | None = None,
) -> list[SupplementalText]:
    if not supplemented_bys:
        return []
    if stack is None:
        stack = set()
    plural = is_subject_plural(state)
    result: list[SupplementalText] = []
    for sb in supplemented_bys:
        has_control = bool(sb.control_id)
        has_option = bool(sb.option_id)
        if has_control == has_option:
            continue
        if sb.control_id:
            if not _is_by_condition_matched(state, DisabledOrHiddenBy(control_id=sb.control_id)):
                continue
        else:
            if not _is_option_id_selected(state, sb.option_id):
                continue
        text = get_text_value(sb.supplemental_text, plural, schema, state, stack).strip()
        if text:
            result.append(SupplementalText(text=text, side=sb.side or "adv"))
    return result


def _apply_weight(text: str, weight: float) -> str:
    if not text.strip():
        return ""
    rounded = round(weight * 10) / 10
    return text if rounded == 1 else f"({text}:{rounded:.1f})"


def _option_by_id(control: Control, option_id: str | None) -> Option | None:
    if option_id is None:
        return None
    for option in control.options:
        if option.id == option_id:
            return option
    return None


def _render_submenu(
    parent_control_id: str,
    option: Option,
    schema: Schema,
    state: State,
    stack: ResolutionStack,
) -> str:
    if not option.submenu:
        return ""
    key = submenu_state_key(parent_control_id, option.id)
    submenu_state = state.controls.get(key)
    if not submenu_state:
        return ""
    plural = is_subject_plural(state)

    # "and" submenus: check for list selections
    checked = [
        child
        for child in option.submenu.options
        if isinstance(submenu_state.selected_options, list)
        and child.id in submenu_state.selected_options
        and not is_hidden(state, child.hidden_bys, child.revealed_bys)
        and not is_disabled(state, child.disabled_bys)
    ]
    if checked:
        return " ".join(get_option_text(child, plural, schema, state, stack) for child in checked)

    # "or" submenus: check for string selection
    if isinstance(submenu_state.selected_options, str):
        selected = next(
            (
                child
                for child in option.submenu.options
                if child.id == submenu_state.selected_options
                and not is_hidden(state, child.hidden_bys, child.revealed_bys)
                and not is_disabled(state, child.disabled_bys)
            ),
            None,
        )
        return get_option_text(selected, plural, schema, state, stack) if selected else ""

    return ""


def _render_option_with_modifiers(
    parent_control_id: str,
    option: Option,
    schema: Schema,
    state: State,
    stack: ResolutionStack,
) -> str:
    modifier_text = _render_submenu(parent_control_id, option, schema, state, stack)
    plural = is_subject_plural(state)
    option_text = get_option_text(option, plural, schema, state, stack)
    if not modifier_text:
        return option_text
    if option.submenu and option.submenu.kind in ("and-adv", "or-adv"):
        return f"{option_text} {modifier_text}"
    return f"{modifier_text} {option_text}"


def _append_supplements(
    base_text: str,
    control: Control,
    schema: Schema,
    state: State,
    stack: ResolutionStack,
) -> str:
    if not base_text.strip():
        return ""
    supplements = get_supplemental_texts(schema, state, control.supplemented_bys, stack)
    if not supplements:
        return base_text
    prepend = [s.text for s in supplements if s.side == "adj"]
    append = [s.text for s in supplements if s.side == "adv"]
    return " ".join([*prepend, base_text, *append])


def _get_control_text(
    control: Control,
    schema: Schema,
    state: State,
    option: Option | None = None,
    stack: ResolutionStack | None = None,
) -> str:
    if stack is None:
        stack = set()
    plural = is_subject_plural(state)
    if option and option.custom_control_text:
        return get_text_value(option.custom_control_text, plural, schema, state, stack)
    if control.custom_text:
        return get_text_value(control.custom_text, plural, schema, state, stack)
    return get_text_value(control.text, plural, schema, state, stack)


def _render_control_segments(
    control: Control,
    schema: Schema,
    state: State,
    stack: ResolutionStack | None = None,
) -> list[Segment]:
    if stack is None:
        stack = set()
    if is_hidden(state, control.hidden_bys, control.revealed_bys):
        return []
    cs = state.controls.get(control.id)
    if not cs:
        return []
    disabled = is_disabled(state, control.disabled_bys)
    own_weight = cs.weight
    plural = is_subject_plural(state)

    if control.kind == "toggle":
        if disabled or not is_toggle_enabled(cs):
            return []
        if isinstance(cs.selected_options, bool):
            if not control.options and control.global_substitutions:
                return []
            if control.options:
                base = get_option_text(control.options[0], plural, schema, state, stack)
            else:
                base = _get_control_text(control, schema, state, None, stack)
            return [Segment(text=_append_supplements(base, control, schema, state, stack), weight=own_weight)]
        selected = [
            opt for opt in control.options
            if not is_hidden(state, opt.hidden_bys, opt.revealed_bys)
            and not is_disabled(state, opt.disabled_bys)
            and isinstance(cs.selected_options, list)
            and opt.id in cs.selected_options
        ]
        if not selected:
            return []
        combined = ", ".join(
            _render_option_with_modifiers(control.id, opt, schema, state, stack)
            for opt in selected
        ).strip()
        text = _append_supplements(combined, control, schema, state, stack)
        return [Segment(text=text, weight=own_weight)] if text else []

    if control.kind == "global-selector":
        return []

    if control.kind == "required":
        selected = [
            opt for opt in control.options
            if not is_hidden(state, opt.hidden_bys, opt.revealed_bys)
            and not (is_disabled(state, opt.disabled_bys) or disabled)
            and isinstance(cs.selected_options, list)
            and opt.id in cs.selected_options
        ]
        if not selected:
            return []
        combined = ", ".join(
            _render_option_with_modifiers(control.id, opt, schema, state, stack)
            for opt in selected
        ).strip()
        text = _append_supplements(combined, control, schema, state, stack)
        return [Segment(text=text, weight=own_weight)] if text else []

    if control.kind == "hidden-opposite":
        if not is_triggered_by(state, control.hidden_opposite_bys) or disabled:
            return []
        selected = [
            opt for opt in control.options
            if not is_hidden(state, opt.hidden_bys, opt.revealed_bys)
            and not is_disabled(state, opt.disabled_bys)
            and isinstance(cs.selected_options, list)
            and opt.id in cs.selected_options
        ]
        if not selected:
            return []
        text = _append_supplements(
            ", ".join(
                _render_option_with_modifiers(control.id, opt, schema, state, stack)
                for opt in selected
            ).strip(),
            control, schema, state, stack,
        )
        return [Segment(text=text, weight=own_weight)] if text else []

    radio_kinds = {"or", "or-adv", "or-adj", "or-prefix"}
    if control.kind in radio_kinds:
        sel_id = cs.selected_options if not disabled and isinstance(cs.selected_options, str) else None
        option = _option_by_id(control, sel_id) if sel_id else None
        if not option or is_hidden(state, option.hidden_bys, option.revealed_bys) or is_disabled(state, option.disabled_bys):
            return []
        text = _render_option_with_modifiers(control.id, option, schema, state, stack)
        if control.kind == "or-adv":
            text = f"{_get_control_text(control, schema, state, option, stack)} {text}"
        if control.kind == "or-adj":
            text = f"{text} {_get_control_text(control, schema, state, option, stack)}"
        text = _append_supplements(text, control, schema, state, stack)
        return [Segment(text=text, weight=own_weight)] if text else []

    # and-commas, and-commas-adj, and-commas-adv, and-spaces-adj
    selected = [
        opt for opt in control.options
        if not is_hidden(state, opt.hidden_bys, opt.revealed_bys)
        and not (is_disabled(state, opt.disabled_bys) or disabled)
        and isinstance(cs.selected_options, list)
        and opt.id in cs.selected_options
    ]
    if not selected:
        return []

    option_values = [
        _render_option_with_modifiers(control.id, opt, schema, state, stack)
        for opt in selected
    ]

    if control.kind == "and-commas":
        combined = ", ".join(option_values)
    elif control.kind == "and-commas-adj":
        combined = ", ".join(
            f"{option_values[i]} {_get_control_text(control, schema, state, selected[i], stack)}"
            for i in range(len(selected))
        )
    elif control.kind == "and-commas-adv":
        combined = ", ".join(
            f"{_get_control_text(control, schema, state, selected[i], stack)} {option_values[i]}"
            for i in range(len(selected))
        )
    elif control.kind == "and-spaces-adj":
        combined = f"{' '.join(option_values)} {_get_control_text(control, schema, state, selected[0], stack)}"
    else:
        combined = ", ".join(option_values)

    combined = _append_supplements(combined.strip(), control, schema, state, stack)
    return [Segment(text=combined.strip(), weight=own_weight)] if combined.strip() else []


def _first_rendered_part(
    control: Control,
    schema: Schema,
    state: State,
    stack: ResolutionStack,
) -> Segment | None:
    segments = _render_control_segments(control, schema, state, stack)
    return segments[0] if segments else None


def _merge_segments(segments: list[Segment]) -> list[Segment]:
    merged: list[Segment] = []
    for seg in segments:
        if not seg.text:
            continue
        if merged and merged[-1].weight == seg.weight:
            merged[-1] = Segment(text=f"{merged[-1].text}, {seg.text}", weight=seg.weight)
        else:
            merged.append(Segment(text=seg.text, weight=seg.weight))
    return merged


def _effective_weight(section_weight: float, control_weight: float) -> float:
    return section_weight if control_weight == 1 else control_weight


def _build_section_segments(
    section: Section,
    schema: Schema,
    state: State,
    target: PromptTarget,
    stack: ResolutionStack | None = None,
) -> list[Segment]:
    if stack is None:
        stack = set()
    if (section.prompt_target or "positive") != target:
        return []
    if is_hidden(state, section.hidden_bys, section.revealed_bys):
        return []

    section_weight = state.sections.get(section.id, type("", (), {"weight": 1})).weight
    parts: list[Segment] = []
    i = 0

    while i < len(section.controls):
        control = section.controls[i]

        if control.kind == "or-prefix":
            prefix = _first_rendered_part(control, schema, state, stack)
            next_control = section.controls[i + 1] if i + 1 < len(section.controls) else None

            if not next_control:
                if prefix:
                    parts.append(Segment(
                        text=prefix.text,
                        weight=_effective_weight(section_weight, prefix.weight),
                    ))
                i += 1
                continue

            next_rendered = _first_rendered_part(next_control, schema, state, stack)

            if prefix and next_rendered:
                parts.append(Segment(
                    text=f"{prefix.text} {next_rendered.text}",
                    weight=_effective_weight(
                        section_weight,
                        next_rendered.weight if next_rendered.weight != 1 else prefix.weight,
                    ),
                ))
                i += 2
                continue

            if prefix and not next_rendered and next_control.kind == "or-adj" and next_control.custom_text:
                parts.append(Segment(
                    text=f"{prefix.text} {get_text_value(next_control.custom_text, is_subject_plural(state), schema, state, stack)}",
                    weight=_effective_weight(section_weight, prefix.weight),
                ))
                i += 2
                continue

            if not prefix and next_rendered:
                parts.append(Segment(
                    text=next_rendered.text,
                    weight=_effective_weight(section_weight, next_rendered.weight),
                ))
                i += 2
                continue

            i += 1
            continue

        for part in _render_control_segments(control, schema, state, stack):
            parts.append(Segment(
                text=part.text,
                weight=_effective_weight(section_weight, part.weight),
            ))
        i += 1

    return _merge_segments(parts)


def _render_control_value(
    control: Control,
    schema: Schema,
    state: State,
    stack: ResolutionStack | None = None,
) -> str:
    if stack is None:
        stack = set()
    return join_parts([seg.text for seg in _render_control_segments(control, schema, state, stack)])


def _render_section_value(
    section: Section,
    schema: Schema,
    state: State,
    stack: ResolutionStack | None = None,
) -> str:
    if stack is None:
        stack = set()
    return join_parts([
        seg.text
        for seg in _build_section_segments(section, schema, state, section.prompt_target or "positive", stack)
    ])


def render_section(
    section: Section,
    schema: Schema,
    state: State,
    target: PromptTarget,
) -> list[str]:
    merged = _build_section_segments(section, schema, state, target)
    if not merged:
        return []
    return [_apply_weight(part.text, part.weight) for part in merged]


def build_prompt(schema: Schema, state: State, target: PromptTarget) -> str:
    raw = join_parts([
        text
        for section in schema.sections
        for text in render_section(section, schema, state, target)
    ])
    return apply_substitutions(raw, get_active_substitutions(schema, state), schema, state)
