# Minimal Code Gate

Date: 2026-07-02

Source idea: ponytail (github.com/DietrichGebert/ponytail) — "the best code is the
code you never wrote." Same root as the global Code Craft rule (minimum code);
this gate adds an operational ladder to check before generating.

This ladder is the code-specialized instance of the precedent-first rule in
`agent-os/review/reasoning-base.md` (own history -> mature human solutions ->
composition -> invent). For non-code "how do we solve X" questions, use that rule.

## Trigger

Before writing code, adding a dependency, or adding a feature.
Not for pure conversation, docs, or analysis.

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

## Report

When triggered, report: which rung it stopped at + why (e.g. "rung 2: reused X").

## Boundary

```text
- Less code != less safety. Keep error handling, security, and correctness intact.
- Pairs with the scope rule: this gate enforces "do not add" (no over-engineering).
  It does NOT license "do less" — full implementation when the user asked for full.
```
