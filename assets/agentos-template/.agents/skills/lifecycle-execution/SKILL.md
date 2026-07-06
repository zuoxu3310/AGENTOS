---
name: lifecycle-execution
description: Runs the Agent OS non-small task lifecycle from intake through contract, route checks, verification, final response, and handoff. Use when handling resumed or multi-step work.
---

# Lifecycle Execution

Thin Codex adapter for the repo-local Agent OS kernel.

## Source

Read:

```text
agent-os/boot.md
agent-os/router.md
agent-os/workflows/agent-execution-lifecycle.md
```

## Trigger

Use for non-small work, resumed work, context-sensitive work, or tasks that need route checkpoints and verified final wording.

## Output Shape

```yaml
lifecycle_execution:
  active_user_object:
  task_contract:
  route:
  verification:
  final_response:
  handoff_or_memory:
```

Do not copy kernel text into this wrapper.
