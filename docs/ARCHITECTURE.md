# AgentOS Architecture

## Why

A model under pressure drifts toward the appearance of work: agreeing, skipping review, declaring done. AgentOS separates understanding, independent review, and execution ownership into seats so no single thread can fake all three, and enforces their order with hooks that only look at mechanical facts.

## The chain (三省六部)

```text
relay (太监)   the user's session once `agentos` is invoked; carries exact words both ways
中书 Zhongshu  reconstructs the goal; sends the RAW increment to 门下 before forming a candidate;
               fixes the contract after 门下 pass; verifies and records the one delivery
门下 Menxia    Phase A independent reading (never sees the candidate first); Phase B compared verdict;
               the only seat that may record the user's bypass, quoting the user verbatim
尚书 Shangshu  turns the approved package into a plan, records dispatch, creates the one-shot
               executor, verifies its evidence, records integration
执行体          the only seat that changes the workspace, and only after a dispatch
御史 Yushi     background scribe of confirmed mistakes (wiki/errors/)
```

Codex Desktop: seats are project threads created with the Desktop's `codex_app` tools and titled `<seat>｜<task>`; the relay may open only 中书省; 中书 opens 门下省/尚书省/御史台; 尚书 opens 执行体. Claude Code: seats are native subagents (`.claude/agents/agentos-*.md`) spawned the same way.

## Mechanical enforcement

One shared hook, `aos_chain_gate.py` (byte-identical for both runtimes), decides on two facts:

1. **Who is calling** — the runtime's agent identity on Claude, or the hook-owned thread registry (`agent-os/state/seats.json`, `agent-os/state/sessions/`) on Codex. A session that invoked `agentos` is bound as the relay; a session that did not is unbound and every hook is silent for it.
2. **What the ledger says** — the append-only task record `agent-os/state/tasks/<task>.jsonl`.

From these it enforces: the relay creates a task only with the user's exact words and no finish conditions; ledger lines are written only as the caller's own seat; skill receipts (`aos_skill_receipt.py`, SHA-256 of each seat's SKILL.md) before phase work; 门下 pass before 尚书 receives work; dispatch before the executor writes; terminal and failure records always writable; reads never denied; deny reasons name the next legal step. Nothing in the hooks classifies user intent from keywords.

## Long-task state and memory

Long work keeps a small session-local `active_work` record (goal, `done_when`, open items, next action, status, evidence). Pause/stop/resume are relay ledger records; delivery unbinds the relay. Project memory lives in the four root ledgers and `wiki/`; both survive updates.

## Evidence boundary

Tests, the linter, and the validator prove structure and hook behaviour on recorded inputs. Only a live session proves that a runtime trusted the hooks and that the seats did the thinking their skills require.
