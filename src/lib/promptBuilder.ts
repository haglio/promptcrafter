import type { BuilderState, Condition, ControlDefinition, OptionDefinition, Schema, PromptTarget, SectionDefinition } from './types';

function selected(state: BuilderState, controlId: string, optionId?: string): boolean {
  const control = state.controls[controlId];
  if (!control) return false;
  if (optionId) return control.selectedOptionId === optionId || control.checkedOptionIds.includes(optionId);
  return Boolean(control.selectedOptionId) || control.checkedOptionIds.length > 0 || control.toggleOn;
}

export function meetsConditions(state: BuilderState, conditions?: Condition[]): boolean {
  if (!conditions || conditions.length === 0) return false;
  return conditions.some((condition) => {
    if (condition.type === 'toggle-on') return state.controls[condition.controlId]?.toggleOn ?? false;
    return selected(state, condition.controlId, condition.optionId);
  });
}

function isHidden(state: BuilderState, node: { hides?: Condition[] }): boolean {
  return meetsConditions(state, node.hides);
}

function isDisabled(state: BuilderState, node: { disables?: Condition[] }): boolean {
  return meetsConditions(state, node.disables);
}

function applyWeight(text: string, weight: number): string {
  if (!text.trim()) return '';
  const rounded = Math.round(weight * 10) / 10;
  return rounded === 1 ? text : `(${text}:${rounded.toFixed(1)})`;
}

function joinParts(parts: string[]): string {
  return parts.filter(Boolean).join(', ').replace(/\s+,/g, ',').replace(/,\s*,/g, ', ').trim().replace(/,$/, '');
}

function optionById(control: ControlDefinition, id?: string): OptionDefinition | undefined {
  return control.options?.find((option) => option.id === id);
}

export function submenuStateKey(parentControlId: string, optionId: string) {
  return `${parentControlId}__${optionId}__submenu`;
}

function renderSubmenu(parentControlId: string, option: OptionDefinition, state: BuilderState): string {
  if (!option.submenu) return '';

  const key = submenuStateKey(parentControlId, option.id);
  const submenuState = state.controls[key];
  if (!submenuState) return '';

  const checked = option.submenu.options.filter(
    (child) =>
      submenuState.checkedOptionIds.includes(child.id) &&
      !isHidden(state, child) &&
      !isDisabled(state, child),
  );
  if (checked.length > 0) return checked.map((child) => child.id).join(' ');

  const selected = option.submenu.options.find(
    (child) =>
      child.id === submenuState.selectedOptionId &&
      !isHidden(state, child) &&
      !isDisabled(state, child),
  );
  return selected?.id ?? '';
}

function renderOptionWithModifiers(parentControlId: string, option: OptionDefinition, state: BuilderState): string {
  const modifierText = renderSubmenu(parentControlId, option, state);
  const placement = option.submenu?.placement ?? 'before';
  const isPlural = isSubjectPlural(state)
  const optionText = getOptionText(option, isPlural)
  if (!modifierText) return optionText;
  return placement === 'after' ? `${optionText} ${modifierText}` : `${modifierText} ${optionText}`;
}

function firstRenderedPart(control: ControlDefinition, state: BuilderState, parentWeighted = false): string {
  return renderControl(control, state, parentWeighted)[0] ?? '';
}

