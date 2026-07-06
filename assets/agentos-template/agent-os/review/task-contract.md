# Task Contract

Date: 2026-07-01

## Purpose

Task Contract fixes the task target before execution and protects it during tools, files, subagents, reports, context compression, and handoff.

Use it after Reasoning Base and Intent-Causal Gate.

## When To Use

Use a full Task Contract for non-small tasks:

```text
- multi-step work
- file edits with user-visible consequences
- agent behavior, root-cause, audit, strategy, or product meaning work
- work that may use subagents or many tools
- work where support artifacts can be mistaken for completion
- work likely to survive context compression or handoff
```

Skip the full contract for tiny, clear, reversible tasks. Use the micro contract instead.

## Core Rules

```text
- Form a Task Contract before planning, delegation, tool-heavy work, or file edits on non-small tasks.
- Pin active user object, user-visible success, requested layer, deliverable, invariants, forbidden substitutions, evidence standard, autonomy, ask-required conditions, and handoff minimum state.
- Keep the contract short enough to preserve execution focus.
- Tests, files, scripts, plans, reports, source gates, runtime checks, and subagent reports are support artifacts unless the contract explicitly makes them the deliverable.
- Completion requires evidence that the active user object changed or became usable to the user.
- If execution discovers that the contract is wrong or incomplete, stop promotion to mainline and update the contract before continuing.
```

## Micro Contract

```yaml
task_contract_micro:
  active_user_object:
  deliverable:
  forbidden_substitution:
  evidence_standard:
  per_turn_audit_reported: required (append agent-os/state/audit-log.md + report block in answer)
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

## Handoff Minimum

If interrupted, preserve:

```yaml
handoff_min_state:
  active_user_object:
  task_contract:
  current_route:
  completed_evidence:
  open_blockers:
  forbidden_substitutions:
  next_safe_action:
```

## Completion Link

Before completion wording, run:

```text
agent-os/review/completion-gate.md
agent-os/review/evidence-to-claim-gate.md
```

