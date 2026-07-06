# Task Contract v1 Templates

Date: 2026-07-01

Use this after Reasoning Base and Intent-Causal Gate. It fixes the task target before execution and protects it during tools, files, subagents, reports, context compression, and handoff.

## When To Use

Use full Task Contract for non-small tasks:

```text
- multi-step work
- file edits with user-visible consequences
- agent behavior, root-cause, audit, strategy, or product meaning work
- work that may use subagents or many tools
- work where support artifacts can be mistaken for completion
- work likely to survive context compression or handoff
```

Skip full contract for tiny, clear, reversible tasks. Use the micro contract instead.

## Micro Contract

```yaml
task_contract_micro:
  active_user_object:
  deliverable:
  forbidden_substitution:
  evidence_standard:
```

## Full Task Contract

```yaml
task_contract:
  active_user_object:
    description:
    why_it_matters:

  user_visible_success:
    description:
    how_user_can_tell:

  requested_layer:
    layer: conversation | document | code | runtime | research | workflow | policy | memory | other
    notes:

  deliverable:
    primary:
    format:
    location:

  non_substitutable_invariants:
    - invariant:
      reason:

  forbidden_substitutions:
    - proxy:
      why_forbidden:

  evidence_standard:
    required_evidence:
    insufficient_evidence:

  autonomy:
    agent_may_decide:
    must_ask_user_before:

  ask_required_when:
    - condition:
      why_it_changes_route:

  handoff_min_state:
    active_user_object:
    current_route:
    completed_evidence:
    open_blockers:
    forbidden_substitutions:
    next_safe_action:
```

## Completion Gate

Run before saying done, ready, complete, fixed, delivered, or equivalent.

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

Completion rules:

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

Forbidden completion claims:

```text
- "Tests passed, therefore task complete" when user_visible_success is not tested.
- "Report written, therefore audit complete" when causal claims are not verified.
- "Subagent found X, therefore mainline changed" without source verification and promotion gate.
- "Source gate complete, therefore persona/source task complete" when requested source priority is not satisfied.
- "Runtime works, therefore LLM dialogue entry works" when requested_layer is conversation.
```

