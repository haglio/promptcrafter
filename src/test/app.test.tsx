import { describe, expect, it, vi } from 'vitest';
import { fireEvent, render, screen, within } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import App from '../App';
import { testSchema } from './fixtures/testSchema';

const globalSelectorControlLabel = 'colorize';
const globalSelectorOptionOneLabel = 'green';
const globalSelectorOptionTwoLabel = 'black';
const matchedRadioControlLabel = 'eye color';
const matchedRadioOptionOneLabel = 'green';
const matchedRadioOptionTwoLabel = 'black';
const matchedCheckboxControlLabel = 'render style';
const matchedCheckboxOptionOneLabel = 'green tinted';
const matchedCheckboxOptionTwoLabel = 'black and white';

function getSectionByHeading(headingText: string): HTMLElement {
  const heading = screen.getByRole('heading', { name: headingText });
  const section = heading.closest('section');
  expect(section).not.toBeNull();
  return section as HTMLElement;
}

function getSectionHeaderActions(section: HTMLElement): HTMLElement {
  const headerActions = section.querySelector('.section-header-actions');
  expect(headerActions).not.toBeNull();
  return headerActions as HTMLElement;
}

function getControlByText(controlText: string): HTMLElement {
  const control = screen
    .getAllByText(controlText)
    .map((element) => element.closest('.control'))
    .find((element) => element !== null);
  expect(control).not.toBeNull();
  return control as HTMLElement;
}

