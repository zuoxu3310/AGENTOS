# Task Contract

## Purpose

Task Contract states what the user must receive before work starts, keeps long
tasks intact across messages and compression, and makes the AI stop at the
finish line.

## Choose The Smallest Contract

A short, clear, single-result task uses one implicit finish sentence and no
state file. Use persistent `active_work` when the task crosses user messages,
contains several work segments or finish conditions, may be compressed or
delegated, or otherwise needs recovery.

Do not create persistent state merely because several tools are useful. Several
tools can belong to one work segment with one purpose, expected result, and stop
condition held in the current model context.

## Long-Task State

Each runtime session owns one local JSON state file under
`agent-os/state/active-work/`:

```yaml
active_work:
  goal: one sentence describing the result the user must receive
  done_when:
    - observable, falsifiable finish condition
  open_items:
    - unfinished work required by done_when
  next_action: an exact member of open_items, or empty when none is actionable
  latest_user_delta: what the latest real user message changed
  status: active | blocked | done
  blocker: filled only when blocked
  report_state: not_due | pending | delivered
  completion:
    - condition: exact string from done_when
      evidence:
        - file, command result, runtime observation, or other direct evidence
```

## Rules

- `open_items` may contain only work required by `done_when`.
- `next_action` must be a real open item while work is active.
- A new user message changes only what it actually addresses. Preserve every
  unaffected finish condition and open item.
- State restored after startup, resume, clear, or compression preserves
  attention, not execution authority.
- The current work segment is not another file or event graph. Several tools
  may run inside it without repeated reminders.
- Do not call a task done until every `done_when` condition appears exactly once
  in `completion` with relevant evidence, `open_items` is empty, and no blocker
  remains.
- When done, do not add more work. Verify, set `report_state: pending`, deliver,
  and stop. Reopen work only when new evidence or a later user message creates a
  real obligation.
- When blocked, record the blocker and set `report_state: pending` if a formal
  user report is due.
- Hooks do not decide whether a task is long, what the goal means, or whether a
  user message changes it. The main model and task skills make those judgments.

## Evidence Boundary

Tests, files, plans, reports, source gates, and worker reports are support
artifacts unless the user asked for them. Evidence must prove the corresponding
finish condition, not merely that work happened.

Before completion wording, use:

```text
agent-os/review/completion-gate.md
agent-os/review/evidence-to-claim-gate.md
```

## Delivery Boundary

For a finished or blocked long task, the first Stop continues the same main
model once. Recheck whether the task is actually done, what the user received,
what remains, and what the user must decide or do. Then remove avoidable jargon,
translation-like wording, internal process detail, and filler without hiding a
risk, boundary, or unfinished item.

Short replies are delivered on the first generation unless later live tests
show a real need for a different rule.
