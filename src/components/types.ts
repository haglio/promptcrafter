export type Actions = {
  setSectionWeight: (sectionId: string, weight: number) => void;
  setControlWeight: (controlId: string, weight: number) => void;
  setRadio: (controlId: string, optionId: string) => void;
  toggleCheck: (controlId: string, optionId: string) => void;
  setToggle: (controlId: string, value: boolean) => void;
  setGlobalSelector: (controlId: string, toggleOn: boolean, optionId: string) => void;
};