describe('PromptCrafter UI', () => {
  describe('updating prompts', () => {
    it('updates the positive prompt pane when positive controls change', async () => {
      const user = userEvent.setup();
      render(<App schema={testSchema} />);

      let positive = screen.getByRole('textbox', { name: 'Positive prompt' });
      expect(positive).toHaveValue(
        'space robo dino demon monster',
      );

      await user.click(screen.getByLabelText('bone'));
      await user.click(screen.getByLabelText('towering'));
      await user.click(screen.getByLabelText('wings'));
      await user.click(screen.getByLabelText('mechanical'));

      positive = screen.getByRole('textbox', { name: 'Positive prompt' });
      expect(positive).toHaveValue(
        'space robo dino demon monster, outline towering, bone armor, mechanical wings',
      );
    });

    it('updates the negative prompt pane when negative controls change', async () => {
      const user = userEvent.setup();
      render(<App schema={testSchema} />);

      let negative = screen.getByRole('textbox', { name: 'Negative prompt' });
      expect(negative).toHaveValue(
        'no clutter, blurry',
      );

      await user.click(screen.getByLabelText('extra limbs'));

      negative = screen.getByRole('textbox', { name: 'Negative prompt' });
      expect(negative).toHaveValue(
        'no clutter, blurry, extra limbs',
      );
    });

    it('positive prompt auto mode rejects edits, manual mode accepts edits, and switching back restores auto output', async () => {
      const user = userEvent.setup();
      render(<App schema={testSchema} />);

      const positive = screen.getByRole('textbox', { name: 'Positive prompt' });
      const initialAuto = 'space robo dino demon monster';
      expect(positive).toHaveValue(initialAuto);
      expect(positive).toBeDisabled();

      await user.type(positive, 'attempted auto edit');
      expect(positive).toHaveValue(initialAuto);

      const positivePromptArea = positive.closest('section');
      expect(positivePromptArea).not.toBeNull();

      await user.click(within(positivePromptArea as HTMLElement).getByRole('button', { name: /manual/i }));
      expect(positive).toBeEnabled();

      await user.clear(positive);
      await user.type(positive, 'manual prompt');
      expect(positive).toHaveValue('manual prompt');

      await user.click(within(positivePromptArea as HTMLElement).getByRole('button', { name: /auto/i }));

      expect(positive).toBeDisabled();
      expect(positive).toHaveValue(initialAuto);
    });

    it('negative prompt auto mode rejects edits, manual mode accepts edits, and switching back restores auto output', async () => {
      const user = userEvent.setup();
      render(<App schema={testSchema} />);

      const negative = screen.getByRole('textbox', { name: 'Negative prompt' });
      const initialAuto = 'no clutter, blurry';
      expect(negative).toHaveValue(initialAuto);
      expect(negative).toBeDisabled();

      await user.type(negative, 'attempted auto edit');
      expect(negative).toHaveValue(initialAuto);

      const negativePromptArea = negative.closest('section');
      expect(negativePromptArea).not.toBeNull();

      await user.click(within(negativePromptArea as HTMLElement).getByRole('button', { name: /manual/i }));
      expect(negative).toBeEnabled();

      await user.clear(negative);
      await user.type(negative, 'manual negative prompt');
      expect(negative).toHaveValue('manual negative prompt');

      await user.click(within(negativePromptArea as HTMLElement).getByRole('button', { name: /auto/i }));

      expect(negative).toBeDisabled();
      expect(negative).toHaveValue(initialAuto);
    });

    it('renders the PromptCrafter shell on first load without collapsing to a blank root', () => {
      render(<App schema={testSchema} />);

      expect(screen.getByRole('heading', { name: 'PromptCrafter' })).toBeInTheDocument();
      expect(screen.getByRole('textbox', { name: 'Positive prompt' })).toBeInTheDocument();
      expect(screen.getByRole('textbox', { name: 'Negative prompt' })).toBeInTheDocument();
    });
  });

  describe('global selector controls', () => {
    it('hides global selector options while the control is off', () => {
      render(<App schema={testSchema} />);

      const globalSelectorControl = getControlByText(globalSelectorControlLabel);
      expect(within(globalSelectorControl).getByRole('checkbox', { name: globalSelectorControlLabel })).not.toBeChecked();
      expect(within(globalSelectorControl).queryByRole('radio', { name: globalSelectorOptionOneLabel })).not.toBeInTheDocument();
      expect(within(globalSelectorControl).queryByRole('radio', { name: globalSelectorOptionTwoLabel })).not.toBeInTheDocument();
    });

    it('shows global selector options while the control is on', async () => {
      const user = userEvent.setup();
      render(<App schema={testSchema} />);

      const globalSelectorControl = getControlByText(globalSelectorControlLabel);
      await user.click(within(globalSelectorControl).getByRole('checkbox', { name: globalSelectorControlLabel }));

      expect(within(globalSelectorControl).getByRole('checkbox', { name: globalSelectorControlLabel })).toBeChecked();
      expect(within(globalSelectorControl).getByRole('radio', { name: globalSelectorOptionOneLabel })).toBeInTheDocument();
      expect(within(globalSelectorControl).getByRole('radio', { name: globalSelectorOptionTwoLabel })).toBeInTheDocument();
    });

    it('hides global selector options again when the control is turned off', async () => {
      const user = userEvent.setup();
      render(<App schema={testSchema} />);

      const globalSelectorControl = getControlByText(globalSelectorControlLabel);
      await user.click(within(globalSelectorControl).getByRole('checkbox', { name: globalSelectorControlLabel }));
      await user.click(within(globalSelectorControl).getByRole('checkbox', { name: globalSelectorControlLabel }));

      expect(within(globalSelectorControl).queryByRole('radio', { name: globalSelectorOptionOneLabel })).not.toBeInTheDocument();
    });

    it('selecting global selector option 1 selects matching options in single-select controls', async () => {
      const user = userEvent.setup();
      render(<App schema={testSchema} />);

      const globalSelectorControl = getControlByText(globalSelectorControlLabel);
      await user.click(within(globalSelectorControl).getByRole('checkbox', { name: globalSelectorControlLabel }));
      await user.click(within(globalSelectorControl).getByRole('radio', { name: globalSelectorOptionOneLabel }));

      const matchedRadioControl = getControlByText(matchedRadioControlLabel);
      expect(within(matchedRadioControl).getByRole('radio', { name: matchedRadioOptionOneLabel })).toBeChecked();
      expect(within(matchedRadioControl).getByRole('radio', { name: matchedRadioOptionTwoLabel })).not.toBeChecked();
    });

    it('selecting global selector option 2 selects matching options in single-select controls', async () => {
      const user = userEvent.setup();
      render(<App schema={testSchema} />);

      const globalSelectorControl = getControlByText(globalSelectorControlLabel);
      await user.click(within(globalSelectorControl).getByRole('checkbox', { name: globalSelectorControlLabel }));
      await user.click(within(globalSelectorControl).getByRole('radio', { name: globalSelectorOptionTwoLabel }));

      const matchedRadioControl = getControlByText(matchedRadioControlLabel);
      expect(within(matchedRadioControl).getByRole('radio', { name: matchedRadioOptionTwoLabel })).toBeChecked();
      expect(within(matchedRadioControl).getByRole('radio', { name: matchedRadioOptionOneLabel })).not.toBeChecked();
    });

    it('selecting global selector option 1 selects matching options in multi-select controls', async () => {
      const user = userEvent.setup();
      render(<App schema={testSchema} />);

      const globalSelectorControl = getControlByText(globalSelectorControlLabel);
      await user.click(within(globalSelectorControl).getByRole('checkbox', { name: globalSelectorControlLabel }));
      await user.click(within(globalSelectorControl).getByRole('radio', { name: globalSelectorOptionOneLabel }));

      const matchedCheckboxControl = getControlByText(matchedCheckboxControlLabel);
      expect(within(matchedCheckboxControl).getByRole('checkbox', { name: matchedCheckboxOptionOneLabel })).toBeChecked();
      expect(within(matchedCheckboxControl).getByRole('checkbox', { name: matchedCheckboxOptionTwoLabel })).not.toBeChecked();
    });

    it('selecting global selector option 2 selects matching options in multi-select controls', async () => {
      const user = userEvent.setup();
      render(<App schema={testSchema} />);

      const globalSelectorControl = getControlByText(globalSelectorControlLabel);
      await user.click(within(globalSelectorControl).getByRole('checkbox', { name: globalSelectorControlLabel }));
      await user.click(within(globalSelectorControl).getByRole('radio', { name: globalSelectorOptionTwoLabel }));

      const matchedCheckboxControl = getControlByText(matchedCheckboxControlLabel);
      expect(within(matchedCheckboxControl).getByRole('checkbox', { name: matchedCheckboxOptionTwoLabel })).toBeChecked();
      expect(within(matchedCheckboxControl).getByRole('checkbox', { name: matchedCheckboxOptionOneLabel })).not.toBeChecked();
    });

    it('switching between global selector options replaces prior matching selections', async () => {
      const user = userEvent.setup();
      render(<App schema={testSchema} />);

      const globalSelectorControl = getControlByText(globalSelectorControlLabel);
      await user.click(within(globalSelectorControl).getByRole('checkbox', { name: globalSelectorControlLabel }));
      await user.click(within(globalSelectorControl).getByRole('radio', { name: globalSelectorOptionOneLabel }));
      await user.click(within(globalSelectorControl).getByRole('radio', { name: globalSelectorOptionTwoLabel }));

      const matchedRadioControl = getControlByText(matchedRadioControlLabel);
      expect(within(matchedRadioControl).getByRole('radio', { name: matchedRadioOptionTwoLabel })).toBeChecked();
      expect(within(matchedRadioControl).getByRole('radio', { name: matchedRadioOptionOneLabel })).not.toBeChecked();

      const matchedCheckboxControl = getControlByText(matchedCheckboxControlLabel);
      expect(within(matchedCheckboxControl).getByRole('checkbox', { name: matchedCheckboxOptionTwoLabel })).toBeChecked();
      expect(within(matchedCheckboxControl).getByRole('checkbox', { name: matchedCheckboxOptionOneLabel })).not.toBeChecked();
    });
  });

  describe('disabling and hiding', () => {
    it('applies disabledBys at the section level', async () => {
      const user = userEvent.setup();
      render(<App schema={testSchema} />);

      const section = getSectionByHeading('section disabled target');
      expect(section).not.toHaveClass('disabled');

      await user.click(screen.getByRole('checkbox', { name: 'is portrait' }));

      expect(getSectionByHeading('section disabled target')).toHaveClass('disabled');
    });

    it('applies disabledBys at the control level', async () => {
      const user = userEvent.setup();
      render(<App schema={testSchema} />);

      const modes = getSectionByHeading('modes');
      expect(within(modes).getByLabelText('low')).toBeEnabled();

      await user.click(within(modes).getByRole('checkbox', { name: 'is portrait' }));

      expect(within(getSectionByHeading('modes')).getByLabelText('low')).toBeDisabled();
    });

    it('applies disabledBys at the option level', async () => {
      const user = userEvent.setup();
      render(<App schema={testSchema} />);

      const modes = getSectionByHeading('modes');
      expect(within(modes).getByLabelText('floating')).toBeEnabled();

      await user.click(within(modes).getByRole('checkbox', { name: 'is portrait' }));

      expect(within(getSectionByHeading('modes')).getByLabelText('floating')).toBeDisabled();
    });

    it('applies hiddenBys at the section level', async () => {
      const user = userEvent.setup();
      render(<App schema={testSchema} />);

      expect(screen.getByRole('heading', { name: 'section hidden target' })).toBeInTheDocument();

      await user.click(screen.getByRole('checkbox', { name: 'is portrait' }));

      expect(screen.queryByRole('heading', { name: 'section hidden target' })).not.toBeInTheDocument();
    });

    it('applies hiddenBys at the control level', async () => {
      const user = userEvent.setup();
      render(<App schema={testSchema} />);

      const modes = getSectionByHeading('modes');
      expect(within(modes).getByText('portrait focus')).toBeInTheDocument();

      await user.click(within(modes).getByRole('checkbox', { name: 'is portrait' }));

      expect(within(getSectionByHeading('modes')).queryByText('portrait focus')).not.toBeInTheDocument();
    });

    it('applies hiddenBys at the option level', async () => {
      const user = userEvent.setup();
      render(<App schema={testSchema} />);

      const modes = getSectionByHeading('modes');
      expect(within(modes).getByLabelText('airborne')).toBeInTheDocument();

      await user.click(within(modes).getByRole('checkbox', { name: 'is portrait' }));

      expect(within(getSectionByHeading('modes')).queryByLabelText('airborne')).not.toBeInTheDocument();
    });
  });

  describe('plurality in UI labels', () => {
    it('shows plural section label when subject is plural', async () => {
      const user = userEvent.setup();
      render(<App schema={testSchema} />);

      expect(screen.getByRole('heading', { name: 'accent' })).toBeInTheDocument();

      await user.click(screen.getByLabelText('two'));

      expect(screen.getByRole('heading', { name: 'accents' })).toBeInTheDocument();
      expect(screen.queryByRole('heading', { name: 'accent' })).not.toBeInTheDocument();
    });

    it('shows plural control label when subject is plural', async () => {
      const user = userEvent.setup();
      render(<App schema={testSchema} />);

      expect(screen.getByText('stance')).toBeInTheDocument();

      await user.click(screen.getByLabelText('two'));

      expect(screen.getByText('stances')).toBeInTheDocument();
      expect(screen.queryByText('stance')).not.toBeInTheDocument();
    });

    it('shows plural option label when subject is plural', async () => {
      const user = userEvent.setup();
      render(<App schema={testSchema} />);

      expect(screen.getByText('hero')).toBeInTheDocument();

      await user.click(screen.getByLabelText('two'));

      expect(screen.getByText('heroes')).toBeInTheDocument();
      expect(screen.queryByText('hero')).not.toBeInTheDocument();
    });

    it('applies toggle-driven global substitutions to section, control, option labels, and prompt text', async () => {
      const user = userEvent.setup();
      render(<App schema={testSchema} />);

      const torsoSection = getSectionByHeading('torso references');
      expect(within(torsoSection).getByText('torso mentions')).toBeInTheDocument();
      expect(within(torsoSection).getByLabelText('torso badge')).toBeInTheDocument();
      expect(within(torsoSection).getByLabelText('torsos')).toBeInTheDocument();

      await user.click(screen.getByRole('checkbox', { name: 'thorax mode' }));

      const thoraxSection = getSectionByHeading('thorax references');
      expect(screen.queryByRole('heading', { name: 'torso references' })).not.toBeInTheDocument();
      expect(within(thoraxSection).getByText('thorax mentions')).toBeInTheDocument();
      expect(within(thoraxSection).getByLabelText('thorax badge')).toBeInTheDocument();
      expect(within(thoraxSection).getByLabelText('thoraces')).toBeInTheDocument();

      await user.click(within(thoraxSection).getByLabelText('thorax badge'));
      await user.click(within(thoraxSection).getByLabelText('thoraces'));

      expect(screen.getByRole('textbox', { name: 'Positive prompt' })).toHaveValue(
        'space robo dino demon monster, replace thorax terminology, thorax badge, thoraces',
      );
    });
  });

  describe("weights", () => {
    it('affecting the prompt by lowering weight below 1', async () => {
      const user = userEvent.setup();
      render(<App schema={testSchema} />);

      await user.click(screen.getByLabelText('bone'));
      const control = getControlByText('armor');
      const weight = within(control).getByRole('slider');

      fireEvent.change(weight, { target: { value: '0.6' } });
      expect(screen.getByRole('textbox', { name: 'Positive prompt' })).toHaveValue(
        'space robo dino demon monster, (bone armor:0.6)',
      );
    });

    it('affecting the prompt by raising weight above 1', () => {
      render(<App schema={testSchema} />);

      const section = getSectionByHeading('negative modes');
      const actions = getSectionHeaderActions(section);
      const slider = within(actions).getByRole('slider');

      fireEvent.change(slider, { target: { value: '2.5' } });
      expect(screen.getByRole('textbox', { name: 'Negative prompt' })).toHaveValue('(no clutter:2.5), blurry');
    });

    it("shouldn't show the weight slider for a section if no option has been selected for any of its controls", () => {
      render(<App schema={testSchema} />);

      const section = getSectionByHeading('details');
      const actions = getSectionHeaderActions(section);
      expect(within(actions).queryByRole('slider')).not.toBeInTheDocument();
    });

    it("shouldn't show the weight slider for a control if no option has been selected for it", () => {
      render(<App schema={testSchema} />);

      const control = getControlByText('armor');
      expect(within(control).queryByRole('slider')).not.toBeInTheDocument();
    });

    it("reset button doesn't appear until weight slider deviates from 1 for a section", () => {
      render(<App schema={testSchema} />);

      const section = getSectionByHeading('negative modes');
      const actions = getSectionHeaderActions(section);
      const slider = within(actions).getByRole('slider');

      expect(within(section).queryByRole('button', { name: '↺' })).not.toBeInTheDocument();

      fireEvent.change(slider, { target: { value: '2.5' } });
      expect(within(section).getByRole('button', { name: '↺' })).toBeInTheDocument();
    });

    it("reset button doesn't appear until weight slider deviates from 1 for a control", async () => {
      const user = userEvent.setup();
      render(<App schema={testSchema} />);

      await user.click(screen.getByLabelText('bone'));
      const control = getControlByText('armor');
      const slider = within(control).getByRole('slider');

      expect(within(control).queryByRole('button', { name: '↺' })).not.toBeInTheDocument();

      fireEvent.change(slider, { target: { value: '2.0' } });
      expect(within(control).getByRole('button', { name: '↺' })).toBeInTheDocument();
    });

    it("pushing reset causes the weight to return to 1, affecting the prompt and slider and re-hiding the reset button, for a section's weight slider reset button", async () => {
      const user = userEvent.setup();
      render(<App schema={testSchema} />);

      const section = getSectionByHeading('negative modes');
      const actions = getSectionHeaderActions(section);
      const slider = within(actions).getByRole('slider');

      fireEvent.change(slider, { target: { value: '2.5' } });
      expect(screen.getByRole('textbox', { name: 'Negative prompt' })).toHaveValue('(no clutter:2.5), blurry');
      expect(slider).toHaveValue('2.5');

      await user.click(within(section).getByRole('button', { name: '↺' }));

      expect(slider).toHaveValue('1');
      expect(screen.getByRole('textbox', { name: 'Negative prompt' })).toHaveValue('no clutter, blurry');
      expect(within(section).queryByRole('button', { name: '↺' })).not.toBeInTheDocument();
    });

    it("pushing reset causes the weight to return to 1, affecting the prompt and slider and re-hiding the reset button, for a control's weight slider reset button", async () => {
      const user = userEvent.setup();
      render(<App schema={testSchema} />);

      await user.click(screen.getByLabelText('bone'));
      const control = getControlByText('armor');
      const slider = within(control).getByRole('slider');

      fireEvent.change(slider, { target: { value: '2.0' } });
      expect(screen.getByRole('textbox', { name: 'Positive prompt' })).toHaveValue(
        'space robo dino demon monster, (bone armor:2.0)',
      );
      expect(slider).toHaveValue('2');

      await user.click(within(control).getByRole('button', { name: '↺' }));

      expect(screen.getByRole('textbox', { name: 'Positive prompt' })).toHaveValue(
        'space robo dino demon monster, bone armor',
      );
      expect(slider).toHaveValue('1');
      expect(within(control).queryByRole('button', { name: '↺' })).not.toBeInTheDocument();
    });
  });

  describe('copy buttons', () => {
    it('copies the positive prompt text', async () => {
      const user = userEvent.setup();
      const writeText = vi.fn().mockResolvedValue(undefined);
      Object.defineProperty(navigator, 'clipboard', {
        configurable: true,
        value: { writeText },
      });

      render(<App schema={testSchema} />);

      const positivePrompt = screen.getByRole('textbox', { name: 'Positive prompt' });
      const positivePromptArea = positivePrompt.closest('section');
      expect(positivePromptArea).not.toBeNull();

      await user.click(within(positivePromptArea as HTMLElement).getByRole('button', { name: 'Copy prompt' }));

      expect(writeText).toHaveBeenCalledTimes(1);
      expect(writeText).toHaveBeenCalledWith('space robo dino demon monster');
    });

    it('copies the negative prompt text', async () => {
      const user = userEvent.setup();
      const writeText = vi.fn().mockResolvedValue(undefined);
      Object.defineProperty(navigator, 'clipboard', {
        configurable: true,
        value: { writeText },
      });

      render(<App schema={testSchema} />);

      const negativePrompt = screen.getByRole('textbox', { name: 'Negative prompt' });
      const negativePromptArea = negativePrompt.closest('section');
      expect(negativePromptArea).not.toBeNull();

      await user.click(within(negativePromptArea as HTMLElement).getByRole('button', { name: 'Copy prompt' }));

      expect(writeText).toHaveBeenCalledTimes(1);
      expect(writeText).toHaveBeenCalledWith('no clutter, blurry');
    });

    it('copies a section prompt text', async () => {
      const user = userEvent.setup();
      const writeText = vi.fn().mockResolvedValue(undefined);
      Object.defineProperty(navigator, 'clipboard', {
        configurable: true,
        value: { writeText },
      });

      render(<App schema={testSchema} />);

      const section = getSectionByHeading('negative modes');
      await user.click(within(section).getByRole('button', { name: 'Copy section' }));

      expect(writeText).toHaveBeenCalledTimes(1);
      expect(writeText).toHaveBeenCalledWith('no clutter');
    });
  });

  describe('export button', () => {
    it('opens the export dialog and saves the current prompt combo through the desktop bridge', async () => {
      const user = userEvent.setup();
      const exportPromptCombo = vi.fn().mockResolvedValue({
        fileName: 'my-combo.json',
        filePath: 'C:\\repo\\output\\my-combo.json',
      });

      window.promptCrafterDesktop = {
        copyText: vi.fn().mockResolvedValue(true),
        exportPromptCombo,
      };

      render(<App schema={testSchema} />);

      await user.click(screen.getByRole('button', { name: 'Export JSON' }));

      expect(screen.getByRole('dialog', { name: 'Export prompt combo' })).toBeInTheDocument();

      const nameInput = screen.getByLabelText('File name');
      await user.clear(nameInput);
      await user.type(nameInput, 'my-combo');
      await user.click(screen.getByRole('button', { name: 'Save export' }));

      expect(exportPromptCombo).toHaveBeenCalledTimes(1);
      expect(exportPromptCombo).toHaveBeenCalledWith('my-combo', {
        positive: 'space robo dino demon monster',
        negative: 'no clutter, blurry',
      });
      expect(screen.getByRole('status')).toHaveTextContent('Saved my-combo.json');
    });
  });
});
