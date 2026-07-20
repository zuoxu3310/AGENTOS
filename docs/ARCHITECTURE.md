# AgentOS Architecture

## The control loop

AgentOS implements one loop:

```text
understand and set a finish line
    → execute within the accepted scope
    → verify each finish condition
    → stop and deliver clearly
    → preserve only useful memory
```

The main model owns interpretation and judgment. A reusable skill may help it reason, review evidence, route memory, or compile a workflow. Hooks are deliberately narrower because a mechanical program cannot reliably infer product meaning from a command string or tool name.

## Runtime boundaries

### SessionStart

On startup, resume, clear, or compaction recovery, it injects only the current long-task goal, finish conditions, open items, next action, latest user change, and state path.

### UserPromptSubmit

For every real user message, it reminds the main model to reinterpret the request. Internal Stop continuations are marked and do not masquerade as new user work.

### PreToolUse

It performs only deterministic checks: Codex delegation must use the vendored Dynamic Workflow runner, worker prompts must contain the required XML structure, and structured tools may be denied when they explicitly name a forbidden target. It does not parse shell text to guess whether a command is important or mutating.

### PostToolUse

It stays silent for ordinary tools. A structured edit to AgentOS, the Wiki, or a governed root ledger runs the relevant linter and returns only mechanical failures.

### Stop

When a long task is complete or blocked and `report_state` is `pending`, Stop asks the same main model for one delivery reread. The second Stop releases the answer and records `delivered`. Short replies have no mandatory second generation.

## Long-task state

Long work uses one session-local `active_work` record with:

- a one-sentence goal;
- observable `done_when` conditions;
- only the `open_items` needed to reach those conditions;
- a `next_action` that names an open item;
- the latest user correction;
- active, blocked, or done status;
- report state;
- condition-by-condition evidence.

Several tools can serve one work segment. The system does not build an event graph or repeat the goal before every tool call. Once all conditions have evidence and no open item or blocker remains, additional “helpful” optimization is outside the contract.

## Canonical rules and projections

`agent-os/rules-card.md` is the only resident AgentOS rule body. The installer generates the AgentOS-managed block in `AGENTS.md` and creates Claude's native rules projection. Runtime configuration contains activation details, not another rule source.

## Workflows

Codex chooses direct work (`NO_DELEGATION`) or delegates through `vendor/claude-dynamic-workflows-codex`. That vendored runner is the only delegated execution engine. Claude uses its native Workflow and does not load the Codex adapter.

## Memory

The four root ledgers answer distinct questions: current plan, verified progress, durable decisions, and current handoff. The Wiki stores selectively loaded task notes, distilled chats, reusable knowledge, raw-source provenance, and confirmed error learning. Existing project memory belongs to the project and is preserved during updates.

## Evidence boundary

Automated checks can prove file structure, projections, hook response shapes, state validation, and observed test behavior. They cannot prove that a model understood the user correctly or that a real runtime trusted a changed hook. Those claims require live session evidence.
