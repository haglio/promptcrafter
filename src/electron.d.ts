export {};

declare global {
  interface Window {
    promptCrafterDesktop?: {
      copyText(text: string): Promise<boolean>;
    };
  }
}
