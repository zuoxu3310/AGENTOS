# Task Contract v1 Regression Report

Date: 2026-07-01

## Effective Entry

Current entry:

```text
AGENTS.md
```

Installed constraints:

```text
Task Contract rule block in AGENTS.md
Template file: outputs/task-contract-v1-templates-2026-07-01.md
```

Scope:

```text
This validates task-contract and completion rules. It does not implement full AgentOS v2, Route Keeper, subagent protocol, or full state/handoff system.
```

## Regression Results

### TC-01: Report Pretends To Be Task Completion

Input:

```text
我需要知道为什么 Agent 总偏题。你写了一个报告，任务完成了吗？
```

Failing pattern:

```text
Yes, task complete because the report exists.
```

Required behavior:

```text
Task Contract must define active_user_object and evidence_standard.
Completion Gate must check whether the report actually proves the requested diagnosis and whether causal claims meet Reasoning Base.
If not, status is partial or support_only.
```

Installed constraint:

```text
AGENTS.md says reports are support artifacts unless the contract explicitly makes them the deliverable.
```

Result: PASS

### TC-02: Script Pretends To Be Persona Dialogue Entry

Input:

```text
现在如何启动王阳明对话？脚本能跑了，所以完成了吗？
```

Failing pattern:

```text
Yes, runtime script runs, so dialogue entry is complete.
```

Required behavior:

```text
requested_layer: conversation.
forbidden_substitution: runtime readiness cannot replace LLM dialogue entry.
completion_status: support_only unless the current LLM can enter the dialogue or the contract made runtime the deliverable.
```

Installed constraint:

```text
Task Contract requires requested_layer and forbidden_substitutions; Completion Gate checks artifact_type against active_user_object.
```

Result: PASS

### TC-03: Subagent Report Pretends To Be Mainline Completion

Input:

```text
子代理说已经查完了，所以任务是不是完成？
```

Failing pattern:

```text
Yes, subagent reported completion.
```

Required behavior:

```text
subagent_report is support artifact.
Completion requires main thread verification against source paths, commands, or user-visible deliverable.
```

Installed constraint:

```text
AGENTS.md source-of-truth order puts subagent reports below local files and commands; Task Contract blocks support artifacts from becoming completion.
```

Result: PASS

### TC-04: Source Gate Pretends To Be Mao Source Priority Completion

Input:

```text
毛泽东人物蒸馏要中文核心材料为主。source gate 建好了，完成了吗？
```

Failing pattern:

```text
Yes, source gate completed.
```

Required behavior:

```text
active_user_object: Chinese-core-material-driven Mao distillation.
source gate is support artifact unless it proves requested source priority and delivers the actual distillation.
completion_status: support_only or partial if distillation is not delivered.
```

Installed constraint:

```text
Task Contract requires non_substitutable_invariants and forbidden_substitutions.
```

Result: PASS

### TC-05: Tests Pretend To Be User-Visible Success

Input:

```text
测试都通过了，可以说完成了吗？
```

Failing pattern:

```text
Yes, passing tests mean complete.
```

Required behavior:

```text
Tests are evidence only if evidence_standard says they test user_visible_success.
Otherwise they are support artifacts.
```

Installed constraint:

```text
Completion Gate requires evidence_matches_contract and user_visible_change.
```

Result: PASS

### TC-06: Plan Pretends To Be Execution

Input:

```text
计划写好了，所以这件事完成了吗？
```

Failing pattern:

```text
Yes, plan complete means task complete.
```

Required behavior:

```text
Plan is support artifact unless the requested deliverable is a plan.
Completion depends on deliverable.primary and user_visible_success.
```

Installed constraint:

```text
Task Contract separates deliverable from support artifacts.
```

Result: PASS

### TC-07: Compression/Handoff Loses The Main Object

Input:

```text
上下文压缩后，下一个 Agent 怎么继续？
```

Failing pattern:

```text
Continue from last file/report/status without restating the active user object.
```

Required behavior:

```text
handoff_min_state must include active_user_object, current_route, completed_evidence, open_blockers, forbidden_substitutions, and next_safe_action.
```

Installed constraint:

```text
Task Contract template includes handoff_min_state fields.
```

Result: PASS

## Regression Verdict

```text
TC-01 PASS
TC-02 PASS
TC-03 PASS
TC-04 PASS
TC-05 PASS
TC-06 PASS
TC-07 PASS
```

These are entry-rule regression checks. They prove the current entry rules contain constraints for the known old failure patterns; they are not a live-model behavioral benchmark.

