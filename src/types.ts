// state

export type State = {
  controls: Record<string, ControlState>;
  sections: Record<string, { weight: number }>;
  positiveText: string;
  negativeText: string;
  positiveMode: 'auto' | 'manual';
  negativeMode: 'auto' | 'manual';
};

export type ControlState = {
  selectedOptionId?: string;    // only relevant for 'or' types
  checkedOptionIds: string[];   // only relevant for 'and' types
  toggleOn: boolean;            // only relevant for 'toggle' types
  weight: number;
};

// schema

export type Schema = {
  sections: Section[];
};

export type Section = BaseItem & {
  promptTarget?: PromptTarget;
  controls: Control[];
};

export type Control = BaseItem & {
  kind: ControlKind;
  customText?: string;
  customPluralText?: string;
  initiallySelected?: boolean; // only relevant for toggle types
  options?: Option[];
};

export type Option = BaseItem & {
  submenu?: Submenu;
  initiallySelected?: boolean;
};

export type Submenu = {
  kind?: 'and' | 'or';
  placement?: 'before' | 'after';
  options: Option[];
};

// other

export type BaseItem = {
  text: string;
  pluralText?: string;
  hiddenBys?: Condition[];
  disabledBys?: Condition[];
};

export type PromptTarget = 'positive' | 'negative';

type ControlKind =
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
