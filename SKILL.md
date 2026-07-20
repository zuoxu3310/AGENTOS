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

Before promoting a changed installer bundle, run its standard-library behavior suite:

```bash
python3 scripts/test_installer_behavior.py
```

## Rules

- Do not call a written explanation, plan, or partial copy a completed install.
- Do not silently overwrite user files. The installer merges entry docs and root ledgers or backs up replaced files under `.agentos-backups/`.
- Existing `agent-os/state/**` and `wiki/**` files are protected data: reinstalling may add missing template files but never replaces existing files in those trees.
- `.claude/settings.json` and `.codex/hooks.json` are JSON-merged. Unrelated user keys and hooks survive; only AgentOS-owned `aos_*.py` hook commands are refreshed, with exactly one AgentOS Stop gate per runtime.
- `.codex/config.toml` is TOML-validated, then only AgentOS developer instructions and `features.hooks` are merged. Unrelated keys remain in place and no duplicate `[features]` table is emitted.
- Invalid existing JSON or TOML remains byte-identical. The installer reports `partial`, records an explicit `merge-failed-*` action, and exits non-zero.
- Do not install dependencies or edit global configuration.
- Treat `agent-os/` as the kernel. Generate the AgentOS-managed block in
  `AGENTS.md` from `agent-os/rules-card.md`; keep Claude's native projection at
  `.claude/rules/agentos-local-rules.md`. Configuration, skills, and hooks are
  adapters, not additional static rule sources.
- If validation fails, report the exact missing path or failing command. The validator requires the shared long-task state helper, task-state tests at unit/integration/scenario layers, and the attention hooks in both runtime trees.

## Resources

- `assets/agentos-template/`: full AgentOS project template.
- `scripts/install-agentos.py`: deterministic installer.
- `scripts/validate-agentos-install.py`: structural smoke validator.


## Attention And Mechanical Hooks

The template wires SessionStart, UserPromptSubmit, Stop, prompt-craft, and
governed-document lint hooks for Claude and Codex. Codex also has one
deterministic guard that rejects native delegation so delegated work uses only
the vendored Dynamic Workflow runner.

SessionStart restores only the current session's long-task goal, finish
conditions, open items, and next action. UserPromptSubmit reminds the main model
to reinterpret every real user message. Stop requests one same-model delivery
reread only when a completed or blocked long task is marked pending. Tool hooks
do not decide intent, route, authorization, or semantic completion.

- If the target already has `.claude/settings.json`, the installer JSON-merges the hook config and never removes existing user settings.
- Claude hooks take effect from the next Claude Code session in the target project; the first session may ask the user to approve the new project hooks.
- Codex hooks take effect from the next Codex session after the project `.codex/` layer and every current Hook definition is trusted. An update that changes a Hook entry changes its hash and requires review again; successful installation or validation does not prove runtime activation.
- Other runtimes remain report-based (`Manual until wired`) unless fresh runtime evidence proves automatic triggering.
- Publish the `.agents/skills/agentos-kernel-installer` bundle as the release source; `.claude` and `.codex` copies are byte-identical mirrors, not independent forks.
