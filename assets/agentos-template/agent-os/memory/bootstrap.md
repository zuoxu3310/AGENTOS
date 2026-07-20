# Memory Bootstrap

## Purpose

Create or repair the minimum AgentOS memory structure without inventing project
state. Ongoing routing and lifecycle behavior belong exclusively to
`agent-os/memory/routing.md`.

## Required Memory Scaffold

```text
PLANS.md  PROGRESS.md  DECISIONS.md  HANDOFF.md
wiki/index.md  wiki/log.md
wiki/TASKS/  wiki/CHATS/  wiki/errors/  wiki/knowledge/
wiki/raw/  wiki/raw/MANIFEST.md  wiki/docs/  wiki/ledgers/
wiki/ledgers/PLANS.md -> ../../PLANS.md
wiki/ledgers/PROGRESS.md -> ../../PROGRESS.md
wiki/ledgers/DECISIONS.md -> ../../DECISIONS.md
wiki/ledgers/HANDOFF.md -> ../../HANDOFF.md
```

## Initialization

1. Inspect before writing and preserve user-owned files.
2. Create only missing directories and empty structural artifacts.
3. Create ledger symlinks only when the targets are the canonical root files.
4. Never infer progress, decisions, plans, or handoff state from filenames.
5. Run `python3 agent-os/tools/aos-lint.py` after initialization.

## Ownership Boundary

`AGENTS.md` and `CLAUDE.md` remain separate runtime entry files. Do not replace
them with Wiki symlinks. The AgentOS installer owns scaffold merge behavior;
global bootstrap skills are optional helpers for non-AgentOS projects.

## Completion Evidence

Bootstrap is complete only when the required paths exist, ledger links resolve,
the raw manifest exists, Wiki areas are reachable from the index, and existing
user files were preserved.
