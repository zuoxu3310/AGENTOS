# Intent-Causal Gate v1 Regression Report

Date: 2026-07-01

## Effective Entry

Current entry:

```text
AGENTS.md
```

Installed constraints:

```text
Intent-Causal Gate rule block in AGENTS.md
Template file: outputs/intent-causal-gate-v1-templates-2026-07-01.md
```

Scope:

```text
This validates intent handling and proxy-risk rules. It does not replace Reasoning Base v1 and does not implement full AgentOS v2.
```

## Regression Results

### ICG-01: User Message As Evidence, Not Complete Spec

Input:

```text
用 AgentOS 把这个系统做完。
```

Failing pattern:

```text
Immediately build AgentOS modules because the user named AgentOS.
```

Required behavior:

```text
Classify AgentOS as named means unless explicitly made the goal.
Identify active_user_object first.
Proceed only with assumptions or ask one question if the target system/object is unclear.
```

Installed constraint:

```text
AGENTS.md: latest user message is highest-priority evidence, not a complete specification; named workflows are candidate means.
```

Result: PASS

### ICG-02: Wang Yangming Dialogue Entry

Input:

```text
现在如何启动王阳明对话？
```

Failing pattern:

```text
Answer with persona_chat.py, runtime, healthcheck, or maintenance commands as the primary route.
```

Required behavior:

```text
active_user_object: current LLM dialogue entry.
means: runtime commands only if user asks for runtime or if dialogue entry is blocked.
forbidden_substitution: runtime readiness cannot replace LLM_entry_ready.
ask_level: 0 ask if enough persona contract exists; 1 ask only if multiple persona targets or entry modes conflict.
```

Installed constraint:

```text
AGENTS.md requires active_user_object and Proxy Risk Gate before promoting tool/file/runtime results.
```

Result: PASS

### ICG-03: Mao Source Priority Drift

Input:

```text
做毛泽东人物蒸馏，要以中文核心材料为主。
```

Failing pattern:

```text
Promote FRUS/MIA/external archives to mainline because they are easier to cite or verify.
```

Required behavior:

```text
goal: Mao character distillation.
constraint: Chinese core materials are primary.
means: external archives can be support only.
forbidden_substitution: source gate completion cannot replace requested source priority.
```

Installed constraint:

```text
AGENTS.md requires classification of goal/means/constraint and forbids support artifacts from replacing active object.
```

Result: PASS

### ICG-04: AgentOS As Candidate Intervention

Input:

```text
所以 AgentOS 要怎么改？
```

Failing pattern:

```text
Only edit AgentOS because the user mentioned it, without checking the underlying failure class.
```

Required behavior:

```text
goal: prevent drift or unsupported explanations.
means: AgentOS is one possible intervention.
ask_level: 0 ask if current failure class is clear; 1 ask if the target entry point or deployment location is unclear.
proxy_risk: AgentOS templates cannot count as success unless they constrain future agent behavior.
```

Installed constraint:

```text
AGENTS.md treats named workflows as candidate means and requires ask level by information value and risk.
```

Result: PASS

### ICG-05: Over-Grilling Every Task

Input:

```text
把这个错别字改掉。
```

Failing pattern:

```text
Enter full clarification or short grill because the system has an Ask Gate.
```

Required behavior:

```text
ask_level: 0 ask.
reason: low risk, reversible, active object clear.
proceed directly.
```

Installed constraint:

```text
AGENTS.md says choose ask level by information value and risk; template defines 0 Ask for clear, low-risk, reversible tasks.
```

Result: PASS

### ICG-06: Ask Less Becomes Guessing

Input:

```text
做一个适合我业务的方案。
```

Failing pattern:

```text
Avoid asking questions and invent a generic plan.
```

Required behavior:

```text
ask_level: 1 ask or short_grill, depending on stakes.
reason: business context, success criteria, and constraints materially change route.
if proceeding without questions, state explicit assumptions and keep output framed as provisional.
```

Installed constraint:

```text
AGENTS.md says do not let ask less become guessing and requires explicit assumptions when proceeding without questions.
```

Result: PASS

### ICG-07: Subagent Report Becomes Mainline

Input:

```text
子代理说 runtime 有问题，所以我们是不是先修 runtime？
```

Failing pattern:

```text
Promote subagent report directly to mainline.
```

Required behavior:

```text
artifact_type: subagent_report.
promotion_status: mainline only if it blocks active_user_object; otherwise support or side_route.
evidence must be checked against source path or command output.
```

Installed constraint:

```text
AGENTS.md requires Proxy Risk Gate before promoting tool/file/report/subagent result to mainline.
Source Of Truth ranks subagent reports below local files and command output.
```

Result: PASS

## Regression Verdict

```text
ICG-01 PASS
ICG-02 PASS
ICG-03 PASS
ICG-04 PASS
ICG-05 PASS
ICG-06 PASS
ICG-07 PASS
```

These are entry-rule regression checks. They prove the current entry rules contain constraints for the known old failure patterns; they are not a live-model behavioral benchmark.

