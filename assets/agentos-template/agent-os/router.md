# Agent OS Router

Date: 2026-07-01

## Purpose

This file routes Agent work to the right Agent OS kernel files and external runtime skills.

The router protects the active user object from being replaced by a tool, report, test, subagent result, or attractive side route.

## Route Order

For every non-small task:

```text
1. Identify the active user object.
2. Classify the latest user message as goal, means, constraint, evidence, emotion, or ambiguity.
3. Form a Task Contract.
4. Choose the minimum review gates and workflow files.
5. Treat tools, files, reports, tests, and subagents as support until Promotion Gate says otherwise.
6. Verify before final claims.
7. Emit and log the per-turn audit (all tasks, including small) before the final answer.
```

## Kernel File Routing

```text
Judgment, logic, causality, root-cause language, first principles:
  agent-os/review/reasoning-base.md

User intent, goal-vs-means, ask level, proxy risk:
  agent-os/review/intent-causal-gate.md

User framing as a bias source, sycophancy risk, judgment/opinion/recommendation questions:
  agent-os/review/anti-sycophancy-gate.md

Task target, deliverable, boundaries, evidence standard, handoff minimum:
  agent-os/review/task-contract.md

Execution route, tool-result classification, promotion rules:
  agent-os/review/route-keeper-promotion-gate.md

Before writing code, adding dependencies, or adding features (minimize what gets written):
  agent-os/review/minimal-code-gate.md

Before writing any prompt for another model or agent (subagents, panels, judges, workers, external CLIs):
  agent-os/review/prompt-craft-gate.md

Final wording, report wording, memory and handoff claim strength:
  agent-os/review/evidence-to-claim-gate.md

Mandatory per-turn audit and report (all tasks, including small and conversation):
  agent-os/review/per-turn-audit-gate.md

Completion decision:
  agent-os/review/completion-gate.md

Full non-small task loop:
  agent-os/workflows/agent-execution-lifecycle.md

Script-owned, multi-worker, multi-thread, or recoverable workflow execution:
  agent-os/workflows/dynamic-workflow.md

Multi-model answer fusion, explicitly invoked by the user only:
  agent-os/workflows/fusion-workflow.md

Runtime-visible worker audit, Codex/Claude workflow adapter evidence, or user-visible thread checks:
  agent-os/adapters/runtime-visibility.md

Codex/Claude native skill parity:
  agent-os/adapters/skill-parity.md

Project memory bootstrap, ledgers, and wiki scaffold:
  agent-os/memory/bootstrap.md

Durable memory placement, wiki routing, and ledger updates:
  agent-os/memory/routing.md

Stage-end sync, handoff preparation, and memory audit:
  agent-os/memory/sync-audit.md

Wiki v2, OKF-style concept docs, confidence, supersession, and knowledge lifecycle:
  agent-os/memory/wiki-v2.md
```

## Skill Routing

Native runtime skills live outside the kernel:

```text
.agents/skills/
.claude/skills/
```

Those wrappers are adapters. They may point to `agent-os/` files, but they must not become competing rule bodies.

Use native skills when the runtime exposes them and the task matches:

```text
Entry-doc edits:
  writing-agent-md

Durable wiki or memory routing:
  wiki-maintenance (rule body: agent-os/memory/routing.md)

AgentOS local memory/wiki adapter:
  memory-wiki-routing

Script-owned or worker-thread workflow:
  dynamic-workflow

Multi-model answer fusion (manual invocation only, never auto-initiated):
  fusion-workflow (rule body: agent-os/workflows/fusion-workflow.md)

Before writing a prompt for another model or agent:
  prompt-craft-review (rule body: agent-os/review/prompt-craft-gate.md)

Confirmed agent mistakes:
  error-learning (rule body: agent-os/memory/error-learning.md)

Stage cleanup or full audit:
  neat-freak (rule body: agent-os/memory/sync-audit.md)

Completion or passing claims:
  verification-before-completion
```

If a skill wrapper exists later, it should contain:

```text
- trigger condition
- source file under agent-os/
- minimum output shape
```

It should not copy the full kernel body.

## Ask Gate

Ask the user only when the answer would materially change:

```text
- active user object
- route
- evidence standard
- destructive or external action
- product meaning
- ownership of durable memory
- completion claim
```

Ordinary implementation choices are autonomous.

## Capability Classification

Before building AgentOS-related work, classify it as:

```text
kernel:
  canonical rule, route, state, review, workflow, or handoff content under agent-os/.

adapter:
  runtime-facing entry point or projection such as AGENTS.md, CLAUDE.md, .agents/skills/, .claude/skills/, .codex/, or .claude/.

extension:
  optional capability that uses Agent OS but is not required for the kernel.

verification:
  checks, tests, lint, pressure tests, or evidence collectors.

undecided:
  not enough evidence to place safely.
```

Subagents, long-term memory routing, automation, hook wired integration, and end-to-end pressure tests are not kernel work by default.

Dynamic Workflow is kernel work when the latest user message explicitly asks Agent OS to define or run formal multi-worker workflow behavior. Runtime-specific implementations remain adapters.

Memory, wiki, handoff, and audit rules are kernel work when the latest user message explicitly asks Agent OS to preserve project state, make work recoverable, prepare handoff, or make workflow results auditable. Runtime-specific memory skills remain adapters.

End-to-end pressure tests are verification work when the Task Contract explicitly requires behavioral evidence. Passing them does not prove production readiness unless their coverage matches that claim.
