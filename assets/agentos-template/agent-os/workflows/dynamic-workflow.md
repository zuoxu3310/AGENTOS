# Dynamic Workflow

Date: 2026-07-01

## Purpose

Dynamic Workflow is the Agent OS workflow for script-owned, multi-worker execution.

Use it when the active user object requires more than one independently recoverable Agent thread, role, or execution branch.

It is a workflow contract, not a runtime by itself. Runtime adapters implement it through their native mechanisms.

## Kernel Classification

```text
kernel:
  this file, because it defines the canonical Agent OS workflow contract.

adapter:
  Codex App Server, Codex app thread tools, Claude Dynamic Workflows, Claude Agent Teams, or any runtime-specific thread API.

extension:
  dashboards, long-term memory sync, broad subagent libraries, automation hooks, and pressure-test harnesses.

verification:
  probes, state-board checks, thread read/list/resume checks, and end-to-end run records.
```

Do not treat a runtime adapter, tool, or worker report as the workflow itself.

## First Principles

```text
active object:
  a workflow run that holds the plan, starts child work, preserves state, and returns verified synthesis.

invariants:
  - The main thread owns the route.
  - The workflow runner owns the plan and state board.
  - Worker threads are child workflows or support artifacts until verified.
  - State board is the source of workflow progress.
  - Evidence gates decide what can be promoted.
  - Runtime success is not content correctness.
```

## Entry Criteria

Use Dynamic Workflow only when at least one is true:

```text
- The task naturally splits into independent roles or branches.
- The user explicitly asks for multi-thread, multi-agent, worker, team, or workflow execution.
- Work must preserve recoverable state across long turns, crashes, or handoff.
- The task needs independent review before promotion.
```

Do not use it for tiny, linear, low-risk tasks.

## Required Contract

Before running a Dynamic Workflow, form a Task Contract that includes:

```yaml
dynamic_workflow_contract:
  active_user_object:
  requested_layer: workflow | runtime | adapter | verification | other
  workflow_run:
    name:
    run_id:
    cost_profile: minimal | standard | expanded
  worker_plan:
    - role:
      task:
      dependency:
  state_board:
    path:
    required_fields:
      - run_id
      - workflow_status
      - steps
      - worker thread ids
      - worker roles
      - prompts or task refs
      - statuses
      - result refs
      - verification checks
      - visibility checks
      - monitor checks
      - promotion gate notes
  monitor_policy:
    heartbeat_or_poll_interval:
    stale_after:
    max_repair_attempts:
    replacement_rule:
    role_reuse_downgrade_rule:
  evidence_standard:
  forbidden_substitutions:
  recovery_rule:
  final_synthesis_rule:
```

## Execution Model

Run this order:

```text
1. phase_0_probe when the runtime route is unproven.
2. initialize_workflow_run.
3. write initial state board.
4. start worker threads through the selected runtime adapter.
5. checkpoint every external effect before and after it runs.
6. run the Worker Monitor until each required worker is completed, failed, repaired, or explicitly downgraded.
7. read/list/resume or equivalent each worker thread.
8. persist each worker result as a result_ref.
9. run Route Keeper / Promotion Gate before synthesis.
10. write final synthesis with worker thread ids and evidence limits.
11. verify state board, worker recovery, monitor decisions, and final claim wording.
```

## Step Discipline

Every external effect must be represented as a named step.

Minimum step states:

```text
pending
running
completed
failed
canceled
```

Minimum step fields:

```yaml
step:
  name:
  status:
  started_at:
  completed_at:
  result_summary:
  error:
```

Use stable descriptive step names. If steps are generated from a changing list, include a stable role or item id in the name.

## Worker Monitor / Reaper

Starting workers is not enough. The workflow runner must monitor them until the workflow can safely synthesize, repair, or downgrade.

The monitor owns runtime liveness, result_ref readiness, and repair decisions. It does not judge worker content correctness; content still goes through Route Keeper / Promotion Gate and Evidence-to-Claim Gate.

Minimum monitor fields in the state board:

