export type PromptTarget = 'positive' | 'negative';

export type ControlKind =
  | 'or'
  | 'or-adv'
  | 'or-adj'
  | 'or-prefix'
  | 'and-commas'
  | 'and-commas-adv'
  | 'and-spaces-adj'
  | 'required'
  | 'toggle';

export type Condition = {
  controlId: string;
  optionId?: string;
};

export type Submenu = {
  kind?: 'and' | 'or';
  placement?: 'before' | 'after';
  options: Option[];
};

export type Option = {
  id: string;
  plural?: string;
  beginOn?: boolean;
  hides?: Condition[];
  disables?: Condition[];
  submenu?: Submenu;
};

export type Control = {
  id: string;
  kind: ControlKind;
  promptTarget?: PromptTarget;
  customText?: string;
  beginOn?: boolean;
  options?: Option[];
  hides?: Condition[];
  disables?: Condition[];
};

export type Section = {
  id: string;
  promptTarget?: PromptTarget;
  controls: Control[];
  hides?: Condition[];
  disables?: Condition[];
};

export type Schema = {
  sections: Section[];
};

export type ControlState = {
  selectedOptionId?: string;
  checkedOptionIds: string[];
  toggleOn: boolean;
  weight: number;
};

export type State = {
  controls: Record<string, ControlState>;
  sections: Record<string, { weight: number }>;
  positiveText: string;
  negativeText: string;
  positiveBound: boolean;
  negativeBound: boolean;
};
