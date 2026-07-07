---
name: neat-freak
description: Use when a project needs stage-end cleanup, handoff preparation, documentation-memory reconciliation, full memory audit, or when the user asks to sync, tidy, clean up docs, update memory, prepare handoff, make the project newcomer-ready, or run a full audit.
---

# Neat Freak

## AgentOS Coordination

In projects with `agent-os/`, the kernel law `agent-os/memory/sync-audit.md`
governs and this skill coordinates it. Two AgentOS-specific audit items: check
that `agent-os/state/current.md` is fresh (it must not lag the newest
`agent-os/state/audit-log.md` entries), and attach a recognition-type acceptance
quiz to large handoffs per `agent-os/review/completion-gate.md` (user may waive).

## Purpose

`neat-freak` is the project cleanup coordinator. It decides what kind of cleanup is needed and routes work to the right memory skill.

It is not the owner of every document. It coordinates:
- entry docs -> `writing-agent-md`
- project memory scaffold -> `project-memory-bootstrap`
- routine memory placement, wiki work, and memory promotion -> `wiki-maintenance`
- confirmed errors -> `error-learning`
- error compression -> `error-neat`

## Modes

### Light Sync

Default when the user says "整理一下", "同步一下", "update memory", "tidy", or the session ends after a normal task.

Scope:
- touched files
- directly related docs
- `HANDOFF.md` when next state changed
- `PROGRESS.md` when work completed with evidence
- `DECISIONS.md` only for durable decisions

Do not scan the entire project.

### Promote

Use when the session produced durable information.

Route:
- completed work -> `PROGRESS.md`
- decision and reason -> `DECISIONS.md`
- next-agent state -> `HANDOFF.md`
- key user intent -> `wiki/CHATS/`
- reusable project knowledge -> `wiki/knowledge/`
- confirmed mistake -> `error-learning`

Use `wiki-maintenance` for `wiki/CHATS/`, `wiki/knowledge/`, `wiki/docs/`, `wiki/raw/`, `wiki/index.md`, and `wiki/log.md`.

### Full Audit

Use only when the user explicitly asks:
- "全能大清扫"
- "全量清扫"
- "full audit"
- "deep clean"
- "全项目体检"
- "新人能直接上手"
- "阶段结束彻底整理"
- "把这个项目整理到可交接"

Scope:
- `CLAUDE.md` / `AGENTS.md`
- `PLANS.md`
- `PROGRESS.md`
- `DECISIONS.md`
- `HANDOFF.md`
- `wiki/TASKS/`
- `wiki/CHATS/`
- `wiki/errors/`
- `wiki/docs/`
- `wiki/`
- `wiki/raw/`
- `wiki/raw/MANIFEST.md`
- `wiki/index.md`
- `wiki/log.md`
- README and runnable commands
- GitNexus index status when available

## Full Audit Checks

Check:
- entry docs contain stable rules, not current progress
- `PLANS.md` contains plans, not history
- `PROGRESS.md` entries include evidence
- `DECISIONS.md` entries include why
- `HANDOFF.md` reflects current state
- `wiki/TASKS/` task contracts have Goal, Boundaries, Evidence, Autonomy, Handoff
- `wiki/CHATS/` stores distilled intent, not full transcript dumps
- `wiki/errors/` is healthy under `error-learning` rules
- `wiki/` pages are reachable from `wiki/index.md`
- `wiki/raw/` is treated as source material, with parse/link/skip status in `wiki/raw/MANIFEST.md` when useful
- paths, commands, and docs match the actual repo

For code-structure claims, use GitNexus when the repo is indexed. Do not use wiki summaries as code evidence.

## Safety

Do not delete documents by default. List deletion candidates and ask unless the user explicitly requested deletion.

Archive instead of deleting when possible.

Do not modify global `~/.claude/CLAUDE.md` or `~/.codex/AGENTS.md` unless the user explicitly asks for global rule changes.

## Workflow

1. Choose mode: Light Sync, Promote, or Full Audit.
2. Inspect existing memory scaffold. If missing and project is persistent, use `project-memory-bootstrap`.
3. Route entry-doc edits to `writing-agent-md`.
4. Route wiki/chat/index/log work to `wiki-maintenance`.
5. Route confirmed mistakes to `error-learning`.
6. Route unhealthy error records to `error-neat`.
7. Verify changed files.
8. Report concise results: changed files, risks, unresolved decisions.

## Output

Keep the final summary short:

```text
同步完成:
- 更新: <files and reason>
- 发现风险: <items or none>
- 需要 the user 决定: <items or none>
- 当前能否交接: <yes/no and why>
```

## References

Read when needed:
- [references/sync-matrix.md](references/sync-matrix.md)
- [references/agent-paths.md](references/agent-paths.md)
