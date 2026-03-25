import { useEffect, useMemo, useState } from 'react';
import { Prompt } from './components/Prompt';
import { Section } from './components/Section';
import { exportPromptCombo } from './lib/export';
import { buildPrompt } from './lib/prompt';
import { createInitialState } from './lib/state';
import { getToggleSelectionsForNextState } from './lib/toggle-state';
import type { Schema, State } from './types';

function ExportDialog({
  initialName,
  onCancel,
  onSave,
  pending,
  error,
}: {
  initialName: string;
  onCancel: () => void;
  onSave: (name: string) => Promise<void>;
  pending: boolean;
  error: string;
}) {
  const [name, setName] = useState(initialName);

  async function handleSubmit(event: React.FormEvent<HTMLFormElement>) {
    event.preventDefault();
    await onSave(name);
  }

  return (
    <div className="dialog-backdrop" role="presentation">
      <div className="dialog-card" role="dialog" aria-modal="true" aria-labelledby="export-dialog-title">
        <form onSubmit={handleSubmit}>
          <h2 id="export-dialog-title">Export prompt combo</h2>
          <p className="dialog-copy">Choose the JSON filename for the current positive and negative prompts.</p>
          <label className="dialog-field">
            <span>File name</span>
            <input
              autoFocus
              type="text"
              value={name}
              onChange={(event) => setName(event.target.value)}
              placeholder="my prompt combo"
              disabled={pending}
            />
          </label>
          {error ? <p className="dialog-error" role="alert">{error}</p> : null}
          <div className="dialog-actions">
            <button type="button" className="secondary-button" onClick={onCancel} disabled={pending}>
              Cancel
            </button>
            <button type="submit" className="primary-button" disabled={pending || !name.trim()}>
              {pending ? 'Saving...' : 'Save export'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}

export default function App({ schema }: {schema: Schema}) {
  const [state, setState] = useState<State>(() => {
    const initial = createInitialState(schema);
    return {
      ...initial,
      positiveText: buildPrompt(schema, initial, 'positive'),
      negativeText: buildPrompt(schema, initial, 'negative'),
    };
  });
  const [isExportDialogOpen, setIsExportDialogOpen] = useState(false);
  const [exportPending, setExportPending] = useState(false);
  const [exportError, setExportError] = useState('');
  const [exportMessage, setExportMessage] = useState('');
  const schemaControls = useMemo(() => schema.sections.flatMap((section) => section.controls), [schema]);

  const generated = useMemo(() => ({
    positive: buildPrompt(schema, state, 'positive'),
    negative: buildPrompt(schema, state, 'negative'),
  }), [schema, state]);

  const defaultExportName = useMemo(() => {
    const source = `${state.positiveText} ${state.negativeText}`.trim();
    if (!source) return 'prompt-combo';

    const compact = source
      .toLowerCase()
      .replace(/[^a-z0-9]+/g, '-')
      .replace(/^-+|-+$/g, '')
      .slice(0, 48);

    return compact || 'prompt-combo';
  }, [state.negativeText, state.positiveText]);

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

  async function handleExportSave(name: string) {
    try {
      setExportPending(true);
      setExportError('');

      const result = await exportPromptCombo(name, {
        positive: state.positiveText,
        negative: state.negativeText,
      });

      setExportMessage(`Saved ${result.fileName}`);
      setIsExportDialogOpen(false);
    } catch (error) {
      setExportError(error instanceof Error ? error.message : 'Export failed.');
    } finally {
      setExportPending(false);
    }
  }

  const actions = {
    setSectionWeight(sectionId: string, weight: number) {
      setState((current) => ({ ...current, sections: { ...current.sections, [sectionId]: { weight } } }));
    },
    setControlWeight(controlId: string, weight: number) {
      setState((current) => {
        const control = current.controls[controlId];
        if (!control) return current;
        return {
          ...current,
          controls: { ...current.controls, [controlId]: { selectedOptions: control.selectedOptions, enabled: control.enabled, weight } },
        };
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
              enabled: control.enabled,
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
        const schemaControl = schemaControls.find((entry) => entry.id === controlId);
        if (!schemaControl || schemaControl.kind !== 'toggle') return current;

        const selectedOptions = getToggleSelectionsForNextState(schemaControl, control, value);

        return {
          ...current,
          controls: { ...current.controls, [controlId]: { selectedOptions, enabled: value, weight: control.weight } },
        };
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
        const allSchemaControls = schemaControls;

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
      <header className="app-header">
        <h1>PromptCrafter</h1>
        <div className="app-header-actions">
          {exportMessage ? <p className="export-message" role="status">{exportMessage}</p> : null}
          <button
            type="button"
            className="primary-button"
            onClick={() => {
              setExportMessage('');
              setExportError('');
              setIsExportDialogOpen(true);
            }}
          >
            Export JSON
          </button>
        </div>
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

      {isExportDialogOpen ? (
        <ExportDialog
          initialName={defaultExportName}
          onCancel={() => {
            if (exportPending) return;
            setExportError('');
            setIsExportDialogOpen(false);
          }}
          onSave={handleExportSave}
          pending={exportPending}
          error={exportError}
        />
      ) : null}
    </main>
  );
}
