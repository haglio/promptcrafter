import { describe, expect, it } from 'vitest';
// @ts-expect-error plain JS script under test
import { convertCsvTextToSchema } from '../../scripts/csv-to-schema.mjs';
import { createInitialState } from '../lib/state';
import { buildPrompt } from '../lib/prompt';
import type { Schema } from '../types';

describe('csv-to-schema generator', () => {
  it('converts CSV rows into a schema with plurals, references, and submenus', () => {
    const csv = [
      'Section,promptTarget,ControlKind,revealedBy,customText,supplementedBy,globalSubstitutions,all options initially selected,Control,Option 1,Option 2',
      'subject,,or-prefix,,,,,FALSE,count,one,two',
      'subject,,or,,,,,FALSE,alignment,hero,villain',
      'subject,,and-commas,"option:count/two OR option:alignment/hero",outline,"control:count: (adj) [control:alignment]; option:alignment/hero: blazing","[option:alignment/hero] → champion",TRUE,details,"wings (feathered, mechanical)","(and: glowing, smoky) aura"',
      'avoid,negative,and-commas,,,,,TRUE,negatives,blur,noise',
    ].join('\n');

    const result = convertCsvTextToSchema(csv, {
      repoRoot: 'C:/repo',
      outputPath: 'C:/repo/src/lib/schema.ts',
    });

    expect(result.diagnostics).toEqual([]);
    expect(result.source).toContain("export const schema: Schema =");

    const schema = result.schema as Schema | null;
    expect(schema).not.toBeNull();
    if (!schema) return;

    const subject = schema.sections.find((section) => section.id === 'subject');
    const details = subject?.controls.find((control) => control.id === 'details');
    expect(subject).toBeDefined();
    expect(details).toBeDefined();
    if (!subject || !details) return;

    expect(subject.text).toEqual({ singular: 'subject', plural: 'subjects' });
    expect(details.customText).toEqual({ singular: 'outline', plural: 'outlines' });
    expect(details.revealedBys).toEqual([{ optionId: 'two' }, { optionId: 'hero' }]);
    expect(details.initiallySelectedOptions).toEqual(['wings', 'aura']);
    expect(details.options?.[0]?.submenu?.kind).toBe('and-adv');
    expect(details.options?.[1]?.submenu?.kind).toBe('and-adj');
    expect(details.supplementedBys).toEqual([
      {
        controlId: 'count',
        supplementalText: {
          singular: [{ ref: { kind: 'control', id: 'alignment' } }],
          plural: [{ ref: { kind: 'control', id: 'alignment' } }],
        },
        side: 'adj',
      },
      {
        optionId: 'hero',
        supplementalText: { singular: 'blazing', plural: 'blazing' },
      },
    ]);
    expect(details.globalSubstitutions).toEqual([
      {
        from: {
          singular: [{ ref: { kind: 'option', id: 'hero' } }],
          plural: [{ ref: { kind: 'option', id: 'hero' } }],
        },
        to: { singular: 'champion', plural: 'champions' },
      },
    ]);

    const state = createInitialState(schema);
    state.controls.count!.selectedOptions = 'two';
    state.controls.alignment!.selectedOptions = 'hero';
    state.controls.details!.selectedOptions = ['wings'];

    expect(buildPrompt(schema, state, 'positive')).toContain('heroes wings blazing');

    state.controls.alignment!.selectedOptions = 'villain';
    expect(buildPrompt(schema, state, 'positive')).toContain('villains wings');
    expect(buildPrompt(schema, state, 'positive')).not.toContain('heroes wings blazing');
  });

  it('reports references it cannot resolve', () => {
    const csv = [
      'Section,promptTarget,ControlKind,revealedBy,customText,supplementedBy,globalSubstitutions,all options initially selected,Control,Option 1',
      'subject,,and-commas,"option:missing/x",,"option:missing/x: spark",,FALSE,details,wing',
    ].join('\n');

    const result = convertCsvTextToSchema(csv);

    expect(result.schema).toBeNull();
    expect(result.source).toBe('');
    expect(result.diagnostics.some((diagnostic: { message: string }) => diagnostic.message.includes('could not be resolved'))).toBe(true);
  });
});
