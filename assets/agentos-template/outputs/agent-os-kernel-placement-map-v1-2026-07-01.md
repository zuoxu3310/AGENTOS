# Agent OS Kernel Placement Map v1

Date: 2026-07-01

## Purpose

This map says where the current Agent OS kernel content should live when it is migrated into a real `agent-os/` directory.

It does not build the directory yet. It prevents the next step from mixing kernel rules, adapters, extensions, and verification tools.

## Target Shape

```text
agent-os/
  boot.md
  router.md
  review/
    reasoning-base.md
    intent-causal-gate.md
    task-contract.md
    route-keeper-promotion-gate.md
    evidence-to-claim-gate.md
    completion-gate.md
  workflows/
    agent-execution-lifecycle.md
    dynamic-workflow.md
  skills/
  state/
    current.md
  handoffs/
  tools/
    aos-lint.py
```

Adapter files stay outside the kernel:

```text
AGENTS.md
CLAUDE.md
.agents/skills/
.claude/skills/
.codex/hooks.json
.codex/hooks/
.codex/
.claude/
```

## Placement Rules

```text
boot.md:
  Startup sequence and minimum files an Agent must read before acting.

router.md:
  Task routing, skill routing, ask gate, and when a native skill wrapper should point into Agent OS.

review/:
  Rules that decide whether reasoning, intent, contracts, routes, evidence, reports, or completion claims are allowed.

workflows/:
  Ordered execution loops that connect review gates across a full task.
  Dynamic Workflow belongs here when it defines canonical multi-worker execution rules.

skills/:
  Reusable Agent OS methods that are not native runtime skills by themselves.

state/current.md:
  Current task state, active user object, contract, route, evidence state, and next safe action.

handoffs/:
  Interruption-safe transfer records.

tools/aos-lint.py:
  Structural checks only. It does not prove Agent OS works behaviorally.
```

## Six-Layer Placement

```text
Reasoning Base:
  agent-os/review/reasoning-base.md
  Why: governs judgment, logic, causality, root-cause language, and first principles.

Intent-Causal Gate:
  agent-os/review/intent-causal-gate.md
  Why: decides what the user is really trying to make true before work begins.

Task Contract:
  agent-os/review/task-contract.md
  Why: pins the active user object, deliverable, boundaries, evidence standard, and handoff minimum.

Route Keeper / Promotion Gate:
  agent-os/review/route-keeper-promotion-gate.md
  Why: prevents tools, tests, reports, files, or subagent conclusions from replacing the main task.

Evidence-to-Claim Gate:
  agent-os/review/evidence-to-claim-gate.md
  Why: controls what Agents may claim in final answers, summaries, handoffs, and memory.

Agent Execution Lifecycle:
  agent-os/workflows/agent-execution-lifecycle.md
  Why: orders the gates into a runnable task loop.

Dynamic Workflow:
  agent-os/workflows/dynamic-workflow.md
  Why: defines script-owned, multi-worker, recoverable workflow execution and runtime-adapter evidence rules.
```

## Report And Completion Placement

Report Gate is not a separate reasoning layer. It is the reporting-facing application of Evidence-to-Claim Gate.

Place it as a section inside:

```text
agent-os/review/evidence-to-claim-gate.md
```

Completion Gate is also not a new reasoning layer. It is a compiled review view that points to completion rules from:

```text
agent-os/review/task-contract.md
agent-os/review/evidence-to-claim-gate.md
agent-os/workflows/agent-execution-lifecycle.md
```

If materialized, place it at:

```text
agent-os/review/completion-gate.md
```

Its job is to answer one question: is there enough evidence to say the active user object is complete?

## Adapter Placement

`AGENTS.md` and `CLAUDE.md` should contain only the minimum startup rules and pointers into `agent-os/`.

Native skill wrappers should live where the Agent runtime can see them:

```text
.agents/skills/<skill-name>/SKILL.md
.claude/skills/<skill-name>/SKILL.md
```

Each wrapper should be thin:

```text
trigger:
  when to use this skill

source:
  read `agent-os/...`

output:
  required minimum result
```

The wrapper should not duplicate full kernel rules.

Codex enforcement hooks live in:

```text
.codex/hooks.json
.codex/hooks/
```

They are adapters for runtime enforcement. They may enforce kernel invariants,
but they must not become competing rule bodies.

## Integration Plan

Directly enter Agent OS kernel:

```text
- Reasoning Base
- Intent-Causal Gate
- Task Contract
- Route Keeper / Promotion Gate
- Evidence-to-Claim Gate
- Agent Execution Lifecycle
- Dynamic Workflow
```

Remain as templates until migration:

```text
- outputs/reasoning-base-v1-templates-2026-07-01.md
- outputs/intent-causal-gate-v1-templates-2026-07-01.md
- outputs/task-contract-v1-templates-2026-07-01.md
- outputs/route-keeper-promotion-gate-v1-templates-2026-07-01.md
- outputs/evidence-to-claim-gate-v1-templates-2026-07-01.md
- outputs/agent-execution-lifecycle-v1-templates-2026-07-01.md
```

Need thin native skill wrappers later:

```text
- reasoning and causality review
- intent and task contract review
- route and promotion review
- evidence-to-claim review
- lifecycle execution
```

Do not do in this step:

```text
- subagent protocol
- long-term memory routing
- automation platform
- hook wired integration
- end-to-end pressure test
- global install
- copying full kernel text into native skill wrappers
```

## Migration Order

```text
1. Create `agent-os/` skeleton.
2. Move or rewrite the six kernel gate docs into target kernel paths.
3. Convert AGENTS.md and CLAUDE.md into thin adapters.
4. Add native skill wrappers that point to kernel files.
5. Add aos-lint structural checks.
6. Only after that, consider subagents, memory, automation, hooks, and pressure tests as extensions or verification work.
```
