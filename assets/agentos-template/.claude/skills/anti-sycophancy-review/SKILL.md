---
name: anti-sycophancy-review
description: De-anchors a judgment from the asker's framing. Trigger on judgment or evaluation questions, decisions, one-sided framing, confirmation-seeking, or contested topics — never for mechanical execution.
---

# Anti-Sycophancy Review

Thin Claude adapter for the repo-local Agent OS kernel.

## Source

Read:

```text
agent-os/review/anti-sycophancy-gate.md
```

## Trigger

Use when the user explicitly requests a framing audit, or a contested high-risk
judgment needs adversarial tools beyond the normal conclusion/basis/change-
condition record. Do not auto-run for every judgment or mechanical execution.

## Output Shape

```yaml
anti_sycophancy_review:
  framing_assumptions:
  tool_used:
  unanchored_judgment:
  divergence_from_framed_answer:
```

Do not copy kernel text into this wrapper.
