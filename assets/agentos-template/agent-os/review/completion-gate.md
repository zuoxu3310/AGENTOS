# Completion Gate

Date: 2026-07-01

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
  claimed_completion:
  user_visible_change:
  delivered_artifact:
  artifact_type: answer | file | test | script | report | runtime | source_gate | subagent_report | template | plan | other
  evidence_matches_contract: yes | no | partial
  forbidden_substitution_check:
  support_artifacts:
  remaining_gaps:
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

For large deliveries (multi-file changes, new subsystems, long working sessions),
attach a short recognition-type quiz (choice/judgment questions) to the completion
report so the user can verify their own understanding before accepting. The user
may waive it. A delivery the user cannot pass a quiz on is submitted, not yet
accepted — and each quiz calibrates the user as a verifier at zero study cost.

## Forbidden Completion Claims

```text
- "Tests passed, therefore task complete" when user_visible_success is not tested.
- "Report written, therefore audit complete" when causal claims are not verified.
- "Subagent found X, therefore mainline changed" without source verification and promotion gate.
- "Source gate complete, therefore persona/source task complete" when requested source priority is not satisfied.
- "Runtime works, therefore LLM dialogue entry works" when requested_layer is conversation.
- "aos-lint passed, therefore Agent OS works" because aos-lint proves structure only.
- "Turn done" without emitting the per-turn audit block and appending it to agent-os/state/audit-log.md. No turn completes without its audit reported (agent-os/review/per-turn-audit-gate.md).
```

## Evidence Requirements

For this Agent OS kernel migration, completion requires:

```text
- agent-os/ directory and required files exist.
- Six layers are placed in the mapped kernel paths.
- boot.md defines minimum startup.
- router.md defines task routing and skill-use timing.
- review/ contains Reasoning, Intent, Contract, Route, Evidence, Report, and Completion gate coverage.
- tools/aos-lint.py checks structure and states that it is not behavioral proof.
- AGENTS.md points to agent-os/ while preserving existing adapter excerpts.
- Old RB, ICG, TC, RKP, ECG, AEL checks pass.
- Agent OS kernel migration checks pass.
- Documentation hygiene checks pass.
```

