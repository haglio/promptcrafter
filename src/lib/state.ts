import type { State, Control, ControlState, Schema, Section } from '../types';

function createControlState(control: Control): ControlState {
  if (control.kind === 'toggle') {
    if (Array.isArray(control.initiallySelectedOptions)) {
      return { selectedOptions: control.initiallySelectedOptions, weight: 1 };
    }

    return { selectedOptions: control.initiallySelectedOptions as boolean ?? false, weight: 1 };
  }
  if (control.kind === 'global-selector') {
    // false = off, string = on (with selected option id, or '' if none chosen)
    const initial = control.initiallySelectedOptions;
    if (initial === true) return { selectedOptions: '', weight: 1 };
    if (typeof initial === 'string') return { selectedOptions: initial, weight: 1 };
    return { selectedOptions: false, weight: 1 };
  }
  if (control.kind === 'required') {
    return {
      selectedOptions: (control.initiallySelectedOptions as string[] | undefined) ?? (control.options ?? []).map((option) => option.id),
      weight: 1,
    };
  }
  if (control.kind === 'hidden-opposite') {
    return { selectedOptions: control.initiallySelectedOptions as string[] ?? [], weight: 1 };
  }
  const isRadio = control.kind.startsWith('or');
  if (isRadio) {
    return { selectedOptions: control.initiallySelectedOptions as string ?? '', weight: 1 };
  } else {
    return { selectedOptions: control.initiallySelectedOptions as string[] ?? [], weight: 1 };
  }
}

function walkControls(controls: Control[], bucket: Record<string, ControlState>) {
  for (const control of controls) {
    bucket[control.id] = createControlState(control);
    for (const option of control.options ?? []) {
      if (option.submenu) {
        const submenu = option.submenu;
        const isRadio = submenu.kind.startsWith('or');
        if (isRadio) {
          bucket[`${control.id}__${option.id}__submenu`] = {
            selectedOptions: '',
            weight: 1,
          };
        } else {
          bucket[`${control.id}__${option.id}__submenu`] = {
            selectedOptions: [],
            weight: 1,
          };
        }
      }
    }
  }
}

function createSectionState(sections: Section[]) {
  return Object.fromEntries(sections.map((section) => [section.id, { weight: 1 }]));
}

export function createInitialState(schema: Schema): State {
  const controls: Record<string, ControlState> = {};
  for (const section of schema.sections) walkControls(section.controls, controls);
  return {
    controls,
    sections: createSectionState(schema.sections),
    positiveText: '',
    negativeText: '',
    positiveMode: 'auto',
    negativeMode: 'auto',
  };
}
