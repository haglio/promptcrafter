# PromptCrafter

A local-only Vite + React + TypeScript prototype for building positive and negative prompts from ordered controls.

## Stack

- Vite + React + TypeScript
- Vitest + Testing Library
- Config-driven prompt schema in `src/lib/schema.ts`

## Run locally

```bash
npm install
npm run dev
```

That command is the normal browser dev server with hot reload.

## Desktop Launcher

PromptCrafter can also run as a desktop app from this repo root:

- `PromptCrafter.lnk` - shortcut to pin to Taskbar
- `scripts/` - Electron host, icon, and shortcut scripts
- `promptcrafter-launcher.log` - launcher-level startup log
- `promptcrafter-stdout.log` - captured build/runtime stdout
- `promptcrafter-stderr.log` - captured build/runtime stderr

The launcher does not open a browser tab. It:

1. launches PromptCrafter as a real Electron desktop app
2. manages a local Vite dev server for live reload when running from the repo
3. opens that URL in its own Chromium-based window with a real Taskbar identity
4. captures launcher and renderer diagnostics in the repo root logs

The desktop window now uses the standard Electron model instead of the previous Python/Qt experiment. That change is intentional: PromptCrafter’s web app was rendering internally, but the old host surface still painted as a blank white rectangle on this machine.

Frontend bootstrap errors inside the embedded window are echoed back into `promptcrafter-launcher.log`, so renderer failures can be debugged from the repo without attaching browser devtools.

The main PromptCrafter shortcut is intentionally the live-reload desktop app. If Vite is not already running, the Electron host starts it automatically and reuses it on later launches.

## Refresh The Icon

```powershell
py -3 ".\scripts\Generate-PromptCrafterIcon.py"
```

## Rebuild The Shortcut

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File ".\scripts\Update-PromptCrafterShortcut.ps1"
```

## Test

```bash
npm run test:watch
```

Launcher contract test:

```powershell
py -3 -m unittest tests.test_launcher_contract -v
```

Electron dev shell:

```bash
npm run desktop:dev
```

`npm run desktop:dev` is the same live-reload desktop workflow used by the Taskbar shortcut. It opens Electron against the managed Vite server and keeps schema/UI edits live inside the desktop window.

## Repo Notes

- There is no separate nested source repo here. PromptCrafter is this repo.
- The pinned Taskbar shortcut is the development desktop app, not a packaged production build.
- If Git still surfaces old `CRLF` warnings for files you edited before the policy changed, restaging after that file is rewritten will clear them.
