---
name: project-memory-bootstrap
description: Use when starting or upgrading a project that needs durable AI memory, project wiki scaffolding, handoff files, task contracts, chat notes, decisions, progress logs, or cross-session continuity for Claude, Codex, or other coding agents.
---

# Project Memory Bootstrap

## AgentOS Coordination

If the project has `agent-os/` (or AgentOS is about to be installed), do NOT run
this skill: the AgentOS installer ships the full memory scaffold, and its entry
docs are separate per-runtime adapters. In particular, never create the root
symlink scheme (`AGENTS.md`/`CLAUDE.md` -> `wiki/AGENTS.md`) in an AgentOS
project — merge-installs onto symlinked entry files would corrupt both channels.
This skill serves non-AgentOS projects only. Kernel law: `agent-os/memory/bootstrap.md`.

## Purpose

Initialize a full memory scaffold at project start so future agents do not reconstruct context from chat history.

Core rule: create the full structure early, but do not invent content to fill it. Empty placeholders are allowed.

## When to Use

Use when:
- A project may last more than one session.
- The user asks to initialize project memory, wiki, docs, handoff, plans, decisions, or agent continuity.
- A project already has scattered notes and needs a stable memory layout.
- Claude/Codex/other agents need the same project state.

Do not use for a one-off answer with no persistent project directory.

## Scaffold

Create or preserve:

```text
wiki/AGENTS.md
wiki/index.md
wiki/log.md
wiki/errors/_INDEX.md
wiki/docs/README.md
wiki/raw/README.md
wiki/raw/MANIFEST.md
wiki/ledgers/PLANS.md -> ../../PLANS.md
wiki/ledgers/PROGRESS.md -> ../../PROGRESS.md
wiki/ledgers/DECISIONS.md -> ../../DECISIONS.md
wiki/ledgers/HANDOFF.md -> ../../HANDOFF.md
wiki/TASKS/README.md
wiki/TASKS/MYSUB-01-task-card-template.md
wiki/CHATS/README.md
wiki/CHATS/YYYY-MM-DD-chat-notes-template.md
wiki/knowledge/
AGENTS.md -> wiki/AGENTS.md
CLAUDE.md -> wiki/AGENTS.md
PLANS.md
PROGRESS.md
DECISIONS.md
HANDOFF.md
errors/ -> wiki/errors/
docs/ -> wiki/docs/
```

## Document Roles

- `wiki/AGENTS.md`: canonical cross-agent operating rules; single source of truth.
- `AGENTS.md`: root symlink to `wiki/AGENTS.md`; Codex reads this.
- `CLAUDE.md`: root symlink to `wiki/AGENTS.md`; Claude reads this.
- `PLANS.md`: canonical active and recently completed plans, not a full history.
- `PROGRESS.md`: canonical append-only timeline of completed work and evidence.
- `DECISIONS.md`: canonical append-only decisions and why they were made.
- `HANDOFF.md`: canonical current state for the next agent; keep it short and current.
- `wiki/ledgers/PLANS.md`, `wiki/ledgers/PROGRESS.md`, `wiki/ledgers/DECISIONS.md`, `wiki/ledgers/HANDOFF.md`: wiki-side symlinks back to root ledgers, so wiki can index them without moving the truth.
- `wiki/index.md`: map of durable docs, ledgers, and wiki pages.
- `wiki/log.md`: append-only memory maintenance log.
- `wiki/TASKS/`: one task contract per non-trivial task.
- `wiki/CHATS/`: distilled key chat decisions, not full transcripts.
- `wiki/errors/`: confirmed agent errors and repeated failure modes.
- `wiki/docs/`: user-facing or engineering docs; prefer Markdown/text. Binary originals belong in `wiki/raw/`.
- `wiki/raw/`: original sources; not all are directly ingestible. Track parse/link/skip status in `wiki/raw/MANIFEST.md`.
- `wiki/knowledge/`: compiled Markdown/text project knowledge and reusable methodology.
- `errors/`: root symlink to `wiki/errors/` for old habits and tools.
- `docs/`: root symlink to `wiki/docs/` for old habits and tools.
- `wiki/`: project memory root. It may read, summarize, cite, and link to ledgers but must not replace `PLANS.md`, `PROGRESS.md`, `DECISIONS.md`, or `HANDOFF.md`.

## Index Layer

The scaffold separates code structure from project memory:

- GitNexus: symbols, calls, imports, processes, impact analysis, detect-changes, and code wiki generation.
- `wiki-maintenance`: chats, raw sources, compiled knowledge, `wiki/index.md`, `wiki/log.md`, and promotion into canonical ledgers.
- Graphify/OpenTology: optional experiments for searchable docs/wiki/raw graphs after benchmarking.

