# AgentOS Quickstart

Get AgentOS running in a project in under a minute. Requirements: **Python 3** (for the
installer and hooks) and, for the end-to-end check, **Node.js**.

## 1. Get the installer

```bash
git clone https://github.com/zuoxu3310/AGENTOS.git
```

## 2. Install the kernel into your project

```bash
python3 AGENTOS/scripts/install-agentos.py /path/to/your/project
```

This copies the `agent-os/` kernel plus the runtime adapters into your project. It is
non-destructive: existing `CLAUDE.md` and the root ledgers are merged (a marked AgentOS
block is appended), and anything replaced is backed up under `.agentos-backups/`.

## 3. Validate

```bash
python3 AGENTOS/scripts/validate-agentos-install.py /path/to/your/project
python3 /path/to/your/project/agent-os/tools/aos-lint.py
```

`validate` should print `"status": "passed"` with `hook_wiring: wired` for both Claude
and Codex. `aos-lint` should print `AgentOS structural lint PASS`.

## 4. Start a session

Open the project in Claude Code or Codex. On the **next** session:

- The SessionStart hook injects the rules card and the current state digest.
- Each turn must append a per-turn audit entry, or the Stop hook blocks the turn from
  finishing.
- The first session may ask you to approve the new project hooks — approve them to
  enable enforcement.

## 5. Configure the two policy slots (optional)

AgentOS ships persona-neutral. If you want them:

- **Owner tag** — set the "Start every user-facing answer with …" line in `AGENTS.md`
  and `.codex/agentos-local-rules.md`.
- **Output language** — set the "Language and reader policy" block in `AGENTS.md`,
  `.claude/rules/agentos-local-rules.md`, and `.codex/agentos-local-rules.md`.

## Upgrading

Re-run the installer against the same project. The kernel and adapters are synced;
`AGENTS.md` is re-projected and the old copy is backed up; your **live state**
(`agent-os/state/`) and **`wiki/`** are preserved untouched.

## Disabling hooks temporarily

```bash
export AOS_HOOK_DISABLE=1   # hooks degrade to no-ops
```

## Troubleshooting

- **`validate` shows `stop-hook-not-wired`** — the target's `.claude/settings.json` or
  `.codex/hooks.json` did not merge the Stop hook. Re-run the installer; it JSON-merges
  and never removes your existing settings.
- **`aos-lint` FAIL: missing pattern** — a kernel file was edited so a required section
  no longer matches. The failure names the exact file and pattern.
- **A turn won't finish** — the Stop hook is doing its job: append the per-turn audit
  entry to `agent-os/state/audit-log.md` and end your answer with the audit block.
