import type { State, Control, ControlState, Schema, Section } from '../types';

function createControlState(control: Control): ControlState {
  if (control.kind === 'toggle') {
    return { checkedOptionIds: [], toggleOn: control.beginOn ?? false, weight: 1, selectedOptionId: undefined };
  }
  if (control.kind === 'required') {
    const always = control.options?.find((option) => option.beginOn) ?? control.options?.[0];
    return { checkedOptionIds: always ? [always.id] : [], toggleOn: false, weight: 1, selectedOptionId: always?.id };
  }
  const isRadio = control.kind.startsWith('or');
  const preselected = control.options?.find((option) => option.beginOn);
  return {
    checkedOptionIds: isRadio ? [] : (control.options?.filter((option) => option.beginOn).map((option) => option.id) ?? []),
    toggleOn: false,
    weight: 1,
    selectedOptionId: isRadio ? preselected?.id : undefined,
  };
}

function walkControls(controls: Control[], bucket: Record<string, ControlState>) {
  for (const control of controls) {
    bucket[control.id] = createControlState(control);
    for (const option of control.options ?? []) {
      if (option.submenu) {
        bucket[`${control.id}__${option.id}__submenu`] = {
          checkedOptionIds: option.submenu.options.filter((o) => o.beginOn).map((o) => o.id),
          selectedOptionId: option.submenu.kind === 'or'
            ? option.submenu.options.find((o) => o.beginOn)?.id
            : undefined,
          toggleOn: false,
          weight: 1,
        };
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
    positiveBound: true,
    negativeBound: true,
  };
}