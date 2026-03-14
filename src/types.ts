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
  selectedOptions: boolean | string | string[];
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
  initiallySelectedOptions?: boolean | string | string[];
  options?: Option[];
};

export type Option = BaseItem & {
  customControlText?: string;
  customControlPluralText?: string;
  submenu?: Submenu;
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
  supplementedBys?: SupplementedBy[];
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

export type SupplementedBy =
  | {
      controlText: string;
      optionText?: never;
      supplementalText: string;
    }
  | {
      controlText?: never;
      optionText: string;
      supplementalText: string;
    };
