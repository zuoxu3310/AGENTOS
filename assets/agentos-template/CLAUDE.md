# CLAUDE.md

This is the Claude Code adapter for the repo-local AgentOS kernel.

Resident law lives in `.claude/rules/agentos-local-rules.md` (auto-injected every
session; carries the per-turn audit invariant enforced by the Stop hook and the
skill trigger table). Dynamic state (next audit number, current object) is
injected by the SessionStart hook.

For non-small tasks, read `agent-os/boot.md` and route through `agent-os/router.md`.

`agent-os/` is the canonical kernel. This file, `AGENTS.md` (the Codex-side
adapter/projection), the enforcement hooks in `.claude/hooks/`, and the thin
wrappers in `.claude/skills/` are adapters/projections, not the kernel.
Claude skill wrappers do not include Codex `agents/openai.yaml` metadata.

Run `python3 agent-os/tools/aos-lint.py` after kernel edits (also auto-run by hook).
