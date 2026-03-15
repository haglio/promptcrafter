import type { BaseItem, State, Control, Option, Section, DisabledOrHiddenBy, SupplementedBy, GlobalSubstitution, Schema, TextValue, SupplementalText } from '../types';

export function getTextValue(text: TextValue, isPlural: boolean): string {
  if (typeof text === 'string') return text;
  return isPlural ? text.plural : text.singular;
}

export function getItemText(item: BaseItem, isPlural: boolean): string {
  return getTextValue(item.text, isPlural);
}

export function getOptionText(option: Option, isPlural: boolean): string {
  return getItemText(option, isPlural)
}

function escapeRegex(source: string): string {
  return source.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
}

function replaceWholeWord(input: string, from: string, to: string): string {
  const trimmedFrom = from.trim();
  if (!trimmedFrom) return input;
  return input.replace(new RegExp(`\\b${escapeRegex(trimmedFrom)}\\b`, 'gi'), to);
}

export function applySubstitutions(text: string, substitutions: GlobalSubstitution[]): string {
  let next = text;
  for (const substitution of substitutions) {
    if (substitution.fromPlural && substitution.toPlural) {
      next = replaceWholeWord(next, substitution.fromPlural, substitution.toPlural);
    }
    next = replaceWholeWord(next, substitution.from, substitution.to);
  }
  return next;
}

export function getActiveSubstitutions(schema: Schema, state: State): GlobalSubstitution[] {
  const substitutions: GlobalSubstitution[] = [];

  for (const section of schema.sections) {
    if (isHidden(state, section.hiddenBys) || isDisabled(state, section.disabledBys)) continue;

    for (const control of section.controls) {
      if (control.kind !== 'toggle') continue;
      if (isHidden(state, control.hiddenBys) || isDisabled(state, control.disabledBys)) continue;

      const isEnabled = state.controls[control.id]?.selectedOptions as boolean | undefined;
      if (!isEnabled) continue;

      substitutions.push(...(control.globalSubstitutions ?? []));
    }
  }

  return substitutions;
}

export function getDisplayItemText(item: BaseItem, isPlural: boolean, schema: Schema, state: State): string {
  return applySubstitutions(getItemText(item, isPlural), getActiveSubstitutions(schema, state));
}

export function getDisplayOptionText(option: Option, isPlural: boolean, schema: Schema, state: State): string {
  return applySubstitutions(getOptionText(option, isPlural), getActiveSubstitutions(schema, state));
}

export function isSubjectPlural(state: State): boolean {
  return state.controls.count?.selectedOptions == 'two'
}

export function sectionHasAtLeastOneSelectedOption(section: Section, state: State) {
  return section.controls.some((control) => controlHasAtLeastOneSelectedOption(control, state));
}

export function controlHasAtLeastOneSelectedOption(control: Control, state: State) {
  const s = state.controls[control.id];
  if (!s) return false;

  if (control.kind === 'required') return true;
  if (control.kind === 'toggle') return s.selectedOptions as boolean;
  if (control.kind === 'global-selector') return s.selectedOptions !== false;

  if (control.kind.startsWith('or')) {
    return Boolean(s.selectedOptions as string);
  }

  return (s.selectedOptions as string[]).length > 0;
}

export function submenuStateKey(parentControlId: string, optionId: string) {
  return `${parentControlId}__${optionId}__submenu`;
}

export function joinParts(parts: string[]): string {
  return parts.filter(Boolean).join(', ').replace(/\s+,/g, ',').replace(/,\s*,/g, ', ').trim().replace(/,$/, '');
}

function hasAnySelection(selectedOptions: boolean | string | string[]): boolean {
  if (typeof selectedOptions === 'boolean') return selectedOptions;
  if (typeof selectedOptions === 'string') return Boolean(selectedOptions);
  return selectedOptions.length > 0;
}

function isOptionIdSelected(state: State, optionId: string): boolean {
  return Object.values(state.controls).some(({ selectedOptions }) => {
    if (typeof selectedOptions === 'string') return selectedOptions === optionId;
    if (Array.isArray(selectedOptions)) return selectedOptions.includes(optionId);
    return false;
  });
}

function isByConditionMatched(state: State, by: DisabledOrHiddenBy): boolean {
  if (!by.controlId) return false;

  const controlState = state.controls[by.controlId];
  if (!controlState) return false;

  const { selectedOptions } = controlState;

  if (!by.optionId) return hasAnySelection(selectedOptions);

  if (typeof selectedOptions === 'string') return selectedOptions === by.optionId;
  if (Array.isArray(selectedOptions)) return selectedOptions.includes(by.optionId);
  return false;
}

export function isDisabled(state: State, disabledBys?: DisabledOrHiddenBy[]): boolean {
  if (!disabledBys || disabledBys.length === 0) return false;
  return disabledBys.some((disabledBy) => isByConditionMatched(state, disabledBy));
}

export function isHidden(state: State, hiddenBys?: DisabledOrHiddenBy[]): boolean {
  if (!hiddenBys || hiddenBys.length === 0) return false;
  return hiddenBys.some((hiddenBy) => isByConditionMatched(state, hiddenBy));
}

export function getSupplementalTexts(state: State, supplementedBys?: SupplementedBy[]): SupplementalText[] {
  if (!supplementedBys || supplementedBys.length === 0) return [];
  return supplementedBys
    .filter((supplementedBy) => {
      const hasControlId = Boolean(supplementedBy.controlId);
      const hasOptionId = Boolean(supplementedBy.optionId);

      if (hasControlId === hasOptionId) return false;

      if (supplementedBy.controlId) {
        return isByConditionMatched(state, { controlId: supplementedBy.controlId });
      }

      return isOptionIdSelected(state, supplementedBy.optionId as string);
    })
    .map((supplementedBy) => ({
      text: supplementedBy.supplementalText.trim(),
      side: supplementedBy.side ?? 'adv',
    }))
    .filter((supplementedBy) => Boolean(supplementedBy.text));
}
