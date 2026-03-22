const { contextBridge, ipcRenderer } = require('electron');

contextBridge.exposeInMainWorld('promptCrafterDesktop', {
  copyText(text) {
    return ipcRenderer.invoke('promptcrafter:copy-text', text);
  },
});
