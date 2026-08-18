# AgentOS Router

## Purpose

Map an observed task condition to one canonical AgentOS document or native
runtime capability. The active user object remains the route anchor.

## Route Table

| Condition | Canonical document | Runtime skill or adapter |
|---|---|---|
| Any substantive judgment — the cognitive procedure | `agent-os/workflows/cognition.md` | constitutive duty of every seat |
| What the system is, how its parts collaborate | `agent-os/architecture.md` | read on demand |
| First-principles, causal, root-cause, or judgment review | `agent-os/review/reasoning-base.md` | `reasoning-causality-review` |
| Intent, goal-versus-means, authority, or question admission | `agent-os/review/intent-causal-gate.md` | `intent-contract-review` |
| Explicit adversarial or anti-sycophancy review | `agent-os/review/anti-sycophancy-gate.md` | `anti-sycophancy-review` |
| Completion contract and evidence standard | `agent-os/review/task-contract.md` | `lifecycle-execution` |
| Route drift or promotion of tool and worker output | `agent-os/review/route-keeper-promotion-gate.md` | `route-promotion-review` |
| Code, dependency, or feature creation | `agent-os/review/minimal-code-gate.md` | `minimal-code-review` |
| Engineering plan: three translations, acceptance standard, time budget | `agent-os/review/engineering-gate.md` | `engineering-plan-review` |
| Prompt for another model, worker, panel, or judge | `agent-os/review/prompt-craft-gate.md` | `prompt-craft-review` |
| Claim wording, memory, handoff, or completion evidence | `agent-os/review/evidence-to-claim-gate.md` | `evidence-claim-review` |
| Shaping any user-facing delivery or report | `agent-os/review/delivery-gate.md` | `delivery-review` |
| Completion, status, problem, or decision reporting | `agent-os/review/task-contract.md` + `agent-os/review/evidence-to-claim-gate.md` | `lifecycle-execution` |
| Full task lifecycle | `agent-os/workflows/agent-execution-lifecycle.md` | `lifecycle-execution` |
| Task orchestration on Claude (three departments, user-invoked) | `agent-os/rules-card.md` | `agentos` skill: the session becomes 中书, spawns `agentos-menxia` / `agentos-shangshu` |
| Vague intent or explicit think-through deliberation | `agent-os/workflows/think-through.md` | constitutive Zhongshu duty (the bound session on Claude, `agentos-zhongshu` thread on Codex) |
| Task orchestration on Codex (three departments, user-invoked) | `agent-os/adapters/codex-workflow.md` | `agentos` skill relay; Desktop threads via `codex_app.create_thread` |
| Explicit multi-model answer fusion | `agent-os/workflows/fusion-workflow.md` | `fusion-workflow` |
| Durable memory, Wiki, ledgers, or handoff | `agent-os/memory/routing.md` | `memory-wiki-routing` |
| Stage-end reconciliation or error routing | `agent-os/memory/routing.md` | `memory-wiki-routing` |
| Confirmed mistake, post-delivery error learning | `agent-os/memory/error-learning.md` | `agentos-yushi` background censor |

## Runtime Routes

- The chain is opt-in on both runtimes: the user invokes the `agentos` skill
  (`.agents/skills/agentos/`, `.claude/skills/agentos/`). Same kernel, two
  transports: on Codex the invoking thread is the relay and carries the user's
  exact words to the 中书 thread and back; on Claude the invoking session itself
  is 中书 and spawns the other seats as subagents. An invocation without task
  content opens nothing.
- Codex: seats are project threads created through `codex_app.create_thread`;
  `.codex/agents/` supplies developer
  instructions and the chain gate keeps their order. No thread simulates another seat.
- Claude: seats are `.claude/agents/` (`agentos-zhongshu` first); native
  Workflow and Superpowers serve inside the chain.
- Native skill roots are `.agents/skills/` and `.claude/skills/`. Skill files
  are adapters and must point back to their canonical kernel document.

## Routing Boundary

Load only routes triggered by the present task. A route changes what to read;
it does not create authority, promote support work into the user object, or
prove completion.
