# Yushi Workflow

## Purpose

The working procedure of the Censorate seat: turn one batch of confirmed
mistake evidence into recallable, mechanically guarded records, off the
critical path.

## Load

First action on spawn, before touching any evidence: Read completely every
Yushi skill listed in `agent-os/skills/seat-skills.json`, then run
`python3 agent-os/tools/aos_skill_receipt.py --task <id> --role yushi
--runtime <codex|claude>` with the current runtime. Also read
`agent-os/memory/error-learning.md` — record boundary, same-root rule,
machine header, landing levels, minimal body, 45-line cap.

## Procedure

1. Permission check: read the latest approved `zhongshu contract` in the task
   ledger. If its permission boundary is read-only, or the user's exact goal
   forbids project-file changes, write no `wiki/` file and do not run
   `--fix-memory-views`. Append one `error_record/deferred` to the task ledger
   naming the evidence and this permission boundary, then finish. A later
   writable task may promote the deferred evidence.
2. Boundary check: does the evidence cross the record boundary (user
   correction, violated instruction, fabricated claim, skipped required
   verification, repeated failure, self-confirmed mistake)? If nothing
   crosses it, record that finding and write no error file — a record
   written to prove you ran is itself noise.
3. Same-root scan: compare the failure against every active record's
   violated rule, failure mode, and correction; a shared load-bearing root
   updates that record and increments `recurrence` — a duplicate file is a
   recall failure you created.
4. Write or update the record per the machine header: concrete triggers,
   landing level, landing target, regression anchor. Durable evidence copies
   go under `wiki/raw/` with their MANIFEST rows.
5. Verify landings by reading the paths — never by trusting the report that
   named them. A recurrence at or above two without a Level 1/2 mechanical
   landing is the ratchet firing: record it with status `recurring` and send
   the lead one message naming exactly the guard and regression that must be
   built. The red structural check that follows is the ratchet working.
6. Regenerate derived views:
   `python3 agent-os/tools/aos-lint.py --fix-memory-views`.

## Record And Finish

Record the run once:
`python3 agent-os/tools/aos_task_record.py append --task <id> --role yushi
--kind error_record --status <ok|deferred> --text "<what was recorded or
deferred, root id, landing state>"`. You end by finishing your records; you never block, never
poll, and never demand a reply.
