import { describe, expect, it } from 'vitest';
import { createInitialState } from '../lib/state';
import { testSchema } from './fixtures/testSchema';
import { buildPrompt } from '../lib/prompt';

describe('prompt building', () => {
  describe('control kinds', () => {
    it("renders the 'or' control kind", () => {
      const state = createInitialState(testSchema);
      state.controls['alignment'].selectedOptions = 'hero';

      expect(buildPrompt(testSchema, state, 'positive')).toBe('space robo dino demon monster, hero');
    });

    it("renders the 'or-prefix' control kind", () => {
      const state = createInitialState(testSchema);
      state.controls['element prefix'].selectedOptions = 'void';
      state.controls['armor'].selectedOptions = 'chrome';

      const prompt = buildPrompt(testSchema, state, 'positive');
      expect(prompt).toContain('void chrome armor');
      expect(prompt).not.toContain('void,');
    });

    it("renders the 'or-adv' control kind", () => {
      const state = createInitialState(testSchema);
      state.controls['movement'].selectedOptions = 'swiftly';

      expect(buildPrompt(testSchema, state, 'positive')).toBe('space robo dino demon monster, movement swiftly');
    });

    it("renders the 'or-adj' control kind", () => {
      const state = createInitialState(testSchema);
      state.controls['armor'].selectedOptions = 'chrome';

      expect(buildPrompt(testSchema, state, 'positive')).toBe('space robo dino demon monster, chrome armor');
    });

    it("renders the 'and-commas' control kind", () => {
      const state = createInitialState(testSchema);
      state.controls['appendages'].selectedOptions = ['wings', 'horns'];

      expect(buildPrompt(testSchema, state, 'positive')).toBe(
        'space robo dino demon monster, wings, horns',
      );
    });

    it("renders the 'and-commas-adv' control kind", () => {
      const state = createInitialState(testSchema);
      state.controls['stance'].selectedOptions = ['lunging', 'three-quarter'];

      expect(buildPrompt(testSchema, state, 'positive')).toBe(
        'space robo dino demon monster, stance lunging, stance three-quarter',
      );
    });

    it("renders the 'and-spaces-adj' control kind", () => {
      const state = createInitialState(testSchema);
      state.controls['render style'].selectedOptions = ['cinematic', 'volumetric'];

      expect(buildPrompt(testSchema, state, 'positive')).toBe(
        'space robo dino demon monster, cinematic volumetric render style',
      );
    });
  });

  describe('custom text', () => {
    it("renders custom text for the 'or-adv' control kind", () => {
      const state = createInitialState(testSchema);
      state.controls['silhouette'].selectedOptions = 'towering';

      expect(buildPrompt(testSchema, state, 'positive')).toBe('space robo dino demon monster, outline towering');
    });

    it("renders custom text for the 'or-adj' control kind", () => {
      const state = createInitialState(testSchema);
      state.controls['surface treatment'].selectedOptions = 'runed';

      expect(buildPrompt(testSchema, state, 'positive')).toBe('space robo dino demon monster, runed plating');
    });

    it("renders custom text for the 'and-commas-adv' control kind", () => {
      const state = createInitialState(testSchema);
      state.controls['sitting on'].selectedOptions = ['etchings', 'glow'];

      expect(buildPrompt(testSchema, state, 'positive')).toBe(
        'space robo dino demon monster, alighting upon etchings, alighting upon glow',
      );
    });

    it("renders custom text for the 'and-spaces-adj' control kind", () => {
      const state = createInitialState(testSchema);
      state.controls['finish profile'].selectedOptions = ['matte', 'pearlescent'];

      expect(buildPrompt(testSchema, state, 'positive')).toBe('space robo dino demon monster, matte pearlescent finish');
    });
  });

  describe('submenu kinds', () => {
    it("renders the 'or-adj' submenu kind", () => {
      const state = createInitialState(testSchema);
      state.controls['appendages'].selectedOptions = ['wings'];
      state.controls['appendages__wings__submenu'].selectedOptions = 'mechanical';

      expect(buildPrompt(testSchema, state, 'positive')).toBe('space robo dino demon monster, mechanical wings');
    });

    it("renders the 'or-adv' submenu kind", () => {
      const state = createInitialState(testSchema);
      state.controls['appendages'].selectedOptions = ['horns'];
      state.controls['appendages__horns__submenu'].selectedOptions = 'wishily';

      expect(buildPrompt(testSchema, state, 'positive')).toBe('space robo dino demon monster, horns wishily');
    });

    it("renders the 'and-adj' submenu kind", () => {
      const state = createInitialState(testSchema);
      state.controls['appendages'].selectedOptions = ['tail'];
      state.controls['appendages__tail__submenu'].selectedOptions = ['barbed', 'segmented'];

      expect(buildPrompt(testSchema, state, 'positive')).toBe('space robo dino demon monster, barbed segmented tail');
    });

    it("renders the 'and-adv' submenu kind", () => {
      const state = createInitialState(testSchema);
      state.controls['appendages'].selectedOptions = ['antennae'];
      state.controls['appendages__antennae__submenu'].selectedOptions = ['arched', 'flared'];

      expect(buildPrompt(testSchema, state, 'positive')).toBe('space robo dino demon monster, antennae arched flared');
    });
  });

  describe('weights', () => {
    it('applies control weight', () => {
      const state = createInitialState(testSchema);
      state.controls['alignment'].selectedOptions = 'hero';
      state.controls['alignment'].weight = 3;

      expect(buildPrompt(testSchema, state, 'positive')).toBe('space robo dino demon monster, (hero:3.0)');
    });

    it('applies section weight', () => {
      const state = createInitialState(testSchema);
      state.controls['alignment'].selectedOptions = 'hero';
      state.sections['subject-core'].weight = 5;

      expect(buildPrompt(testSchema, state, 'positive')).toContain('(space robo dino demon monster, hero:5.0)');
    });

    it('control weight overrides section weight for that control', () => {
      const state = createInitialState(testSchema);
      state.controls['alignment'].selectedOptions = 'hero';
      state.sections['subject-core'].weight = 5;
      state.controls['alignment'].weight = 3;
      state.controls['silhouette'].selectedOptions = 'towering';

      const prompt = buildPrompt(testSchema, state, 'positive');
      expect(prompt).toContain('(space robo dino demon monster:5.0), (hero:3.0), (outline towering:5.0)');
    });
  });

  it('builds the negative prompt independently', () => {
    const state = createInitialState(testSchema);
    state.controls['neg-quality'].selectedOptions = ['blurry', 'extra limbs'];

    expect(buildPrompt(testSchema, state, 'negative')).toBe('no clutter, blurry, extra limbs');
  });

  describe('plurality', () => {
    it('uses pluralText at the control level', () => {
      const state = createInitialState(testSchema);
      state.controls['count'].selectedOptions = 'two';
      state.controls['stance'].selectedOptions = ['lunging'];

      expect(buildPrompt(testSchema, state, 'positive')).toContain('stances lunging');
      expect(buildPrompt(testSchema, state, 'positive')).not.toContain('stance lunging');
    });

    it('uses pluralText at the option level', () => {
      const state = createInitialState(testSchema);
      state.controls['count'].selectedOptions = 'two';
      state.controls['alignment'].selectedOptions = 'hero';

      expect(buildPrompt(testSchema, state, 'positive')).toContain('heroes');
      expect(buildPrompt(testSchema, state, 'positive')).not.toContain('hero,');
    });

    it('uses customPluralText at the control level', () => {
      const state = createInitialState(testSchema);
      state.controls['count'].selectedOptions = 'two';
      state.controls['finish profile'].selectedOptions = ['matte', 'pearlescent'];

      expect(buildPrompt(testSchema, state, 'positive')).toContain('matte pearlescent finishes');
    });
  });
});
