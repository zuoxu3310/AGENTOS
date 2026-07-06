---
name: intent-contract-review
description: Separates user goals from candidate means and pins task contracts. Use when intent, ask level, boundaries, deliverables, forbidden substitutions, or completion evidence are unclear.
---

# Intent Contract Review

Thin Codex adapter for the repo-local Agent OS kernel.

## Source

Read:

```text
agent-os/boot.md
agent-os/router.md
agent-os/review/intent-causal-gate.md
agent-os/review/task-contract.md
```

## Trigger

Use before non-small work when the real user goal, candidate means, ask level, task contract, boundaries, or evidence standard needs to be fixed.

## Output Shape

```yaml
intent_contract_review:
  active_user_object:
  goal_means_split:
  ask_level:
  task_contract:
  forbidden_substitutions:
  evidence_standard:
```

Do not copy kernel text into this wrapper.
