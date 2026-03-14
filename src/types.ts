// state

export type State = {
  controls: Record<string, ControlState>;
  sections: Record<string, SectionState>;
  positiveText: string;
  negativeText: string;
  positiveMode: 'auto' | 'manual';
  negativeMode: 'auto' | 'manual';
};

export type SectionState = {
  weight: number;
}

export type ControlState = {
  selectedOption?: string;
  checkedOptions?: string[];
  toggledOn?: boolean;
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
  initiallySelected?: boolean;
  options?: Option[];
};

export type Option = BaseItem & {
  submenu?: Submenu;
  initiallySelected?: boolean;
};

export type Submenu = {
  kind: SubmenuKind;
  options: Option[];
};

// other

export type BaseItem = {
  text: string;
  pluralText?: string;
  hiddenBys?: DisabledOrHiddenBy[];
  disabledBys?: DisabledOrHiddenBy[];
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

type SubmenuKind =
  | 'or-adv'
  | 'or-adj'
  | 'and-adv'
  | 'and-adj';

export type DisabledOrHiddenBy = {
  controlText?: string;
  optionText?: string;
};
