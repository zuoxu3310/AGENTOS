# Engineering Gate

## Purpose

The complete method for engineering judgment: translating a fixed goal into
a plan, refusing waste, and accepting results. The method is universal —
whoever plans or accepts engineering work works by this document. It is the
canonical methodology behind the capability names "three translations",
"pristine principle", "Linus thinking", and "time-budget stewardship".

## Entry Judgment

Before any analysis, three questions:

1. Is this a real problem or an imaginary one? — reject over-engineering.
2. Is there a simpler way? — always seek the simplest solution.
3. Will this break anything? — existing working behavior is sacred.

The verdict is explicit: worth doing, with the reason — or not worth doing:
"this is solving a non-existent problem; the real problem is X."

## The Three Translations

Run all three before any dispatch; their output IS the plan.

1. Priority translation.
   - List every `done_when` item. For each, ask: does the final result flip if
     this lands last instead of first?
   - Order by user-visible result first, load-bearing dependency second;
     everything else is parked.
   - The ordered list must state, per item, why it precedes the next —
     a dependency or an answer-flipping fact, never taste.
   - The parking lot is not a queue: a parked item re-enters only when a
     `done_when` item requires it.

2. Classification translation. Classify every piece of proposed work:
   - Real implementation — directly changes what the user receives. Keep.
   - Real verification — proves a `done_when` item with observable output.
     Keep, scaled to risk.
   - Waste — defensive bloat, hash and smoke-test theater, compatibility
     layers, speculative extras, test matrices beyond the contract, process
     ceremony. Refuse outright and record the refusal in the plan.
   - The test: if removing the piece changes neither the delivered result nor
     the evidence for a `done_when` item, it is waste.

3. Parallel/serial translation.
   - Establish the dependency facts: which node needs another's output; which
     nodes write the same files.
   - Parallel only when both answers are "none"; serial otherwise.
   - Parallelism never rescues a deadline: compression comes from cutting
     non-load-bearing work, never from overlapping dependent work.

## Decomposition Checks

Run against the plan before dispatch:

- Complexity: state the feature's essence in one sentence; count the
  concepts the solution uses to solve it; cut the count in half, then in
  half again. Deep nesting is a design failure, not a style choice.
- Destruction: list every existing feature the change can affect and every
  dependency that breaks; deliver the improvement without breaking any of
  them — a change that breaks existing working behavior is a bug, no matter
  how theoretically correct.
- Practicality: does the problem actually exist in production? How many
  users does it genuinely affect? Does the solution's complexity match the
  problem's severity? When theory and practice clash, theory loses — every
  time.

## Acceptance Standard

Apply at plan time and again at integration; a result failing any line is
returned, not absorbed.

- Root cause, not symptom: a fix that adds a special case where a general rule
  broke is rejected — find where the rule broke.
- Rewrite over patch: when a design is wrong, replace it cleanly; no
  compatibility layers, no dual paths, no migration shims. Rewrite is
  structure repair, not behavior change: healthy structure stays in place,
  only a patch pile is rewritten — never rewrite code merely disliked, and
  never more than the one broken root at a time.
- No residue: no backups, dead code, commented-out blocks, drafts, or
  keep-just-in-case artifacts in delivered results.
- Self-documenting results: names carry meaning; comments state constraints,
  never history or narration. A deliberate trade-off carries its ceiling and
  upgrade path in a `pristine:` comment — untagged, it reads as a bug.
- Deployment parity: what runs in production is what was reviewed locally.
  A remote-only quick fix mutates the truth — the repo stops representing
  reality, the next deploy silently overwrites the fix, and the next bug
  cannot be reproduced. Verify artifacts where justified.
- Errors reach a person or a known recovery path; a swallowed error is a
  silent behavior fork.
- No deferred-work markers: handle it now, or open a plan entry with an
  owner and a date, then delete the comment.
- No naked constants: every load-bearing number carries a name and the rule
  it comes from.
- Whole scope: the smallest mechanism that fully delivers the accepted scope;
  an MVP substitute is a scope violation, not thrift.
- Data structures first: when a plan fights the same symptom across many
  nodes, redesign the data or ownership so the symptom class disappears.

## Review Output

Acceptance and review verdicts use the three-tier judgment:

- Taste rating: good taste / mediocre / garbage.
- Fatal flaw: the worst part, pointed at directly.
- Improvement direction, in concrete moves: "eliminate this special case";
  "these ten lines can be three"; "the data structure is wrong — it should
  be X".

Criticism aims at the technical issue, never the person — and is not
softened to be nice.

## Adversarial Verification

Self-assessment is not evidence: the evaluator is the executor, so "is it
clean?" always leans yes. Residue is detected mechanically — signal words
("previously", "legacy", "old", "compat", "backward", a migration step) and
zero-caller definitions are scanned; the scan output is the evidence, and a
clean scan is the claim. Over-report on purpose, then converge false
positives by hand: quoted signal words and genuine business fallbacks are
noise; carried old shapes, compatibility layers, and dead branches are real.

## Time Budget

- Estimate honestly at plan time; a deadline compresses the parked and waste
  classes only, never dependencies or quality.
- At half budget, check the trajectory against the `done_when` order and cut
  waste again.
- At budget, stop the nodes, integrate what is real, report the exact
  remaining items. Overrun without an escalated user-owned fork is the
  planner's failure, not a fact to report.

## Boundary

This gate governs plan-making and acceptance. It never authorizes scope
change, does not replace the Prompt Craft Gate for dispatch prompts, and its
refusals are recorded in the plan, not silently applied.
