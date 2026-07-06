# Agent OS Kernel Definition v1

Date: 2026-07-01

## Essence

Agent OS is a repo-local working-guide directory for Agents in a project.

In plain terms: `agent-os/` is where the project keeps the operating rules that tell Agents how to understand the task, route the work, use skills, preserve state, review claims, and hand off safely.

## Kernel Definition

```text
Agent OS kernel:
  the canonical `agent-os/` directory in a project.

Primary job:
  keep Agents working on the real user object through rules, routing, state, review gates, workflows, and handoffs.

Not primary job:
  replace every agent runtime, become a global install, or turn tools, hooks, reports, tests, or subagents into the task itself.
```

## Canonical Core

`agent-os/` is the source of truth for Agent OS content inside a repo.

It owns:

```text
- boot rules
- task routing
- current state
- review gates
- reusable project workflows
- handoff records
- structural checks
```

It should not depend on one Agent product's private memory as its only source of truth.

## Adapters And Projections

These are entry points or runtime projections, not the kernel:

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

They may point into `agent-os/`, summarize a boot rule, expose a native skill trigger, or run an adapter check. They should not become competing rule bodies.

Native skill wrappers should stay thin:

```text
- trigger condition
- what file under `agent-os/` to read
- what minimum output shape is expected
```

They should not copy the full kernel text unless there is a verified runtime reason.

## Supporting Capabilities

The following are support capabilities unless the latest user message explicitly makes them the current deliverable:

```text
- subagent protocol
- long-term memory routing
- automation platform
- hooks
- end-to-end pressure tests
- benchmark harnesses
- dashboards
```

Support capabilities can enforce, test, or extend Agent OS, but they are not the Agent OS kernel by default.

Dynamic Workflow is kernel content when it defines the canonical workflow contract under `agent-os/workflows/`. Codex App Server, Claude Dynamic Workflows, Claude Agent Teams, and other runtime mechanisms are adapters that implement that contract.

Hook claims are runtime-scoped. Claude Code is wired through `.claude/settings.json`
and `.claude/hooks/`. Codex is wired through `.codex/hooks.json` and `.codex/hooks/`, including SessionStart state injection, UserPromptSubmit audit baseline capture, Stop hook audit verification, kernel-edit lint, and enforcement-layer edit guard.
Other runtimes remain `Manual until wired` unless fresh runtime evidence proves
automatic triggering in that runtime.

`tools/aos-lint.py` can prove structural health only. It cannot prove that Agent OS actually improves task behavior.

## Capability Classification

Before building a new AgentOS-related capability, classify it as one of:

```text
kernel:
  canonical rule, route, state, review, workflow, or handoff content under `agent-os/`.

adapter:
  runtime-specific entry or projection such as AGENTS.md, CLAUDE.md, `.agents/skills/`, `.claude/skills/`, `.codex/`, or `.claude/`.

extension:
  optional capability that can use Agent OS but is not required for the kernel, such as subagent orchestration or long-term memory sync.

verification:
  checks, tests, lint, pressure tests, or evidence collectors.

undecided:
  not enough evidence to place safely; do not implement as kernel until the active user object is clarified.
```

## Six Current Gates

The current six layers belong to the Agent OS kernel because they define how Agents work, not merely how one report is written:

```text
1. Reasoning Base
2. Intent-Causal Gate
3. Task Contract
4. Route Keeper / Promotion Gate
5. Evidence-to-Claim Gate
6. Agent Execution Lifecycle
```

They must be placed through Placement Map v1 before any migration into a real `agent-os/` directory.

## First-Principles Contract

Agent OS exists to prevent these failures:

```text
- mistaking a tool for the user's goal
- replacing the active user object with a report or test pass
- treating subagent output as fact without source verification
- inventing causal explanations after the fact
- changing routes during execution without noticing
- claiming completion without evidence
- losing state during handoff or context compression
```

So the kernel must stay small, canonical, and behavior-facing.

If a file does not help Agents decide what to do, when to do it, how to verify it, or how to hand it off, it probably does not belong in the kernel.
