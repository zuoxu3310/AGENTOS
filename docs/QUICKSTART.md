# AgentOS Quickstart

## 1. Install into a project

```bash
python3 scripts/install-agentos.py /path/to/project
```

The installer adds the AgentOS kernel, the `agentos` relay skill, the seat contracts, and the runtime hooks. Existing entry documents and configuration are merged; existing Wiki and AgentOS state files are preserved. Use `--dry-run` to inspect the planned actions first.

## 2. Validate the installed structure

```bash
python3 scripts/validate-agentos-install.py /path/to/project
python3 /path/to/project/agent-os/tools/aos-lint.py
```

Validation proves structure, hook wiring, projections, and document contracts. It does not prove that a runtime has trusted or invoked the hooks.

## 3. Start a session — ordinary chat by default

Open a new Codex Desktop or Claude Code session in the project and approve the changed project hooks when the runtime asks. Nothing about the chain applies yet; SessionStart only says that AgentOS is installed.

## 4. Run the chain when you want it

```text
$agentos <your request>     # Codex Desktop
/agentos <your request>     # Claude Code
```

The session becomes the relay: it records your exact words, opens `中书省｜<task>` (a visible Desktop thread on Codex, a subagent on Claude), and relays every later message verbatim. 中书 opens 门下省 and 尚书省; 尚书 opens 执行体; 御史台 appears only for confirmed mistakes. Watch the task ledger at `agent-os/state/tasks/<task>.jsonl`: skill receipts, 门下 Phase A before any candidate, comparison pass, dispatch, one executor result, integration, delivery.

Say "先停" or "关掉" to pause or stop; `$agentos 继续 <task>` (or `/agentos 继续 <task>`) resumes; after delivery the session is ordinary chat again.

## Updating an existing project

Run the same installer command again. Replaced files are backed up under `.agentos-backups/<timestamp>/`; `agent-os/state/**` and `wiki/**` are never overwritten; retired AgentOS files (old controllers, forced entry agents) are removed after backup.
