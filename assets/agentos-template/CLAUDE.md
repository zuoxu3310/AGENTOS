# Claude Code Adapter

Claude loads the shared resident contract through
`.claude/rules/agentos-local-rules.md`.

- Claude uses native Workflow for orchestration and keeps Superpowers enabled.
- The Codex-only Dynamic Workflow adapter is not installed under
  `.claude/skills/`.
- `.claude/settings.json` and `.claude/hooks/` restore long-task attention, check
  worker-prompt structure, and lint governed documents after structured edits.
- `agent-os/` remains the kernel; this file contains no shared behavior rules.
