export type PromptTarget = 'positive' | 'negative';

export type ControlKind =
  | 'or'
  | 'or-leading-title-if-non-empty'
  | 'or-trailing-title-if-non-empty'
  | 'or-no-comma-prefix-of-next'
  | 'and-comma-separated'
  | 'and-comma-leading-text'
  | 'and-space-separated'
  | 'and-space-trailing-title-if-non-empty'
  | 'required'
  | 'toggle';

export type Condition = {
  type: 'selected' | 'toggle-on';
  controlId: string;
  optionId?: string;
};

export type Submenu = {
  selectionMode?: 'many' | 'one';
  placement?: 'before' | 'after';
  options: OptionDefinition[];
};

export type OptionDefinition = {
  id: string;
  plural?: string;
  defaultSelected?: boolean;
  hides?: Condition[];
  disables?: Condition[];
  submenu?: Submenu;
};

export type ControlDefinition = {
  id: string;
  kind: ControlKind;
  promptTarget?: PromptTarget;
  titleText?: string;
  leadingText?: string;
  defaultWeight?: number;
  defaultToggleOn?: boolean;
  options?: OptionDefinition[];
  hides?: Condition[];
  disables?: Condition[];
};

export type SectionDefinition = {
  id: string;
  defaultWeight?: number;
  promptTarget?: PromptTarget;
  controls: ControlDefinition[];
  hides?: Condition[];
  disables?: Condition[];
};

export type Schema = {
  sections: SectionDefinition[];
};

export type ControlState = {
  selectedOptionId?: string;
  checkedOptionIds: string[];
  toggleOn: boolean;
  weight: number;
};

export type BuilderState = {
  controls: Record<string, ControlState>;
  sections: Record<string, { weight: number }>;
  positiveText: string;
  negativeText: string;
  positiveBound: boolean;
  negativeBound: boolean;
};