# Memory Bootstrap

Date: 2026-07-01

## Purpose

Memory Bootstrap defines the minimum project-memory scaffold required for Agent OS continuity.

Use it when a project is expected to continue across turns, threads, agents, or handoffs.

It is a kernel rule. Runtime skills such as project-memory-bootstrap are adapters that may implement this rule, but they are not the source of truth.

## Kernel Classification

```text
kernel:
  agent-os/memory/bootstrap.md, because it defines required Agent OS memory structure.

storage:
  root canonical ledgers and wiki/ directories.

adapter:
  Codex skills, Claude skills, shell scripts, and other runtime-specific setup helpers.

verification:
  scaffold checks, lint checks, and file-existence checks.
```

Do not copy a runtime skill into Agent OS as kernel text. Extract stable rules and keep runtime-specific paths inside adapters.

## First Principles

```text
active object:
  a project state that future agents can recover without reconstructing everything from chat history.

invariants:
  - agent-os/ is the kernel.
  - wiki/ is project memory storage, not the kernel.
  - Root ledgers are canonical work-state files.
  - Entry docs are adapters into the kernel.
  - Existing user documents are preserved unless the user approves ownership changes.
  - Empty starter files are allowed; invented status is not.
```

## Required Memory Scaffold

Create or preserve:

```text
PLANS.md
PROGRESS.md
DECISIONS.md
HANDOFF.md
wiki/index.md
wiki/log.md
wiki/TASKS/
wiki/CHATS/
wiki/errors/
wiki/knowledge/
wiki/raw/
wiki/raw/MANIFEST.md
wiki/docs/
wiki/ledgers/
wiki/ledgers/PLANS.md -> ../../PLANS.md
wiki/ledgers/PROGRESS.md -> ../../PROGRESS.md
wiki/ledgers/DECISIONS.md -> ../../DECISIONS.md
wiki/ledgers/HANDOFF.md -> ../../HANDOFF.md
```

`AGENTS.md` and `CLAUDE.md` remain runtime entry adapters. If they already exist as real files, preserve them unless the user explicitly approves converting them into symlinks or changing ownership.

In particular, do not adopt the standalone project-memory-bootstrap scaffold's
root-symlink scheme (`AGENTS.md`/`CLAUDE.md` -> `wiki/AGENTS.md`) inside an AgentOS
project: the installer ships separate per-runtime adapters, and merge-installs onto
symlinked entry files would write both blocks into one shared file and corrupt both
channels. In AgentOS projects the installer owns this scaffold; the standalone skill
serves non-AgentOS projects only.

## Ledger Roles

```text
PLANS.md:
  active and recent plans; not a historical archive.

PROGRESS.md:
  append-only completed work with evidence.

DECISIONS.md:
  durable decisions with reasons and scope.

HANDOFF.md:
  current next-agent state; short, current, and actionable.
```

Do not scatter plan, progress, decision, or handoff state into wiki pages.

## Wiki Roles

```text
wiki/TASKS/:
  task contracts and task-specific evidence boundaries.

wiki/CHATS/:
  distilled user intent, scope changes, and short quotes when exact wording matters.

wiki/errors/:
  confirmed repeated agent mistakes and corrections.

wiki/knowledge/:
  compiled reusable project knowledge and methodology.

wiki/raw/:
  original source material and source inventory.

wiki/docs/:
  human-facing or engineering documentation.

wiki/index.md:
  map of durable memory.

wiki/log.md:
  append-only memory maintenance operations.
```

## Initialization Rules

```text
1. Inspect existing files before writing.
2. Preserve existing entry docs and user documents.
3. Create missing ledgers and wiki directories.
4. Create wiki-side ledger symlinks when safe.
5. Write only observed current state, explicit user decisions, and verified evidence.
6. Record memory operations in wiki/log.md.
7. Keep wiki/index.md reachable and current.
```

## Completion Evidence

Memory bootstrap is complete only when:

```text
- required root ledgers exist
- required wiki directories exist
- wiki/raw/MANIFEST.md exists
- wiki/index.md reaches the memory areas
- wiki/log.md records the operation
- wiki/ledgers links or equivalent references point to root ledgers
- no existing entry document was overwritten or silently converted
- verification checks cover the scaffold
```

