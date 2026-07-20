# Codex Workflow Adapter

## Purpose

This is the Codex-only Dynamic Workflow source for AgentOS. It combines the
AgentOS control contract with the complete vendored runtime from
[`scasella/claude-dynamic-workflows-codex`](https://github.com/scasella/claude-dynamic-workflows-codex).

There is one delegated execution engine:

```text
NO_DELEGATION -> the main conversation does the work directly
delegated      -> the vendored Dynamic Workflow runner executes the workflow
```

Direct main-conversation work is not a second workflow backend. Native Codex
collaboration workers are not an alternative delegated route. Claude keeps its
native Workflow and Superpowers; do not project this adapter into
`.claude/skills/`.

The runtime is vendored at a reviewed upstream revision:

```text
vendor/claude-dynamic-workflows-codex/
vendor/claude-dynamic-workflows-codex/runner/bin/run-workflow.js
vendor/claude-dynamic-workflows-codex/references/authoring.md
vendor/claude-dynamic-workflows-codex/references/runner-readme.md
vendor/claude-dynamic-workflows-codex/examples/
vendor/claude-dynamic-workflows-codex.AGENTOS.md
```

The vendored directory is the runtime source. This adapter owns AgentOS policy:
routing, cheapest-capable model selection, prompts, permissions, write
ownership, evidence promotion, and completion.

## The Routing Decision

Route every non-small Codex task before starting a delegated run. The result is
exactly one of:

```text
NO_DELEGATION:
  One owner can finish safely; the work is tightly coupled, sequential, or
  cheaper and more reliable in the main conversation.

delegated:
  A named failure mode justifies a Dynamic Workflow script and runner process.
```

Delegate when at least one condition is load-bearing:

- genuinely independent branches benefit from parallel execution;
- a bounded specialist context improves the result;
- a fresh reviewer is needed before a costly claim or write;
- a race can test independent strategies against a declared acceptance check;
- a long-lived worker should retain expensive context across turns;
- a long-running run needs journaling, recovery, supervision, or a human gate.

Task size and worker count are not delegation rules. Every worker, phase, and
workflow variant must advance the completion contract or reduce an evidenced
risk enough to justify its coordination cost and token cost.

## Harness Compiler

Compile rough intent into the smallest executable harness that addresses a
named failure mode:

```text
fan-out and synthesize:
  Independent perspectives reduce premature convergence or partition a fixed
  inventory; a final synthesis verifies and merges their results.

staged pipeline:
  Items advance through discovery, verification, and action without unnecessary
  global barriers.

adversarial verification:
  A fresh worker that did not produce the artifact tests important claims or
  edits and defaults to unverified when evidence is weak.

loop until dry:
  Coverage is unknown; deduplicate across rounds and stop after a bounded number
  of dry rounds, a round cap, or the budget envelope.

race and cancel:
  Independent strategies compete against a predeclared acceptance check; keep
  the verified winner and cancel unneeded live workers.

sessionful steering:
  A worker retains useful context; the controller waits, inspects, steers the
  same Codex thread, or replaces it when independence is more important.

human checkpoint:
  Scope, spending, destructive action, production risk, or a value choice
  belongs to the user; pause at a declared `human()` gate with a resume path.

fleet:
  Two to four workflow variants test materially different bets under one
  supervised budget and synthesis contract.
```

Patterns may compose, but each extra component must name the failure mode it
prevents. Functional roles beat decorative personas. One-shot fresh context is
the default for independent review; sessionful workers are for real context
reuse or steering.

## Runtime And DSL

Workflow scripts are plain JavaScript executed by the vendored dependency-free
Node runner. Reusable AgentOS scripts live under `workflows/`; run journals live
under `.workflow-journal/`. A script may use the complete upstream authoring
surface:

```text
export const meta
agent(prompt, options)
parallel(items, worker, options)
pipeline(items, stages)
phase(name, options, work)
workflow(reference, args)
human(question, options)
log(...values)
args
budget.total / budget.spent() / budget.remaining()

agent.start(prompt, options)
agent.waitAny(sessions, options)
session.steer(message, options)
session.wait() / session.poll() / session.cancel() / session.close()
```

Use strict output schemas where structured results matter, including
`additionalProperties: false`. Put source materials before the assignment and
keep the actual question or work order last.

Before spending tokens, plan the workflow:

```bash
node vendor/claude-dynamic-workflows-codex/runner/bin/run-workflow.js workflows/<name>.workflow.js --plan --sandbox read-only --budget <tokens>
```

Then execute the same reviewed script with the selected model, effort, sandbox,
budget, journal, and run id. Do not pass the upstream wrapper's blanket
`--frontier` default unless the whole run is explicitly frontier-only. Prefer
per-call `model` and `effort` options so each role gets the cheapest capable
configuration. CLI `--pin-model` and `--pin-effort` deliberately override every
per-call choice and therefore require a run-level reason.

Use `--sandbox read-only` unless a worker must write. A workspace-writing run
still follows AgentOS permission and single-writer rules. Use `--tui` or `--gui`
only when live monitoring or answering `human()` gates there is useful; use
`--interactive` for a supervisor without a viewer.

## Worker And Model Routing

Use the cheapest capable model, not the cheapest model in isolation:

```text
cheap_worker:
  bounded extraction, enumeration, formatting, polling, fixture generation,
  and mechanically verifiable work.

frontier_worker:
  architecture, synthesis, conflict resolution, root-cause analysis, security,
  ambiguous product judgment, recall-critical reading or exhaustive extraction,
  and review where a miss is costly. A task is not cheap-worker work merely
  because its output is a list; use a cheap worker only when omissions are
  mechanically detectable.

escalation:
  start cheap only when the task is bounded and verifiable; escalate after an
  ambiguous result, failed check, missing evidence, or expanded scope.
```

Resolve tiers to models currently exposed by the local Codex app-server. Current
examples are `gpt-5.6-terra` for bounded work and `gpt-5.6-sol` for pivotal
frontier work; these names are examples, not permanent policy. Reasoning effort
follows ambiguity and the cost of a miss. Do not treat a multi-agent harness as
a reason to pin every worker to the largest model or highest effort.

## Ownership And Prompt Contract

- The main conversation owns the user goal, task contract, routing decision,
  permissions, synthesis, and final claims.
- Each writable artifact has one single writer at a time.
- Parallel workers have disjoint write scopes or return read-only findings.
- An independent reviewer must not share the writer's role or contaminated
  context when clean independence is claimed.
- Before every model call or session start, apply `prompt-craft-review`. A worker
  prompt states the active object, supplied materials, boundaries, evidence
  standard, output contract, write scope, and self-check, with the assignment
  last.
- Runner outputs are support artifacts until checked against source files,
  commands, tests, or runtime evidence.

## Involvement And Decision Rights

Choose one involvement mode for each delegated run:

```text
hands_off:
  Continue with safe reversible defaults; stop before user-owned decisions.

checkpointed (default):
  Pause only at declared scope, write, budget, risk, destructive, or value forks.

interactive:
  Keep a supervisor channel open because the user asked to steer the run live.
```

The user retains decisions about scope changes, spending, destructive actions,
production risk, and values. Every `human()` gate states the question, affected
work, safe default when one exists, and exact resume action. A controller may
steer workers within the accepted contract; it cannot silently grant itself new
authority.

## Planning And Budget

`--plan` is a no-model-call estimate: it counts planned calls and assigns
estimated effort cost. It is a lower bound, not a price guarantee. Record the
user limit, maximum workers, maximum rounds, timeout, and stop-or-escalate
condition whenever they change execution.

The runner checks the token ceiling before starting new calls. Concurrent calls
already in flight can finish above the requested ceiling, so `--budget` is an
admission ceiling rather than a mathematically exact hard cap. Size read-heavy
workers from measured or observed costs when available, not from effort labels
alone. Never spend a material budget without the user's authority.

When the ceiling is reached, preserve completed work and expose a resumable
checkpoint. A budget stop never converts partial work into completion.

## State Board And Journal

The runner journal owns per-call and per-session execution state. AgentOS owns
the user contract and promotion state. Do not maintain a competing worker
backend registry.

```yaml
codex_workflow:
  run_id:
  active_user_object:
  completion_contract:
  routing_decision: NO_DELEGATION | delegated
  routing_reason:
  failure_mode:
  harness_shape: direct | fan_out_and_synthesize | staged_pipeline | adversarial_verification | loop_until_dry | race_and_cancel | sessionful_steering | fleet | mixed
  execution_engine: vendored_dynamic_workflow_runner
  script_path:
  journal_path:
  result_path:
  workspace_fingerprint:
  involvement_mode: hands_off | checkpointed | interactive
  model_policy:
  budget_envelope:
    user_limit:
    max_workers:
    max_rounds:
    stop_or_escalate_when:
  write_owners:
  checkpoints:
  promotion_notes:
  next_action:
```

The workspace fingerprint records the inputs on which cached results depend: a
commit id when available plus the relevant dirty-file or content state. Before
`--resume`, verify that fingerprint. If relevant inputs changed or cannot be
compared safely, start a fresh run instead of promoting stale journal entries.

Use unique `--run-id` or `--journal` values for concurrent variants. Do not let
two runs append to the same journal. Preserve the script, args, model policy,
budget, journal, final result, and fingerprint as the resume contract.

## Monitor, Steer, Recover

Starting a process is not completion. Monitor required phases until every
required branch is completed, repaired, canceled, superseded, or explicitly
downgraded with its consequence recorded.

Use runner-native control:

```text
wait for the first actionable session: agent.waitAny
reuse warm context:                    session.steer / session.wait / session.poll
cancel a losing strategy:              session.cancel
finish a retained thread:              session.close
inspect or answer several runs:         runner/bin/fleet.js
supervise a fleet:                      runner/bin/supervise.js
```

Recovery order:

1. retry or resume the same journal when its script and workspace fingerprint
   still match;
2. continue the same live session only when its context remains relevant and
   trustworthy;
3. replace the failed role with the same bounded contract;
4. reuse another role only with an explicit independence downgrade;
5. stop at a real contract, authority, or budget blocker.

Never mark the original worker completed after replacement. Its state remains
failed or superseded. For a race, preserve winning evidence and useful negative
results, then cancel remaining live sessions. For loop-until-dry, deduplicate
against every prior round and enforce both dry-round and maximum-round stops.

## Surface And Runtime Evidence

After a run, inspect and summarize it with the vendored tools:

```bash
node vendor/claude-dynamic-workflows-codex/runner/bin/map-run.js --journal <journal> --no-color
node vendor/claude-dynamic-workflows-codex/runner/bin/summarize-run.js --journal <journal>
node vendor/claude-dynamic-workflows-codex/runner/bin/view-run.js --journal <journal>
```

Record actual run id, start and terminal state, result reference, token usage,
model and effort, repairs, and journal readability. App-server thread ids and a
runner viewer prove runner-level traceability; they do not prove that internal
workers are user-visible Codex Desktop tasks. Create separate user-visible Codex
tasks only when the user explicitly requests that product effect.

## Execution Order

1. Fix the user goal, completion contract, evidence, and permission boundary.
2. Stage the current turn admission. Delegation must be `true`, and its paths,
   budget, write scope, and external commitments must fit the accepted authority.
3. Name the failure mode and select `NO_DELEGATION` or `delegated`.
4. If delegated, compile the minimum harness and author its workflow script.
5. Apply Prompt Craft, model routing, effort, sandbox, budget, and one-writer
   policy to every call.
6. Record the workspace fingerprint and run `--plan` before model calls.
7. Obtain any missing spending, write, destructive, or product authority.
8. Execute only through the vendored Dynamic Workflow runner.
9. Monitor, steer, answer declared gates, repair, cancel, or resume through the
   runner journal and session controls.
10. Inspect the result, map, summary, costs, and referenced evidence.
11. Run route and evidence promotion checks, then synthesize in the main
    conversation.

## Promotion And Completion

A runner event proves that a call or session existed and returned something. It
does not prove factual, causal, recommendation, edit, or completion claims.

A delegated run is complete only when required branches have terminal handling,
result references exist, relevant source or command evidence has been checked,
recovery and visibility claims match observations, the main conversation has
verified promoted claims, open obligations are empty, and the user-visible
completion contract is met.

If interrupted, preserve the run id, script, contract, journal, fingerprint,
model policy, write ownership, terminal states, result references, last verified
checkpoint, and exact next action.
