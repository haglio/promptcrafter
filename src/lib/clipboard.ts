export async function copyTextToClipboard(text: string): Promise<void> {
  if (navigator.clipboard?.writeText) {
    await navigator.clipboard.writeText(text);
    return;
  }

  if (window.promptCrafterDesktop?.copyText) {
    await window.promptCrafterDesktop.copyText(text);
    return;
  }

  throw new Error('Clipboard support is not available.');
}
