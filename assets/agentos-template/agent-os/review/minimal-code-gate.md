# Minimal Work And Code Gate

## Purpose

Prevent unnecessary code, dependencies, and feature surface at the moment they
would be created, while preserving the full accepted user-visible result.

Use the least mechanism that fully delivers the contracted scope. Minimal
mechanism never means partial functionality. The best code is the code never
written — lazy means efficient, not careless.

This gate prevents both over-engineering and performative work. Code, documents,
tests, abstractions, tools, workers, status updates, and process artifacts are
means. None is justified merely because it makes the work look rigorous.

## Trigger

Before each non-trivial step, identify which contracted user-visible result it
advances or which evidenced risk it reduces. If neither applies, do not take the
step.

The check is internal. There is no mandatory visible report; surface it only
when it changes scope, risk, authority, or an answer the user must decide.

For code, dependency, or feature work, also use the decision ladder below. It is
the code-specialized instance of the precedent-first rule in
`agent-os/review/reasoning-base.md`.

## Decision Ladder

Before generating new code, ask in order. Stop at the first rung that hits.

```text
1. Does it need to exist at all?      (YAGNI — real need, or over-completeness?)
2. Already in the codebase?           (search existing implementations first)
3. In the standard library?
4. A native platform / language feature?
5. In an already-installed dependency?
6. A one-liner?
7. Only then: minimum viable implementation.
```

Any rung hits -> stop there, do not generate further down.

The ladder runs after you understand the problem, not instead of it: read the
task and the code it touches, trace the real flow end to end, then climb. The
smallest change in the wrong place is not lazy — it is a second bug.

A bug report names a symptom, not the root: grep every caller of the function
you touch and fix the shared function once — one guard there is a smaller diff
than one per caller, and patching only the reported path leaves a sibling
caller still broken.

## Working Rules

```text
- No abstractions that were not explicitly requested.
- No new dependency if it can be avoided.
- No boilerplate nobody asked for.
- Deletion over addition; boring over clever; fewest files possible.
- The shortest working diff wins, but only once the problem is understood.
- Question complex requests: "do you actually need X, or does Y cover it?"
- When two standard-library approaches are the same size, pick the
  edge-case-correct one — minimal means less code, never the flimsier
  algorithm.
- A deliberate simplification that cuts a real corner (a global lock, an
  O(n^2) scan, a naive heuristic) carries a `ponytail:` comment naming the
  ceiling and the upgrade path; untagged, the trade-off reads as a bug.
```

## Boundary

```text
- Less code != less safety. Never cut: understanding the problem, input
  validation at trust boundaries, error handling that prevents data loss,
  security, accessibility, the calibration real hardware needs, or anything
  explicitly requested.
- Less mechanism != less scope. Deliver every accepted capability.
- Non-trivial logic leaves ONE runnable check behind — the smallest thing
  that fails if the logic breaks; no frameworks, no fixtures required.
  Trivial one-liners need no test.
- Add a worker only when its output is load-bearing and its benefit exceeds
  coordination cost.
- Add a document or status update only when it is a required deliverable, durable
  continuation state, or evidence the user needs.
```
