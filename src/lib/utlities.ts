import type { State, Control, Option, Section, DisabledOrHiddenBy } from '../types';

export function getOptionText(option: Option, isPlural: boolean): string {
  return isPlural && option.pluralText ? option.pluralText : option.text
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

export function isDisabled(state: State, disabledBys?: DisabledOrHiddenBy[]): boolean {
  if (!disabledBys || disabledBys.length === 0) return false;
  return disabledBys.some((disabledBy) => {
     return state.controls[disabledBy.controlText]?.selectedOptions as boolean ?? false;
  });
}

export function isHidden(state: State, hiddenBys?: DisabledOrHiddenBy[]): boolean {
  if (!hiddenBys || hiddenBys.length === 0) return false;
  return hiddenBys.some((hiddenBy) => {
     return state.controls[hiddenBy.controlText]?.selectedOptions as boolean ?? false;
  });
}
