import type { Control, Option, PromptTarget, Schema, Section, State } from "../types";
import { applySubstitutions, getActiveSubstitutions, getOptionText, getTextValue, isSubjectPlural, joinParts, submenuStateKey, isHidden, isDisabled, getSupplementalTexts, isTriggeredBy } from "./utlities";
import type { Segment } from "./types";

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
  const isPlural = isSubjectPlural(state);

  const checked = option.submenu.options.filter(
    (child) =>
      (submenuState.selectedOptions as string[]).includes(child.id) &&
      !isHidden(state, child.hiddenBys, child.revealedBys) &&
      !isDisabled(state, child.disabledBys),
  );
  if (checked.length > 0) return checked.map((child) => getOptionText(child, isPlural)).join(' ');

  const selected = option.submenu.options.find(
    (child) =>
      child.id === (submenuState.selectedOptions as string) &&
      !isHidden(state, child.hiddenBys, child.revealedBys) &&
      !isDisabled(state, child.disabledBys),
  );
  return selected ? getOptionText(selected, isPlural) : '';
}

function renderOptionWithModifiers(parentControlId: string, option: Option, state: State): string {
  const modifierText = renderSubmenu(parentControlId, option, state);
  const isPlural = isSubjectPlural(state)
  const optionText = getOptionText(option, isPlural)
  if (!modifierText) return optionText;
  return option.submenu?.kind === 'and-adv' || option.submenu?.kind === 'or-adv' ? 
    `${optionText} ${modifierText}` : 
    `${modifierText} ${optionText}`;
}

function appendSupplements(baseText: string, state: State, control: Control): string {
  if (!baseText.trim()) return '';
  const supplementalTexts = getSupplementalTexts(state, control.supplementedBys);
  if (supplementalTexts.length === 0) return baseText;

  const prependTexts = supplementalTexts
    .filter((supplementalText) => supplementalText.side === 'adj')
    .map((supplementalText) => supplementalText.text);
  const appendTexts = supplementalTexts
    .filter((supplementalText) => supplementalText.side === 'adv')
    .map((supplementalText) => supplementalText.text);

  return [...prependTexts, baseText, ...appendTexts].join(' ');
}

function getControlText(control: Control, state: State, option?: Option): string {
  const isPlural = isSubjectPlural(state);
  if (option?.customControlText) return getTextValue(option.customControlText, isPlural);
  if (control.customText) return getTextValue(control.customText, isPlural);

  return getTextValue(control.text, isPlural);
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
  if (isHidden(state, control.hiddenBys, control.revealedBys)) return [];
  const controlState = state.controls[control.id];
  if (!controlState) return [];
  const disabled = isDisabled(state, control.disabledBys);
  const ownWeight = controlState.weight;
  const isPlural = isSubjectPlural(state);

  if (control.kind === 'toggle') {
    if (!(controlState.selectedOptions as boolean) || disabled) return [];
    const base = control.options?.[0] ? getOptionText(control.options[0], isPlural) : getTextValue(control.text, isPlural);
    return [{ text: appendSupplements(base, state, control), weight: ownWeight }];
  }

  if (control.kind === 'global-selector') {
    return [];
  }

  if (control.kind === 'required') {
    const base = control.options?.[0] ? getOptionText(control.options[0], isPlural) : getTextValue(control.text, isPlural);
    return [{ text: appendSupplements(base, state, control), weight: ownWeight }];
  }

  if (control.kind === 'hidden-opposite') {
    if (!isTriggeredBy(state, control.hiddenOppositeBys) || disabled) return [];

    const selectedOptions = (control.options ?? []).filter((option) => {
      if (isHidden(state, option.hiddenBys, option.revealedBys) || isDisabled(state, option.disabledBys)) return false;
      return (controlState.selectedOptions as string[]).includes(option.id);
    });
    if (selectedOptions.length === 0) return [];

    const text = appendSupplements(
      selectedOptions.map((option) => renderOptionWithModifiers(control.id, option, state)).join(', ').trim(),
      state,
      control,
    );

    return text ? [{ text, weight: ownWeight }] : [];
  }

  const radioKinds = new Set([
    'or',
    'or-adv',
    'or-adj',
    'or-prefix',
  ]);

  if (radioKinds.has(control.kind)) {
    const option = optionById(control, disabled ? undefined : controlState.selectedOptions as string);
    if (!option || isHidden(state, option.hiddenBys, option.revealedBys) || isDisabled(state, option.disabledBys)) return [];
    let text = renderOptionWithModifiers(control.id, option, state);
    if (control.kind === 'or-adv') text = `${getControlText(control, state, option)} ${text}`;
    if (control.kind === 'or-adj') text = `${text} ${getControlText(control, state, option)}`;
    text = appendSupplements(text, state, control);
    return text ? [{ text, weight: ownWeight }] : [];
  }

  const selectedOptions = (control.options ?? []).filter((option) => {
    if (isHidden(state, option.hiddenBys, option.revealedBys) || isDisabled(state, option.disabledBys) || disabled) return false;
    return (controlState.selectedOptions as string[]).includes(option.id);
  });
  if (selectedOptions.length === 0) return [];

  const optionValues = selectedOptions.map((option) => renderOptionWithModifiers(control.id, option, state));

  let combined = '';
  switch (control.kind) {
    case 'and-commas':
      combined = optionValues.join(', ');
      break;
    case 'and-commas-adv':
      combined = selectedOptions.map((option, index) => `${getControlText(control, state, option)} ${optionValues[index]}`).join(', ');
      break;
    case 'and-spaces-adj':
      combined = `${optionValues.join(' ')} ${getControlText(control, state, selectedOptions[0])}`;
      break;
    default:
      combined = optionValues.join(', ');
  }

  combined = appendSupplements(combined.trim(), state, control);

  return combined.trim() ? [{ text: combined.trim(), weight: ownWeight }] : [];
}

export function renderSection(section: Section, state: State, target: PromptTarget): string[] {
  if ((section.promptTarget ?? 'positive') !== target) return [];
  if (isHidden(state, section.hiddenBys, section.revealedBys)) return [];

  const sectionWeight = state.sections[section.id]?.weight ?? 1;
  const parts: Segment[] = [];

  for (let i = 0; i < section.controls.length; i += 1) {
    const control = section.controls[i];
    if (!control) continue;

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
  return applySubstitutions(
    joinParts(renderSection(section, state, target)),
    getActiveSubstitutions(schema, state),
  );
}

export function buildPrompt(schema: Schema, state: State, target: PromptTarget): string {
  return applySubstitutions(
    joinParts(schema.sections.flatMap((section) => renderSection(section, state, target))),
    getActiveSubstitutions(schema, state),
  );
}
