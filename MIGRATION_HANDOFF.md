# PromptCrafter Launcher Handoff

PromptCrafter now uses a single Electron-based desktop launcher rooted in this repo.

## Final Model

- There is no separate wrapper repo and no nested source repo.
- `PromptCrafter.lnk` is the primary launcher to pin to Taskbar.
- The pinned launcher targets `node_modules\electron\dist\electron.exe` with `.` as its argument.
- The Electron main process lives in `scripts/electron-main.mjs`.
- The Electron preload bridge lives in `scripts/electron-preload.cjs`.
- The launcher starts or reuses a local Vite dev server and then opens PromptCrafter in a real desktop window.
- Hot reload is part of the normal desktop workflow.

## Key Commands

- Browser dev server: `npm run dev`
- Desktop dev shell: `npm run desktop:dev`
- Shortcut refresh: `powershell -NoProfile -ExecutionPolicy Bypass -File ".\scripts\Update-PromptCrafterShortcut.ps1"`
- Icon refresh: `py -3 ".\scripts\Generate-PromptCrafterIcon.py"`
- UI tests: `npm run test`
- Launcher contract tests: `py -3 -m unittest tests.test_launcher_contract -v`

## Logging

- `promptcrafter-launcher.log`
- `promptcrafter-stdout.log`
- `promptcrafter-stderr.log`

Frontend bootstrap and runtime diagnostics are echoed into `promptcrafter-launcher.log`.

## Important Notes

- The earlier Python/Qt launcher path was abandoned because the app rendered internally but still painted as a blank white surface on this machine.
- The packaged-runtime experiment was also abandoned. PromptCrafter now has one launcher path instead of dual dev/prod launcher models.
- If the launcher fails before the UI appears, check `promptcrafter-launcher.log` first.
- Line endings are now governed by `.gitattributes` and `.editorconfig`. Repository text files should stay LF by default, while `.ps1`/`.bat`/`.cmd` remain CRLF.
