# Current AgentOS State

Date: 2026-07-01

## Active Task

```yaml
last_kernel_migration: Agent OS Kernel Migration v1 installed with Codex and Claude adapters
active_user_object: null
status: installed_waiting_for_user_task

task_contract: null

route:
  current_mainline: wait for the latest user message, then route through agent-os/boot.md and agent-os/router.md
  support_artifacts:
    - agent-os/
    - AGENTS.md
    - CLAUDE.md
    - .agents/skills/
    - .claude/skills/
    - wiki/
    - root ledgers
  blockers: []
  side_routes_parked: []

evidence_state:
  verified:
    - AgentOS scaffold was installed from the bundled global skill template.
  limitations:
    - Installation proves file structure only.
    - Runtime-specific skill auto-triggering, hooks, worker visibility, and production durable replay require separate task evidence.

next_safe_action:
  Read the latest user message, reconstruct the task contract for non-small work, and load only the AgentOS kernel files selected by agent-os/router.md.
```
