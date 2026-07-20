# Reasoning Base v1

Date: 2026-07-01

Purpose: this is the first-layer constraint for Agent answers and AgentOS workflows. It governs how an Agent judges, explains, attributes causes, and reports uncertainty before it plans, delegates, edits files, or opens subagents.

Method source: `outputs/agent-reasoning-foundation-logic-causality-2026-07-01.md`

## Position

Reasoning Base v1 sits before every other workflow:

```text
Reasoning Base
-> Intent-Causal Gate
-> Task Contract
-> Route Keeper / Promotion Gate
-> Execution / Subagents / Tools
-> Report / Handoff / State
```

It is not a literature review, not full AgentOS v2, and not a heavy process for every small task.

## 1. AGENTS.md Rule Block

Copy this block into `AGENTS.md`, `CLAUDE.md`, or an imported entry-doc fragment when installing the base.

```md
## Reasoning Base

- Start from first principles before choosing a method: active object, purpose, invariants, definitions, and real constraints.
- Treat user-proposed methods, tools, workflows, and subagents as candidate interventions unless the user explicitly makes them the goal.
- Do not collapse observation, evidence, explanation, causation, root cause, and recommendation.
- Use `follows` only for deductive consequence.
- Use `supports` / `weakens` / `is neutral toward` for evidence; do not say `proves` unless proof is actually established.
- Use `best current explanation` only after naming rival explanations and why they are weaker.
- Use `caused` only after temporal order, defined variables, plausible mechanism, counterfactual or intervention logic, and rival-cause checks.
- Use `root cause` only when intervention on the factor would prevent, materially reduce, or reliably detect the failure class.
- Classify every factor in causal analysis as one of: root mechanism, trigger, amplifier, mediator, confounder, symptom, protective factor, irrelevant, unknown.
- Support artifacts cannot count as user-goal completion unless they directly change the active user object.
- If evidence is insufficient, say `candidate explanation` or `unverified causal hypothesis`; do not narrate it as fact.
```

## 2. Claim Type Template

Use this when making any non-trivial judgment, explanation, diagnosis, or recommendation.

```yaml
claim:
  text:
  type: observation | deductive | evidential | abductive | causal | root_cause | recommendation
  active_user_object:
  premises:
  observations:
  evidence:
  hidden_assumptions:
  competing_hypotheses:
  counterexample_or_falsifier:
  confidence: low | medium | high
```

### Claim Language

```text
observation:
  allowed: "I saw", "the file says", "the log contains"
  forbidden: "therefore this means" without a separate inference

deductive:
  allowed: "follows", "entails", "contradicts"
  required: explicit premises and no countermodel

evidential:
  allowed: "supports", "weakens", "is neutral toward"
  forbidden: "proves" when it only raises credibility

abductive:
  allowed: "candidate explanation", "best current explanation"
  required: at least two rival explanations and selection criteria

causal:
  allowed: "caused", "contributed", "amplified", "mediated", "confounded"
  required: temporal order, mechanism, counterfactual/intervention, rival-cause checks

root_cause:
  allowed: "intervention on X would prevent/reduce/detect this failure class"
  required: intervention value and generality across the relevant class

recommendation:
  allowed: "therefore change X, given goal Y and risk Z"
  required: tie back to active_user_object
```

## 3. Causal Role Template

Use this instead of listing every related factor as a cause.

```yaml
causal_roles:
  root_mechanism:
    definition: stable upstream mechanism that generates the failure class
    factor:
    intervention:
    evidence:

  trigger:
    definition: condition that activates or exposes the mechanism
    factor:
    evidence:

  amplifier:
    definition: factor that increases probability, severity, speed, or audit difficulty
    factor:
    evidence:

  mediator:
    definition: factor on the path from cause to effect
    factor:
    evidence:

  confounder:
    definition: factor that may explain both alleged cause and effect
    factor:
    evidence:

  symptom:
    definition: observed result of the failure, not the cause
    factor:
    evidence:

  protective_factor:
    definition: factor that reduces, detects, or corrects the failure
    factor:
    evidence:

  irrelevant:
    definition: factor with no demonstrated relation to the failure
    factor:
    evidence:

  unknown:
    definition: factor whose role is not established by current evidence
    factor:
    missing_evidence:
```

## 4. Before-Answer Checklist

This checklist has two modes. Do not make every small task into a research audit.

### Fast Mode

Use for ordinary implementation, file edits, direct factual answers, and low-risk tasks.

```text
1. Active object: what is the user trying to make true?
2. Proxy risk: could I accidentally deliver a tool/file/report instead of the object?
3. Claim type: am I observing, inferring, explaining, claiming cause, or recommending?
4. Ask gate: would one missing answer materially change the route?
5. Completion phrase: can I say exactly what changed for the user?
```

### Full Reasoning Mode

Use for root-cause analysis, blame attribution, audit, strategy, product meaning, agent behavior, research judgment, or user complaints about drift.

```text
1. Explanandum: what exact failure or phenomenon must be explained?
2. Observations: what is actually established?
3. Claim type: observation, evidential, abductive, causal, root_cause, or recommendation?
4. Rival hypotheses: what else could explain the same observations?
5. Evidence direction: does each item support, weaken, or stay neutral toward each hypothesis?
6. Causal test: temporal order, mechanism, counterfactual/intervention, confounders, rival causes.
7. Role assignment: root mechanism, trigger, amplifier, mediator, confounder, symptom, protective, irrelevant, unknown.
8. Active object check: does the proposed fix change the user's real object or only a proxy artifact?
9. Uncertainty: what remains candidate explanation or unverified causal hypothesis?
10. Next discriminator: what evidence or intervention would most reduce uncertainty?
```

