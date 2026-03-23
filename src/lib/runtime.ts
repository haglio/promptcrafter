import type {
  BaseItem,
  Control,
  DisabledOrHiddenBy,
  GlobalSubstitution,
  Option,
  PromptTarget,
  Schema,
  Section,
  SupplementalText,
  SupplementedBy,
  State,
  TextReference,
  TextValue,
} from '../types';
import type { Segment } from './types';

type ResolutionStack = Set<string>;

function isTemplateTextValue(
  text: TextValue,
): text is {
  singular: import('../types').TextPart[];
  plural?: import('../types').TextPart[];
} {
  return typeof text !== 'string' && Array.isArray(text.singular);
}

function normalizeResolvedText(text: string): string {
  return text.replace(/\s+/g, ' ').trim();
}

function escapeRegex(source: string): string {
  return source.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
}

function replaceWholeWord(input: string, from: string, to: string): string {
  const trimmedFrom = from.trim();
  if (!trimmedFrom) return input;
  return input.replace(new RegExp(`\\b${escapeRegex(trimmedFrom)}\\b`, 'gi'), to);
}

export function isSubjectPlural(state: State): boolean {
  return state.controls.count?.selectedOptions == 'two';
}

export function controlHasAtLeastOneSelectedOption(control: Control, state: State) {
  const current = state.controls[control.id];
  if (!current) return false;

  if (control.kind === 'required') return true;
  if (control.kind === 'toggle') return hasAnySelection(current.selectedOptions);
  if (control.kind === 'global-selector') return current.selectedOptions !== false;
  if (control.kind.startsWith('or')) return Boolean(current.selectedOptions as string);

  return (current.selectedOptions as string[]).length > 0;
}

export function sectionHasAtLeastOneSelectedOption(section: Section, state: State) {
  return section.controls.some((control) => controlHasAtLeastOneSelectedOption(control, state));
}

export function submenuStateKey(parentControlId: string, optionId: string) {
  return `${parentControlId}__${optionId}__submenu`;
}

export function joinParts(parts: string[]): string {
  return parts
    .filter(Boolean)
    .join(', ')
    .replace(/\s+,/g, ',')
    .replace(/,\s*,/g, ', ')
    .trim()
    .replace(/,$/, '');
}

function hasAnySelection(selectedOptions: boolean | string | string[]): boolean {
  if (typeof selectedOptions === 'boolean') return selectedOptions;
  if (typeof selectedOptions === 'string') return Boolean(selectedOptions);
  return selectedOptions.length > 0;
}

function isOptionIdSelected(state: State, optionId: string): boolean {
  return Object.values(state.controls).some(({ selectedOptions }) => {
    if (typeof selectedOptions === 'string') return selectedOptions === optionId;
    if (Array.isArray(selectedOptions)) return selectedOptions.includes(optionId);
    return false;
  });
}

function isByConditionMatched(state: State, by: DisabledOrHiddenBy): boolean {
  if (!by.controlId) {
    return by.optionId ? isOptionIdSelected(state, by.optionId) : false;
  }

  const controlState = state.controls[by.controlId];
  if (!controlState) return false;

  const { selectedOptions } = controlState;

  if (!by.optionId) return hasAnySelection(selectedOptions);
  if (typeof selectedOptions === 'string') return selectedOptions === by.optionId;
  if (Array.isArray(selectedOptions)) return selectedOptions.includes(by.optionId);
  return false;
}

export function isTriggeredBy(state: State, conditions?: DisabledOrHiddenBy[]): boolean {
  if (!conditions || conditions.length === 0) return false;
  return conditions.some((condition) => isByConditionMatched(state, condition));
}

export function isDisabled(state: State, disabledBys?: DisabledOrHiddenBy[]): boolean {
  return isTriggeredBy(state, disabledBys);
}

export function isHidden(
  state: State,
  hiddenBys?: DisabledOrHiddenBy[],
  revealedBys?: DisabledOrHiddenBy[],
): boolean {
  if (isTriggeredBy(state, hiddenBys)) return true;
  if (!revealedBys || revealedBys.length === 0) return false;
  return !isTriggeredBy(state, revealedBys);
}

function findControl(schema: Schema, controlId: string): Control | undefined {
  for (const section of schema.sections) {
    const match = section.controls.find((control) => control.id === controlId);
    if (match) return match;
  }
  return undefined;
}

function findSection(schema: Schema, sectionId: string): Section | undefined {
  return schema.sections.find((section) => section.id === sectionId);
}

