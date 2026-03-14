import type { State, Control, ControlState, Schema, Section } from '../types';

function createControlState(control: Control): ControlState {
  if (control.kind === 'toggle') {
    return { checkedOptions: [], toggledOn: control.initiallySelected ?? false, weight: 1, selectedOption: undefined };
  }
  if (control.kind === 'required') {
    const always = control.options?.find((option) => option.initiallySelected) ?? control.options?.[0];
    return { checkedOptions: always ? [always.text] : [], toggledOn: false, weight: 1, selectedOption: always?.text };
  }
  const isRadio = control.kind.startsWith('or');
  const preselected = control.options?.find((option) => option.initiallySelected);
  return {
    checkedOptions: isRadio ? [] : (control.options?.filter((option) => option.initiallySelected).map((option) => option.text) ?? []),
    toggledOn: false,
    weight: 1,
    selectedOption: isRadio ? preselected?.text : undefined,
  };
}

function walkControls(controls: Control[], bucket: Record<string, ControlState>) {
  for (const control of controls) {
    bucket[control.text] = createControlState(control);
    for (const option of control.options ?? []) {
      if (option.submenu) {
        bucket[`${control.text}__${option.text}__submenu`] = {
          checkedOptions: option.submenu.options.filter((o) => o.initiallySelected).map((o) => o.text),
          selectedOption: option.submenu.kind.startsWith('or')
            ? option.submenu.options.find((o) => o.initiallySelected)?.text
            : undefined,
          toggledOn: false,
          weight: 1,
        };
      }
    }
  }
}

function createSectionState(sections: Section[]) {
  return Object.fromEntries(sections.map((section) => [section.text, { weight: 1 }]));
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