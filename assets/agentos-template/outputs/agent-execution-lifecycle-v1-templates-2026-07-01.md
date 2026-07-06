# Agent Execution Lifecycle v1 Templates

Date: 2026-07-01

Use this for non-small tasks. It connects Reasoning Base, Intent-Causal Gate, Task Contract, Route Keeper / Promotion Gate, verification, and Evidence-to-Claim Gate into one minimum execution loop.

## Purpose

Agent Execution Lifecycle is not a new reasoning layer. It is the order of operations that makes the existing layers run together:

```text
intake -> reasoning_base_check -> intent_gate -> task_contract -> execution_plan -> route_checkpoints -> verification -> evidence_to_claim_gate -> final_response -> handoff_or_memory
```

Small, clear, reversible tasks can use a short path. Non-small tasks must use the lifecycle at the appropriate depth.

## Scope Boundaries

```text
- Do not build a full subagent system.
- Do not build a memory system.
- Do not build an automation dashboard.
- Do not turn every command into a long report.
- Do create a minimum closed loop that keeps the five prior gates in order.
```

## Micro Lifecycle

Use this for medium-low-risk tasks that still are not tiny:

```yaml
agent_lifecycle_micro:
  active_user_object:
  task_contract:
  route:
  verification:
  evidence_to_claim_gate:
  final_response:
```

## Full Lifecycle

```yaml
agent_execution_lifecycle:
  intake:
    latest_user_message:
    source_of_truth_order:
    initial_user_visible_need:
    small_task_decision: tiny_skip | non_small_lifecycle_required

  reasoning_base_check:
    active_object:
    first_principles:
    claim_type_risks:
    causal_language_risks:
    proxy_risk:

  intent_gate:
    classified_user_content:
      goal:
      means:
      constraints:
      evidence:
      ambiguity:
    active_user_object:
    ask_level: 0_ask | 1_ask | short_grill | full_clarification
    assumptions_when_not_asking:

  task_contract:
    contract_status: formed | needs_rebuild | blocked
    deliverable:
    evidence_standard:
    forbidden_substitutions:
    ask_required_when:

  execution_plan:
    steps:
    verification_points:
    delegation_allowed:
    stop_conditions:

  route_checkpoints:
    - trigger:
      artifact_or_branch:
      changes_active_user_object: yes | no | unknown
      promotion_class: mainline | support | blocker | side_route | discard
      return_to_mainline_rule:

  verification:
    checks_run:
    evidence_collected:
    evidence_gaps:
    completion_evidence_status: sufficient | insufficient | blocked

  evidence_to_claim_gate:
    key_claims:
      - claim:
        claim_type:
        evidence_source:
        evidence_strength:
        allowed_wording:
        downgrade_or_remove:

  final_response:
    answer:
    evidence_summary:
    limits_or_risks:
    next_step_if_any:

  handoff_or_memory:
    needed: yes | no
    destination:
    active_user_object:
    contract:
    route:
    evidence_state:
    open_blockers:
```

## Failure Fallbacks

```text
intent unclear:
  Return to Intent-Causal Gate. Ask only if the answer materially changes route, risk, scope, validation, or user-visible success.

contract invalid:
  Rebuild Task Contract before further execution.

branch hijack:
  Return to Route Keeper / Promotion Gate. Classify the branch and restore the mainline.

evidence insufficient:
  Return to Verification, gather stronger evidence, or downgrade the claim through Evidence-to-Claim Gate.

completion evidence insufficient:
  Do not final the task. Continue verification, or report partial/blocker status without completion wording if user-facing status is needed.
```

## Forbidden Shortcuts

```text
- Do not skip Task Contract and execute directly on a non-small task.
- Do not treat a plan as completion.
- Do not use test pass alone to final the task.
- Do not write a subagent report into final_response without source-path, command, or file verification.
- Do not handoff a conclusion that has not passed Evidence-to-Claim Gate.
- After context compression, do not continue unless active_user_object, contract, route, and evidence_state are preserved or reconstructed from sources.
```

## Context Compression Resume State

Before or after context compression, preserve:

```yaml
context_compression_resume_state:
  active_user_object:
  contract:
  route:
  evidence_state:
  last_route_checkpoint:
  next_safe_action:
```
