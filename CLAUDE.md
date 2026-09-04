# promptcrafter — Project-Specific Instructions

Shared rules are in the global `~/.claude/CLAUDE.md`. This file contains only promptcrafter-specific overrides.

## Repo-specific gotchas

### Dead-code test must name explicit targets, not scan `.`

`tests/test_dead_code.py` runs vulture against `promptcrafter` and `scripts` by
name. Do **not** revert it to `vulture . --exclude ...,.claude`: agents work from
a `.claude/worktrees/<name>` checkout whose root path contains `.claude`, so
`--exclude .claude` matches the worktree root and vulture self-excludes
*everything* — the scan becomes a no-op that always passes and hides real dead
code. See the test's module docstring for the full rationale.

### A script run by path imports the *primary* checkout, not your worktree

The venv carries an editable install of `promptcrafter` pointing at
`~/workspace/Haglio/promptcrafter` — the primary checkout, i.e. `main`. Python
puts the *script's own directory* on `sys.path`, not the cwd, so
`python /tmp/probe.py` from inside a worktree resolves `import promptcrafter` to
the primary checkout and your edits are invisible. Nothing errors; the probe
just answers about `main`.

This is worse than it sounds, because the failure looks like success: a
differential harness comparing "before" against "after" reports zero differences
and you conclude the refactor is safe. That happened on 2026-08-30 — the sweep
said 171,960 states identical, and it was comparing `main` against a file, with
the working tree not loaded at all. It was caught only by a negative control (a
deliberate one-line break that the harness should have flagged and didn't).

So, in any throwaway script:

```python
import sys
WORKTREE = "/Users/.../promptcrafter/.claude/worktrees/<name>"
sys.path.insert(0, WORKTREE)          # before importing promptcrafter
import promptcrafter
assert promptcrafter.__file__.startswith(WORKTREE)
```

`python -c` from the worktree root is fine (cwd is on the path) and so is
pytest (rootdir goes on the path), which is why the suite never sees this.
**And always give a differential harness a negative control** — break something
on purpose once and check the harness notices. A comparison tool that cannot
fail is not evidence.

## The committed schema is a demo, and the app does not run it

`promptcrafter/schema.py` is three fabricated sections -- heroes, villains,
pigeons. It is not what the user sees. The real schema is their own prompt
vocabulary, which is exactly what `app_support.sanitize` refuses to let near a
commit, so it lives in a git-ignored `schema.local.json` beside the checkout and
`promptcrafter/schema_overlay.py` reads it at launch. No overlay, no problem: a
public clone, CI, and every worktree fall back to the demo, which is what keeps
the suite deterministic wherever it runs.

Two things follow. **The demo may never grow toward the real one** -- not one
real option, not one real section name, however much more useful a realistic
demo would be to read. And **the overlay is where the user's edits go**: an
agent asked to add a control is almost always being asked about their schema,
not about the three sections in the tree, so ask which before editing
`schema.py`.

The overlay's JSON keeps the **camelCase** spelling the schema was authored in
(`promptTarget`, `initiallySelectedOptions`, `supplementedBys`) rather than the
snake_case of the dataclasses; `schema_from_document` is the single place the
two vocabularies meet, and `tests/test_schema_overlay.py` pins every key.

## Test fixtures must be fabricated, never copied from the real library

Every fixture value that stands in for library data — a video title, a filename,
a performer or studio name, prompt text — must be **invented**. Never paste a
real one out of the media library to make a test feel realistic.

This is not a style note. It is the single thing that has actually leaked private
data into these repos: an agent writing a test reached for a real filename or
performer name because it was handy, and it rode into a public commit. Nothing in
the app's *design* pulls library text into source — the library lives outside
every repo, read at runtime through the git-ignored overlays — so this habit is
the only remaining path for a real name to get committed, and the only thing
stopping it is you following this rule.

Do not lean on the sanitize guard to catch it. `app_support.sanitize` fails
the suite when a **known** blocked term appears in the tracked tree, but a brand-
new performer name it has never seen passes every check and lands. The guard is a
backstop for names already known; it cannot see the next one.

So fabricate fully. Use `Jane Doe`, `Example Studio`, `scene one`, the
`alpha`/`beta`/`gamma` act placeholders the committed `content.example.json`
already uses. The near miss that still counts: taking a real filename and
changing a character or two — it is still that clip, still that performer. Make
it up from scratch, don't lightly edit a real one.

## Judging a branch before it lands

Every worktree carries `launch_preview_branch.vbs` (tracked). Double-clicking it
runs THAT worktree's code as its own app instance: the primary checkout's venv,
the worktree as the working directory, and the worktree's own
`schema.local.json`. Two things to do before handing one over: **copy the
primary's `schema.local.json` into the worktree root**, or the preview comes up
on the fabricated demo and shows three sections of heroes and pigeons rather
than the thing under review; and check the launch windowlessly with
`python -m pytest tests/test_launch_smoke.py`, which replays the whole import
phase in a fresh interpreter under the launcher's own working directory and
`PYTHONPATH`.

The working directory is the part that fails silently. The venv carries an
editable install pointing at the primary, so a preview started anywhere else
resolves `import promptcrafter` to `main`: the app comes up, looks fine, and
reviews the wrong code. The launcher moves to its own folder first for that
reason — see the import trap under Repo-specific gotchas.

**Never start it yourself. Hand the link and stop.** Any command that runs the
vbs, or a bare `python -m promptcrafter`, puts a window over whatever the user
is doing and takes their focus; a preview that appears unannounced gets closed
in irritation, and whatever else they had running of that app usually goes with
it. Starting it is theirs, on their schedule, and the launcher is named
distinctly from `PromptCrafter.lnk` so a review cycle cannot run against the
live app by mistake.

The preview is part of delivering any user-facing change, not an extra: the user
judges mergability by clicking through the real app. **It comes BEFORE the pull
request, and their verdict is what opens one** — see Landing below, where opening
a non-draft PR here merges the work hands-off. Push it with `gh pr create --fill
--draft` if the branch should be visible first, and `gh pr ready` once they say
it is good.

## Landing — GitHub merge queue, not local ff-merge

This repo is public at `github.com/haglio/promptcrafter` with a merge-queue ruleset on
`main`, so the global "ff-merge into the primary checkout under
`.git/agent-merge.lock`" flow does NOT apply here:

- **Land through a pull request.** From your worktree: commit, `git fetch origin
  && git rebase origin/main`, `git push -u origin <branch>`, then
  `gh pr create --fill`. Auto-merge arms itself; the queue rebases your PR onto
  `main`, runs the required check, and merges it when green. Don't ff-merge into
  the primary checkout, don't push `main` directly, and never force-push `main`.
- **The `.git/agent-merge.lock` is retired here** — the GitHub queue serializes.
- **Sync local checkouts by pulling.** `main` advances only on origin (via the
  queue), so the primary checkout and worktrees update with
  `git pull --ff-only origin main`; the running app self-updates the same way.
  The primary is only ever fast-forwarded — never reset or merged-into.
- **A red required check** (`.github/workflows/merge-gate.yml`) can't land.

Everything else in the global CLAUDE.md — work in a worktree, green tests before
you push, clean handoff — still applies.