function findOption(schema: Schema, optionId: string): Option | undefined {
  for (const section of schema.sections) {
    for (const control of section.controls) {
      for (const option of control.options ?? []) {
        if (option.id === optionId) return option;
        const submenuOption = option.submenu?.options.find((child) => child.id === optionId);
        if (submenuOption) return submenuOption;
      }
    }
  }

  return undefined;
}

function resolveReferenceValue(
  reference: TextReference,
  isPlural: boolean,
  schema: Schema,
  state: State,
  stack: ResolutionStack,
): string {
  const key = `${reference.kind}:${reference.id}:${isPlural ? 'plural' : 'singular'}`;
  if (stack.has(key)) return '';

  const nextStack = new Set(stack);
  nextStack.add(key);

  if (reference.kind === 'option') {
    const option = findOption(schema, reference.id);
    return option ? getOptionText(option, isPlural, schema, state, nextStack) : '';
  }

  if (reference.kind === 'control') {
    const control = findControl(schema, reference.id);
    return control ? renderControlValue(control, schema, state, nextStack) : '';
  }

  const section = findSection(schema, reference.id);
  return section ? renderSectionValue(section, schema, state, nextStack) : '';
}

export function getTextValue(
  text: TextValue,
  isPlural: boolean,
  schema?: Schema,
  state?: State,
  stack: ResolutionStack = new Set(),
): string {
  if (typeof text === 'string') return text;

  if (isTemplateTextValue(text)) {
    if (!schema || !state) return '';

    const parts = isPlural ? text.plural ?? text.singular : text.singular;
    return normalizeResolvedText(
      parts
        .map((part) =>
          typeof part === 'string'
            ? part
            : resolveReferenceValue(part.ref, isPlural, schema, state, stack),
        )
        .join(''),
    );
  }

  return isPlural ? text.plural : text.singular;
}

export function getItemText(
  item: BaseItem,
  isPlural: boolean,
  schema?: Schema,
  state?: State,
  stack?: ResolutionStack,
): string {
  return getTextValue(item.text, isPlural, schema, state, stack);
}

export function getOptionText(
  option: Option,
  isPlural: boolean,
  schema?: Schema,
  state?: State,
  stack?: ResolutionStack,
): string {
  return getItemText(option, isPlural, schema, state, stack);
}

export function getActiveSubstitutions(schema: Schema, state: State): GlobalSubstitution[] {
  const substitutions: GlobalSubstitution[] = [];

  for (const section of schema.sections) {
    if (isHidden(state, section.hiddenBys, section.revealedBys) || isDisabled(state, section.disabledBys)) continue;

    for (const control of section.controls) {
      if (control.kind !== 'toggle') continue;
      if (isHidden(state, control.hiddenBys, control.revealedBys) || isDisabled(state, control.disabledBys)) continue;

      const enabled = hasAnySelection(state.controls[control.id]?.selectedOptions as boolean | string | string[]);
      if (!enabled) continue;

      substitutions.push(...(control.globalSubstitutions ?? []));
    }
  }

  return substitutions;
}

export function applySubstitutions(
  text: string,
  substitutions: GlobalSubstitution[],
  schema: Schema,
  state: State,
): string {
  let next = text;

  for (const substitution of substitutions) {
    const fromPlural = getTextValue(substitution.fromPlural ?? substitution.from, true, schema, state).trim();
    const toPlural = getTextValue(substitution.toPlural ?? substitution.to, true, schema, state).trim();
    const from = getTextValue(substitution.from, false, schema, state).trim();
    const to = getTextValue(substitution.to, false, schema, state).trim();

    if (fromPlural && toPlural) {
      next = replaceWholeWord(next, fromPlural, toPlural);
    }
    if (from && to) {
      next = replaceWholeWord(next, from, to);
    }
  }

  return next;
}

export function getDisplayItemText(item: BaseItem, isPlural: boolean, schema: Schema, state: State): string {
  return applySubstitutions(getItemText(item, isPlural, schema, state), getActiveSubstitutions(schema, state), schema, state);
}

export function getDisplayOptionText(option: Option, isPlural: boolean, schema: Schema, state: State): string {
  return applySubstitutions(getOptionText(option, isPlural, schema, state), getActiveSubstitutions(schema, state), schema, state);
}

