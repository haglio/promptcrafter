import type { State, Control, Option, Section, DisabledOrHiddenBy } from '../types';

export function getOptionText(option: Option, isPlural: boolean): string {
  return isPlural && option.pluralText ? option.pluralText : option.text
}

export function isSubjectPlural(state: State): boolean {
  return state.controls.count?.selectedOption == 'two'
}

export function sectionHasAtLeastOneSelection(section: Section, state: State) {
  return section.controls.some((control) => controlHasAtLeastOneSelection(control, state));
}

export function controlHasAtLeastOneSelection(control: Control, state: State) {
  const s = state.controls[control.text];

  if (control.kind === 'required') return true;
  if (control.kind === 'toggle') return s.toggledOn;

  if (control.kind.startsWith('or')) {
    return Boolean(s.selectedOption);
  }

  return s.checkedOptions.length > 0;
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
     return state.controls[disabledBy.controlText]?.toggledOn ?? false;
  });
}

export function isHidden(state: State, hiddenBys?: DisabledOrHiddenBy[]): boolean {
  if (!hiddenBys || hiddenBys.length === 0) return false;
  return hiddenBys.some((hiddenBy) => {
     return state.controls[hiddenBy.controlText]?.toggledOn ?? false;
  });
}
