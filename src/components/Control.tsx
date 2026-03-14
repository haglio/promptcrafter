import { getOptionText, meetsConditions, isSubjectPlural, controlHasSelection } from '../lib/utlities';
import type { State, Control } from '../types';
import { Submenu } from './Submenu';
import { Actions } from './types';
import { Weight } from './Weight';

export function Control({
  control,
  state,
  actions,
  submenuKind,
}: {
  control: Control;
  state: State;
  actions: Actions;
  submenuKind?: 'and' | 'or';
}) {
  if (meetsConditions(state, control.hiddenBys)) return null;
  const controlState = state.controls[control.text];
  const disabled = meetsConditions(state, control.disabledBys);
  const isSubmenuOverride = submenuKind !== undefined;
  const isRadio = isSubmenuOverride
    ? submenuKind === 'or'
    : control.kind.startsWith('or');
  const isCheckboxList = isSubmenuOverride
    ? submenuKind === 'and' || control.kind === 'required'
    : control.kind.startsWith('and') || control.kind === 'required';
  const isPlural = isSubjectPlural(state)

  return (
    <div className={`control ${disabled ? 'disabled' : ''}`}>
      <div className="control-header">
        <strong>{control.text}</strong>
        {controlHasSelection(control, state) && (
          <Weight
            label={control.text}
            value={controlState.weight}
            onChange={(value) => actions.setControlWeight(control.text, value)}
          />
        )}
      </div>

      {control.kind === 'toggle' && (
        <div className="option-group">
          <label className="inline-control toggle-switch">
            <input
              type="checkbox"
              aria-label={control.text}
              checked={controlState.toggleOn}
              disabled={disabled}
              onChange={(event) => actions.setToggle(control.text, event.target.checked)}
            />
            <span className="toggle-track" />
          </label>
        </div>
      )}

      {isRadio && (
        <div className="option-group">
          {(control.options ?? []).map((option) => {
            if (meetsConditions(state, option.hiddenBys)) return null;
            const optionDisabled = disabled || meetsConditions(state, option.disabledBys);
            const checked = controlState.selectedOptionId === option.text;
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
                  parentControlId={control.text}
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
            if (meetsConditions(state, option.hiddenBys)) return null;
            const optionDisabled =
              disabled ||
              control.kind === 'required' ||
              meetsConditions(state, option.disabledBys);
            const checked = controlState.checkedOptionIds.includes(option.text);

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
                    parentControlId={control.text}
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
