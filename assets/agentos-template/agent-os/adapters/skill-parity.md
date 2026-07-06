# Skill Parity Matrix

Date: 2026-07-01

## Purpose

AgentOS does not unify Codex and Claude skill file formats. It unifies capabilities by requiring each runtime to have a native adapter skill that points back to the same AgentOS kernel capability.

## Rule

```text
same capability:
  allowed

same copied skill format:
  not allowed

kernel source:
  agent-os/

runtime adapters:
  .agents/skills/
  .claude/skills/
```

Codex skills may include `agents/openai.yaml`. Claude skills must not depend on Codex UI metadata.

## Matrix

| AgentOS capability | Kernel source | Codex native skill | Claude native skill | Status |
|---|---|---|---|---|
| Reasoning Base / causality | `agent-os/review/reasoning-base.md` | `.agents/skills/reasoning-causality-review/SKILL.md` | `.claude/skills/reasoning-causality-review/SKILL.md` | present |
| Intent + Task Contract | `agent-os/review/intent-causal-gate.md`, `agent-os/review/task-contract.md` | `.agents/skills/intent-contract-review/SKILL.md` | `.claude/skills/intent-contract-review/SKILL.md` | present |
| Route Keeper / Promotion Gate | `agent-os/review/route-keeper-promotion-gate.md` | `.agents/skills/route-promotion-review/SKILL.md` | `.claude/skills/route-promotion-review/SKILL.md` | present |
| Evidence + Completion Gate | `agent-os/review/evidence-to-claim-gate.md`, `agent-os/review/completion-gate.md` | `.agents/skills/evidence-claim-review/SKILL.md` | `.claude/skills/evidence-claim-review/SKILL.md` | present |
| Agent Execution Lifecycle | `agent-os/workflows/agent-execution-lifecycle.md` | `.agents/skills/lifecycle-execution/SKILL.md` | `.claude/skills/lifecycle-execution/SKILL.md` | present |
| Dynamic Workflow / worker audit | `agent-os/workflows/dynamic-workflow.md`, `agent-os/adapters/runtime-visibility.md` | `.agents/skills/dynamic-workflow/SKILL.md` | `.claude/skills/dynamic-workflow/SKILL.md` | added |
| Memory + Wiki routing | `agent-os/memory/bootstrap.md`, `agent-os/memory/routing.md`, `agent-os/memory/sync-audit.md`, `agent-os/memory/wiki-v2.md` | `.agents/skills/memory-wiki-routing/SKILL.md` | `.claude/skills/memory-wiki-routing/SKILL.md` | added |
| Anti-Sycophancy Gate | `agent-os/review/anti-sycophancy-gate.md` | `.agents/skills/anti-sycophancy-review/SKILL.md` | `.claude/skills/anti-sycophancy-review/SKILL.md` | added |
| Minimal Code Gate | `agent-os/review/minimal-code-gate.md` | `.agents/skills/minimal-code-review/SKILL.md` | `.claude/skills/minimal-code-review/SKILL.md` | added |
| Per-Turn Audit Gate | `agent-os/review/per-turn-audit-gate.md` | entry docs, unconditional every turn (no wrapper) | entry docs, unconditional every turn (no wrapper) | added |
| Prompt Craft Gate | `agent-os/review/prompt-craft-gate.md` | `.agents/skills/prompt-craft-review/SKILL.md` | `.claude/skills/prompt-craft-review/SKILL.md` | added |
| Fusion Workflow | `agent-os/workflows/fusion-workflow.md` | `.agents/skills/fusion-workflow/SKILL.md` | `.claude/skills/fusion-workflow/SKILL.md` | added |

## Support Skills

Global skills such as `project-memory-bootstrap`, `wiki-maintenance`, and `neat-freak` are support skills. They may inform AgentOS memory behavior, but they do not replace the repo-local AgentOS kernel or the local Codex/Claude parity adapters.

## Verification Standard

Skill parity requires:

```text
- both runtime paths exist
- each SKILL.md has parseable frontmatter with name and description
- Codex skill validates with Codex quick_validate.py
- Claude skill validates with Claude skill-creator quick_validate.py
- Codex-only `agents/openai.yaml` stays under .agents/skills
- Claude skills do not require Codex openai.yaml
```
