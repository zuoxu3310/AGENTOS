---
name: intent-contract-review
description: Separates user goals from candidate means, decides question admission, and pins task contracts. Use before planning, implementation, delegation, or tool-heavy execution — unconditionally, not only when intent feels unclear.
---

# Intent Contract Review

Thin Claude adapter for the repo-local Agent OS kernel.

## Source

Read:

```text
agent-os/review/intent-causal-gate.md
agent-os/review/task-contract.md
```

## Trigger

Use before planning, implementation, delegation, or tool-heavy execution — unconditionally; the confident wrong reading is what this method exists to catch.

## Output Shape

```yaml
intent_contract_review:
  active_user_object:
  user_visible_success:
  goal_means_split:
  question_decision:
  task_contract:
  forbidden_substitutions:
  evidence_standard:
```

Do not copy kernel text into this wrapper.
