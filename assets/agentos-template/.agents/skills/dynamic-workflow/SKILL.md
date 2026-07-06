---
name: dynamic-workflow
description: Runs AgentOS Dynamic Workflow for script-owned, multi-worker, multi-thread, recoverable, or auditable workflow execution. Use when a task asks for Codex worker threads, Claude Dynamic Workflows, Agent Teams, Three-Agent Squad, state boards, worker visibility, worker recovery, or promotion-gated synthesis.
---

# Dynamic Workflow

Thin Codex adapter for the repo-local AgentOS kernel.

## Source

Read:

```text
agent-os/boot.md
agent-os/router.md
agent-os/workflows/dynamic-workflow.md
agent-os/review/route-keeper-promotion-gate.md
agent-os/review/evidence-to-claim-gate.md
```

## Trigger

Use when the active task needs independently recoverable workers, runtime thread evidence, state-board execution, workflow visibility classification, Three-Agent Squad, or final synthesis from worker outputs.

## Codex Runtime Rule

Prefer Codex app thread tools for user-visible workers:

```text
list_projects -> create_thread -> list_threads -> read_thread -> navigate_to_codex_page
```

Use `codex app-server --stdio` only for background adapter probes or when user-visible auditability is not required. App-server readable threads do not prove Desktop visibility.

## Output Shape

```yaml
dynamic_workflow:
  active_user_object:
  contract:
  runner_or_thread_route:
  state_board_path:
  workers:
    - role:
      threadId:
      title:
      hostId:
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

Worker outputs remain support artifacts until verified against source paths, command output, files, or user-visible Codex thread evidence.
