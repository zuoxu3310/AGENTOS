# Runtime Visibility Adapter

## Purpose

This adapter standard defines when an AgentOS workflow worker is visible enough for Master ZX to audit.

For Codex it supports `agent-os/adapters/codex-workflow.md`. For Claude it
describes evidence boundaries for Claude's native Workflow; it does not install
or replace that Workflow.

## Classification

```text
kernel:
  promotion and evidence gates under agent-os/

adapter:
  Codex workflow adapter and thread tools; Claude native Workflow evidence

verification:
  list/read/open checks, state boards, final reports, E2E pressure-test artifacts
```

## Codex Visible Thread Standard

For a Codex worker to count as user-visible, the evidence must include:

```yaml
codex_worker_visibility:
  threadId:
  title:
  hostId:
  cwd:
  source:
  creation_route: codex_app.create_thread | codex_app.send_message_to_thread | codex_app_server | other
  list_threads:
    status:
    evidence:
  read_thread:
    status:
    evidence:
  open_or_navigation:
    status:
    evidence:
  visibility:
    tool_readable:
    listable:
    user_visible:
    auditable:
```

`codex_app.create_thread` creates user-owned threads that can appear in Codex Desktop. `codex app-server --stdio` can create recoverable background threads, but app-server readability is not enough to claim Desktop visibility.

## Codex Probe Order

Run this order before claiming user-visible auditability:

```text
1. list_projects when a repo-scoped visible thread is needed.
2. create_thread only when the user explicitly asked for a new/background thread.
3. list_threads by stable title or query.
4. read_thread by threadId and hostId when available.
5. navigate_to_codex_page or equivalent UI-open evidence.
6. Write a state board with all four visibility fields.
```

If the current workspace is not available as a Codex project, a `projectless` probe can establish Desktop-visible thread mechanics, but it does not prove repo-scoped worker workflow completion.

## Claude Visibility Standard

When Claude is the active runtime, use Claude's native workflow mechanism:

```text
Claude Dynamic Workflows for script-owned orchestration
Claude Agent Teams for team-style coordination
```

Claude evidence must be runtime-native. Do not substitute Codex thread fields for Claude. Required equivalents:

```yaml
claude_worker_visibility:
  run_or_thread_id:
  role:
  title_or_label:
  runtime_surface:
  state_ref:
  output_ref:
  recoverable:
  user_visible_or_downgraded:
  audit_evidence:
```

## Promotion Rule

Visibility evidence promotes only the existence, recoverability, and auditability of the worker.

It does not promote worker conclusions. Worker claims still pass through Route Keeper / Promotion Gate and Evidence-to-Claim Gate.

## Claim Boundary

Allowed:

```text
This worker is user-visible in Codex Desktop within the recorded evidence scope.
```

Allowed when only app-server evidence exists:

```text
This worker is tool-readable and listable, but user-visible auditability is not established.
```

Forbidden without UI-open or equivalent evidence:

```text
Master ZX can audit this worker in Codex Desktop.
```
