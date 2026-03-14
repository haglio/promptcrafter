import { isHidden, isDisabled, isSubjectPlural, controlHasAtLeastOneSelectedOption, getOptionText } from '../lib/utlities';
import type { State, Control } from '../types';
import { Actions } from './types';
import { Weight } from './Weight';
import { Submenu } from './Submenu';

function ControlHeader({
  control,
  state,
  actions,
}: {
  control: Control;
  state: State;
  actions: Actions;
}) {
  const controlState = state.controls[control.text];
  if (!controlState) return null;

  return (
    <div className="control-header">
      <strong>{control.text}</strong>
      {controlHasAtLeastOneSelectedOption(control, state) && control.kind !== 'or-prefix' && (
        <Weight
          value={controlState.weight}
          disabled={false}
          onChange={(value) => actions.setControlWeight(control.text, value)}
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
}: {
  control: Control;
  state: State;
  actions: Actions;
  disabled: boolean;
}) {
  const controlState = state.controls[control.text];
  if (!controlState) return null;

  return (
    <div className="option-group">
      <label className="inline-control toggle-switch">
        <input
          type="checkbox"
          aria-label={control.text}
          checked={controlState.selectedOptions as boolean}
          disabled={disabled}
          onChange={(event) => actions.setToggle(control.text, event.target.checked)}
        />
        <span className="toggle-track" />
      </label>
    </div>
  );
}

function RadioControl({
  control,
  state,
  actions,
  disabled,
}: {
  control: Control;
  state: State;
  actions: Actions;
  disabled: boolean;
}) {
  const controlState = state.controls[control.text];
  if (!controlState) return null;
  const isPlural = isSubjectPlural(state);

  return (
    <div className="option-group">
      {(control.options ?? []).map((option) => {
        if (isHidden(state, option.hiddenBys)) return null;
        const optionDisabled = disabled || isDisabled(state, option.disabledBys);
        const checked = controlState.selectedOptions === option.text;
        return (
          <div key={option.text} className="option-stack">
            <label className="inline-control">
              <input
                type="radio"
                name={control.text}
                checked={checked}
                disabled={optionDisabled}
                onClick={() => {
                  if (checked) {
                    actions.setRadio(control.text, '');
                  } else {
                    actions.setRadio(control.text, option.text);
                  }
                }}
                readOnly
              />
              <span>{getOptionText(option, isPlural)}</span>
            </label>
            {checked && <Submenu
              parentControlText={control.text}
              option={option}
              state={state}
              actions={actions}
            />}
          </div>
        );
      })}
    </div>
  );
}

function CheckboxControl({
  control,
  state,
  actions,
  disabled,
}: {
  control: Control;
  state: State;
  actions: Actions;
  disabled: boolean;
}) {
  const controlState = state.controls[control.text];
  if (!controlState) return null;
  const isPlural = isSubjectPlural(state);

  return (
    <div className="option-group">
      {(control.options ?? []).map((option) => {
        if (isHidden(state, option.hiddenBys)) return null;
        const optionDisabled =
          disabled ||
          control.kind === 'required' ||
          isDisabled(state, option.disabledBys);
        const checked = (controlState.selectedOptions as string[]).includes(option.text);

        return (
          <div key={option.text} className="option-stack">
            <label className="inline-control">
              <input
                type="checkbox"
                checked={checked}
                disabled={optionDisabled}
                onChange={() => actions.toggleCheck(control.text, option.text)}
              />
              <span>{getOptionText(option, isPlural)}</span>
            </label>
            {checked && (
              <Submenu
                parentControlText={control.text}
                option={option}
                state={state}
                actions={actions}
              />
            )}
          </div>
        );
      })}
    </div>
  );
}

export function Control({
  control,
  state,
  actions,
  noTopBorder = false
}: {
  control: Control;
  state: State;
  actions: Actions;
  noTopBorder?: boolean;
}) {
  const hidden = isHidden(state, control.hiddenBys);
  if (hidden) return null;

  const controlState = state.controls[control.text];
  if (!controlState) return null;

  const disabled = isDisabled(state, control.disabledBys);

  const controlComponentKind = control.kind === 'toggle' ? 'toggle' : control.kind.startsWith('or') ? 'radio' : 'checkbox';

  let controlComponent: JSX.Element | null = null;
  switch (controlComponentKind) {
    case 'toggle':
      controlComponent = <ToggleControl control={control} state={state} actions={actions} disabled={disabled} />;
      break;
    case 'radio':
      controlComponent = <RadioControl control={control} state={state} actions={actions} disabled={disabled} />;
      break;
    case 'checkbox':
      controlComponent = <CheckboxControl control={control} state={state} actions={actions} disabled={disabled} />;
      break;
  }

  return (
    <div className={`control ${disabled ? 'disabled' : ''} ${noTopBorder ? 'no-top-border' : ''}`}>
      <ControlHeader control={control} state={state} actions={actions} />
      {controlComponent}
    </div>
  );
}
