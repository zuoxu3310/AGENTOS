# Agent OS Skills

Reusable Agent OS methods can live here.

This directory is not a native runtime skill directory by itself.

Native wrappers, if added later, belong in:

```text
.agents/skills/
.claude/skills/
```

Wrappers should point back to `agent-os/` files and stay thin.

Codex enforcement hooks are not skills. They live in `.codex/hooks.json` and
`.codex/hooks/` and remain runtime adapters.
