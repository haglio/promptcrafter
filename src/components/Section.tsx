import { buildSectionPrompt } from "../lib/prompt";
import { meetsConditions, sectionHasSelection } from "../lib/utlities";
import type { State, Schema, Section } from "../types";
import { Control } from "./Control";
import type { Actions } from "./types";
import { Weight } from "./Weight";

export function Section({
  section,
  state,
  actions,
  schema,
}: {
  section: Section;
  state: State;
  actions: Actions;
  schema: Schema;
}) {
  if (meetsConditions(state, section.hiddenBys)) return null;
  const disabled = meetsConditions(state, section.disabledBys);
  const sectionWeight = state.sections[section.text].weight;
  const sectionPrompt = buildSectionPrompt(schema, state, section.promptTarget ?? 'positive', section.text);

  return (
    <section className={`section ${disabled ? 'disabled' : ''}`}>
      <div className="section-header">
        <div>
          <button
            type="button"
            className="copy-button"
            aria-label="Copy section"
            onClick={() => navigator.clipboard.writeText(sectionPrompt)}
          >
            <svg viewBox="0 0 24 24" width="16" height="16" fill="currentColor" aria-hidden="true">
              <path d="M16 1H6a2 2 0 0 0-2 2v12h2V3h10V1zm3 4H10a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h9a2 2 0 0 0 2-2V7a2 2 0 0 0-2-2zm0 16H10V7h9v14z"/>
            </svg>
          </button>
          <label className="section-label"><h3>{section.text}</h3></label>
        </div>
        <div className="section-header-actions">
          {sectionHasSelection(section, state) && (
            <Weight
              value={sectionWeight}
              disabled={false}
              onChange={(value) => actions.setSectionWeight(section.text, value)}
            />
          )}
        </div>
      </div>
      {section.controls.map((control) => <Control key={control.text} control={control} state={state} actions={actions} parentWeighted={sectionWeight > 1} />)}
    </section>
  );
}
