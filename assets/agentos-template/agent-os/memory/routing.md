# Memory Routing

Date: 2026-07-01

## Purpose

Memory Routing decides where durable project information belongs.

Use it before writing plans, progress, decisions, handoff state, task contracts, chat distillations, durable knowledge, or source inventories.

It is the Agent OS kernel rule for project memory placement. Runtime skills such as wiki-maintenance are adapters.

## Source Order

When memory sources conflict, use:

```text
1. Latest user message
2. Current main conversation
3. agent-os/ kernel files
4. Root ledgers
5. wiki/ indexed memory
6. Local files and command output
7. Subagent reports after source verification
8. Older memory
```

Do not use wiki summaries as code evidence. Do not use subagent reports as facts until checked against source paths, command output, or files.

## Routing Table

```text
Per-turn raw audit trail (every turn appends):
  agent-os/state/audit-log.md

Active or recent plan:
  PLANS.md

Completed work with evidence:
  PROGRESS.md

Durable decision and reason:
  DECISIONS.md

Current next-agent state:
  HANDOFF.md

Non-trivial task contract:
  wiki/TASKS/

Distilled user intent or scope change:
  wiki/CHATS/

Confirmed repeated agent mistake:
  wiki/errors/

Original source material:
  wiki/raw/ and wiki/raw/MANIFEST.md

Compiled reusable project knowledge:
  wiki/knowledge/

Human-facing or engineering docs:
  wiki/docs/

Code structure facts:
  source files, command output, or a verified code index before optional wiki summary
```

If one artifact contains several memory types, split it into the correct destinations.

## Wiki Boundary

```text
wiki/ is memory storage.
agent-os/ is the kernel.
root ledgers are canonical work-state files.
entry docs are runtime adapters.
```

Wiki pages may link, summarize, and cite ledgers. They must not replace ledgers.

## Ledger Boundary

```text
audit-log.md: per-turn raw trail; every turn appends one entry.
PROGRESS.md: promoted milestones only — work that durably changed the project.
  Promote from audit-log when milestone-worthy; do not mirror every turn.
PLANS.md: the active cross-turn plan.
HANDOFF.md: refreshed at stage end with resumable state.
```

## Write Rules

Before writing durable memory:

```yaml
memory_write_gate:
  content:
  destination:
  claim_type:
  evidence_source:
  source_strength:
  index_update_needed:
  log_update_needed:
```

Write only what the evidence supports. If a claim is uncertain, mark it as unresolved or downgrade the wording.

Key memory claims carry a re-runnable anchor (the exact command, path, or query), and
every number or factual claim is labeled verified or unverified — Evidence-to-Claim
Gate rules apply to memory writes too.

## Index And Log

Every durable wiki or doc page should be reachable from `wiki/index.md`.

Every memory maintenance operation should append to `wiki/log.md` with:

```text
date
operation
source
updated files
evidence
next action
```

## Ingest Classification

Classify before absorbing any source into memory:

```text
direct read: .md .txt .json .yaml .toml .csv .tsv .log .diff and small source files
tool-required: .pdf .docx .xlsx .pptx, HTML exports, OCR-heavy images
link-only by default: images, audio, video, archives, binaries, large generated output
never ingest blindly: secrets, credentials, private transcripts, dependency folders
```

If a source cannot be reliably parsed, record it in `wiki/raw/MANIFEST.md` and link
it from `wiki/index.md`; do not claim it was ingested.

## Chat Distillation

Store distilled decisions, not transcripts: `wiki/CHATS/YYYY-MM-DD-topic.md` with
context, user decisions, scope changes, short quotes (only when exact wording
matters), and follow-ups. Save full transcripts only when the user explicitly asks.

## Forbidden Substitutions

```text
- Do not put all state into HANDOFF.md.
- Do not put current progress into AGENTS.md or CLAUDE.md.
- Do not scatter ledgers into wiki pages.
- Do not save full chat transcripts unless the user asks for transcripts.
- Do not treat old wiki methodology as current Agent OS kernel.
- Do not treat a memory write as task completion unless the active user object is memory itself.
```

