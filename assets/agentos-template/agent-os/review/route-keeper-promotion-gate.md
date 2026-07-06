# Route Keeper / Promotion Gate

Date: 2026-07-01

## Purpose

Route Keeper is the main thread's execution discipline. It keeps the active user object from being replaced by locally correct tool output, files, tests, reports, source gates, runtime discoveries, or subagent conclusions.

## Core Rules

```text
- After every significant tool result, subagent report, file edit, test, report, source gate, or runtime discovery, run a Route Checkpoint.
- The checkpoint question is: did this change `active_user_object`?
- Classify each significant artifact or branch as `mainline`, `support`, `blocker`, `side_route`, or `discard`.
- Promote to `mainline` only when it directly advances the Task Contract's `active_user_object` and evidence has been checked against source paths, command output, or files.
- Runtime, FRUS, source gate, subagent report, test pass, and report done are support by default.
- Keep support artifacts when useful, but do not let them replace the active user object.
- If an artifact is a blocker, take the narrow action needed to unblock and then return to mainline.
- If a branch is `side_route` or `discard`, park it or drop it and return to mainline.
```

## Classification

```text
mainline:
  Directly advances the task contract's active_user_object.

blocker:
  Must be resolved before the active_user_object can be achieved.

support:
  Helps execution or evidence, but cannot satisfy the task contract by itself.

side_route:
  Locally useful or interesting, but outside the current task contract.

discard:
  Does not serve the task contract or increases drift risk.
```

## Micro Route Checkpoint

```yaml
route_checkpoint:
  active_user_object:
  artifact_or_branch:
  does_it_change_active_user_object: yes | no | unknown
  promotion_class: mainline | support | blocker | side_route | discard
  next_action:
```

## Promotion Gate

Use this before promoting any artifact, branch, test, report, or subagent conclusion into the mainline.

```yaml
promotion_gate:
  artifact_or_branch:
  source:
  claim_type: observation | inference | explanation | causal | completion | recommendation | handoff | other
  relation_to_task_contract: directly_advances | required_to_unblock | supports | conflicts | unrelated | drift_risk
  promotion_class: mainline | support | blocker | side_route | discard
  evidence_checked:
  user_visible_impact:
  return_to_mainline_rule:
```

## Promotion Rules

```text
- mainline requires a direct relation to active_user_object and checked evidence.
- blocker requires a narrow unblock action, not a new open-ended project.
- support can be retained, cited, or used, but cannot be called completion.
- side_route can be parked for later only if it does not interrupt the current contract.
- discard should be dropped without ceremony unless it affects risk or handoff.
- If evidence is missing, classify as support, side_route, discard, or blocker; do not promote.
```

## Known Drift Triggers

```text
runtime:
  A runtime check shows something can run. It does not prove the user's requested layer is complete unless runtime behavior is the active_user_object.

FRUS:
  A FRUS artifact can support source or persona work, but it does not replace the user-visible object or task contract.

source gate:
  A source gate can verify evidence quality, but it does not by itself satisfy product meaning, dialogue quality, route, or completion.

subagent report:
  A subagent report is not fact until checked against source paths, commands, or files. Even when true, it must pass Promotion Gate.

test pass:
  A passing test proves only the tested property. It is support unless the task contract defines that tested property as the active user object.

report done:
  A written report is completion only when the task contract makes that report the deliverable and its evidence standard is satisfied.
```

