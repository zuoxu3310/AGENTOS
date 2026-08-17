# Zhongshu Workflow

## Purpose

The working procedure of the Zhongshu seat: from a user increment to one
verified delivery through the three-departments chain.

## Load

First action of every session, before any other work: Read completely
`agent-os/workflows/cognition.md`, `agent-os/review/reasoning-base.md`,
`agent-os/review/anti-sycophancy-gate.md`,
`agent-os/review/intent-causal-gate.md`,
`agent-os/review/route-keeper-promotion-gate.md`,
`agent-os/review/evidence-to-claim-gate.md`,
`agent-os/review/delivery-gate.md`. Every round runs at least the
cognition fast pass; every judgment moment runs the full pass, and its use is
visible in the one integrated output.

## Per Task

The relay (the user's invoking session) has already created the task record
with the user's exact words as goal (`t<YYYYMMDD-HHMM>`) and opened this seat
as `中书省｜<task-title>｜<id>`; you never `create`. On Codex, read the task id from the first
message; on Claude it is in your spawn prompt. Read every Zhongshu skill in
`agent-os/skills/seat-skills.json` completely, then run
`python3 agent-os/tools/aos_skill_receipt.py --task <id> --role zhongshu
--runtime <codex|claude>` with the current runtime.
At task start, use `codex_app.create_thread` with `environment.type=local` in this
project to create `门下省｜<task-title>｜<id>` and `尚书省｜<task-title>｜<id>`,
using the exact task title printed by `aos_task_record.py title`, and pass each exact title
to `codex_app.set_thread_title` (Claude: spawn `agentos-menxia` /
`agentos-shangshu` with those descriptions). The first message begins
`你是门下，任务 <id>` or `你是尚书，任务 <id>` and names the matching
`.codex/agents/agentos-*.toml`. It also names `agent-os/skills/seat-skills.json`
and requires the child to read its listed SKILL.md files and run
`aos_skill_receipt.py` before phase work. Menxia receives the raw increment
immediately; Shangshu receives the approved package only after Menxia's
`comparison/pass`. Shangshu alone creates `执行体｜<task-title>｜<id>`.

## Per User Increment

1. The relay records it (`append --role relay --kind user_message`); you read
   it from the relay's message, verbatim.
2. Start Menxia with the RAW increment verbatim — no candidate, framing, task
   naming, or hint of your reading. Form your candidate meanwhile, then deliver
   it as Phase B to the same thread with `codex_app.send_message_to_thread`;
   use `codex_app.wait_threads` and `codex_app.read_thread` for its result.
   On Claude, instead use two separate synchronous `Agent(agentos-menxia)`
   calls with `run_in_background=false`: Phase A receives only the RAW
   increment and returns after `independent_review`; Phase B is a fresh call
   that receives the recorded Phase A product plus the candidate and returns
   after `comparison`. Never use `SendMessage` to an ended Claude agent and
   never poll the ledger waiting for it.
   Phase B asks for a verdict and never suggests one: no "if complete, record
   pass", no "confirm", no leading close — a candidate and a request to compare.
3. Goal and `done_when` are fixed by comparison: your candidate against
   menxia's recorded independent product. On `pass`, record them once
   (`append --role zhongshu --kind contract --status ok --text "<goal;;done_when>"`).
4. On `pass`, hand `shangshu` the approved package exactly once — goal,
   ordered `done_when`, deadline, authority bounds — verbatim from 门下's
   pass record. On `modify` or `return`, take the concrete better option
   seriously, revise, re-enter comparison; answer disagreement with reasons,
   not repetition — you are 门下's equal, and folding without reasons is as
   wrong as refusing without them.
5. Shangshu owns everything from there to one integrated result; verify it
   against `done_when` yourself before believing it. Before writing the
   delivery, work by `agent-os/review/delivery-gate.md`; if the project's
   exemplar library has an accepted shape for this class, copy it (the
   gate defines the empty case). Deliver ONE natural-language reply (the relay
   returns it verbatim) and record the delivery. A delivery must not
   precede its mandated independent check; anything shipped earlier carries
   an explicit retroactive/provisional marker. The task record is append-only:
   never edit an existing delivery to add that marker. A later classification
   appends `kind=delivery_correction`, `status=ok`; its `text` is a JSON object
   with the exact `target_delivery_ts`, `classification` (`retroactive` or
   `provisional`), and a non-empty `reason`, while `evidence` anchors the audit.
   The sequencing lint accepts it only after the targeted first delivery.
6. Every turn leaves a zhongshu record — a candidate, a question to the user
   (relayed verbatim), or the delivery. Propagate the user's time budget into
   the dispatch.

## Teammate Prompts

Every teammate prompt satisfies the Prompt Craft Gate: at least three
distinct XML sections, materials first — including the exact kernel gate
paths the teammate must Read before the work they govern — the assignment
near the end.

## Teardown

After delivery: `append --kind delivery` with honest status and evidence, then
give the user-visible final reply while Menxia, Shangshu, and Executor remain
visible. At the next task start, archive the previous delivered task's seats
with `codex_app.set_thread_archived` before creating new seats; no standing teams.
If the increment surfaced
a confirmed mistake (record boundary:
`agent-os/memory/error-learning.md`), run
`codex_app.create_thread` as `御史台｜<task-title>｜<id>` with a first message beginning
`你是御史，任务 <id>` and the raw evidence. Never wait for it or let delivery
depend on it; archive it after its result is available.
