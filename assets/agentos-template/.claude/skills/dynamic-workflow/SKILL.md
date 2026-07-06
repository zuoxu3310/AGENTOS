---
name: dynamic-workflow
description: Runs AgentOS Dynamic Workflow for script-owned, multi-worker, multi-thread, recoverable, or auditable workflow execution. Use when a task asks for Claude Dynamic Workflows, Agent Teams, Codex worker threads, Three-Agent Squad, state boards, worker visibility, worker recovery, or promotion-gated synthesis.
---

# Dynamic Workflow

Thin Claude adapter for the repo-local AgentOS kernel.

## Source

Read:

```text
agent-os/boot.md
agent-os/router.md
agent-os/workflows/dynamic-workflow.md
agent-os/review/route-keeper-promotion-gate.md
agent-os/review/evidence-to-claim-gate.md
```

## Runtime Rule

Use Claude's native workflow mechanism when Claude is the active runtime:

```text
Claude Dynamic Workflows for script-owned orchestration
Claude Agent Teams only when the task is team-style coordination
```

Do not copy Codex App Server assumptions into Claude. Claude must provide its own recoverable run/thread evidence, worker outputs, state-board equivalent, and visibility or audit downgrade.

## Output Shape

```yaml
dynamic_workflow:
  active_user_object:
  contract:
  runtime_route:
  state_board_path:
  workers:
    - role:
      thread_or_run_id:
      title:
      cwd:
      source:
      visibility:
        tool_readable:
        listable:
        user_visible:
        auditable:
      result_ref:
  promotion_gate:
  final_synthesis:
  evidence_limits:
```

Worker outputs remain support artifacts until verified against source paths, command output, files, or runtime-visible thread evidence.
