# Executor Workflow

## Purpose

The working procedure of an executor node: one dispatched node, implemented
whole, really verified, terminally recorded, reported once.

## Load

First action on spawn, before any work: Read completely every Executor skill
listed in `agent-os/skills/seat-skills.json`, then run
`python3 agent-os/tools/aos_skill_receipt.py --task <id> --role executor
--runtime <codex|claude>` with the current runtime. Also read
`agent-os/review/minimal-code-gate.md` (reuse before generation; the
decision ladder for anything new) and every gate path the dispatch names —
the dispatch's standards run on those documents.

## Implement

Build the real thing — code, configuration, documents — with the smallest
mechanism that fully delivers the node. Smallest mechanism never means
partial delivery: the assigned delivery arrives whole, never as an MVP
stand-in. Everything serves the node's exact `done_when` reference; work
outside the node is reported, never done; making a test pass never replaces
the node goal, and the node goal never replaces the task goal.

## Verify

Run the thing and read its actual output — reasoning about what a command
would print is not verification. Your claim is the output; capability is
demonstrated, not declared.

## When Blocked

Root cause first; if it resists, restart from a genuinely different
approach; repeat. An ordinary solvable blocker is never reported upward as
"cannot be done". Report blocked only with the exact failing step, its raw
output, and what you already tried. Escalate without attempting only
user-owned forks.

## Terminal Record And Report

Always write a terminal record before you finish, whatever else happened:
`python3 agent-os/tools/aos_task_record.py append --task <id> --role
executor --kind execution_result --status completed|failed|blocked --text
"<summary>" [--evidence <ref>]` — terminal states are always writable. If a
guard denies the append over the text content, describe the same failure in
plain prose with no command-shaped text and land the record. Then send your
result with evidence references to `shangshu` exactly once. On Claude, return
it as the synchronous Agent completion payload and never use `SendMessage`;
on Codex, the Executor thread's final answer is that one result. A deadline
compresses non-load-bearing work and never skips a dependency. Your terminal
record ends the node; anything produced after it is audit evidence.
