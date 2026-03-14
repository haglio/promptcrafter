import { describe, expect, it } from 'vitest';
import { createInitialState } from '../lib/state';
import { testSchema } from './fixtures/testSchema';
import { buildPrompt } from '../lib/prompt';

describe('prompt building', () => {
  it('builds a combined positive prompt from mixed control kinds', () => {
    const state = createInitialState(testSchema);

    // 'or'
    state.controls['alignment'].selectedOptions = 'hero';

    // 'or-prefix'
    state.controls['element prefix'].selectedOptions = 'void';

    // 'or-adv', with custom text
    state.controls['silhouette'].selectedOptions = 'towering';

    // 'or-adj'
    state.controls['armor'].selectedOptions = 'chrome';

    // TODO: 'or-adj', with custom text

    // 'and-commas', with submenu TODO: but this isn't good enough; we need to test all four different kinds of submenus
    state.controls['appendages'].selectedOptions = ['wings', 'tail'];
    state.controls['appendages__wings__submenu'].selectedOptions = ['mechanical'];

    // 'and-commas-adv'
    state.controls['stance'].selectedOptions = ['lunging', 'three-quarter'];

    // 'and-commas-adv', with custom text
    state.controls['sitting on'].selectedOptions = ['etchings', 'glow'];

    // 'and-spaces-adj'
    state.controls['render style'].selectedOptions = ['cinematic', 'volumetric'];

    // TODO: 'and-spaces-adj', with custom text

    expect(buildPrompt(testSchema, state, 'positive')).toBe(
      'space robo dino demon monster, hero, outline towering, void chrome armor, mechanical wings, tail, alighting upon etchings, alighting upon glow, stance lunging, stance three-quarter, cinematic volumetric render style',
    );
  });

  // TODO: test of disabledBys ... apparently disabledBys can apply at the the section level, control level, and option level

  // TODO: test of hiddenBys... same as with disabledBys, but also we don't have an example of these in the real schema anymore, but I'm fairly confident that we will need it

  it('parts of sections - weights override section weight', () => {
    const state = createInitialState(testSchema);
    state.controls['alignment'].selectedOptions = 'hero';
    state.sections['subject-core'].weight = 5;
    state.controls['alignment'].weight = 3;
    state.controls['silhouette'].selectedOptions = 'towering';

    const prompt = buildPrompt(testSchema, state, 'positive');
    expect(prompt).toContain('(space robo dino demon monster:5.0), (hero:3.0), (outline towering:5.0)');
  });

  it('builds the negative prompt independently', () => {
    const state = createInitialState(testSchema);
    state.controls['neg-quality'].selectedOptions = ['blurry', 'extra limbs'];

    expect(buildPrompt(testSchema, state, 'negative')).toBe('no clutter, blurry, extra limbs');
  });

  // TODO: test of plurality; customText needs to support plurality, see "sweater" in real-life prompt for example why. and make sure that pluralText doesn't work only for Controls but also Options and Sections
})