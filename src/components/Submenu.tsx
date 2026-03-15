import { isHidden, isDisabled, getDisplayOptionText, isSubjectPlural, submenuStateKey } from '../lib/utlities';
import type { State, Option, Schema } from '../types';
import type { Actions } from './types';

function SubmenuRadio({
  parentControlId,
  option,
  state,
  actions,
  schema,
}: {
  parentControlId: string;
  option: Option;
  state: State;
  actions: Actions;
  schema: Schema;
}) {
  if (!option.submenu) return null;
  const key = submenuStateKey(parentControlId, option.id);
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
          const checked = submenuState.selectedOptions === child.id;
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
              <span>{getDisplayOptionText(child, isPlural, schema, state)}</span>
            </label>
          );
        })}
      </div>
    </div>
  );
}

function SubmenuCheckbox({
  parentControlId,
  option,
  state,
  actions,
  schema,
}: {
  parentControlId: string;
  option: Option;
  state: State;
  actions: Actions;
  schema: Schema;
}) {
  if (!option.submenu) return null;
  const key = submenuStateKey(parentControlId, option.id);
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
          const checked = (submenuState.selectedOptions as string[]).includes(child.id);
          return (
            <label key={child.id} className="inline-control">
              <input
                type="checkbox"
                checked={checked}
                disabled={disabled}
                onChange={() => actions.toggleCheck(key, child.id)}
              />
              <span>{getDisplayOptionText(child, isPlural, schema, state)}</span>
            </label>
          );
        })}
      </div>
    </div>
  );
}

export function Submenu({
  parentControlId,
  option,
  state,
  actions,
  schema,
}: {
  parentControlId: string;
  option: Option;
  state: State;
  actions: Actions;
  schema: Schema;
}) {
  if (!option.submenu) return null;
  const kind = option.submenu.kind;

  const discriminant = kind.startsWith('or') ? 'radio' : 'checkbox';

  switch (discriminant) {
    case 'radio':
      return <SubmenuRadio parentControlId={parentControlId} option={option} state={state} actions={actions} schema={schema} />;
    case 'checkbox':
      return <SubmenuCheckbox parentControlId={parentControlId} option={option} state={state} actions={actions} schema={schema} />;
  }
}
