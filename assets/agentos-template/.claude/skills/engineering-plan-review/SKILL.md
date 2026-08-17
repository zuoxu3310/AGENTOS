---
name: engineering-plan-review
description: Runs the engineering plan method — the three translations (priority, classification, parallel/serial), the pristine/Linus acceptance standard, and the time budget — before turning an approved goal into execution nodes, before dispatching work, and when accepting results. Use when translating an approved goal into a plan, at half budget, at budget, and when accepting engineering results.
---

# Engineering Plan Review

Thin Claude adapter for the repo-local Agent OS kernel.

## Source

Read:

```text
agent-os/review/engineering-gate.md
```

## Trigger

Use before turning an approved goal into execution nodes, before dispatching work, at the half-budget and at-budget checkpoints, and when accepting results. Not for pure conversation or understanding work.

## Output Shape

```yaml
engineering_plan_review:
  ordered_priorities:
  refused_as_waste:
  parallel_nodes:
  serial_nodes:
  time_budget:
  acceptance_verdict:
```

Do not copy kernel text into this wrapper.
