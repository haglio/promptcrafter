import { useEffect, useMemo, useState } from 'react';
import { createInitialState } from './lib/state';
import type { State, Schema } from './types';
import { buildPrompt } from './lib/prompt';
import { Prompt } from './components/Prompt';
import { Section } from './components/Section';

export default function App({schema}: {schema: Schema}) {
  const [state, setState] = useState<State>(() => {
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
      positiveText: current.positiveMode === 'auto' ? generated.positive : current.positiveText,
      negativeText: current.negativeMode === 'auto' ? generated.negative : current.negativeText,
    }));
  }, [generated.negative, generated.positive]);

  const actions = {
    setSectionWeight(sectionId: string, weight: number) {
      setState((current) => ({ ...current, sections: { ...current.sections, [sectionId]: { weight } } }));
    },
    setControlWeight(controlId: string, weight: number) {
      setState((current) => {
        const control = current.controls[controlId];
        if (!control) return current;
        return { ...current, controls: { ...current.controls, [controlId]: { selectedOptionId: control.selectedOptionId, checkedOptionIds: control.checkedOptionIds, toggleOn: control.toggleOn, weight } } };
      });
    },
    setRadio(controlId: string, optionId: string) {
      setState((current) => {
        const control = current.controls[controlId];
        if (!control) return current;
        return { ...current, controls: { ...current.controls, [controlId]: { selectedOptionId: optionId, checkedOptionIds: control.checkedOptionIds, toggleOn: control.toggleOn, weight: control.weight } } };
      });
    },
    toggleCheck(controlId: string, optionId: string) {
      setState((current) => {
        const control = current.controls[controlId];
        if (!control) return current;
        const exists = control.checkedOptionIds.includes(optionId);
        return {
          ...current,
          controls: {
            ...current.controls,
            [controlId]: {
              selectedOptionId: control.selectedOptionId,
              checkedOptionIds: exists ? control.checkedOptionIds.filter((value) => value !== optionId) : [...control.checkedOptionIds, optionId],
              toggleOn: control.toggleOn,
              weight: control.weight,
            },
          },
        };
      });
    },
    setToggle(controlId: string, value: boolean) {
      setState((current) => {
        const control = current.controls[controlId];
        if (!control) return current;
        return { ...current, controls: { ...current.controls, [controlId]: { selectedOptionId: control.selectedOptionId, checkedOptionIds: control.checkedOptionIds, toggleOn: value, weight: control.weight } } };
      });
    },
  };

  return (
    <main className="app-shell">
      <header>
        <h1>PromptCrafter</h1>
      </header>

      <div className="prompt-stack">
        <Prompt
          label="Positive prompt"
          value={state.positiveText}
          mode={state.positiveMode}
          onChange={(value) => setState((current) => ({ ...current, positiveText: value }))}
          onToggleMode={(mode) => setState((current) => ({ ...current, positiveMode: mode, positiveText: mode === 'auto' ? generated.positive : current.positiveText }))}
        />
        <Prompt
          label="Negative prompt"
          value={state.negativeText}
          mode={state.negativeMode}
          onChange={(value) => setState((current) => ({ ...current, negativeText: value }))}
          onToggleMode={(mode) => setState((current) => ({ ...current, negativeMode: mode, negativeText: mode === 'auto' ? generated.negative : current.negativeText }))}
        />
      </div>

      <div className="sections">
        {schema.sections.map((section) => <Section key={section.text} section={section} state={state} actions={actions} schema={schema} />)}
      </div>
    </main>
  );
}