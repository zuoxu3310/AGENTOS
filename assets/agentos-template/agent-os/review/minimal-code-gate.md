# Minimal Work And Code Gate

## Purpose

Prevent unnecessary code, dependencies, and feature surface at the moment they
would be created, while preserving the full accepted user-visible result.

Use the least mechanism that fully delivers the contracted scope. Minimal
mechanism never means partial functionality.

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

## Boundary

```text
- Less code != less safety. Keep error handling, security, and correctness intact.
- Less mechanism != less scope. Deliver every accepted capability.
- Add a test only when it protects a behavior or risk that matters to the contract.
- Add a worker only when its output is load-bearing and its benefit exceeds
  coordination cost.
- Add a document or status update only when it is a required deliverable, durable
  continuation state, or evidence the user needs.
```
