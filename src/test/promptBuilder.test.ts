import { describe, expect, it } from 'vitest';
import { buildPrompt } from '../lib/promptBuilder';
import { createInitialState } from '../lib/state';
import { testSchema } from './fixtures/testSchema';

describe('prompt builder', () => {
  it('builds a combined positive prompt from mixed control kinds', () => {
    const state = createInitialState(testSchema);
    state.controls['alignment'].selectedOptionId = 'hero';
    state.controls['silhouette'].selectedOptionId = 'towering';
    state.controls['element prefix'].selectedOptionId = 'void';
    state.controls['armor'].selectedOptionId = 'chrome';
    state.controls['appendages'].checkedOptionIds = ['wings', 'tail'];
    state.controls['appendages__wings__submenu'].checkedOptionIds = ['mechanical'];
    state.controls['sitting on'].checkedOptionIds = ['etchings', 'glow'];
    state.controls['stance'].checkedOptionIds = ['lunging', 'three-quarter'];
    state.controls['render style'].checkedOptionIds = ['cinematic', 'volumetric'];
    state.controls['camera angle'].selectedOptionId = 'low';

    expect(buildPrompt(testSchema, state, 'positive')).toBe(
      'space robo dino demon monster, hero, silhouette towering, void chrome armor, mechanical wings, tail, sitting on etchings, sitting on glow, lunging three-quarter, cinematic volumetric render, low',
    );
  });

  it('wraps an entire section when a section weight is increased', () => {
    const state = createInitialState(testSchema);
    state.controls['alignment'].selectedOptionId = 'hero';
    state.sections['subject-core'].weight = 3;
    state.controls['alignment'].weight = 5;

    const prompt = buildPrompt(testSchema, state, 'positive');
    expect(prompt).toContain('(space robo dino demon monster, hero:3.0)');
    expect(prompt).not.toContain(':5');
  });

  it('builds the negative prompt independently', () => {
    const state = createInitialState(testSchema);
    state.controls['neg-quality'].checkedOptionIds = ['blurry', 'extra limbs'];

    expect(buildPrompt(testSchema, state, 'negative')).toBe('no clutter, blurry, extra limbs');
  });
})