export {};

declare global {
  interface PromptExportPayload {
    positive: string;
    negative: string;
  }

  interface PromptExportResult {
    filePath: string;
    fileName: string;
  }

  interface Window {
    promptCrafterDesktop?: {
      copyText(text: string): Promise<boolean>;
      exportPromptCombo(name: string, payload: PromptExportPayload): Promise<PromptExportResult>;
    };
  }
}