```yaml
worker_monitor:
  policy:
    heartbeat_or_poll_interval:
    stale_after:
    max_repair_attempts:
    replacement_rule:
    role_reuse_downgrade_rule:
  workers:
    - role:
      thread_id:
      status: pending | running | completed | failed | stale | repaired | superseded | downgraded
      last_seen_at:
      last_checked_at:
      turn_status:
      result_ref:
      result_ref_exists: true | false | unknown
      tool_readable: true | false | unknown
      listable: true | false | unknown
      resume_or_rejoin: passed | failed | unknown
      repair_attempts:
        - thread_id:
          route: retry_same_thread | replacement_thread | fork | role_reuse | manual_downgrade
          status:
          result_ref:
          evidence:
          downgrade:
```

Monitor loop:

```text
1. Poll or read every required worker by stable role and thread id.
2. Check turn/run status, last activity, listability, readability, and result_ref existence.
3. If a worker is still running but active, keep it running and update last_seen_at.
4. If a worker is stale, record stale status before attempting repair.
5. Repair with the narrowest route that can preserve the role: retry same thread, replacement thread, fork, role reuse, or manual downgrade.
6. Record every repair attempt in the state board before using its output.
7. If a replacement or role reuse succeeds, mark the original worker as superseded or failed, not completed.
8. If role reuse or a fork from another role is used, downgrade independence and forbid clean-team wording.
9. Do not enter final synthesis until every required worker is completed, failed with explicit handling, or intentionally downgraded.
```

Stale worker indicators:

```text
- read/list succeeds but the turn never progresses within the monitor policy.
- thread is readable but not listable when listability is required.
- worker says it will write result_ref but result_ref is still missing after the allowed window.
- worker result_ref exists but was written by a different role or replacement route.
- replacement thread exists but cannot be recovered or linked to the state board.
```

Allowed monitor outcomes:

```text
completed:
  Worker finished, result_ref exists, and runtime evidence is recorded.

repaired:
  Original worker failed or stalled; a replacement produced result_ref with repair evidence.

downgraded:
  Workflow can continue, but the claim boundary must name the missing property, such as clean independence or user-visible auditability.

blocked:
  Required worker evidence cannot be produced or downgraded without changing the Task Contract.
```

Monitor evidence can support runtime claims only. It cannot promote worker factual claims, recommendations, causal claims, root-cause claims, or completion claims.

## Runtime Adapter Requirements

A runtime adapter is acceptable only if it can produce recoverable evidence for worker threads.

Minimum adapter evidence:

```text
- real worker thread id or workflow run id
- started status
- completed or failed turn/run status
- readable worker result
- list/search or equivalent discoverability
- resume/rejoin or equivalent recovery path
- monitorable liveness or poll status
- result_ref existence check
- visibility classification
- state-board record that survives the current turn
```

If the adapter cannot create or recover real threads, do not run the full workflow. Report the failed probe instead.

## Visibility And Audit Requirements

Thread existence is not enough for user auditability.

Classify every worker thread or child workflow with all four fields:

```yaml
visibility:
  tool_readable: true | false | unknown
  listable: true | false | unknown
  user_visible: true | false | unknown
  auditable: true | false | unknown
  evidence:
  downgrade:
```

Definitions:

```text
tool_readable:
  A runtime tool can read the thread, run, or child workflow by id.

listable:
  A runtime list or search operation can find the worker by stable title, run id, or equivalent metadata.

user_visible:
  the user can see or open the worker in the target user-facing runtime surface, or an explicit UI-level verification proves that surface visibility.

auditable:
  The state board, worker id, result ref, final synthesis, and user-visible or explicitly downgraded visibility evidence can be checked together.
```

If `user_visible` is false or unknown, the workflow may still be useful as a background run, but the final wording must downgrade:

```text
allowed:
  "background worker thread was tool-readable and listable"

forbidden:
  "the user can audit this worker in the UI"
  "the thread is user-visible"
```

User-visible auditability is required before claiming that a Dynamic Workflow run is fully auditable by the user.

## Codex Adapter Rule

For Codex, the preferred implementation path is:

