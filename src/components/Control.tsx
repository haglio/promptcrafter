import type { ReactNode } from 'react';
import { isHidden, isDisabled, isSubjectPlural, controlHasAtLeastOneSelectedOption, getDisplayOptionText, getDisplayItemText } from '../lib/utlities';
import type { State, Control, Schema } from '../types';
import { Actions } from './types';
import { Weight } from './Weight';
import { Submenu } from './Submenu';

function renderCheckboxOptions({
  control,
  state,
  actions,
  disabled,
  schema,
  disableIndividualOptions = false,
}: {
  control: Control;
  state: State;
  actions: Actions;
  disabled: boolean;
  schema: Schema;
  disableIndividualOptions?: boolean;
}) {
  const controlState = state.controls[control.id];
  if (!controlState) return null;
  const isPlural = isSubjectPlural(state);

  return (control.options ?? []).map((option) => {
    if (isHidden(state, option.hiddenBys, option.revealedBys)) return null;
    const optionDisabled =
      disabled ||
      disableIndividualOptions ||
      isDisabled(state, option.disabledBys);
    const checked = Array.isArray(controlState.selectedOptions) && controlState.selectedOptions.includes(option.id);

    return (
      <div key={option.id} className="option-stack">
        <label className="inline-control">
          <input
            type="checkbox"
            checked={checked}
            disabled={optionDisabled}
            onChange={() => actions.toggleCheck(control.id, option.id)}
          />
          <span>{getDisplayOptionText(option, isPlural, schema, state)}</span>
        </label>
        {checked && (
          <Submenu
            parentControlId={control.id}
            option={option}
            state={state}
            actions={actions}
            schema={schema}
          />
        )}
      </div>
    );
  });
}

function ControlHeader({
  control,
  state,
  actions,
  schema,
}: {
  control: Control;
  state: State;
  actions: Actions;
  schema: Schema;
}) {
  const controlState = state.controls[control.id];
  if (!controlState) return null;
  const controlLabel = getDisplayItemText(control, isSubjectPlural(state), schema, state);

  return (
    <div className="control-header">
      <strong>{controlLabel}</strong>
      {controlHasAtLeastOneSelectedOption(control, state) && control.kind !== 'or-prefix' && (
        <Weight
          value={controlState.weight}
          disabled={false}
          onChange={(value) => actions.setControlWeight(control.id, value)}
        />
      )}
    </div>
  );
}

function ToggleControl({
  control,
  state,
  actions,
  disabled,
  schema,
}: {
  control: Control;
  state: State;
  actions: Actions;
  disabled: boolean;
  schema: Schema;
}) {
  const controlState = state.controls[control.id];
  if (!controlState) return null;
  const controlLabel = getDisplayItemText(control, isSubjectPlural(state), schema, state);
  const checked = Array.isArray(controlState.selectedOptions)
    ? controlState.selectedOptions.length > 0
    : Boolean(controlState.selectedOptions);
  const hasOptionList = (control.options?.length ?? 0) > 1 && Array.isArray(controlState.selectedOptions);

  return (
    <div className="option-group">
      <label className="inline-control toggle-switch">
        <input
          type="checkbox"
          aria-label={controlLabel}
          checked={checked}
          disabled={disabled}
          onChange={(event) => actions.setToggle(control.id, event.target.checked)}
        />
        <span className="toggle-track" />
      </label>
      {checked && hasOptionList ? renderCheckboxOptions({ control, state, actions, disabled, schema }) : null}
    </div>
  );
}

function RadioControl({
  control,
  state,
  actions,
  disabled,
  schema,
}: {
  control: Control;
  state: State;
  actions: Actions;
  disabled: boolean;
  schema: Schema;
}) {
  const controlState = state.controls[control.id];
  if (!controlState) return null;
  const isPlural = isSubjectPlural(state);

  return (
    <div className="option-group">
      {(control.options ?? []).map((option) => {
        if (isHidden(state, option.hiddenBys, option.revealedBys)) return null;
        const optionDisabled = disabled || isDisabled(state, option.disabledBys);
        const checked = controlState.selectedOptions === option.id;
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
              <span>{getDisplayOptionText(option, isPlural, schema, state)}</span>
            </label>
            {checked && <Submenu
              parentControlId={control.id}
              option={option}
              state={state}
              actions={actions}
              schema={schema}
            />}
          </div>
        );
      })}
    </div>
  );
}

