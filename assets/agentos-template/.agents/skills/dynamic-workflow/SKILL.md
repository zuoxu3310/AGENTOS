---
name: dynamic-workflow
description: Codex-only AgentOS router and runtime adapter. For every non-small Codex task, decide NO_DELEGATION or compile the smallest failure-mode-driven workflow and execute delegated work only through the vendored Dynamic Workflow runner. Use for independent branches, specialist workers, pipelines, races, warm session steering, human gates, recovery, fleets, or independent review.
---

# Dynamic Workflow

Use this Skill because AgentOS needs one consistent Codex orchestration path.
Claude keeps its native Workflow and Superpowers.

## Source

Read completely:

```text
agent-os/boot.md
agent-os/router.md
agent-os/adapters/codex-workflow.md
agent-os/review/prompt-craft-gate.md
agent-os/review/route-keeper-promotion-gate.md
agent-os/review/evidence-to-claim-gate.md
```

For authoring or operating a delegated run, read the relevant vendored source:

```text
vendor/claude-dynamic-workflows-codex/references/authoring.md
vendor/claude-dynamic-workflows-codex/references/runner-readme.md
vendor/claude-dynamic-workflows-codex/references/fleet-protocol.md
vendor/claude-dynamic-workflows-codex/examples/
```

## Trigger

Route every non-small Codex task. Return exactly one of:

- `NO_DELEGATION`: the main conversation completes the work directly.
- `delegated`: name the failure mode, compile the smallest useful harness, and
  execute it through the vendored runner.

`NO_DELEGATION` is not a workflow backend. Do not use native collaboration
workers as a second delegated route. Do not create a workflow just because a
task is large.

## Delegated Runtime Rule

The sole delegated execution command is:

```bash
node vendor/claude-dynamic-workflows-codex/runner/bin/run-workflow.js <script.js> [options]
```

Author reusable scripts under `workflows/`. Use the full upstream DSL when the
chosen harness needs it: `agent`, `parallel`, `pipeline`, `phase`, `workflow`,
`human`, `budget`, sessionful `agent.start` / `agent.waitAny` /
`session.steer`, journaling and resume, fleet supervision, maps, summaries, TUI,
or GUI.

Run `--plan` before any expensive or adaptive workflow. Apply the AgentOS
cheapest-capable model policy per call; do not inherit the upstream Claude
wrapper's blanket `--frontier` default. Use a read-only sandbox unless a worker
must write, keep one writer per artifact, and obtain authority before material
token spend, destructive actions, or product-risk choices.

Before `--resume`, compare the recorded workspace fingerprint. Start fresh if
relevant inputs changed or safe comparison is unavailable.

Use app thread creation separately only when the user explicitly asks for a
user-visible Codex task. Runner/app-server readability does not prove Codex
Desktop visibility.

## Required Output Shape

```yaml
dynamic_workflow:
  active_user_object:
  contract:
  routing_decision: NO_DELEGATION | delegated
  routing_reason:
  failure_mode:
  harness_shape: direct | fan_out_and_synthesize | staged_pipeline | adversarial_verification | loop_until_dry | race_and_cancel | sessionful_steering | fleet | mixed
  execution_engine: vendored_dynamic_workflow_runner
  script_path:
  journal_path:
  run_id:
  workspace_fingerprint:
  involvement_mode: hands_off | checkpointed | interactive
  model_policy:
  budget_envelope:
  write_owners:
  result_ref:
  promotion_gate:
  final_synthesis:
  resume_action:
  evidence_limits:
```

Runner outputs remain support artifacts until the main conversation verifies
them against source paths, commands, files, tests, or runtime evidence.
