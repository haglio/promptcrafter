import type { BuilderState, ControlDefinition, ControlState, Schema, SectionDefinition } from './types';

function createControlState(control: ControlDefinition): ControlState {
  const defaultWeight = control.defaultWeight ?? 1;
  if (control.kind === 'toggle') {
    return { checkedOptionIds: [], toggleOn: control.defaultToggleOn ?? false, weight: defaultWeight, selectedOptionId: undefined };
  }
  if (control.kind === 'required') {
    const always = control.options?.find((option) => option.defaultSelected) ?? control.options?.[0];
    return { checkedOptionIds: always ? [always.id] : [], toggleOn: false, weight: defaultWeight, selectedOptionId: always?.id };
  }
  const isRadio = control.kind.startsWith('or');
  const preselected = control.options?.find((option) => option.defaultSelected);
  return {
    checkedOptionIds: isRadio ? [] : (control.options?.filter((option) => option.defaultSelected).map((option) => option.id) ?? []),
    toggleOn: false,
    weight: defaultWeight,
    selectedOptionId: isRadio ? preselected?.id : undefined,
  };
}

function walkControls(controls: ControlDefinition[], bucket: Record<string, ControlState>) {
  for (const control of controls) {
    bucket[control.id] = createControlState(control);
    for (const option of control.options ?? []) {
      if (option.submenu) {
        bucket[`${control.id}__${option.id}__submenu`] = {
          checkedOptionIds: option.submenu.options.filter((o) => o.defaultSelected).map((o) => o.id),
          selectedOptionId: option.submenu.selectionMode === 'one'
            ? option.submenu.options.find((o) => o.defaultSelected)?.id
            : undefined,
          toggleOn: false,
          weight: 1,
        };
      }
    }
  }
}

function createSectionState(sections: SectionDefinition[]) {
  return Object.fromEntries(sections.map((section) => [section.id, { weight: section.defaultWeight ?? 1 }]));
}

export function createInitialState(schema: Schema): BuilderState {
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