export function getSupplementalTexts(
  schema: Schema,
  state: State,
  supplementedBys?: SupplementedBy[],
  stack: ResolutionStack = new Set(),
): SupplementalText[] {
  if (!supplementedBys || supplementedBys.length === 0) return [];

  const isPlural = isSubjectPlural(state);

  return supplementedBys
    .filter((supplementedBy) => {
      const hasControlId = Boolean(supplementedBy.controlId);
      const hasOptionId = Boolean(supplementedBy.optionId);

      if (hasControlId === hasOptionId) return false;
      if (supplementedBy.controlId) {
        return isByConditionMatched(state, { controlId: supplementedBy.controlId });
      }

      return isOptionIdSelected(state, supplementedBy.optionId as string);
    })
    .map((supplementedBy) => ({
      text: getTextValue(supplementedBy.supplementalText, isPlural, schema, state, stack).trim(),
      side: supplementedBy.side ?? 'adv',
    }))
    .filter((supplementedBy) => Boolean(supplementedBy.text));
}

function applyWeight(text: string, weight: number): string {
  if (!text.trim()) return '';
  const rounded = Math.round(weight * 10) / 10;
  return rounded === 1 ? text : `(${text}:${rounded.toFixed(1)})`;
}

function optionById(control: Control, id?: string): Option | undefined {
  return control.options?.find((option) => option.id === id);
}

function renderSubmenu(
  parentControlId: string,
  option: Option,
  schema: Schema,
  state: State,
  stack: ResolutionStack,
): string {
  if (!option.submenu) return '';

  const key = submenuStateKey(parentControlId, option.id);
  const submenuState = state.controls[key];
  if (!submenuState) return '';
  const isPlural = isSubjectPlural(state);

  const checked = option.submenu.options.filter(
    (child) =>
      (submenuState.selectedOptions as string[]).includes(child.id) &&
      !isHidden(state, child.hiddenBys, child.revealedBys) &&
      !isDisabled(state, child.disabledBys),
  );
  if (checked.length > 0) {
    return checked.map((child) => getOptionText(child, isPlural, schema, state, stack)).join(' ');
  }

  const selected = option.submenu.options.find(
    (child) =>
      child.id === (submenuState.selectedOptions as string) &&
      !isHidden(state, child.hiddenBys, child.revealedBys) &&
      !isDisabled(state, child.disabledBys),
  );

  return selected ? getOptionText(selected, isPlural, schema, state, stack) : '';
}

function renderOptionWithModifiers(
  parentControlId: string,
  option: Option,
  schema: Schema,
  state: State,
  stack: ResolutionStack,
): string {
  const modifierText = renderSubmenu(parentControlId, option, schema, state, stack);
  const isPlural = isSubjectPlural(state);
  const optionText = getOptionText(option, isPlural, schema, state, stack);
  if (!modifierText) return optionText;

  return option.submenu?.kind === 'and-adv' || option.submenu?.kind === 'or-adv'
    ? `${optionText} ${modifierText}`
    : `${modifierText} ${optionText}`;
}

function appendSupplements(
  baseText: string,
  control: Control,
  schema: Schema,
  state: State,
  stack: ResolutionStack,
): string {
  if (!baseText.trim()) return '';
  const supplementalTexts = getSupplementalTexts(schema, state, control.supplementedBys, stack);
  if (supplementalTexts.length === 0) return baseText;

  const prependTexts = supplementalTexts
    .filter((supplementalText) => supplementalText.side === 'adj')
    .map((supplementalText) => supplementalText.text);
  const appendTexts = supplementalTexts
    .filter((supplementalText) => supplementalText.side === 'adv')
    .map((supplementalText) => supplementalText.text);

  return [...prependTexts, baseText, ...appendTexts].join(' ');
}

function getControlText(
  control: Control,
  schema: Schema,
  state: State,
  option?: Option,
  stack: ResolutionStack = new Set(),
): string {
  const isPlural = isSubjectPlural(state);

  if (option?.customControlText) return getTextValue(option.customControlText, isPlural, schema, state, stack);
  if (control.customText) return getTextValue(control.customText, isPlural, schema, state, stack);

  return getTextValue(control.text, isPlural, schema, state, stack);
}

function firstRenderedPart(
  control: Control,
  schema: Schema,
  state: State,
  stack: ResolutionStack,
): Segment | undefined {
  return renderControlSegments(control, schema, state, stack)[0];
}

function mergeSegments(segments: Segment[]): Segment[] {
  const merged: Segment[] = [];

  for (const segment of segments) {
    if (!segment.text) continue;

    const previous = merged[merged.length - 1];
    if (previous && previous.weight === segment.weight) {
      previous.text = `${previous.text}, ${segment.text}`;
    } else {
      merged.push({ ...segment });
    }
  }

  return merged;
}

