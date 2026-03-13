import { useEffect, useMemo, useState } from 'react';
import { SectionView } from './components/ControlRenderer';
import { PromptArea } from './components/PromptArea';
import { buildPrompt } from './lib/promptBuilder';
import { schema } from './lib/schema';
import { createInitialState } from './lib/state';
import type { BuilderState, Schema } from './lib/types';

export default function App({schema}: {schema: Schema}) {
  const [state, setState] = useState<BuilderState>(() => {
    const initial = createInitialState(schema);
    return {
       ...initial, 
       positiveText: buildPrompt(schema, initial, 'positive'), 
       negativeText: buildPrompt(schema, initial, 'negative') 
    };
  });

  const generated = useMemo(() => ({
    positive: buildPrompt(schema, state, 'positive'),
    negative: buildPrompt(schema, state, 'negative'),
  }), [state]);

  useEffect(() => {
    setState((current) => ({
      ...current,
      positiveText: current.positiveBound ? generated.positive : current.positiveText,
      negativeText: current.negativeBound ? generated.negative : current.negativeText,
    }));
  }, [generated.negative, generated.positive]);

  const actions = {
    setSectionWeight(sectionId: string, weight: number) {
      setState((current) => ({ ...current, sections: { ...current.sections, [sectionId]: { weight } } }));
    },
    setControlWeight(controlId: string, weight: number) {
      setState((current) => ({ ...current, controls: { ...current.controls, [controlId]: { ...current.controls[controlId], weight } } }));
    },
    setRadio(controlId: string, optionId: string) {
      setState((current) => ({ ...current, controls: { ...current.controls, [controlId]: { ...current.controls[controlId], selectedOptionId: optionId } } }));
    },
    toggleCheck(controlId: string, optionId: string) {
      setState((current) => {
        const control = current.controls[controlId];
        const exists = control.checkedOptionIds.includes(optionId);
        return {
          ...current,
          controls: {
            ...current.controls,
            [controlId]: {
              ...control,
              checkedOptionIds: exists ? control.checkedOptionIds.filter((value) => value !== optionId) : [...control.checkedOptionIds, optionId],
            },
          },
        };
      });
    },
    setToggle(controlId: string, value: boolean) {
      setState((current) => ({ ...current, controls: { ...current.controls, [controlId]: { ...current.controls[controlId], toggleOn: value } } }));
    },
  };

  return (
    <main className="app-shell">
      <header>
        <h1>PromptCrafter</h1>
      </header>

      <div className="prompt-stack">
        <PromptArea
          label="Positive prompt"
          value={state.positiveText}
          bound={state.positiveBound}
          onChange={(value) => setState((current) => ({ ...current, positiveText: value }))}
          onToggleBound={(bound) => setState((current) => ({ ...current, positiveBound: bound, positiveText: bound ? generated.positive : current.positiveText }))}
        />
        <PromptArea
          label="Negative prompt"
          value={state.negativeText}
          bound={state.negativeBound}
          onChange={(value) => setState((current) => ({ ...current, negativeText: value }))}
          onToggleBound={(bound) => setState((current) => ({ ...current, negativeBound: bound, negativeText: bound ? generated.negative : current.negativeText }))}
        />
      </div>

      <div className="sections">
        {schema.sections.map((section) => <SectionView key={section.id} section={section} state={state} actions={actions} schema={schema} />)}
      </div>
    </main>
  );
}