---
name: delivery-review
description: Shapes any user-facing delivery or report by the AgentOS delivery gate — fix the delivery's goal (decision, resources, or awareness), lead with the conclusion and its data, pick the matching formula, and copy the project's accepted exemplar shape when one exists. Use before writing any user-facing report, status update, proposal, or answer.
---

# Delivery Review

Thin Claude adapter for the repo-local Agent OS kernel.

## Source

Read:

```text
agent-os/review/delivery-gate.md
```

## Trigger

Use before writing any user-facing delivery: reports, status updates,
proposals, and answers. Not for role-to-role messages inside the chain —
their shapes belong to the seat workflows.

## Output Shape

```yaml
delivery_review:
  delivery_goal: decision | resources | awareness
  conclusion_first_line:
  data_at_real_granularity:
  formula: formal_report | miss_or_problem | routine_status
  exemplar: copied <path> | library_empty_gate_governs
  asks_answered:
```

Do not copy kernel text into this wrapper.