```text
Codex App Server or Codex app thread tools
```

Minimum verified operations:

```text
thread/start
turn/start
turn/completed
thread/read
thread/list or Codex app list_threads
thread/resume or Codex app read/continue equivalent
UI-visible or explicitly downgraded user visibility evidence
```

The Codex adapter may classify created threads as `vscode` source in the app even when `threadSource` is `appServer`; use title, cwd, run id, and thread id to verify discoverability.

Do not treat Codex `read_thread` success as Desktop user visibility. If the user cannot see the thread in the Codex Desktop surface, record `user_visible: unknown` or `false` and downgrade the audit claim.

## Claude Adapter Rule

For Claude, use Claude's native workflow mechanism when available.

Expected route:

```text
Claude Dynamic Workflows for script-owned workflows
Claude Agent Teams only when the active task is team-style coordination
```

Do not copy Codex App Server assumptions into Claude. The Claude adapter must provide its own equivalent evidence: real run/thread ids, recoverable state, worker outputs, and final synthesis boundary.

## Preset: Three-Agent Squad

Three-Agent Squad is the low-cost preset of Dynamic Workflow.

Use it when a small multi-agent split is enough:

```yaml
three_agent_squad:
  cost_profile: minimal
  roles:
    researcher:
      job: extract contract, evidence, constraints, and risks
    builder:
      job: propose or implement the minimal viable route
    reviewer:
      job: check evidence, downgrade claims, and identify gaps
  required_workers: 3
  minimum_checks:
    - each worker has a real recoverable id
    - each worker result has a result_ref
    - each worker passes monitor checks or has explicit repair/downgrade evidence
    - final synthesis cites all worker ids
    - each worker has visibility classification
    - worker claims remain support until checked
```

Three-Agent Squad is not a separate AgentOS layer. It is a preset that saves cost by limiting roles and branches.

## Promotion Rules

Worker outputs are support artifacts by default.

Promote only these to mainline without additional content verification:

```text
- worker thread exists
- worker turn/run completed
- worker result is readable
- worker thread is discoverable
- worker thread is resumable or re-readable
- worker visibility has been classified
- worker monitor status has been classified
- failed or replaced workers are explicitly marked as failed, superseded, repaired, or downgraded
- final synthesis cites ids and result refs
```

Do not promote these without source or command verification:

```text
- factual claims made by workers
- recommendations made by workers
- causal or root-cause claims made by workers
- completion claims made by workers
```

## Completion Evidence

A Dynamic Workflow run is complete only when:

```text
- state board exists and is parseable
- required worker ids exist
- required workers completed or failures are explicitly handled
- Worker Monitor recorded completed, repaired, downgraded, or blocked status for each required worker
- read/list/resume or equivalent recovery checks passed
- result refs exist
- final synthesis cites worker ids
- final synthesis separates worker claims from verified evidence
- visibility checks distinguish tool-readable, listable, user-visible, and auditable
- user-visible gaps are downgraded in final wording
- Evidence-to-Claim Gate allows the completion wording
```

Passing structure checks or writing a report is not enough.

## Handoff Minimum

If interrupted, preserve:

```yaml
dynamic_workflow_handoff:
  active_user_object:
  workflow_contract:
  runner_path:
  state_board_path:
  run_id:
  worker_ids:
  worker_roles:
  completed_steps:
  failed_or_running_steps:
  worker_monitor:
  repair_attempts:
  result_refs:
  visibility:
  last_verified_checkpoint:
  next_safe_action:
  claim_boundary:
```

## Claim Boundary

Allowed wording after a verified run:

```text
The Dynamic Workflow run completed within the verified adapter scope.
```

Allowed wording when user visibility is missing:

```text
The Dynamic Workflow background run completed within the tool-readable adapter scope, but user-visible auditability is not established.
```

Forbidden wording without stronger evidence:

```text
AgentOS is fully automated.
The worker conclusions are true.
This is a production-grade durable workflow runtime.
Hooks are wired automatically.
All future AgentOS workflows are solved.
the user can audit hidden worker threads in the UI.
```
