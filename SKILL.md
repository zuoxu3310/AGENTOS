---
name: agentos-kernel-installer
description: Use when installing, bootstrapping, expanding, or updating AgentOS Kernel in a project; when the user asks to use AgentOS, copy the AgentOS working guide into the current repository, or add AgentOS rules, native skills, wiki, ledgers, and verification files.
---

# AgentOS Kernel Installer

Install the bundled AgentOS project scaffold into the target repository or working directory.

## Workflow

1. Use the current working directory unless the user names another target path.
2. Run:

```bash
python3 scripts/install-agentos.py /path/to/project
```

3. Validate:

```bash
python3 scripts/validate-agentos-install.py /path/to/project
python3 /path/to/project/agent-os/tools/aos-lint.py
```

## Rules

- Do not call a written explanation, plan, or partial copy a completed install.
- Do not silently overwrite user files. `CLAUDE.md` and the root ledgers (`PLANS.md`, `PROGRESS.md`, `DECISIONS.md`, `HANDOFF.md`) merge by appending a marked AgentOS block. `AGENTS.md` is a kernel projection: reinstall syncs it to the canonical template version and backs up the previous copy under `.agentos-backups/`. Other replaced files are backed up there too.
- Reinstall never overwrites live project state: files under `agent-os/state/` and `wiki/` are seeded only on first install and preserved as-is when they already exist. This protects the per-turn audit log, wiki index, and wiki log from being reset to template stubs.
- Do not install dependencies or edit global configuration.
- Treat `agent-os/` as the kernel. Treat `AGENTS.md`, `CLAUDE.md`, `.agents/skills/`, `.claude/skills/`, `.codex/config.toml`, `.codex/hooks.json`, `.codex/hooks/`, `.codex/agentos-local-rules.md`, `.claude/settings.json`, and `.claude/hooks/` as adapters/projections.
- If validation fails, report the exact missing path or failing command.

## Resources

- `assets/agentos-template/`: full AgentOS project template.
- `scripts/install-agentos.py`: deterministic installer.
- `scripts/validate-agentos-install.py`: structural smoke validator.


## Enforcement Hooks (Claude runtime)

The template ships `.claude/hooks/` (5 enforcement hooks + shared helper) wired via `.claude/settings.json`: SessionStart kernel-card injection, per-prompt audit baseline, Stop per-turn-audit verification, kernel-edit lint, and an enforcement-layer edit guard.

- If the target already has `.claude/settings.json`, the installer JSON-merges the hook config and never removes existing user settings.
- Hooks take effect from the next Claude Code session in the target project; the first session may ask the user to approve the new project hooks.
- Codex and other runtimes remain report-based (`Manual until wired`).
