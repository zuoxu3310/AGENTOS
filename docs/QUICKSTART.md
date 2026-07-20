# AgentOS Quickstart

## 1. Install into a project

```bash
python3 scripts/install-agentos.py /path/to/project
```

The installer adds the AgentOS kernel and runtime adapters. Existing project entry documents and configuration are merged. Existing Wiki and AgentOS state files are preserved.

Use `--dry-run` to inspect the planned actions first:

```bash
python3 scripts/install-agentos.py --dry-run /path/to/project
```

## 2. Validate the installed structure

```bash
python3 scripts/validate-agentos-install.py /path/to/project
python3 /path/to/project/agent-os/tools/aos-lint.py
```

Validation checks installation structure, hook wiring, resident-rule projections, memory links, and document contracts. It does not prove that a runtime has trusted or invoked the hooks.

## 3. Start a fresh runtime session

Open a new Codex or Claude Code session in the target project. Review and trust changed project hooks when the runtime asks. Hook approval is runtime state and cannot be inferred from a successful file install.

## 4. Confirm behavior

For a long task, confirm that the session restores only the current goal, finish conditions, open items, and next action. Normal read commands should run without semantic hook warnings. When the long task reaches its finish line, its final delivery should receive one reread; a short direct answer should remain single-pass.

## Updating an existing project

Run the same installer command again. Replaced files are backed up under `.agentos-backups/<timestamp>/`. Existing `agent-os/state/**` and `wiki/**` files are not overwritten.
