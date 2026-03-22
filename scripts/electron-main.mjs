import { app, BrowserWindow, dialog, ipcMain, clipboard } from 'electron';
import { spawn } from 'node:child_process';
import fs from 'node:fs';
import http from 'node:http';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

const APP_ID = 'Alex.PromptCrafter';
const APP_NAME = 'PromptCrafter';
const START_TIMEOUT_MS = 30000;
const DEV_SERVER_URL = process.env.PROMPTCRAFTER_DEV_SERVER_URL || '';
const DEFAULT_DEV_URL = 'http://127.0.0.1:5173/';

function getRepoRoot() {
  return path.resolve(__dirname, '..');
}

function getRuntimeRoot() {
  return app.isPackaged ? path.dirname(process.execPath) : getRepoRoot();
}

function getAppSourceRoot() {
  return app.isPackaged ? app.getAppPath() : getRepoRoot();
}

function getDistRoot() {
  return path.join(getAppSourceRoot(), 'dist');
}

function isDevMode() {
  return !app.isPackaged;
}

function getLogPath(name) {
  return path.join(getRuntimeRoot(), name);
}

const LOG_PATH = getLogPath('promptcrafter-launcher.log');
const STDOUT_LOG = getLogPath('promptcrafter-stdout.log');
const STDERR_LOG = getLogPath('promptcrafter-stderr.log');
const ICON_PATH = path.join(getAppSourceRoot(), 'icon.ico');

function appendLog(message) {
  const timestamp = new Date().toISOString().replace('T', ' ').slice(0, 19);
  try {
    fs.appendFileSync(LOG_PATH, `[${timestamp}] ${message}\n`, 'utf8');
  } catch {}
}

function writeCapturedLine(filePath, message) {
  try {
    fs.appendFileSync(filePath, `${message}\n`, 'utf8');
  } catch {}
}

function wait(ms) {
  return new Promise((resolve) => setTimeout(resolve, ms));
}

function httpGet(url) {
  return new Promise((resolve) => {
    const request = http.get(url, (response) => {
      response.resume();
      resolve(response.statusCode ?? 500);
    });
    request.on('error', () => resolve(null));
    request.setTimeout(1000, () => {
      request.destroy();
      resolve(null);
    });
  });
}

async function waitForUrl(url, timeoutMs) {
  const started = Date.now();
  while ((Date.now() - started) < timeoutMs) {
    const status = await httpGet(url);
    if (status !== null && status < 500) {
      return true;
    }
    await wait(500);
  }
  return false;
}

function startViteDevServer() {
  const env = { ...process.env };
  delete env.ELECTRON_RUN_AS_NODE;
  const child = process.platform === 'win32'
    ? spawn('cmd.exe', ['/d', '/s', '/c', 'npm run dev -- --host 127.0.0.1 --strictPort'], {
        cwd: getRepoRoot(),
        stdio: 'ignore',
        env,
        windowsHide: true,
        detached: false,
      })
    : spawn('npm', ['run', 'dev', '--', '--host', '127.0.0.1', '--strictPort'], {
        cwd: getRepoRoot(),
        stdio: 'ignore',
        env,
        windowsHide: true,
        detached: false,
      });

  child.on('exit', (code, signal) => {
    appendLog(`[DevServer] Vite exited with code ${code ?? 'null'} signal ${signal ?? 'null'}`);
  });

  appendLog(`[DevServer] Started Vite with PID ${child.pid ?? 'unknown'}`);
  return child;
}

process.stdout.write = ((originalWrite) => (chunk, encoding, cb) => {
  writeCapturedLine(STDOUT_LOG, String(chunk).trimEnd());
  return originalWrite.call(process.stdout, chunk, encoding, cb);
})(process.stdout.write.bind(process.stdout));

process.stderr.write = ((originalWrite) => (chunk, encoding, cb) => {
  writeCapturedLine(STDERR_LOG, String(chunk).trimEnd());
  return originalWrite.call(process.stderr, chunk, encoding, cb);
})(process.stderr.write.bind(process.stderr));

