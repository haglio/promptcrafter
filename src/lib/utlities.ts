import type { State, Control, Option, Section, Condition } from '../types';

export function getOptionText(option: Option, isPlural: boolean): string {
  return isPlural && option.pluralText ? option.pluralText : option.text
}

export function isSubjectPlural(state: State): boolean {
  return state.controls.count?.selectedOptionId == 'two'
}

export function sectionHasSelection(section: Section, state: State) {
  return section.controls.some((control) => controlHasSelection(control, state));
}

export function controlHasSelection(control: Control, state: State) {
  const s = state.controls[control.text];

  if (control.kind === 'required') return true;
  if (control.kind === 'toggle') return s.toggleOn;

  if (control.kind.startsWith('or')) {
    return Boolean(s.selectedOptionId);
  }

  return s.checkedOptionIds.length > 0;
}

export function submenuStateKey(parentControlId: string, optionId: string) {
  return `${parentControlId}__${optionId}__submenu`;
}

export function joinParts(parts: string[]): string {
  return parts.filter(Boolean).join(', ').replace(/\s+,/g, ',').replace(/,\s*,/g, ', ').trim().replace(/,$/, '');
}

export function meetsConditions(state: State, conditions?: Condition[]): boolean {
  if (!conditions || conditions.length === 0) return false;
  return conditions.some((condition) => {
     return state.controls[condition.controlId]?.toggleOn ?? false;
  });
}
