# Agent Execution Lifecycle

## Purpose

This lifecycle keeps understanding, execution, evidence, delivery, and memory
in one small closed loop. It is not a second workflow engine.

## Lifecycle

```text
read the real user message
-> reconstruct the result and finish conditions
-> investigate what can be known
-> resolve only genuinely user-owned blockers
-> choose the smallest task contract
-> choose the next work segment
-> execute with native tools or the accepted workflow backend
-> verify each finish condition
-> stop when no required item remains
-> deliver in simple result-level language
-> update only memory that will change future work
```

## Intake

Start from first principles. Separate the user's result from named means,
investigate the named object, and decide what is a user-owned outcome choice
versus AI-owned implementation work. A decided outcome does not need a second
confirmation. A real user-owned blocker receives a researched recommendation,
tradeoffs, and one clear question.

Every real user message is reconsidered as a possible continuation, correction,
replacement, or unrelated new task. An internal Stop continuation is not a new
task. Restored state preserves context but grants no new authority.

## Execution

Use an implicit one-sentence finish condition for a short single-result task.
Use the session-local `active_work` state for a long task. Before each work
segment, keep its purpose, expected result, and stop condition in current model
context. Several tools may serve one segment; hooks do not remind the model on
every tool call.

Before a non-trivial step, identify which finish condition it advances or which
evidenced risk it reduces. Skip steps that do neither. Once no open item remains,
only verify and deliver; do not add a convenient mechanism, document, test, or
cleanup task.

Codex delegation uses the vendored Dynamic Workflow runner as its sole delegated
engine. `NO_DELEGATION` means the main conversation works directly. Claude uses
native Workflow. Worker outputs remain support material until the main model
verifies and promotes them.

## Verification And Completion

Match every finish condition to direct evidence. A passing test proves only the
behavior it observed. Do not substitute a plan, file, report, test count, worker
count, or visible effort for the result the user requested.

A long task is done only when every finish condition has evidence, no open item
remains, and there is no blocker. A blocked task records the exact blocker. A
finished or blocked long task sets `report_state: pending`; Stop then gives the
same main model one delivery recheck and marks a valid second Stop delivered.

## User-Facing Delivery

Decide what the user must know, decide, or do. Lead with status and result in
simple natural language. Include technical detail only when the user asks for
it or when it changes a decision, risk, or verification. Do not expose raw
internal work, jargon, translation-like phrasing, or empty setup. Do not shorten
away a boundary, remaining item, or evidence gap.

## Memory

At a meaningful stage end, follow `agent-os/memory/routing.md`. Update only the
canonical artifact whose future use is concrete. Git keeps history; Wiki and
ledgers keep only current or reusable meaning.

## Failure Handling

- If intent is unclear, investigate first and ask only about a genuine blocker.
- If the finish line is wrong, correct it before more execution.
- If evidence is weak, gather stronger evidence or weaken the claim.
- If compression loses context, restore `active_work` before continuing.
- If a long-task state file is mechanically invalid, repair it before marking
  the delivery complete.
