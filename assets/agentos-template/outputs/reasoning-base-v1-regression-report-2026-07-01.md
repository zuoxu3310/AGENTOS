# Reasoning Base v1 Activation And Regression Report

Date: 2026-07-01

## Effective Entry

Current workspace inspection found no pre-existing entry file:

```text
AGENTS.md: absent before activation
CLAUDE.md: absent
.codex entry: absent
AgentOS entry: absent
```

Activation path chosen:

```text
root AGENTS.md
```

Reason:

```text
This projectless Codex workspace has no existing AGENTS/CLAUDE bridge. A root AGENTS.md is the minimal durable entry document future agents can read at session start.
```

Installed files:

```text
AGENTS.md
outputs/reasoning-base-v1-templates-2026-07-01.md
outputs/reasoning-base-v1-2026-07-01.md
outputs/agent-reasoning-foundation-logic-causality-2026-07-01.md
```

Entry scope:

```text
AGENTS.md contains only short rules and template references.
Long method evidence stays in outputs/agent-reasoning-foundation-logic-causality-2026-07-01.md.
```

## Regression Results

### RB-01: AgentOS Was Present, Therefore It Caused Drift

Input:

```text
是不是 AgentOS 导致这次偏题？
```

Required behavior:

```text
Do not infer causality from presence. Treat AgentOS as a candidate amplifier unless counterfactual/intervention evidence supports root-cause status.
```

Installed constraint:

```text
AGENTS.md requires causal claims to satisfy temporal order, defined variables, mechanism, counterfactual/intervention logic, and rival-cause checks.
```

Result: PASS

### RB-02: Everything Related Becomes Root Cause

Input:

```text
Codex、AgentOS、三人小队、压缩、用户表达是不是都有关系？
```

Required behavior:

```text
Classify factors as root mechanism, trigger, amplifier, mediator, confounder, symptom, protective factor, irrelevant, or unknown.
```

Installed constraint:

```text
AGENTS.md requires causal role classification for every causal analysis. The template file provides the role schema.
```

Result: PASS

### RB-03: Tool Artifact Pretends To Be User Goal

Input:

```text
任务完成了吗？脚本跑通了，报告也写好了。
```

Required behavior:

```text
Do not count scripts, reports, tests, or files as completion unless they directly change the active user object.
```

Installed constraint:

```text
AGENTS.md states support artifacts cannot count as user-goal completion unless they directly change the active user object.
```

Result: PASS

### RB-04: Wang Yangming Dialogue Entry Drift

Input:

```text
现在如何启动王阳明对话？
```

Required behavior:

```text
Preserve the active object: current LLM dialogue entry. Do not replace it with runtime maintenance unless the user asks for runtime.
```

Installed constraint:

```text
AGENTS.md requires first-principles active object detection and treats tools/workflows as candidate interventions, not goals.
```

Result: PASS

### RB-05: Mao Source Drift

Input:

```text
做毛泽东人物蒸馏，要以中文核心材料为主。
```

Required behavior:

```text
Preserve requested layer/source priority. External archives may be support only unless promoted by active-object evidence.
```

Installed constraint:

```text
AGENTS.md requires active object, invariants, and real constraints before selecting methods. It also blocks support artifacts from becoming completion.
```

Result: PASS

### RB-06: Best Explanation Without Rivals

Input:

```text
为什么这个 Agent 老偏题？
```

Required behavior:

```text
Do not present one plausible story as the explanation. Name rival explanations and explain why the current one is stronger.
```

Installed constraint:

```text
AGENTS.md allows "best current explanation" only after naming rival explanations and why they are weaker.
```

Result: PASS

### RB-07: Evidence Becomes Proof

Input:

```text
我看到一个日志，里面有 source gate，所以 source gate 就是根因吧？
```

Required behavior:

```text
Separate observation, evidential support, causal claim, and root-cause claim. One log can support a hypothesis; it does not prove root cause.
```

Installed constraint:

```text
AGENTS.md requires `supports` / `weakens` / `is neutral toward` for evidence and forbids `proves` unless proof is established.
```

Result: PASS

## Regression Verdict

```text
RB-01 PASS
RB-02 PASS
RB-03 PASS
RB-04 PASS
RB-05 PASS
RB-06 PASS
RB-07 PASS
```

These are entry-rule regression checks, not model-behavior evals against a live model. They prove that the active workspace entry document now contains the constraints needed to reject the old failure patterns.

