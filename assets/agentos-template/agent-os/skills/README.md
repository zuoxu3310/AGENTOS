# Agent OS Skills

This directory holds no methods and no shells. Skills are thin invocation
shells living in `.agents/skills/` and `.claude/skills/`, each pointing at
exactly one kernel canon document — see "Skills Are Shells" in
`agent-os/architecture.md`. Codex enforcement hooks are not skills; they live
in `.codex/hooks.json` and `.codex/hooks/`.
