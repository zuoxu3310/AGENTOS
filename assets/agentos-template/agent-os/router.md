# AgentOS Router

## Purpose

Map an observed task condition to one canonical AgentOS document or native
runtime capability. The active user object remains the route anchor.

## Route Table

| Condition | Canonical document | Runtime skill or adapter |
|---|---|---|
| First-principles, causal, root-cause, or judgment review | `agent-os/review/reasoning-base.md` | `reasoning-causality-review` |
| Intent, goal-versus-means, authority, or question admission | `agent-os/review/intent-causal-gate.md` | `intent-contract-review` |
| Explicit adversarial or anti-sycophancy review | `agent-os/review/anti-sycophancy-gate.md` | `anti-sycophancy-review` |
| Non-small completion contract and evidence standard | `agent-os/review/task-contract.md` | `lifecycle-execution` |
| Route drift or promotion of tool and worker output | `agent-os/review/route-keeper-promotion-gate.md` | `route-promotion-review` |
| Code, dependency, or feature creation | `agent-os/review/minimal-code-gate.md` | `minimal-code-review` |
| Prompt for another model, worker, panel, or judge | `agent-os/review/prompt-craft-gate.md` | `prompt-craft-review` |
| Claim wording, memory, handoff, or completion evidence | `agent-os/review/evidence-to-claim-gate.md` | `evidence-claim-review` |
| Completion, status, problem, or decision reporting | `agent-os/review/task-contract.md` + `agent-os/review/evidence-to-claim-gate.md` | `lifecycle-execution` |
| Full non-small lifecycle | `agent-os/workflows/agent-execution-lifecycle.md` | `lifecycle-execution` |
| Codex delegation or recovery | `agent-os/adapters/codex-workflow.md` | `dynamic-workflow` |
| Explicit multi-model answer fusion | `agent-os/workflows/fusion-workflow.md` | `fusion-workflow` |
| Durable memory, Wiki, ledgers, or handoff | `agent-os/memory/routing.md` | `memory-wiki-routing` |
| Stage-end reconciliation or error routing | `agent-os/memory/routing.md` | `memory-wiki-routing` |

## Runtime Routes

- Codex: `$dynamic-workflow` returns `NO_DELEGATION` or uses the vendored runner
  as the one delegated execution engine.
- Claude: use native Workflow and enabled Superpowers; do not load the Codex
  Dynamic Workflow adapter.
- Native skill roots are `.agents/skills/` and `.claude/skills/`. Skill files
  are adapters and must point back to their canonical kernel document.

## Routing Boundary

Load only routes triggered by the present task. A route changes what to read;
it does not create authority, promote support work into the user object, or
prove completion.
