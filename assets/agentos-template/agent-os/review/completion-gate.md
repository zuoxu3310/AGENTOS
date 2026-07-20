# Completion Gate

## Purpose

Completion Gate decides whether there is enough evidence to say the active user object is complete.

It is a compiled review view. It points to:

```text
agent-os/review/task-contract.md
agent-os/review/evidence-to-claim-gate.md
agent-os/workflows/agent-execution-lifecycle.md
```

Completion Gate is not a separate reasoning layer.

## Required Question

```text
Is the active_user_object achieved under the Task Contract's evidence standard?
```

If the answer is not established by evidence, do not use completion wording.

## Completion Template

```yaml
completion_gate:
  active_user_object:
  done_when:
    - condition:
      evidence: []
  open_items:
  blocker:
  evidence_layers:
  user_visible_change:
  delivered_artifact:
  artifact_type: answer | file | test | script | report | runtime | source_gate | subagent_report | template | plan | other
  evidence_matches_contract: yes | no | partial
  forbidden_substitution_check:
  support_artifacts:
  remaining_gaps:
  memory_disposition:
    status: reconciled | not_needed
    destinations:
    reason:
  completion_status: complete | partial | support_only | blocked | not_started
```

## Completion Status

```text
complete:
  The active user object is achieved, user-visible success is satisfied, and required evidence matches the contract.

partial:
  Real progress toward active_user_object, but one or more required evidence items or deliverable conditions remain.

support_only:
  Work produced useful artifacts, but the active user object is not yet achieved.

blocked:
  Active user object cannot proceed without a required user decision or external-state change.

not_started:
  Work has not materially changed the active user object.
```

## Acceptance Quiz

For a large delivery, offer a recognition check only when it helps the user
evaluate the result and Question Admission allows it. It is not mandatory user
labor and cannot substitute for missing completion evidence.

## Forbidden Completion Claims

```text
- "Tests passed, therefore task complete" when user_visible_success is not tested.
- "Report written, therefore audit complete" when causal claims are not verified.
- "Subagent found X, therefore mainline changed" without source verification and promotion gate.
- "Source gate complete, therefore persona/source task complete" when requested source priority is not satisfied.
- "Runtime works, therefore LLM dialogue entry works" when requested_layer is conversation.
- "aos-lint passed, therefore Agent OS works" because aos-lint proves structure only.
- "Task complete" while open obligations or a recorded next action remain.
```

## Evidence Requirements

Completion requires:

```text
- The accepted active goal has its contracted user-visible success.
- Every completion condition appears exactly once with relevant verified
  evidence, and no open item or blocker remains.
- The session-local `active_work` state passes its deterministic schema check.
- Durable memory is updated only when it has concrete future use; Stop does not
  invent semantic memory.
- Deterministic tests prove only tested invariants. Runtime, model-sample, or
  live-task evidence is additionally required when the Task Contract requests
  that layer; no average score hides a safety-critical failure.
- With no open item, further mutation or delegation is unnecessary unless new
  evidence first opens a required item.
```
