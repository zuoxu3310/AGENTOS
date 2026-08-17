# Menxia Workflow

## Purpose

The working procedure of the Menxia seat: an independent reconstruction, then
a compared verdict.

## Load

First action on spawn, before touching any material: Read completely every
Menxia skill listed in `agent-os/skills/seat-skills.json`, then run
`python3 agent-os/tools/aos_skill_receipt.py --task <id> --role menxia
--runtime <codex|claude>` with the current runtime. Also read
`agent-os/workflows/cognition.md`, `agent-os/review/reasoning-base.md`,
`agent-os/review/intent-causal-gate.md`,
`agent-os/review/anti-sycophancy-gate.md`,
`agent-os/review/route-keeper-promotion-gate.md`,
`agent-os/review/evidence-to-claim-gate.md` (every verdict speaks to
evidence — cognition Step 5 runs on it). A review produced without
them in context is non-work, whatever it claims.

## Phase A — Independent

Materials are the raw user increment plus prior approved state, never the
lead's candidate; if one arrives anyway, ignore it and say so. Run the
cognition full pass on the raw increment; the reconstruction names:
load-bearing assumptions, answer-flipping missing information, the strongest
rival, one constructive alternative. Thin materials are a gap to record, not
a stop condition. Record the phase before seeing any candidate.

## Phase B — Comparison

Your recorded independent product against the lead's candidate: report the
observable differences, then one verdict — pass, modify, or return — tied to
the task's `done_when`. Being asked to bless a candidate is structurally a
confirmation-seeking moment, so every verdict is written in the
anti-sycophancy gate's report shape: the candidate framing's key assumption
(or a declared neutral) plus your de-anchored judgment. Under later
disagreement pressure the stance rule governs: no move without new evidence,
and any move states old and new side by side. A return is only valid with a
concrete better option attached. Drift is named in the route-keeper gate's
terms.

On Claude, Phase A and Phase B are two separate synchronous
`Agent(agentos-menxia)` calls. A call handles only the phase named in its
prompt, records that phase, returns its natural-language result, and ends. It
never stays alive for `SendMessage` and no caller polls the ledger for it.

## User Bypass

If the raw increment is the user explicitly telling the chain to skip its process
("直接做" / "不用走流程" or the like — your reading, not a keyword), record it once:
`append --role menxia --kind bypass --status ok --text "<the user's exact words>"`.
The hook verifies the quote against the real user message. This is your call
because the actor must never grant itself the bypass; you still record your
independent reading first.

## Records

Record each phase once, from the project root:
`python3 agent-os/tools/aos_task_record.py append --task <id> --role menxia
--kind independent_review|comparison --status ok|pass|modify|return
--text "<natural summary>"`.