function getMimeType(filePath) {
  const ext = path.extname(filePath).toLowerCase();
  switch (ext) {
    case '.html':
      return 'text/html; charset=utf-8';
    case '.js':
      return 'application/javascript; charset=utf-8';
    case '.css':
      return 'text/css; charset=utf-8';
    case '.json':
      return 'application/json; charset=utf-8';
    case '.svg':
      return 'image/svg+xml';
    case '.png':
      return 'image/png';
    case '.ico':
      return 'image/x-icon';
    default:
      return 'application/octet-stream';
  }
}

function startStaticServer() {
  const distRoot = getDistRoot();
  const server = http.createServer((req, res) => {
    const requestUrl = new URL(req.url || '/', 'http://127.0.0.1');

    if (req.method === 'POST' && requestUrl.pathname === '/__launcher_log__') {
      let body = '';
      req.on('data', (chunk) => {
        body += chunk.toString('utf8');
      });
      req.on('end', () => {
        appendLog(`[Client] ${body}`);
        res.writeHead(204);
        res.end();
      });
      return;
    }

    const relativePath = requestUrl.pathname === '/' ? 'index.html' : requestUrl.pathname.replace(/^\/+/, '');
    const resolvedPath = path.normalize(path.join(distRoot, relativePath));
    if (!resolvedPath.startsWith(distRoot)) {
      res.writeHead(403);
      res.end('Forbidden');
      return;
    }

    fs.readFile(resolvedPath, (error, content) => {
      if (error) {
        appendLog(`[Server] ${req.method} ${requestUrl.pathname} -> ${error.code || 'read-failed'}`);
        res.writeHead(404);
        res.end('Not found');
        return;
      }

      appendLog(`[Server] ${req.method} ${requestUrl.pathname} -> 200`);
      res.writeHead(200, {
        'Content-Type': getMimeType(resolvedPath),
        'Cache-Control': 'no-cache, no-store, must-revalidate',
        Pragma: 'no-cache',
        Expires: '0',
      });
      res.end(content);
    });
  });

  return new Promise((resolve, reject) => {
    server.once('error', reject);
    server.listen(0, '127.0.0.1', () => {
      const address = server.address();
      if (!address || typeof address === 'string') {
        reject(new Error('Failed to determine PromptCrafter server address.'));
        return;
      }
      const url = `http://127.0.0.1:${address.port}/`;
      appendLog(`[Server] Serving ${distRoot} at ${url}`);
      resolve({ server, url });
    });
  });
}

function createSplashWindow() {
  const splash = new BrowserWindow({
    width: 420,
    height: 190,
    resizable: false,
    minimizable: false,
    maximizable: false,
    fullscreenable: false,
    autoHideMenuBar: true,
    show: false,
    title: APP_NAME,
    backgroundColor: '#111827',
    icon: fs.existsSync(ICON_PATH) ? ICON_PATH : undefined,
  });

  const splashHtml = `
    <html>
      <body style="margin:0;background:#111827;color:#f3f4f6;font-family:Segoe UI,sans-serif;display:flex;align-items:center;justify-content:center;">
        <div style="width:100%;padding:24px;">
          <div style="font-size:20px;font-weight:600;margin-bottom:10px;">Loading PromptCrafter...</div>
          <div style="opacity:.85;">Preparing desktop UI.</div>
        </div>
      </body>
    </html>
  `;

  splash.loadURL(`data:text/html;charset=utf-8,${encodeURIComponent(splashHtml)}`);
  splash.once('ready-to-show', () => splash.show());
  return splash;
}

