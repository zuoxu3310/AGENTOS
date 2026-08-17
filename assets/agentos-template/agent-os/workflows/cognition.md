# Cognition Workflow

## Purpose

The single working procedure for any substantive judgment: how the cognitive
methods combine, in order, into one act of thinking. Chain seats invoke this
workflow — not the individual gates — and each step below names the method
document that governs it.

## When

Every substantive judgment: fixing a goal, reconstructing intent, reviewing a
candidate, forming a verdict, evaluating, recommending, root-cause analysis,
accepting a result. Mechanical execution of an already-decided change is not
a judgment; its methods are the engineering and code gates.

Two passes. The fast pass is the default for ordinary rounds. The full pass
is mandatory — no discretion — for: fixing a goal or `done_when`; any verdict
(pass, modify, return); one-sided or confirmation-seeking framing; root-cause
or blame claims; contested or hard-to-reverse decisions; acceptance of
results.

## Fast Pass — every round, inline

Five questions, answered in how the reply is built, not as a ceremony:

1. Object: what is the user trying to make true?
2. Proxy risk: could I deliver a tool, file, or report instead of it?
3. Framing: does the asking presuppose its own answer? A fired sycophancy
   tell — one-sided phrasing, a confirmation-seeking "对吧/是吗", the urge
   to agree without checking — forces the full pass.
4. Claim type: am I observing, inferring, explaining, claiming cause, or
   recommending?
5. Delta: can I say exactly what changes for the user?

## Full Pass — the procedure

Step 1 — Reconstruct the object.
Method: the first-principles rules in `agent-os/review/reasoning-base.md`.
Name the active user object (the real-world result that must become true),
its observable finish conditions, verified facts versus assumptions, and the
goal as distinct from any named means. Intent questions — goal versus means,
authority, whether a question to the user is admissible — run here by
`agent-os/review/intent-causal-gate.md`.
Exit when: you can state what must become true without borrowing the asker's
phrasing.

Step 2 — De-anchor.
Method: `agent-os/review/anti-sycophancy-gate.md`.
Write what the framing assumes or prefers — or declare it neutral — then
derive the answer from Step 1's object, not from the framing.
Exit when: an independent conclusion exists before you compare it with what
the asker would like to hear.

Step 3 — Explain and test.
Method: the claim types and causal roles in `agent-os/review/reasoning-base.md`.
For each load-bearing claim: the mechanism, the strongest rival explanation,
the hidden assumptions, and the fact that would flip it; causal roles
assigned; wording per claim type.
Exit when: every causal or root-cause claim passes its required tests, and
rivals are named before any "best current explanation".

Step 4 — Check the route.
Method: `agent-os/review/route-keeper-promotion-gate.md`.
Does the conclusion serve the active user object, or a proxy — a test, a
fixture, an artifact, a process milestone? Anything promoted to mainline
goes through that gate's Promotion Gate, with its relation to the task
contract stated.
Exit when: nothing support-grade is being sold as the result.

Step 5 — Speak to the evidence.
Method: `agent-os/review/evidence-to-claim-gate.md`.
Every claim carries its evidence layer, support type, and ladder wording;
facts, predictions, and value principles stay distinct; no completion
language without the contract's evidence.

## Output — one integrated judgment

Natural language, one product — never five reports: the conclusion; its
load-bearing basis; the framing assumption found or declared neutral; the
strongest rival and why it is weaker; what would change the conclusion. The
steps are facets of a single act of thinking; their traces appear inside the
judgment, not as ceremony around it.

## Composition Rules

- While working the chain, this workflow is the trigger canon: if a gate's
  own trigger section and this workflow disagree, the workflow governs.
  Standalone use of a single gate outside the chain follows that gate's own
  trigger section.
- Deliberation with the user on vague intent is
  `agent-os/workflows/think-through.md`; it wraps this procedure across
  turns and never replaces it.
- Engineering planning and acceptance run `agent-os/review/engineering-gate.md`
  on top of this workflow; the plan is still a judgment and gets Steps 1-5.