function GlobalSelectorControl({
  control,
  state,
  actions,
  disabled,
  schema,
}: {
  control: Control;
  state: State;
  actions: Actions;
  disabled: boolean;
  schema: Schema;
}) {
  const controlState = state.controls[control.id];
  if (!controlState) return null;
  const controlLabel = getDisplayItemText(control, isSubjectPlural(state), schema, state);
  const isOn = controlState.selectedOptions !== false;
  const selectedOption = isOn ? (controlState.selectedOptions as string) : '';
  const isPlural = isSubjectPlural(state);

  return (
    <div className="option-group">
      <label className="inline-control toggle-switch">
        <input
          type="checkbox"
          aria-label={controlLabel}
          checked={isOn}
          disabled={disabled}
          onChange={(event) => actions.setGlobalSelector(control.id, event.target.checked, selectedOption)}
        />
        <span className="toggle-track" />
      </label>
      {isOn && (
        <div className="global-selector-options">
          {(control.options ?? []).map((option) => {
            if (isHidden(state, option.hiddenBys, option.revealedBys)) return null;
            const optionDisabled = disabled || isDisabled(state, option.disabledBys);
            const checked = selectedOption === option.id;
            return (
              <label key={option.id} className="inline-control">
                <input
                  type="radio"
                  name={control.id}
                  aria-label={getDisplayOptionText(option, isPlural, schema, state)}
                  checked={checked}
                  disabled={optionDisabled}
                  onClick={() => {
                    if (checked) {
                      actions.setGlobalSelector(control.id, true, '');
                    } else {
                      actions.setGlobalSelector(control.id, true, option.id);
                    }
                  }}
                  readOnly
                />
                <span>{getDisplayOptionText(option, isPlural, schema, state)}</span>
              </label>
            );
          })}
        </div>
      )}
    </div>
  );
}

function CheckboxControl({
  control,
  state,
  actions,
  disabled,
  schema,
}: {
  control: Control;
  state: State;
  actions: Actions;
  disabled: boolean;
  schema: Schema;
}) {
  const controlState = state.controls[control.id];
  if (!controlState) return null;

  return (
    <div className="option-group">
      {renderCheckboxOptions({
        control,
        state,
        actions,
        disabled,
        schema,
        disableIndividualOptions: control.kind === 'required',
      })}
    </div>
  );
}

export function Control({
  control,
  state,
  actions,
  schema,
  noTopBorder = false
}: {
  control: Control;
  state: State;
  actions: Actions;
  schema: Schema;
  noTopBorder?: boolean;
}) {
  const hidden = control.kind === 'hidden-opposite' || isHidden(state, control.hiddenBys, control.revealedBys);
  if (hidden) return null;

  const controlState = state.controls[control.id];
  if (!controlState) return null;

  const disabled = isDisabled(state, control.disabledBys);

  const controlComponentKind = control.kind === 'toggle' ? 'toggle' : control.kind === 'global-selector' ? 'global-selector' : control.kind.startsWith('or') ? 'radio' : 'checkbox';

  let controlComponent: ReactNode = null;
  switch (controlComponentKind) {
    case 'toggle':
      controlComponent = <ToggleControl control={control} state={state} actions={actions} disabled={disabled} schema={schema} />;
      break;
    case 'global-selector':
      controlComponent = <GlobalSelectorControl control={control} state={state} actions={actions} disabled={disabled} schema={schema} />;
      break;
    case 'radio':
      controlComponent = <RadioControl control={control} state={state} actions={actions} disabled={disabled} schema={schema} />;
      break;
    case 'checkbox':
      controlComponent = <CheckboxControl control={control} state={state} actions={actions} disabled={disabled} schema={schema} />;
      break;
  }

  return (
    <div className={`control ${disabled ? 'disabled' : ''} ${noTopBorder ? 'no-top-border' : ''}`}>
      <ControlHeader control={control} state={state} actions={actions} schema={schema} />
      {controlComponent}
    </div>
  );
}
