import { getOptionText, isSubjectPlural, meetsConditions, submenuStateKey } from "../lib/utlities";
import type { State, Option } from "../types";
import type { Actions } from "./types";

export function Submenu({
  parentControlId,
  option,
  state,
  actions,
}: {
  parentControlId: string;
  option: Option;
  state: State;
  actions: Actions;
}) {
  if (!option.submenu) return null;
  const key = submenuStateKey(parentControlId, option.id);
  const submenuState = state.controls[key];
  const kind = option.submenu.kind ?? 'and';
  const isPlural = isSubjectPlural(state)

  return (
    <div className="submenu">
      <div className="submenu-option-group">
        {option.submenu.options.map((child) => {
          if (meetsConditions(state, child.hides)) return null;
          const disabled = meetsConditions(state, child.disables);

          if (kind === 'or') {
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
