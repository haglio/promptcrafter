export async function exportPromptCombo(
  name: string,
  payload: PromptExportPayload,
): Promise<PromptExportResult> {
  const desktopBridge = window.promptCrafterDesktop;
  if (!desktopBridge?.exportPromptCombo) {
    throw new Error('Prompt export is only available in the desktop app.');
  }
  return desktopBridge.exportPromptCombo(name, payload);
}
