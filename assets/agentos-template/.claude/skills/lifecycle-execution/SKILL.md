---
name: lifecycle-execution
description: Runs the Agent OS task lifecycle from intake through contract, route checks, verification, final response, and handoff. Use for work that spans messages, resumes, or needs route checkpoints and verified final wording.
---

# Lifecycle Execution

Thin Claude adapter for the repo-local Agent OS kernel.

## Source

Read:

```text
agent-os/workflows/agent-execution-lifecycle.md
agent-os/review/task-contract.md
agent-os/review/evidence-to-claim-gate.md
```

## Trigger

Use for work that spans user messages, resumed work, context-sensitive work, or tasks that need route checkpoints and verified final wording.

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
