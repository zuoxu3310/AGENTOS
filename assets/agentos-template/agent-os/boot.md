# AgentOS Boot

## Purpose

Load only what the current task needs and restore unfinished long work without
restoring old permission.

## Startup Sequence

1. Load the native rules entry: Codex uses the managed block in `AGENTS.md`;
   Claude uses `.claude/rules/agentos-local-rules.md` plus `CLAUDE.md`.
2. Read the SessionStart attention context. If a long task exists, restore its
   goal, finish conditions, open items, next action, latest user change, and
   state path.
3. Re-read the next real user message before deciding whether to continue,
   correct, replace, or start unrelated work.
4. For non-small work, read `agent-os/router.md` and load only the needed gate,
   workflow, adapter, or memory contract.
5. For cross-session project recovery, follow `agent-os/memory/routing.md` and
   selectively read current ledgers and related memory.

Do not preload the whole kernel, static rules through hooks, historical logs,
old permission, or a route event history.

## Load Boundaries

- `agent-os/rules-card.md` is the only resident rule body.
- SessionStart and UserPromptSubmit restore attention only.
- PreToolUse and PostToolUse enforce only deterministic runtime facts.
- `python3 agent-os/tools/aos-lint.py` proves publication structure only. Live
  behavior requires the matching runtime test.