Do not use wiki summaries as code evidence. Do not use code graphs as replacements for project decisions.

## Initialization Flow

1. Inspect existing files first. Never overwrite user documents silently.
2. Create missing directories and missing starter files.
3. Prefer entry-doc single truth: create `wiki/AGENTS.md`, then make root `AGENTS.md` and `CLAUDE.md` symlinks to it. If either root file already exists, preserve it and report that manual migration is needed.
4. Add a short memory-routing section to `wiki/AGENTS.md`:
   - before writing durable project memory -> use `wiki-maintenance` as the router
   - current task contract -> `wiki/TASKS/`
   - actual progress -> root canonical `PROGRESS.md`, also linked at `wiki/ledgers/PROGRESS.md`
   - durable decisions -> root canonical `DECISIONS.md`, also linked at `wiki/ledgers/DECISIONS.md`
   - next-agent state -> root canonical `HANDOFF.md`, also linked at `wiki/ledgers/HANDOFF.md`
   - key chat intent -> `wiki/CHATS/`
   - repeated errors -> `wiki/errors/` (`errors/` root symlink)
   - compiled knowledge -> `wiki/knowledge/`
   - reusable methodology such as Superpowers docs -> `wiki/knowledge/` or `wiki/docs/`
   - raw materials -> `wiki/raw/`
   - raw source status -> `wiki/raw/MANIFEST.md`
   - code structure -> GitNexus when indexed
5. End with a verification summary: created, preserved, skipped, and next recommended file to fill.

## Task Contract Template

For non-trivial work, create `wiki/TASKS/MYSUB-XX-short-name.md` or `wiki/TASKS/YYYY-MM-DD-short-name.md`:

```md
# Task Contract: <name>

## Goal

## Boundaries

## Evidence

## Autonomy

## Handoff
```

## Automation

Use the bundled bootstrap script when a filesystem scaffold is needed:

```bash
python3 ${CLAUDE_SKILL_DIR}/scripts/bootstrap_memory.py /path/to/project
```

The script only creates missing files and directories. It does not overwrite existing files unless explicitly passed `--force`.

## Verification

After initialization, verify:

```bash
test -f AGENTS.md
test -f CLAUDE.md
test -f wiki/AGENTS.md
test -f wiki/index.md
test -f wiki/log.md
test -f PLANS.md
test -f PROGRESS.md
test -f DECISIONS.md
test -f HANDOFF.md
test ! -L PLANS.md
test ! -L PROGRESS.md
test ! -L DECISIONS.md
test ! -L HANDOFF.md
test -d wiki/ledgers
test -L wiki/ledgers/PLANS.md
test -L wiki/ledgers/PROGRESS.md
test -L wiki/ledgers/DECISIONS.md
test -L wiki/ledgers/HANDOFF.md
test -d wiki/TASKS
test -d wiki/CHATS
test -d wiki/raw
test -f wiki/raw/MANIFEST.md
test -d wiki/knowledge
test -d wiki/errors
test -d wiki/docs
test -d errors
test -L errors
test -d docs
test -L docs
```

Report exact files created and existing files left untouched.

## Common Mistakes

- Creating many documents and filling them with invented status.
- Creating separate root `CLAUDE.md` and `AGENTS.md` contents when both can symlink to `wiki/AGENTS.md`.
- Moving root ledgers into `wiki/ledgers/`. Keep root ledgers as canonical files; wiki-side ledger paths link back to them.
- Splitting Goal/Boundaries/Evidence/Autonomy/Handoff into five files; they belong in one task contract.
- Creating root-level `TASKS/`, `CHATS/`, `raw/`, `index.md`, or `log.md`; these belong under `wiki/`.
- Creating real root `errors/` or `docs/` directories in new scaffolds. Their content belongs under `wiki/errors/` and `wiki/docs/`; root paths should be symlinks.
- Putting current progress into `AGENTS.md` or `CLAUDE.md`.
- Letting `HANDOFF.md` become a historical archive. It should be current-state only.
- Scattering `PLANS.md`, `PROGRESS.md`, `DECISIONS.md`, or `HANDOFF.md` into wiki pages.
- Treating "wiki must not replace ledgers" as "wiki cannot read ledgers". It can read and cite them.
- Treating `wiki/raw/` as editable wiki content. Raw sources are source material.
- Treating every file type as directly ingestible. Binary, media, archive, and large generated files should be linked or parsed with the right tool first.
