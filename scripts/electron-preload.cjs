const { contextBridge, ipcRenderer } = require('electron');

contextBridge.exposeInMainWorld('promptCrafterDesktop', {
  copyText(text) {
    return ipcRenderer.invoke('promptcrafter:copy-text', text);
  },
  exportPromptCombo(name, payload) {
    return ipcRenderer.invoke('promptcrafter:export-prompt-combo', { name, payload });
  },
});
