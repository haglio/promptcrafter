import { describe, expect, it } from 'vitest';
import { createInitialState } from '../lib/state';
import { testSchema } from './fixtures/testSchema';
import { buildPrompt } from '../lib/prompt';

function controlState(state: ReturnType<typeof createInitialState>, controlId: string) {
  return state.controls[controlId]!;
}

function sectionState(state: ReturnType<typeof createInitialState>, sectionId: string) {
  return state.sections[sectionId]!;
}

describe('prompt building', () => {
  describe('control kinds', () => {
    it("renders the 'or' control kind", () => {
      const state = createInitialState(testSchema);
      controlState(state, 'alignment').selectedOptions = 'hero';

      expect(buildPrompt(testSchema, state, 'positive')).toBe('space robo dino demon monster, hero');
    });

    it("renders the 'or-prefix' control kind", () => {
      const state = createInitialState(testSchema);
      controlState(state, 'element prefix').selectedOptions = 'void';
      controlState(state, 'armor').selectedOptions = 'chrome';

      const prompt = buildPrompt(testSchema, state, 'positive');
      expect(prompt).toContain('void chrome armor');
      expect(prompt).not.toContain('void,');
    });

    it("renders the 'or-adv' control kind", () => {
      const state = createInitialState(testSchema);
      controlState(state, 'movement').selectedOptions = 'swiftly';

      expect(buildPrompt(testSchema, state, 'positive')).toBe('space robo dino demon monster, movement swiftly');
    });

    it("renders the 'or-adj' control kind", () => {
      const state = createInitialState(testSchema);
      controlState(state, 'armor').selectedOptions = 'chrome';

      expect(buildPrompt(testSchema, state, 'positive')).toBe('space robo dino demon monster, chrome armor');
    });

    it("renders the 'and-commas' control kind", () => {
      const state = createInitialState(testSchema);
      controlState(state, 'appendages').selectedOptions = ['wings', 'horns'];

      expect(buildPrompt(testSchema, state, 'positive')).toBe(
        'space robo dino demon monster, wings, horns',
      );
    });

    it("renders the 'and-commas-adv' control kind", () => {
      const state = createInitialState(testSchema);
      controlState(state, 'stance').selectedOptions = ['lunging', 'three-quarter'];

      expect(buildPrompt(testSchema, state, 'positive')).toBe(
        'space robo dino demon monster, stance lunging, stance three-quarter',
      );
    });

    it("renders the 'and-commas-adj' control kind", () => {
      const schema = structuredClone(testSchema);
      schema.sections[1]?.controls.splice(5, 0, {
        id: 'material vibe',
        text: 'material vibe',
        kind: 'and-commas-adj',
        options: [
          { id: 'crystalline', text: 'crystalline' },
          { id: 'molten', text: 'molten' },
        ],
      });

      const state = createInitialState(schema);
      controlState(state, 'material vibe').selectedOptions = ['crystalline', 'molten'];

      expect(buildPrompt(schema, state, 'positive')).toContain(
        'crystalline material vibe, molten material vibe',
      );
    });

    it("renders the 'and-spaces-adj' control kind", () => {
      const state = createInitialState(testSchema);
      controlState(state, 'render style').selectedOptions = ['cinematic', 'volumetric'];

      expect(buildPrompt(testSchema, state, 'positive')).toBe(
        'space robo dino demon monster, cinematic volumetric render style',
      );
    });

    it("renders the 'global-selector' control kind", () => {
      const state = createInitialState(testSchema);
      controlState(state, 'colorize').selectedOptions = 'green';

      expect(buildPrompt(testSchema, state, 'positive')).toBe('space robo dino demon monster');
    });

    it("initializes the 'global-selector' control kind as off", () => {
      const state = createInitialState(testSchema);

      expect(controlState(state, 'colorize').selectedOptions).toBe(false);
    });

    it("renders the 'hidden-opposite' control kind when its linked option is active", () => {
      const state = createInitialState(testSchema);
      controlState(state, 'temperature').selectedOptions = 'hot';

      expect(buildPrompt(testSchema, state, 'negative')).toBe('no clutter, blurry, cold');
    });

    it("renders multi-option toggles as a comma-separated selection list", () => {
      const schema = structuredClone(testSchema);
      schema.sections[1]?.controls.splice(0, 0, {
        id: 'texture pack',
        text: 'texture pack',
        kind: 'toggle',
        initiallySelectedOptions: ['oak', 'pine'],
        options: [
          { id: 'oak', text: 'oak' },
          { id: 'pine', text: 'pine' },
        ],
      });

      const state = createInitialState(schema);

      expect(buildPrompt(schema, state, 'positive')).toBe(
        'space robo dino demon monster, oak, pine',
      );
    });

    it("renders required controls with all selected options instead of only the first one", () => {
      const schema = structuredClone(testSchema);
      schema.sections[0]?.controls.splice(1, 0, {
        id: 'subject base',
        text: 'subject base',
        kind: 'required',
        options: [
          { id: 'hero', text: 'hero' },
          { id: 'villain', text: 'villain' },
        ],
      });

      const state = createInitialState(schema);

      expect(buildPrompt(schema, state, 'positive')).toBe(
        'space robo dino demon monster, hero, villain',
      );
    });

    it('applies global substitutions for toggles without options without adding extra prompt text', () => {
      const schema = structuredClone(testSchema);
      schema.sections[1]?.controls.splice(0, 0, {
        id: 'thorax mode lite',
        text: 'replace torso terminology',
        kind: 'toggle',
        globalSubstitutions: [
          {
            from: 'torso',
            to: 'thorax',
          },
        ],
        options: [],
      });
      schema.sections[1]?.controls.splice(1, 0, {
        id: 'torso mention',
        text: 'torso mention',
        kind: 'and-commas',
        options: [
          { id: 'torso badge', text: 'torso badge' },
        ],
      });

      const state = createInitialState(schema);
      controlState(state, 'thorax mode lite').selectedOptions = true;
      controlState(state, 'torso mention').selectedOptions = ['torso badge'];

      expect(buildPrompt(schema, state, 'positive')).toBe(
        'space robo dino demon monster, thorax badge',
      );
    });

    it('renders control text or custom text for toggles without options when they are enabled', () => {
      const schema = structuredClone(testSchema);
      schema.sections[1]?.controls.splice(0, 0, {
        id: 'safety mode',
        text: 'safety mode',
        customText: 'keep safe',
        kind: 'toggle',
        options: [],
      });

      const state = createInitialState(schema);
      controlState(state, 'safety mode').selectedOptions = true;

      expect(buildPrompt(schema, state, 'positive')).toBe(
        'space robo dino demon monster, keep safe',
      );
    });
  });

  describe('control custom text', () => {
    it("renders custom text for the 'or-adv' control kind", () => {
      const state = createInitialState(testSchema);
      controlState(state, 'silhouette').selectedOptions = 'towering';

      expect(buildPrompt(testSchema, state, 'positive')).toBe('space robo dino demon monster, outline towering');
    });

    it("renders custom text for the 'or-adj' control kind", () => {
      const state = createInitialState(testSchema);
      controlState(state, 'surface treatment').selectedOptions = 'runed';

      expect(buildPrompt(testSchema, state, 'positive')).toBe('space robo dino demon monster, runed plating');
    });

    it("renders custom text for the 'and-commas-adv' control kind", () => {
      const state = createInitialState(testSchema);
      controlState(state, 'sitting on').selectedOptions = ['etchings', 'glow'];

      expect(buildPrompt(testSchema, state, 'positive')).toBe(
        'space robo dino demon monster, alighting upon etchings, alighting upon glow',
      );
    });

    it("renders custom text for the 'and-commas-adj' control kind", () => {
      const schema = structuredClone(testSchema);
      schema.sections[1]?.controls.splice(5, 0, {
        id: 'surface mood',
        text: 'surface mood',
        customText: 'finish',
        kind: 'and-commas-adj',
        options: [
          { id: 'gleaming', text: 'gleaming' },
          { id: 'weathered', text: 'weathered' },
        ],
      });

      const state = createInitialState(schema);
      controlState(state, 'surface mood').selectedOptions = ['gleaming', 'weathered'];

      expect(buildPrompt(schema, state, 'positive')).toContain(
        'gleaming finish, weathered finish',
      );
    });

    it("renders custom text for the 'and-spaces-adj' control kind", () => {
      const state = createInitialState(testSchema);
      controlState(state, 'finish profile').selectedOptions = ['matte', 'pearlescent'];

      expect(buildPrompt(testSchema, state, 'positive')).toBe('space robo dino demon monster, matte pearlescent finish');
    });
  });

  it('options can override the text of their control', () => {
    const state = createInitialState(testSchema);
    controlState(state, 'silhouette').selectedOptions = 'lanky';

    expect(buildPrompt(testSchema, state, 'positive')).toBe('space robo dino demon monster, frame lanky');
  });

  describe('supplements', () => {
    it('options can apply adv supplements to other controls', () => {
      const state = createInitialState(testSchema);
      controlState(state, 'element prefix').selectedOptions = 'nebula';
      controlState(state, 'surface treatment').selectedOptions = 'runed';

      expect(buildPrompt(testSchema, state, 'positive')).toContain('runed plating within nebula');
    });

    it('controls can apply adv supplements to other controls', () => {
      const state = createInitialState(testSchema);
      controlState(state, 'element prefix').selectedOptions = 'nebula';
      controlState(state, 'armor').selectedOptions = 'chrome';

      expect(buildPrompt(testSchema, state, 'positive')).toContain('chrome armor elemental');
    });

    it('options can apply adj supplements to other controls', () => {
      const state = createInitialState(testSchema);
      controlState(state, 'element prefix').selectedOptions = 'plasma';
      controlState(state, 'surface treatment').selectedOptions = 'runed';

      expect(buildPrompt(testSchema, state, 'positive')).toContain('plasma runed plating');
    });

    it('controls can apply adj supplements to other controls', () => {
      const state = createInitialState(testSchema);
      controlState(state, 'movement').selectedOptions = 'heavily';
      controlState(state, 'armor').selectedOptions = 'chrome';

      expect(buildPrompt(testSchema, state, 'positive')).toContain('moving chrome armor');
    });
  });

  describe('submenu kinds', () => {
    it("renders the 'or-adj' submenu kind", () => {
      const state = createInitialState(testSchema);
      controlState(state, 'appendages').selectedOptions = ['wings'];
      controlState(state, 'appendages__wings__submenu').selectedOptions = 'mechanical';

      expect(buildPrompt(testSchema, state, 'positive')).toBe('space robo dino demon monster, mechanical wings');
    });

    it("renders the 'or-adv' submenu kind", () => {
      const state = createInitialState(testSchema);
      controlState(state, 'appendages').selectedOptions = ['horns'];
      controlState(state, 'appendages__horns__submenu').selectedOptions = 'wishily';

      expect(buildPrompt(testSchema, state, 'positive')).toBe('space robo dino demon monster, horns wishily');
    });

    it("renders the 'and-adj' submenu kind", () => {
      const state = createInitialState(testSchema);
      controlState(state, 'appendages').selectedOptions = ['tail'];
      controlState(state, 'appendages__tail__submenu').selectedOptions = ['barbed', 'segmented'];

      expect(buildPrompt(testSchema, state, 'positive')).toBe('space robo dino demon monster, barbed segmented tail');
    });

    it("renders the 'and-adv' submenu kind", () => {
      const state = createInitialState(testSchema);
      controlState(state, 'appendages').selectedOptions = ['antennae'];
      controlState(state, 'appendages__antennae__submenu').selectedOptions = ['arched', 'flared'];

      expect(buildPrompt(testSchema, state, 'positive')).toBe('space robo dino demon monster, antennae arched flared');
    });
  });

  describe('weights', () => {
    it('applies control weight', () => {
      const state = createInitialState(testSchema);
      controlState(state, 'alignment').selectedOptions = 'hero';
      controlState(state, 'alignment').weight = 3;

      expect(buildPrompt(testSchema, state, 'positive')).toBe('space robo dino demon monster, (hero:3.0)');
    });

    it('applies section weight', () => {
      const state = createInitialState(testSchema);
      controlState(state, 'alignment').selectedOptions = 'hero';
      sectionState(state, 'subject-core').weight = 5;

      expect(buildPrompt(testSchema, state, 'positive')).toContain('(space robo dino demon monster, hero:5.0)');
    });

    it('control weight overrides section weight for that control', () => {
      const state = createInitialState(testSchema);
      controlState(state, 'alignment').selectedOptions = 'hero';
      sectionState(state, 'subject-core').weight = 5;
      controlState(state, 'alignment').weight = 3;
      controlState(state, 'silhouette').selectedOptions = 'towering';

      const prompt = buildPrompt(testSchema, state, 'positive');
      expect(prompt).toContain('(space robo dino demon monster:5.0), (hero:3.0), (outline towering:5.0)');
    });
  });

  it('builds the negative prompt independently', () => {
    const state = createInitialState(testSchema);
    controlState(state, 'neg-quality').selectedOptions = ['blurry', 'extra limbs'];

    expect(buildPrompt(testSchema, state, 'negative')).toBe('no clutter, blurry, extra limbs');
  });

  it('does not render hidden-opposite text when its linked option is inactive', () => {
    const state = createInitialState(testSchema);

    expect(buildPrompt(testSchema, state, 'negative')).toBe('no clutter, blurry');
  });

  describe('revealed bys', () => {
    it('does not render revealed sections, controls, or options until their trigger is active', () => {
      const state = createInitialState(testSchema);
      controlState(state, 'portrait lighting').selectedOptions = 'rim-lit';
      controlState(state, 'portrait pose').selectedOptions = 'close crop';

      expect(buildPrompt(testSchema, state, 'positive')).toBe('space robo dino demon monster');
    });

    it('renders revealed sections, controls, and options when their trigger is active', () => {
      const state = createInitialState(testSchema);
      controlState(state, 'is portrait').selectedOptions = true;
      controlState(state, 'portrait lighting').selectedOptions = 'rim-lit';
      controlState(state, 'portrait pose').selectedOptions = 'close crop';

      expect(buildPrompt(testSchema, state, 'positive')).toBe(
        'space robo dino demon monster, portrait, close crop, rim-lit portrait lighting',
      );
    });
  });

  describe('plurality', () => {
    it('uses pluralText at the control level', () => {
      const state = createInitialState(testSchema);
      controlState(state, 'count').selectedOptions = 'two';
      controlState(state, 'stance').selectedOptions = ['lunging'];

      expect(buildPrompt(testSchema, state, 'positive')).toContain('stances lunging');
      expect(buildPrompt(testSchema, state, 'positive')).not.toContain('stance lunging');
    });

    it('uses pluralText at the option level', () => {
      const state = createInitialState(testSchema);
      controlState(state, 'count').selectedOptions = 'two';
      controlState(state, 'alignment').selectedOptions = 'hero';

      expect(buildPrompt(testSchema, state, 'positive')).toContain('heroes');
      expect(buildPrompt(testSchema, state, 'positive')).not.toContain('hero,');
    });

    it('uses customPluralText at the control level', () => {
      const state = createInitialState(testSchema);
      controlState(state, 'count').selectedOptions = 'two';
      controlState(state, 'finish profile').selectedOptions = ['matte', 'pearlescent'];

      expect(buildPrompt(testSchema, state, 'positive')).toContain('matte pearlescent finishes');
    });

    it('uses plural supplemental text when a supplement supplies singular and plural forms', () => {
      const schema = structuredClone(testSchema);
      const armor = schema.sections
        .flatMap((section) => section.controls)
        .find((control) => control.id === 'armor');

      expect(armor).toBeDefined();
      if (!armor) return;

      armor.supplementedBys = [
        {
          controlId: 'movement',
          supplementalText: {
            singular: 'storm',
            plural: 'storms',
          },
          side: 'adj',
        },
      ];

      const state = createInitialState(schema);
      controlState(state, 'count').selectedOptions = 'two';
      controlState(state, 'movement').selectedOptions = 'heavily';
      controlState(state, 'armor').selectedOptions = 'chrome';

      expect(buildPrompt(schema, state, 'positive')).toContain('storms chrome armor');
    });

    it('applies global substitutions for singular and plural terms when substitution toggle is enabled', () => {
      const state = createInitialState(testSchema);
      controlState(state, 'portrait focus').selectedOptions = ['torso', 'torso side profile', 'torsos'];
      controlState(state, 'thorax mode').selectedOptions = true;

      const prompt = buildPrompt(testSchema, state, 'positive');
      expect(prompt).toContain('thorax, thorax side profile, thoraces');
      expect(prompt).not.toContain('torso');
      expect(prompt).not.toContain('torsos');
    });
  });
});
