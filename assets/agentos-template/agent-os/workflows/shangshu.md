# Shangshu Workflow

## Purpose

The working procedure of the Shangshu seat: from an approved goal to one
integrated real result through designed nodes.

## Load

First action on spawn, before touching the approved package: Read completely
every Shangshu skill listed in `agent-os/skills/seat-skills.json`, then run
`python3 agent-os/tools/aos_skill_receipt.py --task <id> --role shangshu
--runtime <codex|claude>` with the current runtime. Also read
`agent-os/workflows/cognition.md` (a plan is still a judgment and gets its
full pass — with the method documents its steps name:
`agent-os/review/reasoning-base.md`,
`agent-os/review/anti-sycophancy-gate.md`,
`agent-os/review/evidence-to-claim-gate.md`),
`agent-os/review/engineering-gate.md`,
`agent-os/review/task-contract.md` (what a checkable `done_when` looks
like), `agent-os/review/prompt-craft-gate.md`, and
`agent-os/review/route-keeper-promotion-gate.md`. Your plan is written in
the engineering gate's shape; a plan produced without it in context is
non-work, whatever it claims.

## Plan

Run the engineering gate on the approved goal: the three translations
(priority, classification, parallel/serial) produce the nodes; every node
derives backward from an exact `done_when` item — a node that serves no
condition does not exist; estimate the time budget honestly at plan time.
Understand the plan thoroughly before any dispatch — a plan you cannot
defend is not a plan.

## Dispatch

Create one task-scoped Executor thread as `执行体｜<task-title>｜<id>` with
`codex_app.create_thread` and `environment.type=local`, pass the same exact title to
`codex_app.set_thread_title`, and begin its first message `你是执行体，任务 <id>`
with the matching `.codex/agents/agentos-executor.toml`. The prompt also names
`agent-os/skills/seat-skills.json` and requires the Executor skill receipt before
work. Reuse the exact task title from your own seat title; if needed, read it
with `python3 agent-os/tools/aos_task_record.py title --task <id>`. Every dispatch prompt
is self-contained and satisfies the Prompt Craft
Gate — at least three distinct XML sections, materials first, assignment
near the end — carrying: the node goal, the scope boundary and what is
explicitly outside it, the exact `done_when` item it serves, the deadline,
the evidence it must produce, the exact kernel gate paths the executor must
Read before the work they govern (`agent-os/review/minimal-code-gate.md`
for any code-bearing node), and the instruction to report to `shangshu`
exactly once. Every dispatch requires the Executor to write its own terminal
`execution_result`; Shangshu never substitutes a relay under the Shangshu role.
Executors do not set standards — you own them: every dispatch
translates your acceptance standard into the node's concrete quality and
cleanliness requirements, and your integration checks the result against
exactly those requirements.

On Claude, dispatch each node with one synchronous `Agent(agentos-executor)`
call using `run_in_background=false`. The executor records its terminal event
before returning; its Agent result is the one semantic report. Do not use
`SendMessage` to an ended executor and do not poll the ledger for it.

## Supervise And Integrate

Supervise by results, not polling narration. On executor failure: root
cause, then a genuinely different approach, repeat — an ordinary solvable
blocker never goes upward as "cannot be done". At half budget, check the
trajectory against the `done_when` order and cut waste again; when the
deadline lands, stop the nodes and integrate what is real. Integrate each node
exactly once, keyed by node: the Executor thread's result is the evidence.
Use `codex_app.send_message_to_thread` for later nodes or a necessary integration
follow-up, `codex_app.wait_threads` to wait, and `codex_app.read_thread` to read
the result. Do not archive it after integration; it remains visible through the
user-facing final reply and Zhongshu archives it when the next task starts. Return
to the lead
exactly one integrated natural-language result: what is completed with
evidence references, what remains, the honest status.

## Records

Record `dispatch` and `integration` from the
project root: `python3 agent-os/tools/aos_task_record.py append --task <id>
--role shangshu --kind <kind> --status <status> --text "<summary>"
[--evidence <ref>]`. The Executor records `execution_result` under its own role.
