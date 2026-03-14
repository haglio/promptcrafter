import type { Control, Option, PromptTarget, Schema, Section, State } from "../types";
import { getOptionText, isSubjectPlural, joinParts, submenuStateKey, isHidden, isDisabled } from "./utlities";
import type { Segment } from "./types";

function applyWeight(text: string, weight: number): string {
  if (!text.trim()) return '';
  const rounded = Math.round(weight * 10) / 10;
  return rounded === 1 ? text : `(${text}:${rounded.toFixed(1)})`;
}

function optionById(control: Control, id?: string): Option | undefined {
  return control.options?.find((option) => option.text === id);
}

function renderSubmenu(parentControlText: string, option: Option, state: State): string {
  if (!option.submenu) return '';

  const key = submenuStateKey(parentControlText, option.text);
  const submenuState = state.controls[key];
  if (!submenuState) return '';

  const checked = option.submenu.options.filter(
    (child) =>
      (submenuState.selectedOptions as string[]).includes(child.text) &&
      !isHidden(state, child.hiddenBys) &&
      !isDisabled(state, child.disabledBys),
  );
  if (checked.length > 0) return checked.map((child) => child.text).join(' ');

  const selected = option.submenu.options.find(
    (child) =>
      child.text === (submenuState.selectedOptions as string) &&
      !isHidden(state, child.hiddenBys) &&
      !isDisabled(state, child.disabledBys),
  );
  return selected?.text ?? '';
}

function renderOptionWithModifiers(parentControlText: string, option: Option, state: State): string {
  const modifierText = renderSubmenu(parentControlText, option, state);
  const isPlural = isSubjectPlural(state)
  const optionText = getOptionText(option, isPlural)
  if (!modifierText) return optionText;
  return option.submenu?.kind === 'and-adv' || option.submenu?.kind === 'or-adv' ? 
    `${optionText} ${modifierText}` : 
    `${modifierText} ${optionText}`;
}

function getControlText(control: Control, state: State): string {
  const isPlural = isSubjectPlural(state);
  if (isPlural && control.customPluralText) return control.customPluralText;
  if (control.customText) return control.customText;
  if (isPlural && control.pluralText) return control.pluralText;

  return control.text;
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
  if (isHidden(state, control.hiddenBys)) return [];
  const controlState = state.controls[control.text];
  if (!controlState) return [];
  const disabled = isDisabled(state, control.disabledBys);
  const ownWeight = controlState.weight;

  if (control.kind === 'toggle') {
    if (!(controlState.selectedOptions as boolean) || disabled) return [];
    const base = control.options?.[0]?.text ?? control.text;
    return [{ text: base, weight: ownWeight }];
  }

  if (control.kind === 'required') {
    const base = control.options?.[0]?.text ?? control.text;
    return [{ text: base, weight: ownWeight }];
  }

  const radioKinds = new Set([
    'or',
    'or-adv',
    'or-adj',
    'or-prefix',
  ]);

  if (radioKinds.has(control.kind)) {
    const option = optionById(control, disabled ? undefined : controlState.selectedOptions as string);
    if (!option || isHidden(state, option.hiddenBys) || isDisabled(state, option.disabledBys)) return [];
    let text = renderOptionWithModifiers(control.text, option, state);
    if (control.kind === 'or-adv') text = `${getControlText(control, state)} ${text}`;
    if (control.kind === 'or-adj') text = `${text} ${getControlText(control, state)}`;
    return text ? [{ text, weight: ownWeight }] : [];
  }

  const selectedOptions = (control.options ?? []).filter((option) => {
    if (isHidden(state, option.hiddenBys) || isDisabled(state, option.disabledBys) || disabled) return false;
    return (controlState.selectedOptions as string[]).includes(option.text);
  });
  if (selectedOptions.length === 0) return [];

  const optionValues = selectedOptions.map((option) => renderOptionWithModifiers(control.text, option, state));

  let combined = '';
  switch (control.kind) {
    case 'and-commas':
      combined = optionValues.join(', ');
      break;
    case 'and-commas-adv':
      combined = optionValues.map((value) => `${getControlText(control, state)} ${value}`).join(', ');
      break;
    case 'and-spaces-adj':
      combined = `${optionValues.join(' ')} ${getControlText(control, state)}`;
      break;
    default:
      combined = optionValues.join(', ');
  }

  return combined.trim() ? [{ text: combined.trim(), weight: ownWeight }] : [];
}

export function renderSection(section: Section, state: State, target: PromptTarget): string[] {
  if ((section.promptTarget ?? 'positive') !== target) return [];
  if (isHidden(state, section.hiddenBys)) return [];

  const sectionWeight = state.sections[section.text]?.weight ?? 1;
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
  const section = schema.sections.find((s) => s.text === sectionId);
  if (!section) return '';
  return joinParts(renderSection(section, state, target));
}

export function buildPrompt(schema: Schema, state: State, target: PromptTarget): string {
  return joinParts(schema.sections.flatMap((section) => renderSection(section, state, target)));
}