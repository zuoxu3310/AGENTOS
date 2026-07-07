---
name: wiki-maintenance
description: "Use when deciding where durable project memory should be written, or when maintaining a project memory wiki: routing files, ingesting raw sources, querying compiled knowledge, distilling chat logs, promoting task findings, linting stale docs, updating indexes, or appending project memory logs."
---

# Wiki Maintenance

## AgentOS Coordination

In projects with `agent-os/`, the kernel law `agent-os/memory/routing.md` governs
and this skill executes it. Two AgentOS-specific boundaries: the per-turn raw
trail goes to `agent-os/state/audit-log.md` (only promoted milestones enter
`PROGRESS.md`), and memory writes follow the evidence rules there (re-runnable
anchors; numbers labeled verified/unverified).

## Purpose

Maintain the project memory layer after it has been initialized. This skill is also the memory router: before writing any durable project memory, decide the correct destination here.

The wiki is compiled knowledge, not raw chat history.

Use this with projects that have `wiki/`, `wiki/raw/`, `wiki/index.md`, `wiki/log.md`, `wiki/CHATS/`, `wiki/TASKS/`, `wiki/errors/`, `wiki/docs/`, `wiki/ledgers/`, `DECISIONS.md`, `PROGRESS.md`, or `HANDOFF.md`.

Use this before writing or moving:
- project notes
- downloaded research
- generated summaries
- task plans
- progress records
- decisions
- handoff state
- chat distillations
- project docs
- error memories
- subagent reports that should outlive the session

## Core Model

```text
wiki/              -> project memory root
wiki/raw/          -> original sources, not necessarily directly ingestible
wiki/knowledge/    -> compiled Markdown/text knowledge, agent-maintained
wiki/ledgers/      -> wiki-side symlinks to root canonical ledgers
wiki/TASKS/        -> task contracts
wiki/CHATS/        -> distilled chat decisions
wiki/errors/       -> confirmed agent mistakes
wiki/docs/         -> project documentation
wiki/index.md      -> map of durable memory
wiki/log.md        -> append-only activity log
```

## Ingest Boundary

Do not treat every file under `wiki/` as a wiki page.

Direct wiki pages should be Markdown or small plain-text files. Other files are source material until parsed, summarized, or explicitly linked.

Classify first:

- Direct read: `.md`, `.txt`, `.json`, `.yaml`, `.yml`, `.toml`, `.csv`, `.tsv`, `.log`, `.diff`, `.patch`, small source files.
- Tool-required read: `.pdf`, `.docx`, `.xlsx`, `.pptx`, `.html`, exported chats, screenshots with OCR needs.
- Link-only by default: images, audio, video, archives, binaries, large generated outputs, vendor dumps.
- Do not ingest blindly: secrets, credentials, private transcripts, large build outputs, dependency folders.

Allowed outputs:

- durable facts -> `wiki/knowledge/`
- active or recent plans -> `PLANS.md`
- completed work with evidence -> `PROGRESS.md`
- durable decisions and why -> `DECISIONS.md`
- next-agent state -> `HANDOFF.md`
- user intent from conversation -> `wiki/CHATS/`
- confirmed repeated agent mistakes -> `wiki/errors/` through `error-learning`
- source inventory -> `wiki/raw/MANIFEST.md`

If a source cannot be reliably parsed, add it to the manifest and link it from `wiki/index.md`; do not pretend it was ingested.

## Route Before Write

Before creating or moving any durable memory file, classify it and choose one destination:

| Content | Destination |
|---|---|
| Active or recent plan | `PLANS.md` |
| Completed work with evidence | `PROGRESS.md` |
| Durable decision and reason | `DECISIONS.md` |
| Next-agent current state | `HANDOFF.md` |
| Non-trivial task contract | `wiki/TASKS/` |
| Distilled user intent from chat | `wiki/CHATS/` |
| Confirmed repeated agent mistake | `wiki/errors/` through `error-learning` |
| Original source or downloaded material | `wiki/raw/` plus `wiki/raw/MANIFEST.md` |
| Parsed reusable project knowledge | `wiki/knowledge/` |
| Human-facing project documentation | `wiki/docs/` |
| Code structure facts | GitNexus or source files, then optional summary in `wiki/knowledge/` |
| Large binary, cache, dependency, model, video, archive | keep outside wiki; link in `wiki/raw/MANIFEST.md` if useful |

If one item contains several types, split the outputs. Example: a research PDF stays in `wiki/raw/`, its summary goes to `wiki/knowledge/`, and a resulting choice goes to `DECISIONS.md`.

Do not ask the user where to put routine memory. Ask only when the content is sensitive, destructive movement is needed, or the file has two plausible long-term owners.

## Code Graph Boundary

Use GitNexus for code-structure facts when available:
- symbols
- calls
- imports
- processes
- impact analysis
- detect-changes
- coordinated rename

Use `wiki-maintenance` for compiled project memory:
- chats
- raw sources
- compiled wiki
- index and log
- promotion into the canonical ledgers listed below

Do not answer code-impact questions from wiki summaries alone. Do not replace `DECISIONS.md` with code graph output.

## Canonical Ledgers

Do not scatter these files into wiki pages:
- `PLANS.md`: active and recent plans.
- `PROGRESS.md`: high-frequency append-only progress with evidence.
- `DECISIONS.md`: append-only decision archive; each entry needs why.
- `HANDOFF.md`: current next-agent state.

Root ledger files are the canonical files. `wiki/ledgers/` should contain symlinks back to the root ledgers, so wiki can index them without moving the stable project entry points. Treat either path as the same ledger content.

