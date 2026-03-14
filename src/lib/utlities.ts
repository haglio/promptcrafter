import type { BaseItem, State, Control, Option, Section, DisabledOrHiddenBy, SupplementedBy } from '../types';

export function getItemText(item: BaseItem, isPlural: boolean): string {
  return isPlural && item.pluralText ? item.pluralText : item.text;
}

export function getOptionText(option: Option, isPlural: boolean): string {
  return getItemText(option, isPlural)
}

export function isSubjectPlural(state: State): boolean {
  return state.controls.count?.selectedOptions == 'two'
}

export function sectionHasAtLeastOneSelectedOption(section: Section, state: State) {
  return section.controls.some((control) => controlHasAtLeastOneSelectedOption(control, state));
}

export function controlHasAtLeastOneSelectedOption(control: Control, state: State) {
  const s = state.controls[control.text];

  if (control.kind === 'required') return true;
  if (control.kind === 'toggle') return s.selectedOptions as boolean;

  if (control.kind.startsWith('or')) {
    return Boolean(s.selectedOptions as string);
  }

  return (s.selectedOptions as string[]).length > 0;
}

export function submenuStateKey(parentControl: string, option: string) {
  return `${parentControl}__${option}__submenu`;
}

export function joinParts(parts: string[]): string {
  return parts.filter(Boolean).join(', ').replace(/\s+,/g, ',').replace(/,\s*,/g, ', ').trim().replace(/,$/, '');
}

function hasAnySelection(selectedOptions: boolean | string | string[]): boolean {
  if (typeof selectedOptions === 'boolean') return selectedOptions;
  if (typeof selectedOptions === 'string') return Boolean(selectedOptions);
  return selectedOptions.length > 0;
}

function isOptionTextSelected(state: State, optionText: string): boolean {
  return Object.values(state.controls).some(({ selectedOptions }) => {
    if (typeof selectedOptions === 'string') return selectedOptions === optionText;
    if (Array.isArray(selectedOptions)) return selectedOptions.includes(optionText);
    return false;
  });
}

function isByConditionMatched(state: State, by: DisabledOrHiddenBy): boolean {
  if (!by.controlText) return false;

  const controlState = state.controls[by.controlText];
  if (!controlState) return false;

  const { selectedOptions } = controlState;

  if (!by.optionText) return hasAnySelection(selectedOptions);

  if (typeof selectedOptions === 'string') return selectedOptions === by.optionText;
  if (Array.isArray(selectedOptions)) return selectedOptions.includes(by.optionText);
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

export function getSupplementalTexts(state: State, supplementedBys?: SupplementedBy[]): string[] {
  if (!supplementedBys || supplementedBys.length === 0) return [];
  return supplementedBys
    .filter((supplementedBy) => {
      const hasControlText = Boolean(supplementedBy.controlText);
      const hasOptionText = Boolean(supplementedBy.optionText);

      if (hasControlText === hasOptionText) return false;

      if (supplementedBy.controlText) {
        return isByConditionMatched(state, { controlText: supplementedBy.controlText });
      }

      return isOptionTextSelected(state, supplementedBy.optionText as string);
    })
    .map((supplementedBy) => supplementedBy.supplementalText.trim())
    .filter(Boolean);
}