function effectiveWeight(sectionWeight: number, controlWeight: number): number {
  return controlWeight === 1 ? sectionWeight : controlWeight;
}

function renderControlSegments(
  control: Control,
  schema: Schema,
  state: State,
  stack: ResolutionStack = new Set(),
): Segment[] {
  if (isHidden(state, control.hiddenBys, control.revealedBys)) return [];

  const controlState = state.controls[control.id];
  if (!controlState) return [];

  const disabled = isDisabled(state, control.disabledBys);
  const ownWeight = controlState.weight;
  const isPlural = isSubjectPlural(state);

  if (control.kind === 'toggle') {
    if (disabled) return [];

    if (typeof controlState.selectedOptions === 'boolean') {
      if (!controlState.selectedOptions) return [];
      const base = control.options?.[0]
        ? getOptionText(control.options[0], isPlural, schema, state, stack)
        : getTextValue(control.text, isPlural, schema, state, stack);
      return [{ text: appendSupplements(base, control, schema, state, stack), weight: ownWeight }];
    }

    const selectedOptions = (control.options ?? []).filter((option) => {
      if (isHidden(state, option.hiddenBys, option.revealedBys) || isDisabled(state, option.disabledBys)) return false;
      return (controlState.selectedOptions as string[]).includes(option.id);
    });
    if (selectedOptions.length === 0) return [];

    const combined = selectedOptions
      .map((option) => renderOptionWithModifiers(control.id, option, schema, state, stack))
      .join(', ')
      .trim();

    const text = appendSupplements(combined, control, schema, state, stack);
    return text ? [{ text, weight: ownWeight }] : [];
  }

  if (control.kind === 'global-selector') {
    return [];
  }

  if (control.kind === 'required') {
    const selectedOptions = (control.options ?? []).filter((option) => {
      if (isHidden(state, option.hiddenBys, option.revealedBys) || isDisabled(state, option.disabledBys) || disabled) return false;
      return (controlState.selectedOptions as string[]).includes(option.id);
    });
    if (selectedOptions.length === 0) return [];

    const combined = selectedOptions
      .map((option) => renderOptionWithModifiers(control.id, option, schema, state, stack))
      .join(', ')
      .trim();

    const text = appendSupplements(combined, control, schema, state, stack);
    return text ? [{ text, weight: ownWeight }] : [];
  }

  if (control.kind === 'hidden-opposite') {
    if (!isTriggeredBy(state, control.hiddenOppositeBys) || disabled) return [];

    const selectedOptions = (control.options ?? []).filter((option) => {
      if (isHidden(state, option.hiddenBys, option.revealedBys) || isDisabled(state, option.disabledBys)) return false;
      return (controlState.selectedOptions as string[]).includes(option.id);
    });
    if (selectedOptions.length === 0) return [];

    const text = appendSupplements(
      selectedOptions.map((option) => renderOptionWithModifiers(control.id, option, schema, state, stack)).join(', ').trim(),
      control,
      schema,
      state,
      stack,
    );

    return text ? [{ text, weight: ownWeight }] : [];
  }

  const radioKinds = new Set(['or', 'or-adv', 'or-adj', 'or-prefix']);

  if (radioKinds.has(control.kind)) {
    const option = optionById(control, disabled ? undefined : (controlState.selectedOptions as string));
    if (!option || isHidden(state, option.hiddenBys, option.revealedBys) || isDisabled(state, option.disabledBys)) return [];

    let text = renderOptionWithModifiers(control.id, option, schema, state, stack);
    if (control.kind === 'or-adv') text = `${getControlText(control, schema, state, option, stack)} ${text}`;
    if (control.kind === 'or-adj') text = `${text} ${getControlText(control, schema, state, option, stack)}`;
    text = appendSupplements(text, control, schema, state, stack);
    return text ? [{ text, weight: ownWeight }] : [];
  }

  const selectedOptions = (control.options ?? []).filter((option) => {
    if (isHidden(state, option.hiddenBys, option.revealedBys) || isDisabled(state, option.disabledBys) || disabled) return false;
    return (controlState.selectedOptions as string[]).includes(option.id);
  });
  if (selectedOptions.length === 0) return [];

  const optionValues = selectedOptions.map((option) =>
    renderOptionWithModifiers(control.id, option, schema, state, stack),
  );

  let combined = '';
  switch (control.kind) {
    case 'and-commas':
      combined = optionValues.join(', ');
      break;
    case 'and-commas-adj':
      combined = selectedOptions
        .map((option, index) => `${optionValues[index]} ${getControlText(control, schema, state, option, stack)}`)
        .join(', ');
      break;
    case 'and-commas-adv':
      combined = selectedOptions
        .map((option, index) => `${getControlText(control, schema, state, option, stack)} ${optionValues[index]}`)
        .join(', ');
      break;
    case 'and-spaces-adj':
      combined = `${optionValues.join(' ')} ${getControlText(control, schema, state, selectedOptions[0], stack)}`;
      break;
    default:
      combined = optionValues.join(', ');
  }

  combined = appendSupplements(combined.trim(), control, schema, state, stack);
  return combined.trim() ? [{ text: combined.trim(), weight: ownWeight }] : [];
}

