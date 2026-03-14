import { describe, expect, it } from 'vitest';
import { render, screen, within } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import App from '../App';
import { testSchema } from './fixtures/testSchema';

describe('PromptCrafter UI', () => {
  it('updates the prompt panes when controls change', async () => {
    const user = userEvent.setup();
    render(<App schema={testSchema} />);

    await user.click(screen.getByLabelText('bone'));
    await user.click(screen.getByLabelText('towering'));
    await user.click(screen.getByLabelText('wings'));
    await user.click(screen.getByLabelText('mechanical'));

    const positive = screen.getByRole('textbox', { name: 'Positive prompt' });
    expect(positive).toHaveValue(
      'space robo dino demon monster, outline towering, bone armor, mechanical wings',
    );
  });

  it('switches the positive prompt to manual mode so manual edits persist', async () => {
    const user = userEvent.setup();
    render(<App schema={testSchema} />);

    await user.click(screen.getAllByRole('button', { name: /manual/i })[0]);

    const positive = screen.getByRole('textbox', { name: 'Positive prompt' });
    await user.clear(positive);
    await user.type(positive, 'manual prompt');

    await user.click(screen.getByLabelText('bone'));

    expect(positive).toHaveValue('manual prompt');
  });

  it('hides portrait-only controls and disables camera angle when portrait mode is on', async () => {
    const user = userEvent.setup();
    render(<App schema={testSchema} />);

    const modesSectionHeading = screen.getByRole('heading', { name: 'modes' });
    const modesSection = modesSectionHeading.closest('section');
    expect(modesSection).not.toBeNull();

    expect(within(modesSection!).getByText('portrait focus')).toBeInTheDocument();

    await user.click(within(modesSection!).getByRole('checkbox', { name: 'is portrait' }));

    expect(within(modesSection!).queryByText('portrait focus')).not.toBeInTheDocument();
    expect(within(modesSection!).getByLabelText('low')).toBeDisabled();
  });

  // TODO: tests of weight sliders - how when you change it positive or negative it modifies the text in the prompt, and how it shouldn't show the weight slider for sections if no thing has been chosen from that section... and similarly that it doesn't appear for a control, and that in either case the reset button doesn't appear until it deviates from 1, and when you push the reset button it resets to 1

  // TODO: tests of copy buttons, if it's even possible to test the clipboard
});