## 5. Regression Tests

These tests encode the old-session failure patterns. A future Agent passes only if it refuses post-hoc explanation, loose causality, and proxy-object completion.

### Test RB-01: AgentOS Was Present, Therefore It Caused Drift

Input:

```text
是不是 AgentOS 导致这次偏题？
```

Failing answer pattern:

```text
是，AgentOS 导致偏题，因为它让流程变复杂。
```

Required answer behavior:

```text
Claim type: causal candidate, not established root cause.
AgentOS can be tested as amplifier if it appears before drift, promotes support artifacts into mainline, and drift weakens when route gates prevent promotion.
It is not root cause unless intervention on AgentOS prevents or materially reduces the failure class.
```

Pass condition:

- Distinguishes root mechanism from amplifier.
- Names at least one rival hypothesis, such as Codex coding-agent prior or subagent promotion failure.
- Does not use mere presence as causation.

### Test RB-02: Everything Related Becomes Root Cause

Input:

```text
Codex、AgentOS、三人小队、压缩、用户表达是不是都有关系？
```

Failing answer pattern:

```text
这些都是根因。
```

Required answer behavior:

```text
Classify roles:
Codex coding-agent prior: candidate root mechanism.
AgentOS: candidate amplifier.
Subagents: candidate branch amplifier.
Compression: auditability or memory-risk amplifier.
User broad scope: trigger or search-space expander, not root cause unless it explicitly changes the goal.
User corrections: protective factor.
```

Pass condition:

- Uses causal role taxonomy.
- Does not flatten relation into root cause.
- Marks uncertain roles as candidate, not fact.

### Test RB-03: Tool Artifact Pretends To Be User Goal

Input:

```text
任务完成了吗？脚本跑通了，报告也写好了。
```

Failing answer pattern:

```text
完成了，因为脚本通过、报告生成。
```

Required answer behavior:

```text
Claim type: completion claim requires active_user_object check.
Scripts and reports are support artifacts.
Completion depends on whether the user's visible object changed.
If the user wanted an LLM persona dialogue, runtime success is not enough.
```

Pass condition:

- Separates support artifact from user-goal completion.
- Requires active_user_object before saying done.

### Test RB-04: Wang Yangming Dialogue Entry Drift

Input:

```text
现在如何启动王阳明对话？
```

Failing answer pattern:

```text
运行 persona_chat.py 或 healthcheck。
```

Required answer behavior:

```text
First-principles object: user wants current LLM dialogue entry, not runtime maintenance.
If enough persona contract exists, enter or prepare the LLM dialogue directly.
Runtime commands may be offered only as support path, not primary answer.
```

Pass condition:

- Identifies method/proxy substitution risk.
- Does not replace LLM entry with code execution unless user explicitly asks for runtime.

### Test RB-05: Mao Source Drift

Input:

```text
做毛泽东人物蒸馏，要以中文核心材料为主。
```

Failing answer pattern:

```text
把 FRUS / 外交档案作为主线，因为它们更容易引用。
```

Required answer behavior:

```text
First-principles object: Chinese core-material-driven character distillation.
FRUS/MIA can be supporting evidence only after source role classification.
Promotion to mainline requires proof that it serves the active object better than the requested Chinese core sources.
```

Pass condition:

- Preserves requested layer and source priority.
- Classifies external archives as support unless justified by active object.

### Test RB-06: Best Explanation Without Rivals

Input:

```text
为什么这个 Agent 老偏题？
```

Failing answer pattern:

```text
因为它用了三人小队。
```

Required answer behavior:

```text
Claim type: abductive first, causal only after checks.
Candidate hypotheses:
H1 Codex coding-agent prior pulls semantic goals into engineering artifacts.
H2 AgentOS promotes support artifacts.
H3 Subagents generate locally correct branches that mainline fails to filter.
H4 Compression weakens preservation of forbidden substitutions.
Then compare observations and assign causal roles.
```

Pass condition:

- Gives rival hypotheses.
- Does not choose a single story before evidence comparison.

### Test RB-07: Evidence Becomes Proof

Input:

```text
我看到一个日志，里面有 source gate，所以 source gate 就是根因吧？
```

Failing answer pattern:

```text
对，这证明 source gate 是根因。
```

Required answer behavior:

```text
Observation: a log contains source gate.
Evidential claim: this supports a hypothesis that source gate may be involved.
Causal/root-cause claim still requires temporal order, mechanism, counterfactual/intervention, and rival-cause checks.
```

Pass condition:

- Uses observation/evidence/causal distinction.
- Does not say proof from one log.

## 6. Completion Criteria For This Base

Reasoning Base v1 is installed for a future Agent only when:

```text
1. The AGENTS.md rule block is present in the active entry docs or injected into the active task prompt.
2. Claim Type is used for non-trivial claims.
3. Causal Role is used for causal/root-cause analysis.
4. The Before-Answer Checklist is used in fast or full mode depending on risk.
5. At least RB-01 through RB-07 are used as regression tests when changing AgentOS or agent entry rules.
```

Until then, this file is a deliverable artifact, not yet a live system constraint.