function createMainWindow() {
  const window = new BrowserWindow({
    width: 1440,
    height: 960,
    show: false,
    backgroundColor: '#111827',
    autoHideMenuBar: true,
    title: APP_NAME,
    icon: fs.existsSync(ICON_PATH) ? ICON_PATH : undefined,
    webPreferences: {
      preload: path.join(__dirname, 'electron-preload.cjs'),
      contextIsolation: true,
      nodeIntegration: false,
      sandbox: false,
    },
  });

  window.webContents.on('console-message', (_event, level, message, line, sourceId) => {
    appendLog(`[Renderer:${level}] ${message} @ ${sourceId}:${line}`);
  });

  window.webContents.on('render-process-gone', (_event, details) => {
    appendLog(`[UI] Renderer process exited: ${details.reason}`);
  });

  return window;
}

async function main() {
  app.setAppUserModelId(APP_ID);
  appendLog('[UI] Starting PromptCrafter Electron launcher.');

  const splash = createSplashWindow();
  const mainWindow = createMainWindow();
  let url = DEV_SERVER_URL;
  let closeServer = () => {};
  let viteChild = null;

  if (DEV_SERVER_URL) {
    appendLog(`[UI] Using Vite dev server at ${DEV_SERVER_URL}`);
  } else if (isDevMode()) {
    url = DEFAULT_DEV_URL;
    appendLog(`[UI] Using managed Vite dev server at ${url}`);

    const devReady = await waitForUrl(url, 1500);
    if (!devReady) {
      viteChild = startViteDevServer();
      const started = await waitForUrl(url, START_TIMEOUT_MS);
      if (!started) {
        throw new Error(`Vite dev server did not become ready at ${url}`);
      }
    } else {
      appendLog('[DevServer] Reusing already-running Vite dev server.');
    }
  } else {
    const distIndex = path.join(getDistRoot(), 'index.html');
    if (!fs.existsSync(distIndex)) {
      dialog.showErrorBox(APP_NAME, `PromptCrafter build output is missing.\nExpected: ${distIndex}`);
      app.quit();
      return;
    }

    const { server, url: staticUrl } = await startStaticServer();
    url = staticUrl;
    closeServer = () => {
      try {
        server.close();
      } catch {}
    };
    app.on('before-quit', closeServer);
    mainWindow.on('closed', closeServer);
  }

  let readyTimer = null;
  const stopVite = () => {
    if (viteChild && !viteChild.killed) {
      try {
        viteChild.kill();
      } catch {}
    }
  };

  app.on('before-quit', () => {
    closeServer();
    stopVite();
  });
  mainWindow.on('closed', () => {
    closeServer();
    stopVite();
  });

  ipcMain.handle('promptcrafter:copy-text', async (_event, text) => {
    clipboard.writeText(text);
    return true;
  });

  mainWindow.webContents.once('did-finish-load', () => {
    appendLog('[UI] Electron window finished loading PromptCrafter.');
    if (readyTimer) {
      clearTimeout(readyTimer);
    }
    splash.close();
    mainWindow.show();
    mainWindow.focus();
  });

  mainWindow.webContents.on('did-fail-load', (_event, code, description, validatedUrl) => {
    appendLog(`[UI] Electron window failed to load ${validatedUrl}: ${code} ${description}`);
    if (!mainWindow.isDestroyed()) {
      dialog.showErrorBox(APP_NAME, `Failed to load PromptCrafter.\n\n${description}`);
    }
  });

  readyTimer = setTimeout(() => {
    appendLog('[UI] PromptCrafter window did not finish loading before timeout.');
    if (!mainWindow.isDestroyed()) {
      dialog.showErrorBox(APP_NAME, 'PromptCrafter took too long to display.');
      mainWindow.close();
    }
  }, START_TIMEOUT_MS);

  appendLog(`[UI] Loading ${url}`);
  await mainWindow.loadURL(url);
}

app.whenReady().then(main).catch((error) => {
  appendLog('[UI] Launch failed.');
  appendLog(error.stack || String(error));
  dialog.showErrorBox(APP_NAME, `Failed to launch PromptCrafter.\n\nCheck logs:\n${LOG_PATH}`);
  app.quit();
});

app.on('window-all-closed', () => {
  app.quit();
});
