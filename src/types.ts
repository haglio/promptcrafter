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
  // Toggle controls keep their preferred option selections here even while disabled.
  // Other control kinds can infer activity directly from selectedOptions.
  enabled?: boolean;
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
  customText?: TextValue;
  initiallySelectedOptions?: boolean | string | string[];
  globalSubstitutions?: GlobalSubstitution[];
  hiddenOppositeBys?: DisabledOrHiddenBy[];
  options?: Option[];
};

export type Option = BaseItem & {
  customControlText?: TextValue;
  submenu?: Submenu;
};

export type Submenu = {
  kind: SubmenuKind;
  options: Option[];
};

// other

export type BaseItem = {
  id: string;
  text: TextValue;
  hiddenBys?: DisabledOrHiddenBy[];
  revealedBys?: DisabledOrHiddenBy[];
  disabledBys?: DisabledOrHiddenBy[];
  supplementedBys?: SupplementedBy[];
};

export type TextValue =
  | string
  | {
      singular: string;
      plural: string;
    }
  | {
      singular: TextPart[];
      plural?: TextPart[];
    };

export type TextPart =
  | string
  | {
      ref: TextReference;
    };

export type TextReference = {
  kind: 'section' | 'control' | 'option';
  id: string;
};

export type PromptTarget = 'positive' | 'negative';

type ControlKind =
  | 'or'
  | 'or-adv'
  | 'or-adj'
  | 'or-prefix'
  | 'and-commas'
  | 'and-commas-adj'
  | 'and-commas-adv'
  | 'and-spaces-adj'
  | 'required'
  | 'hidden-opposite'
  | 'toggle'
  | 'global-selector';

type SubmenuKind =
  | 'or-adv'
  | 'or-adj'
  | 'and-adv'
  | 'and-adj';

export type DisabledOrHiddenBy = {
  controlId?: string;
  optionId?: string;
};

export type SupplementalSide = 'adv' | 'adj';

export type SupplementalText = {
  text: string;
  side: SupplementalSide;
};

export type SupplementedBy =
  | {
      controlId: string;
      optionId?: never;
      supplementalText: TextValue;
      side?: SupplementalSide;
    }
  | {
      controlId?: never;
      optionId: string;
      supplementalText: TextValue;
      side?: SupplementalSide;
    };

export type GlobalSubstitution = {
  from: TextValue;
  to: TextValue;
  fromPlural?: TextValue;
  toPlural?: TextValue;
};