`wiki/` may summarize or link to these ledgers, but it must not replace them. `DECISIONS.md` keeps its append-only nature. `PROGRESS.md` and `HANDOFF.md` stay dedicated files because they update often and need predictable locations.

These ledgers are first-class memory sources. `wiki-maintenance` may read, query, summarize, cite, link, and promote content into them. The restriction is only against replacing them with scattered wiki pages.

## Methodology Docs

Reusable methods, workflows, and operating manuals belong in `wiki/knowledge/` or `wiki/docs/`. Examples: Superpowers documentation, TDD workflow notes, review methodology, research taste principles, or project-specific operating guides.

Concrete project state produced by those methods does not belong in wiki:
- a Superpowers-generated plan -> `PLANS.md`
- execution progress -> `PROGRESS.md`
- a chosen workflow decision and why -> `DECISIONS.md`
- next-agent continuation state -> `HANDOFF.md`

## Operations

### Route

Use whenever the agent is about to save durable memory and the destination is not already forced by the user.

Steps:
1. Name the content in one sentence.
2. Choose the destination from "Route Before Write".
3. If moving existing files, list source and target before moving unless the user explicitly asked to migrate.
4. Write the file, update the right index or ledger, and append to `wiki/log.md` when project memory changed.
5. Report the final path.

### Ingest

Use when new source material appears in `wiki/raw/` or the user asks to absorb a document, transcript, log, paper, or subagent report.

Steps:
1. Identify the source and keep its original path.
2. Classify the file type: direct read, tool-required read, link-only, or do-not-ingest.
3. Extract only durable facts, decisions, open questions, and contradictions when the source is readable.
4. Update canonical ledgers when the source contains plans, progress, decisions, or handoff state.
5. Write or update relevant `wiki/knowledge/` or `wiki/docs/` pages only for reusable knowledge.
6. Update `wiki/raw/MANIFEST.md` when tracking source status helps future agents.
7. Update `wiki/index.md`.
8. Append one entry to `wiki/log.md`.
9. Report source path, ingest status, changed pages, ledger updates, and unresolved questions.

### Query

Use when answering project-memory questions.

Steps:
1. Read `wiki/index.md` first.
2. Read only relevant `wiki/knowledge/`, `wiki/docs/`, root ledgers, `wiki/ledgers/` symlinks, `wiki/errors/`, or `wiki/CHATS/` files.
3. For code-structure claims, use GitNexus or direct source reads.
4. Answer with source paths.
5. If the answer creates a reusable synthesis, ask whether to file it back or file it when the user has already asked for durable memory.

### Distill Chat

Use when a chat contains future-relevant user intent, scope changes, or decisions.

Store distilled notes in `wiki/CHATS/YYYY-MM-DD-topic.md`:

```md
# Chat Notes - <topic>

## Context

## User Decisions

## Scope Changes

## Short Quotes

## Follow-up
```

Do not save full transcripts unless the user explicitly asks. Keep quotes short.

### Promote

Use at task completion or handoff.

Move durable content to the right canonical place:
- actual completed work -> `PROGRESS.md`
- decision and reason -> `DECISIONS.md`
- next-agent state -> `HANDOFF.md`
- repeated or confirmed mistake -> `wiki/errors/`
- reusable project knowledge -> `wiki/knowledge/`
- reusable methodology or workflow docs -> `wiki/knowledge/` or `wiki/docs/`
- key user intent from chat -> `wiki/CHATS/`

Do not turn plans, progress, decisions, or handoff into scattered wiki pages. Use wiki pages only for reusable concepts, architecture explanations, research notes, or domain knowledge.

### Lint

Use when the user asks to clean, sync, audit, or health-check memory.

Check:
- `wiki/index.md` links point to existing files.
- `HANDOFF.md` reflects current state, not old history.
- `DECISIONS.md` contains reasons, not progress notes.
- `PROGRESS.md` entries include evidence.
- `PLANS.md`, `PROGRESS.md`, `DECISIONS.md`, and `HANDOFF.md` still exist as canonical ledgers and were not replaced by wiki pages.
- `wiki/knowledge/` pages are reachable from `wiki/index.md`.
- `wiki/raw/` files were not edited as compiled knowledge.
- stale claims are marked or replaced when newer evidence exists.

### Archive

Use when old task files or chat notes are no longer active.

Archive by moving or marking old items only when the project already has an archive convention or the user asks. Never delete raw sources or decisions.

## Log Entry Format

Append to `wiki/log.md`:

```md
## YYYY-MM-DD | <operation> | <short topic>

- Source: <path or conversation>
- Updated: <files>
- Evidence: <commands, tests, links, or source paths>
- Next: <next action or none>
```

## Index Rule

Every durable wiki/doc page should be reachable from `wiki/index.md`. If a page is intentionally temporary, keep it in `wiki/TASKS/` or `wiki/CHATS/` instead.

## Common Mistakes

- Rewriting `wiki/raw/` instead of compiling into `wiki/knowledge/`.
- Filing everything into `HANDOFF.md`.
- Scattering `PLANS.md`, `PROGRESS.md`, `DECISIONS.md`, or `HANDOFF.md` into wiki pages.
- Saving long chat transcripts instead of distilled decisions.
- Updating wiki pages without updating `wiki/index.md` and `wiki/log.md`.
- Treating subagent summaries as facts without source paths.

## Extra Reference

For the document map and routing rules, read [references/document-map.md](references/document-map.md).
