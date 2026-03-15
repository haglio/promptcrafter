import { isHidden, isDisabled, sectionHasAtLeastOneSelectedOption, isSubjectPlural, getDisplayItemText } from "../lib/utlities";
import { buildSectionPrompt } from "../lib/prompt";
import type { State, Schema, Section } from "../types";
import { Control } from "./Control";
import type { Actions } from "./types";
import { Weight } from "./Weight";

function CopyButton({
  onClick,
  ariaLabel,
}: {
  onClick: () => void;
  ariaLabel: string;
}) {
  return (
    <button
      type="button"
      className="copy-button"
      aria-label={ariaLabel}
      onClick={onClick}
    >
      <svg viewBox="0 0 24 24" width="16" height="16" fill="currentColor" aria-hidden="true">
        <path d="M16 1H6a2 2 0 0 0-2 2v12h2V3h10V1zm3 4H10a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h9a2 2 0 0 0 2-2V7a2 2 0 0 0-2-2zm0 16H10V7h9v14z"/>
      </svg>
    </button>
  );
}

function SectionHeader({
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
  const sectionWeight = state.sections[section.text]?.weight ?? 1;
  const sectionPrompt = buildSectionPrompt(schema, state, section.promptTarget ?? 'positive', section.text);
  const sectionLabel = getDisplayItemText(section, isSubjectPlural(state), schema, state);

  return (
    <div className="section-header">
      <div>
        <CopyButton
          onClick={() => navigator.clipboard.writeText(sectionPrompt)}
          ariaLabel="Copy section"
        />
        <label className="section-label"><h3>{sectionLabel}</h3></label>
      </div>
      <div className="section-header-actions">
        {sectionHasAtLeastOneSelectedOption(section, state) && (
          <Weight
            value={sectionWeight}
            disabled={false}
            onChange={(value) => actions.setSectionWeight(section.text, value)}
          />
        )}
      </div>
    </div>
  );
}

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
  if (isHidden(state, section.hiddenBys)) return null;
  const disabled = isDisabled(state, section.disabledBys);

  return (
    <section className={`section ${disabled ? 'disabled' : ''}`}>
      <SectionHeader section={section} state={state} actions={actions} schema={schema} />
      {section.controls.map((control, index) => (
        <Control
          key={control.text}
          control={control}
          state={state}
          actions={actions}
          schema={schema}
          noTopBorder={index === 0 || section.controls[index - 1]?.kind === 'or-prefix'}
        />
      ))}
    </section>
  );
}
