import type { Condition, Control, Option, PromptTarget, Schema, Section, State } from "../types";
import { getOptionText, isSubjectPlural, joinParts, meetsConditions, submenuStateKey } from "./utlities";
import { Segment } from "./types";

function isHidden(state: State, node: { hides?: Condition[] }): boolean {
  return meetsConditions(state, node.hides);
}

function isDisabled(state: State, node: { disables?: Condition[] }): boolean {
  return meetsConditions(state, node.disables);
}

function applyWeight(text: string, weight: number): string {
  if (!text.trim()) return '';
  const rounded = Math.round(weight * 10) / 10;
  return rounded === 1 ? text : `(${text}:${rounded.toFixed(1)})`;
}

function optionById(control: Control, id?: string): Option | undefined {
  return control.options?.find((option) => option.id === id);
}

function renderSubmenu(parentControlId: string, option: Option, state: State): string {
  if (!option.submenu) return '';

  const key = submenuStateKey(parentControlId, option.id);
  const submenuState = state.controls[key];
  if (!submenuState) return '';

  const checked = option.submenu.options.filter(
    (child) =>
      submenuState.checkedOptionIds.includes(child.id) &&
      !isHidden(state, child) &&
      !isDisabled(state, child),
  );
  if (checked.length > 0) return checked.map((child) => child.id).join(' ');

  const selected = option.submenu.options.find(
    (child) =>
      child.id === submenuState.selectedOptionId &&
      !isHidden(state, child) &&
      !isDisabled(state, child),
  );
  return selected?.id ?? '';
}

function renderOptionWithModifiers(parentControlId: string, option: Option, state: State): string {
  const modifierText = renderSubmenu(parentControlId, option, state);
  const placement = option.submenu?.placement ?? 'before';
  const isPlural = isSubjectPlural(state)
  const optionText = getOptionText(option, isPlural)
  if (!modifierText) return optionText;
  return placement === 'after' ? `${optionText} ${modifierText}` : `${modifierText} ${optionText}`;
}

function getControlText(control: Control): string {
  return control.customText ?? control.id
}

function firstRenderedPart(control: Control, state: State): Segment | undefined {
  return renderControl(control, state)[0];
}

function mergeSegments(segments: Segment[]): Segment[] {
  const merged: Segment[] = [];
  for (const segment of segments) {
    if (!segment.text) continue;
    const prev = merged[merged.length - 1];
    if (prev && prev.weight === segment.weight) {
      prev.text = `${prev.text}, ${segment.text}`;
    } else {
      merged.push({ ...segment });
    }
  }
  return merged;
}

function effectiveWeight(sectionWeight: number, controlWeight: number): number {
  return controlWeight === 1 ? sectionWeight : controlWeight;
}

function renderControl(control: Control, state: State): Segment[] {
  if (isHidden(state, control)) return [];
  const controlState = state.controls[control.id];
  if (!controlState) return [];
  const disabled = isDisabled(state, control);
  const ownWeight = controlState.weight;

  if (control.kind === 'toggle') {
    if (!controlState.toggleOn || disabled) return [];
    const base = control.options?.[0]?.id ?? control.id;
    return [{ text: base, weight: ownWeight }];
  }

  if (control.kind === 'required') {
    const base = control.options?.[0]?.id ?? control.id;
    return [{ text: base, weight: ownWeight }];
  }

  const radioKinds = new Set([
    'or',
    'or-adv',
    'or-adj',
    'or-prefix',
  ]);

  if (radioKinds.has(control.kind)) {
    const option = optionById(control, disabled ? undefined : controlState.selectedOptionId);
    if (!option || isHidden(state, option) || isDisabled(state, option)) return [];
    let text = renderOptionWithModifiers(control.id, option, state);
    if (control.kind === 'or-adv') text = `${getControlText(control)} ${text}`;
    if (control.kind === 'or-adj') text = `${text} ${getControlText(control)}`;
    return text ? [{ text, weight: ownWeight }] : [];
  }

  const selectedOptions = (control.options ?? []).filter((option) => {
    if (isHidden(state, option) || isDisabled(state, option) || disabled) return false;
    return controlState.checkedOptionIds.includes(option.id);
  });
  if (selectedOptions.length === 0) return [];

  const optionValues = selectedOptions.map((option) => renderOptionWithModifiers(control.id, option, state));

  let combined = '';
  switch (control.kind) {
    case 'and-commas':
      combined = optionValues.join(', ');
      break;
    case 'and-commas-adv':
      combined = optionValues.map((value) => `${getControlText(control)} ${value}`).join(', ');
      break;
    case 'and-spaces-adj':
      combined = `${optionValues.join(' ')} ${getControlText(control)}`;
      break;
    default:
      combined = optionValues.join(', ');
  }

  return combined.trim() ? [{ text: combined.trim(), weight: ownWeight }] : [];
}

export function renderSection(section: Section, state: State, target: PromptTarget): string[] {
  if ((section.promptTarget ?? 'positive') !== target) return [];
  if (isHidden(state, section)) return [];

  const sectionWeight = state.sections[section.id]?.weight ?? 1;
  const parts: Segment[] = [];

  for (let i = 0; i < section.controls.length; i += 1) {
    const control = section.controls[i];

    if (control.kind === 'or-prefix') {
      const prefix = firstRenderedPart(control, state);
      const next = section.controls[i + 1];

      if (!next) {
        if (prefix) {
          parts.push({
            text: prefix.text,
            weight: effectiveWeight(sectionWeight, prefix.weight),
          });
        }
        continue;
      }

      const nextRendered = firstRenderedPart(next, state);

      if (prefix && nextRendered) {
        parts.push({
          text: `${prefix.text} ${nextRendered.text}`,
          weight: effectiveWeight(
            sectionWeight,
            nextRendered.weight !== 1 ? nextRendered.weight : prefix.weight,
          ),
        });
        i += 1;
        continue;
      }

      if (prefix && !nextRendered && next.kind === 'or-adj' && next.customText) {
        parts.push({
          text: `${prefix.text} ${next.customText}`,
          weight: effectiveWeight(sectionWeight, prefix.weight),
        });
        i += 1;
        continue;
      }

      if (!prefix && nextRendered) {
        parts.push({
          text: nextRendered.text,
          weight: effectiveWeight(sectionWeight, nextRendered.weight),
        });
        i += 1;
        continue;
      }

      continue;
    }

    for (const part of renderControl(control, state)) {
      parts.push({
        text: part.text,
        weight: effectiveWeight(sectionWeight, part.weight),
      });
    }
  }

  const merged = mergeSegments(parts);
  if (merged.length === 0) return [];
  return merged.map((part) => applyWeight(part.text, part.weight));
}

export function buildSectionPrompt(
  schema: Schema,
  state: State,
  target: PromptTarget,
  sectionId: string,
): string {
  const section = schema.sections.find((s) => s.id === sectionId);
  if (!section) return '';
  return joinParts(renderSection(section, state, target));
}

export function buildPrompt(schema: Schema, state: State, target: PromptTarget): string {
  return joinParts(schema.sections.flatMap((section) => renderSection(section, state, target)));
}