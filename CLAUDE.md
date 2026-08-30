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

Do not lean on the sanitize guard to catch it. `tools/sanitize_guard.py` fails
the suite when a **known** blocked term appears in the tracked tree, but a brand-
new performer name it has never seen passes every check and lands. The guard is a
backstop for names already known; it cannot see the next one.

So fabricate fully. Use `Jane Doe`, `Example Studio`, `scene one`, the
`alpha`/`beta`/`gamma` act placeholders the committed `content.example.json`
already uses. The near miss that still counts: taking a real filename and
changing a character or two — it is still that clip, still that performer. Make
it up from scratch, don't lightly edit a real one.

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
