import { getOptionText, meetsConditions, submenuStateKey, isSubjectPlural, buildSectionPrompt } from '../lib/promptBuilder';
import type { BuilderState, ControlDefinition, OptionDefinition, Schema, SectionDefinition } from '../lib/types';

type Actions = {
  setSectionWeight: (sectionId: string, weight: number) => void;
  setControlWeight: (controlId: string, weight: number) => void;
  setRadio: (controlId: string, optionId: string) => void;
  toggleCheck: (controlId: string, optionId: string) => void;
  setToggle: (controlId: string, value: boolean) => void;
};

function WeightSlider({
  value,
  disabled,
  onChange,
}: {
  value: number;
  disabled: boolean;
  onChange: (value: number) => void;
}) {
  return (
    <div className="weight-slider">
      {value !== 1 && (
        <button
          type="button"
          className="weight-reset"
          onClick={() => onChange(1)}
          disabled={disabled}
        >
          ↺
        </button>
      )}

      <input
        type="range"
        min="0"
        max="5"
        step="0.1"
        value={value}
        disabled={disabled}
        onChange={(e) => onChange(Number.parseFloat(e.target.value))}
      />
    </div>
  );
}

function OptionSubmenu({
  parentControlId,
  option,
  state,
  actions,
}: {
  parentControlId: string;
  option: OptionDefinition;
  state: BuilderState;
  actions: Actions;
}) {
  if (!option.submenu) return null;
  const key = submenuStateKey(parentControlId, option.id);
  const submenuState = state.controls[key];
  const selectionMode = option.submenu.selectionMode ?? 'many';
  const isPlural = isSubjectPlural(state)

  return (
    <div className="submenu">
      <div className="submenu-option-group">
        {option.submenu.options.map((child) => {
          if (meetsConditions(state, child.hides)) return null;
          const disabled = meetsConditions(state, child.disables);

          if (selectionMode === 'one') {
            const checked = submenuState.selectedOptionId === child.id;
            return (
              <label key={child.id} className="inline-control">
                <input
                  type="radio"
                  name={key}
                  checked={checked}
                  disabled={disabled}
                  onClick={() => actions.setRadio(key, checked ? '' : child.id)}
                  readOnly
                />
                <span>{getOptionText(child, isPlural)}</span>
              </label>
            );
          }

          const checked = submenuState.checkedOptionIds.includes(child.id);
          return (
            <label key={child.id} className="inline-control">
              <input
                type="checkbox"
                checked={checked}
                disabled={disabled}
                onChange={() => actions.toggleCheck(key, child.id)}
              />
              <span>{getOptionText(child, isPlural)}</span>
            </label>
          );
        })}
      </div>
    </div>
  );
}

function sectionHasSelection(section: SectionDefinition, state: BuilderState) {
  return section.controls.some((control) => controlHasSelection(control, state));
}

function controlHasSelection(control: ControlDefinition, state: BuilderState) {
  const s = state.controls[control.id];

  if (control.kind === 'required') return true;
  if (control.kind === 'toggle') return s.toggleOn;

  if (control.kind.startsWith('or')) {
    return Boolean(s.selectedOptionId);
  }

  return s.checkedOptionIds.length > 0;
}

