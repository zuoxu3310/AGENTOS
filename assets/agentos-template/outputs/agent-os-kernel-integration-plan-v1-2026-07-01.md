# Agent OS Kernel Integration Plan v1

Date: 2026-07-01

## Goal

Move the current six reasoning and execution layers toward a real `agent-os/` kernel without expanding the project into subagents, memory systems, automation, hooks, or pressure tests.

This plan is about placement and integration only.

## Direct Kernel Content

These belong directly in the Agent OS kernel:

```text
Reasoning Base:
  target: agent-os/review/reasoning-base.md

Intent-Causal Gate:
  target: agent-os/review/intent-causal-gate.md

Task Contract:
  target: agent-os/review/task-contract.md

Route Keeper / Promotion Gate:
  target: agent-os/review/route-keeper-promotion-gate.md

Evidence-to-Claim Gate:
  target: agent-os/review/evidence-to-claim-gate.md

Agent Execution Lifecycle:
  target: agent-os/workflows/agent-execution-lifecycle.md
```

## Template Material

These stay as migration source material until the real `agent-os/` directory is created:

```text
outputs/reasoning-base-v1-templates-2026-07-01.md
outputs/intent-causal-gate-v1-templates-2026-07-01.md
outputs/task-contract-v1-templates-2026-07-01.md
outputs/route-keeper-promotion-gate-v1-templates-2026-07-01.md
outputs/evidence-to-claim-gate-v1-templates-2026-07-01.md
outputs/agent-execution-lifecycle-v1-templates-2026-07-01.md
```

They are not the final kernel paths.

## Thin Native Skill Wrappers

Later, native runtime skill wrappers can be added here:

```text
.agents/skills/<skill-name>/SKILL.md
.claude/skills/<skill-name>/SKILL.md
```

Each wrapper should contain only:

```text
- trigger condition
- source file under `agent-os/`
- minimum expected output shape
```

Suggested wrappers:

```text
reasoning-causality-review:
  source: agent-os/review/reasoning-base.md

intent-contract-review:
  source: agent-os/review/intent-causal-gate.md and agent-os/review/task-contract.md

route-promotion-review:
  source: agent-os/review/route-keeper-promotion-gate.md

evidence-claim-review:
  source: agent-os/review/evidence-to-claim-gate.md

lifecycle-execution:
  source: agent-os/workflows/agent-execution-lifecycle.md
```

Do not copy the full kernel body into wrappers.

## Entry Adapters

`AGENTS.md` and `CLAUDE.md` should eventually become thinner:

```text
- minimum communication and source-of-truth rules
- boot pointer to agent-os/boot.md
- router pointer to agent-os/router.md
- emergency completion and evidence rules
```

They should not compete with `agent-os/` as the rule source.

## Do Not Move Into This Step

Do not implement these now:

```text
- subagent protocol
- long-term memory routing
- automation platform
- hook wired integration
- end-to-end pressure test
- global Agent OS install
- full native skill bodies copied from kernel files
```

They may become extension or verification work after the kernel directory exists and the six layers are placed.

## Order Of Work

```text
1. Create `agent-os/` skeleton.
2. Add `boot.md` and `router.md` as minimal startup and routing files.
3. Move the six layers into `review/` and `workflows/` according to Placement Map v1.
4. Add `state/current.md` with active user object, contract, route, evidence state, and next safe action.
5. Add `handoffs/` format.
6. Add `tools/aos-lint.py` for structure only.
7. Convert AGENTS.md and CLAUDE.md into thin adapters.
8. Add native skill wrappers that point into `agent-os/`.
9. Run regression checks before claiming migration is complete.
```

## Acceptance Evidence

The integration is complete only when evidence shows:

```text
- `agent-os/` exists and contains the mapped files.
- The six layers are present in their target kernel paths.
- AGENTS.md and CLAUDE.md point to the kernel instead of duplicating it.
- Native skill wrappers are thin pointers, if they exist.
- aos-lint proves structure only and is not used as behavioral proof.
- Existing RB, ICG, TC, RKP, ECG, AEL, and AOK regression checks pass.
```

