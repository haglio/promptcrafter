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
    setState((current) => {
      const nextPositiveText = current.positiveMode === 'auto' ? generated.positive : current.positiveText;
      const nextNegativeText = current.negativeMode === 'auto' ? generated.negative : current.negativeText;

      if (
        current.positiveText === nextPositiveText &&
        current.negativeText === nextNegativeText
      ) {
        return current;
      }

      return {
        ...current,
        positiveText: nextPositiveText,
        negativeText: nextNegativeText,
      };
    });
  }, [generated.negative, generated.positive]);

  const actions = {
    setSectionWeight(sectionId: string, weight: number) {
      setState((current) => ({ ...current, sections: { ...current.sections, [sectionId]: { weight } } }));
    },
    setControlWeight(controlId: string, weight: number) {
      setState((current) => {
        const control = current.controls[controlId];
        if (!control) return current;
        return { ...current, controls: { ...current.controls, [controlId]: { selectedOptions: control.selectedOptions, weight } } };
      });
    },
    setRadio(controlId: string, optionId: string) {
      setState((current) => {
        const control = current.controls[controlId];
        if (!control) return current;
        return { ...current, controls: { ...current.controls, [controlId]: { selectedOptions: optionId, weight: control.weight } } };
      });
    },
    toggleCheck(controlId: string, optionId: string) {
      setState((current) => {
        const control = current.controls[controlId];
        if (!control) return current;
        const selectedOptions = control.selectedOptions as string[];
        const exists = selectedOptions.includes(optionId);
        return {
          ...current,
          controls: {
            ...current.controls,
            [controlId]: {
              selectedOptions: exists ? selectedOptions.filter((value) => value !== optionId) : [...selectedOptions, optionId],
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
        return { ...current, controls: { ...current.controls, [controlId]: { selectedOptions: value, weight: control.weight } } };
      });
    },
    setGlobalSelector(controlId: string, toggleOn: boolean, optionId: string) {
      setState((current) => {
        const control = current.controls[controlId];
        if (!control) return current;
        const previousOptionId = typeof control.selectedOptions === 'string' ? control.selectedOptions : '';
        const newSelectedOptions: string | false = toggleOn ? optionId : false;
        const updatedControls: typeof current.controls = {
          ...current.controls,
          [controlId]: { selectedOptions: newSelectedOptions, weight: control.weight },
        };
        const allSchemaControls = schema.sections.flatMap((s) => s.controls);

        const shouldClearPrevious = Boolean(previousOptionId) && (!toggleOn || previousOptionId !== optionId);
        if (shouldClearPrevious) {
          for (const schemaCtrl of allSchemaControls) {
            if (schemaCtrl.id === controlId) continue;
            const ctrlState = updatedControls[schemaCtrl.id];
            if (!ctrlState) continue;

            if (typeof ctrlState.selectedOptions === 'string') {
              const selected = ctrlState.selectedOptions;
              if (selected && (selected === previousOptionId || selected.includes(previousOptionId))) {
                updatedControls[schemaCtrl.id] = { ...ctrlState, selectedOptions: '' };
              }
            } else if (Array.isArray(ctrlState.selectedOptions)) {
              const filtered = ctrlState.selectedOptions.filter(
                (selected) => selected !== previousOptionId && !selected.includes(previousOptionId),
              );
              if (filtered.length !== ctrlState.selectedOptions.length) {
                updatedControls[schemaCtrl.id] = { ...ctrlState, selectedOptions: filtered };
              }
            }
          }
        }

        if (toggleOn && optionId) {
          for (const schemaCtrl of allSchemaControls) {
            if (schemaCtrl.id === controlId) continue;
            const ctrlState = updatedControls[schemaCtrl.id];
            if (!ctrlState) continue;
            if (typeof ctrlState.selectedOptions === 'string') {
              const match = (schemaCtrl.options ?? []).find((o) => o.id === optionId || o.id.includes(optionId));
              if (match) {
                updatedControls[schemaCtrl.id] = { ...ctrlState, selectedOptions: match.id };
              }
            } else if (Array.isArray(ctrlState.selectedOptions)) {
              const matchingOpts = (schemaCtrl.options ?? [])
                .filter((o) => o.id === optionId || o.id.includes(optionId))
                .map((o) => o.id);
              if (matchingOpts.length > 0) {
                const merged = Array.from(new Set([...ctrlState.selectedOptions, ...matchingOpts]));
                updatedControls[schemaCtrl.id] = { ...ctrlState, selectedOptions: merged };
              }
            }
          }
        }
        return { ...current, controls: updatedControls };
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
        {schema.sections.map((section) => <Section key={section.id} section={section} state={state} actions={actions} schema={schema} />)}
      </div>
    </main>
  );
}
