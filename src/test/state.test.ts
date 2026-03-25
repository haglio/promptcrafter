import { describe, expect, it } from 'vitest';
import { createInitialState } from '../lib/state';
import { createInitialToggleState, getToggleSelectionsForNextState, isToggleEnabled } from '../lib/toggle-state';
import type { Control } from '../types';

function buildToggle(overrides: Partial<Control> = {}): Control {
  return {
    id: 'texture pack',
    text: 'texture pack',
    kind: 'toggle',
    options: [
      { id: 'oak', text: 'oak' },
      { id: 'pine', text: 'pine' },
    ],
    ...overrides,
  };
}

describe('toggle state helpers', () => {
  it('keeps multi-option toggle defaults separate from the enabled flag during initialization', () => {
    const control = buildToggle({ initiallySelectedOptions: ['oak'] });

    expect(createInitialToggleState(control)).toEqual({
      selectedOptions: ['oak'],
      enabled: false,
      weight: 1,
    });
  });

  it('enables a toggle initialized with true using all options when no explicit defaults exist', () => {
    const control = buildToggle({ initiallySelectedOptions: true });

    expect(createInitialToggleState(control)).toEqual({
      selectedOptions: ['oak', 'pine'],
      enabled: true,
      weight: 1,
    });
  });

  it('preserves a multi-option toggle selection when it is turned off and back on', () => {
    const control = buildToggle();
    const selectedOptions = ['oak'];

    const offSelection = getToggleSelectionsForNextState(control, { selectedOptions }, false);
    const onSelection = getToggleSelectionsForNextState(control, { selectedOptions: offSelection }, true);

    expect(offSelection).toEqual(['oak']);
    expect(onSelection).toEqual(['oak']);
  });

  it('still treats direct boolean assignment as enabled for simple toggles', () => {
    expect(isToggleEnabled({ selectedOptions: true })).toBe(true);
    expect(isToggleEnabled({ selectedOptions: false, enabled: true })).toBe(false);
  });
});

describe('initial state creation', () => {
  it('uses toggle helper semantics for multi-option defaults', () => {
    const state = createInitialState({
      sections: [
        {
          id: 'mods',
          text: 'mods',
          controls: [
            buildToggle({ initiallySelectedOptions: ['oak'] }),
          ],
        },
      ],
    });

    expect(state.controls['texture pack']).toEqual({
      selectedOptions: ['oak'],
      enabled: false,
      weight: 1,
    });
  });
});
