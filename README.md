# AgentOS

AgentOS is a repository-local operating layer for Codex and Claude Code. It helps an AI keep the user's real goal in view, work against explicit finish conditions, verify what it claims, preserve useful project memory, and stop when the job is done.

The design has one important boundary: AI performs semantic judgment; hooks only restore attention or check facts that software can determine reliably.

## What it changes

- Ordinary chat stays ordinary. Nothing about the chain applies until the user invokes the `agentos` skill (`$agentos` in Codex Desktop, `/agentos` in Claude Code).
- When invoked, the current session becomes a **relay** (太监): it writes the user's exact words to a task record, opens the **中书 (Zhongshu)** seat, and carries messages back and forth verbatim. It never summarizes, thinks for a seat, or edits files.
- The chain (三省六部) then runs as separate seats: 中书 (understanding + the one final delivery) → 门下 (independent review of the raw request first, then a compared verdict: pass / modify / return) → 尚书 (execution owner) → one-shot **executor** (the only seat that changes the workspace) → 尚书 integration → 中书 verification and delivery; a background 御史 records confirmed mistakes.
- On Codex Desktop every seat is a visible thread titled `<seat>｜<task>`, created with the Desktop's own `codex_app` thread tools; on Claude Code seats are native subagents.
- Order is enforced by one shared hook (`aos_chain_gate.py`) on two mechanical facts only: who is calling (runtime agent identity / hook-owned thread registry) and what the append-only task ledger says. Deny reasons always name the next legal step. Reads are never denied; unbound sessions see silent hooks.
- Each seat must read its listed skills (`agent-os/skills/seat-skills.json`) and record a hash receipt before phase work; ledger lines can only be written as the caller's own seat; the user's bypass is recorded only by 门下 quoting the user verbatim.
- Long tasks keep a small session-local `active_work` record; pause, stop, and resume are relay commands; delivery unbinds the session.

## Install

Python 3 is the only installer dependency.

```bash
git clone https://github.com/zuoxu3310/AGENTOS.git
python3 AGENTOS/scripts/install-agentos.py /path/to/project
python3 AGENTOS/scripts/validate-agentos-install.py /path/to/project
python3 /path/to/project/agent-os/tools/aos-lint.py
```

The installer merges user entry documents and runtime configuration. Existing `agent-os/state/**` and `wiki/**` files are preserved. Replaced files are backed up under the target project's `.agentos-backups/` directory.

After installation or an update, start a new Codex or Claude session in the project. Changed project hooks may require approval before they run.

## Use

Open a session in the installed project. Chat normally, or run the chain:

```text
$agentos 帮我检查这个项目当前是否存在一个明显且可复现的问题     # Codex Desktop
/agentos 请只读确认项目根目录是否有 README.md，并告诉我首行      # Claude Code
```

Everything you say afterwards is relayed verbatim to 中书 until it records the delivery. Say "先停" / "关掉" to pause or stop, and `$agentos 继续 <task-id>` to resume; the relay lists open tasks with `python3 agent-os/tools/aos_task_record.py board`.

## Architecture

```text
user message ── (ordinary chat unless the user invokes `agentos`)
    ↓ relay writes the exact words to the task ledger, opens 中书省｜<task>
中书  reconstructs the goal; sends the RAW increment to 门下 first
门下  Phase A independent reading → Phase B compared verdict (pass/modify/return)
中书  records the contract; hands the approved package to 尚书 verbatim
尚书  plans, records dispatch, creates the one-shot executor, verifies, integrates
中书  verifies against done_when, records delivery → relay returns it verbatim
御史  (background) records confirmed mistakes under wiki/errors/
```

The repository installs these layers:

- `agent-os/`: rules card, review gates, seat workflows, seat-skill manifest, ledger/receipt/lint tools, memory contract.
- `.claude/skills/agentos/` and `.agents/skills/agentos/`: the relay skill for Claude Code and Codex.
- `.claude/agents/agentos-*.md` and `.codex/agents/agentos-*.toml`: the seat contracts (zhongshu, menxia, shangshu, executor, yushi).
- `.claude/hooks/` and `.codex/hooks/`: attention hooks plus the shared chain gate (`aos_chain_gate.py`, byte-identical in both).
- `AGENTS.md`, `CLAUDE.md`, `.codex/config.toml`, `.claude/settings.json`: seat-neutral entry surfaces and hook wiring.
- `PLANS.md`, `PROGRESS.md`, `DECISIONS.md`, `HANDOFF.md`, and `wiki/`: project-owned memory.

## What hooks do not do

Hooks do not decide user intent, whether an action is important, whether a route is correct, or whether an answer is good. Those are semantic judgments for the main model and reusable skills. The linter proves document and installation structure only; it does not prove behavioral quality.

## Verify the release bundle

```bash
python3 scripts/test_installer_behavior.py
python3 assets/agentos-template/agent-os/tools/aos-lint.py
cd assets/agentos-template
python3 -m unittest discover -s tests/unit -p 'test_*.py'
python3 -m unittest discover -s tests/integration -p 'test_*.py'
python3 -m unittest discover -s tests/scenarios -p 'test_*.py'
```

See [Quickstart](docs/QUICKSTART.md) for installation details and [Architecture](docs/ARCHITECTURE.md) for the runtime flow.

## License

Apache-2.0.
