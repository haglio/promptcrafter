import type { Control, ControlState } from '../types';

type ToggleSelectedOptions = boolean | string[];

function getToggleDefaultSelections(control: Control): ToggleSelectedOptions {
  if (Array.isArray(control.initiallySelectedOptions)) {
    return [...control.initiallySelectedOptions];
  }

  if ((control.options?.length ?? 0) > 1) {
    return (control.options ?? []).map((option) => option.id);
  }

  return true;
}

export function createInitialToggleState(control: Control): ControlState {
  if (control.kind !== 'toggle') {
    throw new Error('createInitialToggleState can only be used with toggle controls.');
  }

  const initial = control.initiallySelectedOptions;

  if (Array.isArray(initial)) {
    return {
      selectedOptions: [...initial],
      enabled: false,
      weight: 1,
    };
  }

  if (initial === true) {
    return {
      selectedOptions: getToggleDefaultSelections(control),
      enabled: true,
      weight: 1,
    };
  }

  return {
    selectedOptions: (control.options?.length ?? 0) > 1 ? [] : false,
    enabled: false,
    weight: 1,
  };
}

export function isToggleEnabled(controlState: Pick<ControlState, 'selectedOptions' | 'enabled'>): boolean {
  if (typeof controlState.selectedOptions === 'boolean') {
    return controlState.selectedOptions;
  }

  return controlState.enabled ?? false;
}

export function getToggleSelectionsForNextState(
  control: Control,
  controlState: Pick<ControlState, 'selectedOptions'>,
  enabled: boolean,
): ToggleSelectedOptions {
  if (control.kind !== 'toggle') {
    throw new Error('getToggleSelectionsForNextState can only be used with toggle controls.');
  }

  if (typeof controlState.selectedOptions === 'boolean') {
    return enabled;
  }

  if (!Array.isArray(controlState.selectedOptions)) {
    throw new Error('Toggle controls must use boolean or string[] selectedOptions.');
  }

  if (!enabled) {
    return controlState.selectedOptions;
  }

  // Multi-option toggles keep prior explicit choices; otherwise they fall back to the
  // schema-defined defaults for the first enable action.
  return controlState.selectedOptions.length > 0
    ? controlState.selectedOptions
    : getToggleDefaultSelections(control);
}
