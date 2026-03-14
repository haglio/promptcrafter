import { isHidden, isDisabled, getOptionText, isSubjectPlural, submenuStateKey } from '../lib/utlities';
import type { State, Option } from '../types';
import type { Actions } from './types';

function SubmenuRadio({
  parentControlText,
  option,
  state,
  actions,
}: {
  parentControlText: string;
  option: Option;
  state: State;
  actions: Actions;
}) {
  if (!option.submenu) return null;
  const key = submenuStateKey(parentControlText, option.text);
  const submenuState = state.controls[key];
  if (!submenuState) return null;
  const isPlural = isSubjectPlural(state);

  return (
    <div className="submenu">
      <div className="submenu-option-group">
        {option.submenu.options.map((child) => {
          const hidden = isHidden(state, child.hiddenBys);
          if (hidden) return null;

          const disabled = isDisabled(state, child.disabledBys);
          const checked = submenuState.selectedOption === child.text;
          return (
            <label key={child.text} className="inline-control">
              <input
                type="radio"
                name={key}
                checked={checked}
                disabled={disabled}
                onClick={() => actions.setRadio(key, checked ? '' : child.text)}
                readOnly
              />
              <span>{getOptionText(child, isPlural)}</span>
            </label>
          );
        })}
      </div>
    </div>
  );
}

function SubmenuCheckbox({
  parentControlText,
  option,
  state,
  actions,
}: {
  parentControlText: string;
  option: Option;
  state: State;
  actions: Actions;
}) {
  if (!option.submenu) return null;
  const key = submenuStateKey(parentControlText, option.text);
  const submenuState = state.controls[key];
  if (!submenuState) return null;
  const isPlural = isSubjectPlural(state);

  return (
    <div className="submenu">
      <div className="submenu-option-group">
        {option.submenu.options.map((child) => {
          const hidden = isHidden(state, child.hiddenBys);
          if (hidden) return null;

          const disabled = isDisabled(state, child.disabledBys);
          const checked = submenuState.checkedOptions.includes(child.text);
          return (
            <label key={child.text} className="inline-control">
              <input
                type="checkbox"
                checked={checked}
                disabled={disabled}
                onChange={() => actions.toggleCheck(key, child.text)}
              />
              <span>{getOptionText(child, isPlural)}</span>
            </label>
          );
        })}
      </div>
    </div>
  );
}

export function Submenu({
  parentControlText,
  option,
  state,
  actions,
}: {
  parentControlText: string;
  option: Option;
  state: State;
  actions: Actions;
}) {
  if (!option.submenu) return null;
  const kind = option.submenu.kind;

  const discriminant = kind.startsWith('or') ? 'radio' : 'checkbox';

  switch (discriminant) {
    case 'radio':
      return <SubmenuRadio parentControlText={parentControlText} option={option} state={state} actions={actions} />;
    case 'checkbox':
      return <SubmenuCheckbox parentControlText={parentControlText} option={option} state={state} actions={actions} />;
  }
}
