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
  const key = submenuStateKey(parentControlId, option.text);
  const submenuState = state.controls[key];
  const kind = option.submenu.kind ?? 'and';
  const isPlural = isSubjectPlural(state)

  return (
    <div className="submenu">
      <div className="submenu-option-group">
        {option.submenu.options.map((child) => {
          if (meetsConditions(state, child.hiddenBys)) return null;
          const disabled = meetsConditions(state, child.disabledBys);

          if (kind === 'or') {
            const checked = submenuState.selectedOptionId === child.text;
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
          }

          const checked = submenuState.checkedOptionIds.includes(child.text);
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