function renderControl(control: ControlDefinition, state: BuilderState, parentWeighted = false): string[] {
  if (isHidden(state, control)) return [];
  const controlState = state.controls[control.id];
  if (!controlState) return [];
  const disabled = isDisabled(state, control);
  const ownWeight = parentWeighted ? 1 : controlState.weight;

  if (control.kind === 'toggle') {
    if (!controlState.toggleOn || disabled) return [];
    const base = control.options?.[0]?.id ?? control.id; // don't think I ever need plural here; only id
    return [applyWeight(base, ownWeight)];
  }
  if (control.kind === 'required') {
    const base = control.options?.[0]?.id ?? control.id; // don't think I ever need plural here; only id
    return [applyWeight(base, ownWeight)];
  }

  const radioKinds = new Set(['or', 'or-leading-title-if-non-empty', 'or-trailing-title-if-non-empty', 'or-no-comma-prefix-of-next']);
  if (radioKinds.has(control.kind)) {
    const option = optionById(control, disabled ? undefined : controlState.selectedOptionId);
    if (!option || isHidden(state, option) || isDisabled(state, option)) return [];
    let text = renderOptionWithModifiers(control.id, option, state);
    if (control.kind === 'or-leading-title-if-non-empty' && control.titleText) text = `${control.titleText} ${text}`;
    if (control.kind === 'or-trailing-title-if-non-empty' && control.titleText) text = `${text} ${control.titleText}`;
    const weighted = applyWeight(text, ownWeight);
    return weighted ? [weighted] : [];
  }

  const selectedOptions = (control.options ?? []).filter((option) => {
    if (isHidden(state, option) || isDisabled(state, option) || disabled) return false;
    return controlState.checkedOptionIds.includes(option.id);
  });
  if (selectedOptions.length === 0) return [];

  const optionValues = selectedOptions.map((option) => renderOptionWithModifiers(control.id, option, state));

  let combined = '';

  switch (control.kind) {
    case 'and-comma-separated':
      combined = optionValues.join(', ');
      break;
    case 'and-comma-leading-text':
      combined = optionValues
        .map((value) => `${control.leadingText ?? control.id} ${value}`)
        .join(', ');
      break;
    case 'and-space-separated':
      combined = optionValues.join(' ');
      break;
    case 'and-space-trailing-title-if-non-empty':
      combined = `${optionValues.join(' ')} ${control.titleText ?? control.id}`;
      break;
    default:
      combined = optionValues.join(', ');
  }

  const weightedCombined = applyWeight(combined.trim(), ownWeight);
  return [weightedCombined];
}

function renderSection(section: SectionDefinition, state: BuilderState, target: PromptTarget): string[] {
  if ((section.promptTarget ?? 'positive') !== target) return [];
  if (isHidden(state, section)) return [];

  const sectionWeighted = (state.sections[section.id]?.weight ?? 1) > 1;
  const parts: string[] = [];

  for (let i = 0; i < section.controls.length; i += 1) {
    const control = section.controls[i];

    if (control.kind === 'or-no-comma-prefix-of-next') {
      const prefix = firstRenderedPart(control, state, sectionWeighted);
      const next = section.controls[i + 1];

      if (!next) {
        if (prefix) parts.push(prefix);
        continue;
      }

      const nextRendered = firstRenderedPart(next, state, sectionWeighted);

      if (prefix && nextRendered) {
        parts.push(`${prefix} ${nextRendered}`);
        i += 1;
        continue;
      }

      if (prefix && !nextRendered && next.kind === 'or-trailing-title-if-non-empty' && next.titleText) {
        parts.push(`${prefix} ${next.titleText}`);
        i += 1;
        continue;
      }

      if (!prefix && nextRendered) {
        parts.push(nextRendered);
        i += 1;
        continue;
      }

      continue;
    }

    parts.push(...renderControl(control, state, sectionWeighted));
  }

  const filtered = parts.filter(Boolean);
  if (filtered.length === 0) return [];
  return [applyWeight(joinParts(filtered), state.sections[section.id]?.weight ?? 1)];
}

export function buildPrompt(schema: Schema, state: BuilderState, target: PromptTarget): string {
  return joinParts(schema.sections.flatMap((section) => renderSection(section, state, target)));
}

export function getOptionText(option: OptionDefinition, isPlural: boolean): string {
  return isPlural && option.plural ? option.plural : option.id
}

export function isSubjectPlural(state: BuilderState): boolean {
  return state.controls.count?.selectedOptionId == 'two'
}

export function buildSectionPrompt(
  schema: Schema,
  state: BuilderState,
  target: PromptTarget,
  sectionId: string,
): string {
  const section = schema.sections.find((s) => s.id === sectionId);
  if (!section) return '';
  return joinParts(renderSection(section, state, target));
}
