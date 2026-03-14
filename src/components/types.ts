export type Actions = {
  setSectionWeight: (sectionText: string, weight: number) => void;
  setControlWeight: (controlText: string, weight: number) => void;
  setRadio: (controlText: string, optionText: string) => void;
  toggleCheck: (controlText: string, optionText: string) => void;
  setToggle: (controlText: string, value: boolean) => void;
};
