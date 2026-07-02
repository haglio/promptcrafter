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