function buildSectionSegments(
  section: Section,
  schema: Schema,
  state: State,
  target: PromptTarget,
  stack: ResolutionStack = new Set(),
): Segment[] {
  if ((section.promptTarget ?? 'positive') !== target) return [];
  if (isHidden(state, section.hiddenBys, section.revealedBys)) return [];

  const sectionWeight = state.sections[section.id]?.weight ?? 1;
  const parts: Segment[] = [];

  for (let index = 0; index < section.controls.length; index += 1) {
    const control = section.controls[index];
    if (!control) continue;

    if (control.kind === 'or-prefix') {
      const prefix = firstRenderedPart(control, schema, state, stack);
      const next = section.controls[index + 1];

      if (!next) {
        if (prefix) {
          parts.push({
            text: prefix.text,
            weight: effectiveWeight(sectionWeight, prefix.weight),
          });
        }
        continue;
      }

      const nextRendered = firstRenderedPart(next, schema, state, stack);

      if (prefix && nextRendered) {
        parts.push({
          text: `${prefix.text} ${nextRendered.text}`,
          weight: effectiveWeight(
            sectionWeight,
            nextRendered.weight !== 1 ? nextRendered.weight : prefix.weight,
          ),
        });
        index += 1;
        continue;
      }

      if (prefix && !nextRendered && next.kind === 'or-adj' && next.customText) {
        parts.push({
          text: `${prefix.text} ${getTextValue(next.customText, isSubjectPlural(state), schema, state, stack)}`,
          weight: effectiveWeight(sectionWeight, prefix.weight),
        });
        index += 1;
        continue;
      }

      if (!prefix && nextRendered) {
        parts.push({
          text: nextRendered.text,
          weight: effectiveWeight(sectionWeight, nextRendered.weight),
        });
        index += 1;
        continue;
      }

      continue;
    }

    for (const part of renderControlSegments(control, schema, state, stack)) {
      parts.push({
        text: part.text,
        weight: effectiveWeight(sectionWeight, part.weight),
      });
    }
  }

  return mergeSegments(parts);
}

function renderControlValue(
  control: Control,
  schema: Schema,
  state: State,
  stack: ResolutionStack = new Set(),
): string {
  return joinParts(renderControlSegments(control, schema, state, stack).map((segment) => segment.text));
}

function renderSectionValue(
  section: Section,
  schema: Schema,
  state: State,
  stack: ResolutionStack = new Set(),
): string {
  return joinParts(
    buildSectionSegments(section, schema, state, section.promptTarget ?? 'positive', stack).map(
      (segment) => segment.text,
    ),
  );
}

export function renderSection(
  section: Section,
  schema: Schema,
  state: State,
  target: PromptTarget,
): string[] {
  const merged = buildSectionSegments(section, schema, state, target);
  if (merged.length === 0) return [];
  return merged.map((part) => applyWeight(part.text, part.weight));
}

export function buildSectionPrompt(
  schema: Schema,
  state: State,
  target: PromptTarget,
  sectionId: string,
): string {
  const section = schema.sections.find((entry) => entry.id === sectionId);
  if (!section) return '';

  return applySubstitutions(
    joinParts(renderSection(section, schema, state, target)),
    getActiveSubstitutions(schema, state),
    schema,
    state,
  );
}

export function buildPrompt(schema: Schema, state: State, target: PromptTarget): string {
  return applySubstitutions(
    joinParts(schema.sections.flatMap((section) => renderSection(section, schema, state, target))),
    getActiveSubstitutions(schema, state),
    schema,
    state,
  );
}
