# Memory Sync Audit

Date: 2026-07-01

## Purpose

Memory Sync Audit defines how Agent OS finishes a stage, prepares handoff, and checks memory health.

It is a kernel rule. Runtime skills such as neat-freak coordinate the work as adapters.

## Modes

```text
light_sync:
  Use after normal work when touched memory must be updated.

promotion:
  Use when a session produced durable progress, decisions, handoff state, or reusable knowledge.

stage_audit:
  Use when the user asks for stage-end cleanup, full audit, or newcomer-ready handoff.
```

## Light Sync

Check only files directly related to the current task:

```text
- HANDOFF.md if next state changed
- PROGRESS.md if work completed with evidence
- DECISIONS.md if a durable decision was made
- wiki/index.md and wiki/log.md if wiki pages changed
- task contract if the active task changed
- agent-os/state/current.md if the active task state changed
```

## Promotion

Route durable outputs:

```text
completed work -> PROGRESS.md
decision and reason -> DECISIONS.md
next-agent state -> HANDOFF.md
user intent -> wiki/CHATS/
task contract -> wiki/TASKS/
reusable knowledge -> wiki/knowledge/
confirmed mistake -> wiki/errors/
source inventory -> wiki/raw/MANIFEST.md
```

Promotion does not mean the underlying task is complete. Completion still requires the active user object and Evidence-to-Claim Gate.

## Stage Audit

Check:

```text
- agent-os/ routes match current kernel responsibilities
- AGENTS.md and CLAUDE.md are stable adapters, not progress logs
- PLANS.md contains active or recent plans
- PROGRESS.md entries include evidence
- DECISIONS.md entries include reasons and scope
- HANDOFF.md reflects current state, not old history
- wiki/TASKS/ contracts have goal, boundaries, evidence, autonomy, and handoff
- wiki/CHATS/ contains distilled intent, not full transcript dumps
- wiki/errors/ records confirmed mistakes only
- wiki/index.md reaches durable wiki and doc pages
- wiki/log.md records memory operations
- wiki/raw/MANIFEST.md tracks source status
- Dynamic Workflow visibility claims match evidence
- agent-os/state/current.md is fresh: it must not lag the newest audit-log entries
  (a stale current.md while the audit log moves on is a known failure class)
- large handoffs attach a recognition-type acceptance quiz per
  agent-os/review/completion-gate.md; the user may waive it
```

## Safety

```text
- Do not delete memory by default.
- Ask before destructive moves, global config writes, or entry-doc ownership changes.
- Archive instead of deleting when cleanup is useful.
- Preserve user-authored files unless the user approves a change.
```

## Output Shape

```yaml
memory_sync_audit:
  mode:
  changed_files:
  evidence:
  risks:
  unresolved_decisions:
  handoff_ready: yes | no
```

