---
name: anti-sycophancy-review
description: Steps outside the user's framing on judgment, evaluation, decision, recommendation, or opinion questions where the phrasing may bias the answer. Use before answering one-sided, contested, or judgment-type questions in this Agent OS project.
---

# Anti-Sycophancy Review

Thin Codex adapter for the repo-local Agent OS kernel.

## Source

Read:

```text
agent-os/boot.md
agent-os/router.md
agent-os/review/anti-sycophancy-gate.md
```

## Trigger

Use when the question is a judgment, evaluation, decision, recommendation, opinion, or one-sided framing where the user's phrasing could steer the answer. Do not use for mechanical execution.

## Output Shape

```yaml
anti_sycophancy_review:
  framing_assumptions:
  tool_used:
  unanchored_judgment:
  divergence_from_framed_answer:
```

Do not copy kernel text into this wrapper.
