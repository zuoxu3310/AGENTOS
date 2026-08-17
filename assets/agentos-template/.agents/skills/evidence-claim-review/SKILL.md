---
name: evidence-claim-review
description: Checks evidence strength before final wording, memory, handoff, recommendations, and completion claims. Use when claims need downgrade, support, or completion evidence.
---

# Evidence Claim Review

Thin Codex adapter for the repo-local Agent OS kernel.

## Source

Read:

```text
agent-os/review/evidence-to-claim-gate.md
agent-os/review/completion-gate.md
```

## Trigger

Use before wording that claims completion, cause, root cause, recommendation, handoff state, memory state, or final user-visible status.

## Output Shape

```yaml
evidence_claim_review:
  claim:
  claim_type:
  evidence_source:
  evidence_layer:
  support_type:
  evidence_strength:
  allowed_wording:
  downgrade_or_remove:
  completion_status:   # completion claims run the completion-gate template
```

Do not copy kernel text into this wrapper.
