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
  if (meetsConditions(state, control.hides)) return null;
  const controlState = state.controls[control.id];
  const disabled = meetsConditions(state, control.disables);
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
        <strong>{control.id}</strong>
        {controlHasSelection(control, state) && (
          <Weight
            label={control.id}
            value={controlState.weight}
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
                {checked && <Submenu
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
                  <Submenu
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
