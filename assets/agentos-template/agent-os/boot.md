# Agent OS Boot

Date: 2026-07-01

## Purpose

This file defines the minimum startup path for Agents using this repo-local Agent OS kernel.

Agent OS is the `agent-os/` working-guide directory. Entry documents such as `AGENTS.md` and `CLAUDE.md` are adapters that point here.

## Minimum Startup

When an Agent starts work in this project:

```text
1. Read the latest user message.
2. Read the active entry adapter: AGENTS.md or CLAUDE.md.
3. Read this file: agent-os/boot.md.
4. Read agent-os/router.md.
5. Read agent-os/state/current.md when the task is non-small, resumed, or may cross context.
6. Read only the review gates and workflows selected by router.md.
```

Do not load every file by default. Load the minimum needed to preserve the active user object.

In the Claude Code runtime, a SessionStart hook (`.claude/hooks/aos_session_start.py`)
injects the kernel card — invariants, state digest, and next audit entry number —
automatically at startup, resume, clear, and after compaction.

In trusted Codex projects, Codex reads `AGENTS.md` before work, then project-local
`.codex/config.toml` and `.codex/hooks.json` wire native Codex hooks. The Codex
SessionStart hook injects `.codex/agentos-local-rules.md` plus the dynamic state
digest. Steps 2-4 remain the manual path for untrusted Codex projects, other
runtimes, and deep dives.

Load `agent-os/workflows/dynamic-workflow.md` only when the latest user message or Task Contract requires script-owned, multi-worker, multi-thread, or recoverable workflow execution.

Load `agent-os/workflows/fusion-workflow.md` only when the latest user message explicitly invokes Fusion (multi-model answer fusion). Never load or run it proactively.

Load `agent-os/memory/bootstrap.md`, `agent-os/memory/routing.md`, and `agent-os/memory/sync-audit.md` only when the latest user message or Task Contract requires durable project memory, wiki routing, ledgers, handoff, cleanup, or audit work.

Load `agent-os/adapters/runtime-visibility.md` and `agent-os/adapters/skill-parity.md` only when the task requires runtime-visible worker evidence, Codex/Claude adapter behavior, or native skill parity.

Load `agent-os/memory/wiki-v2.md` when the task mentions Wiki v2, OKF, concept docs, confidence, supersession, graph links, or knowledge lifecycle.

## Mandatory Per-Turn Audit

Every turn — including small, short-path, and pure-conversation turns — must
append one minimal audit entry to `agent-os/state/audit-log.md` and report a
short audit block in the answer. A missing report means the audit was not done.
This is not subject to the small-task short path. Rule body:

```text
agent-os/review/per-turn-audit-gate.md
```

## Source Order

Use this order when sources conflict:

```text
1. Latest user message
2. Current main conversation
3. AGENTS.md / CLAUDE.md adapter
4. agent-os/ kernel files
5. Local files and command output
6. Subagent reports after source verification
7. Older memory
```

Subagent reports are leads until checked against source paths, commands, or files.

## Non-Small Task Startup

For non-small tasks, form or reconstruct:

```yaml
startup_state:
  active_user_object:
  task_contract:
  route:
  evidence_state:
  next_safe_action:
```

Then run the lifecycle from:

```text
agent-os/workflows/agent-execution-lifecycle.md
```

## Boundaries

Do not turn Agent OS startup into a broader system build.

These are support capabilities unless the latest user message explicitly makes one the active deliverable:

```text
- subagent protocol
- automation platform
- hook wired integration
- end-to-end pressure test
- global install
- full native skill wrapper implementation
```

Hook status by runtime:

```text
Claude Code:
  wired via .claude/settings.json + .claude/hooks/
  SessionStart kernel-card injection, per-prompt audit baseline, Stop audit
  verification, kernel-edit lint, enforcement-layer edit guard.

Codex:
  wired via .codex/config.toml + .codex/hooks.json + .codex/hooks/
  SessionStart static discipline-card and dynamic-state injection,
  UserPromptSubmit audit baseline, Stop hook audit verification, kernel-edit
  lint, enforcement-layer edit guard.

Other runtimes:
  Manual until wired unless fresh runtime evidence proves automatic triggering.
```

When the latest user message explicitly makes a listed capability the active deliverable, it moves from support capability to mainline for that Task Contract only.

## Completion Rule

Before saying work is complete, run:

```text
agent-os/review/completion-gate.md
agent-os/review/evidence-to-claim-gate.md
```

For kernel structure, run:

```bash
python3 agent-os/tools/aos-lint.py
```

`aos-lint.py` checks structure only. It does not prove Agent OS works behaviorally.