function ControlView({
  control,
  state,
  actions,
  parentWeighted = false,
  submenuSelectionMode,
}: {
  control: ControlDefinition;
  state: BuilderState;
  actions: Actions;
  parentWeighted?: boolean;
  submenuSelectionMode?: 'many' | 'one';
}) {
  if (meetsConditions(state, control.hides)) return null;
  const controlState = state.controls[control.id];
  const disabled = meetsConditions(state, control.disables);
  const weightDisabled = parentWeighted;
  const isSubmenuOverride = submenuSelectionMode !== undefined;
  const isRadio = isSubmenuOverride
    ? submenuSelectionMode === 'one'
    : control.kind.startsWith('or');
  const isCheckboxList = isSubmenuOverride
    ? submenuSelectionMode === 'many' || control.kind === 'required'
    : control.kind.startsWith('and') || control.kind === 'required';
  const isPlural = isSubjectPlural(state)

  return (
    <div className={`control ${disabled ? 'disabled' : ''}`}>
      <div className="control-header">
        <strong>{control.id}</strong>
        {controlHasSelection(control, state) && (
          <WeightSlider
            label={control.id}
            value={controlState.weight}
            disabled={weightDisabled}
            onChange={(value) => actions.setControlWeight(control.id, value)}
          />
        )}
      </div>

      {control.kind === 'toggle' && (
        <div className="option-group">
          <label className="inline-control toggle-switch">
            <input
              type="checkbox"
              aria-label={control.id}
              checked={controlState.toggleOn}
              disabled={disabled}
              onChange={(event) => actions.setToggle(control.id, event.target.checked)}
            />
            <span className="toggle-track" />
          </label>
        </div>
      )}

      {isRadio && (
        <div className="option-group">
          {(control.options ?? []).map((option) => {
            if (meetsConditions(state, option.hides)) return null;
            const optionDisabled = disabled || meetsConditions(state, option.disables);
            const checked = controlState.selectedOptionId === option.id;
            return (
              <div key={option.id} className="option-stack">
                <label className="inline-control">
                  <input
                    type="radio"
                    name={control.id}
                    checked={checked}
                    disabled={optionDisabled}
                    onClick={() => {
                      if (checked) {
                        actions.setRadio(control.id, '');
                      } else {
                        actions.setRadio(control.id, option.id);
                      }
                    }}
                    readOnly
                  />
                  <span>{getOptionText(option, isPlural)}</span>
                </label>
                {checked && <OptionSubmenu
                  parentControlId={control.id}
                  option={option}
                  state={state}
                  actions={actions}
                />}
              </div>
            );
          })}
        </div>
      )}

      {isCheckboxList && (
        <div className="option-group">
          {(control.options ?? []).map((option) => {
            if (meetsConditions(state, option.hides)) return null;
            const optionDisabled =
              disabled ||
              control.kind === 'required' ||
              meetsConditions(state, option.disables);
            const checked = controlState.checkedOptionIds.includes(option.id);

            return (
              <div key={option.id} className="option-stack">
                <label className="inline-control">
                  <input
                    type="checkbox"
                    checked={checked}
                    disabled={optionDisabled}
                    onChange={() => actions.toggleCheck(control.id, option.id)}
                  />
                  <span>{getOptionText(option, isPlural)}</span>
                </label>
                {checked && (
                  <OptionSubmenu
                    parentControlId={control.id}
                    option={option}
                    state={state}
                    actions={actions}
                  />
                )}
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
}

export function SectionView({
  section,
  state,
  actions,
  schema,
}: {
  section: SectionDefinition;
  state: BuilderState;
  actions: Actions;
  schema: Schema;
}) {
  if (meetsConditions(state, section.hides)) return null;
  const disabled = meetsConditions(state, section.disables);
  const sectionWeight = state.sections[section.id].weight;
  const sectionPrompt = buildSectionPrompt(schema, state, section.promptTarget ?? 'positive', section.id);

  return (
    <section className={`section ${disabled ? 'disabled' : ''}`}>
      <div className="section-header">
        <h2>{section.id}</h2>
        <div className="section-header-actions">
          {sectionPrompt && (
            <button type="button" onClick={() => navigator.clipboard.writeText(sectionPrompt)}>
              Copy
            </button>
          )}
          {sectionHasSelection(section, state) && (
            <WeightSlider
              value={sectionWeight}
              disabled={false}
              onChange={(value) => actions.setSectionWeight(section.id, value)}
            />
          )}
        </div>
      </div>
      {section.controls.map((control) => <ControlView key={control.id} control={control} state={state} actions={actions} parentWeighted={sectionWeight > 1} />)}
    </section>
  );
}