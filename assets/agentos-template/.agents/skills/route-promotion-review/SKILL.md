---
name: route-promotion-review
description: Keeps execution on the active user object and reviews artifact promotion. Use when tool output, tests, runtime checks, files, branches, or subagent reports might replace the main task.
---

# Route Promotion Review

Thin Codex adapter for the repo-local Agent OS kernel.

## Source

Read:

```text
agent-os/review/route-keeper-promotion-gate.md
```

## Trigger

Use after significant tool output, file edits, tests, reports, runtime discoveries, source gates, branch changes, or subagent reports.

## Output Shape

```yaml
route_promotion_review:
  active_user_object:
  artifact_or_branch:
  source:
  claim_type:
  relation_to_task_contract:
  promotion_class:
  evidence_checked:
  user_visible_impact:
  return_to_mainline_rule:
```

Do not copy kernel text into this wrapper.
