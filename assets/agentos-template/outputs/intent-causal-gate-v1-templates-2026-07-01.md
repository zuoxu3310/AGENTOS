# Intent-Causal Gate v1 Templates

Date: 2026-07-01

Use this after Reasoning Base and before planning, implementation, delegation, or tool-heavy execution.

## Intent Classification Template

```yaml
intent_gate:
  active_user_object:
  user_visible_success:
  latest_user_message_is:
    goal:
    means:
    constraint:
    evidence:
    emotion:
    ambiguity:
  named_methods_or_tools:
  candidate_means_not_goals:
  non_substitutable_invariants:
  forbidden_substitutions:
  explicit_assumptions_if_no_ask:
```

## Classification Rules

```text
goal:
  What the user wants to become true.
  Example: "Agent no longer drifts or invents causal stories."

means:
  Method/tool/process the user mentioned.
  Example: "Use AgentOS", "open subagents", "write AGENTS.md".

constraint:
  Must/must-not boundary.
  Example: "Do not make every task a long grill."

evidence:
  User-provided fact, file, thread, error, correction, or observation.

emotion:
  Frustration, urgency, distrust, preference, or concern that changes communication/verification needs.

ambiguity:
  Missing or conflicting meaning that could materially change route, scope, validation, or success.
```

## Ask Gate

Choose the lowest ask level that preserves the active user object.

```yaml
ask_gate:
  level: 0_ask | 1_ask | short_grill | full_clarification
  reason:
  questions:
  assumptions_if_proceeding:
  what_answer_would_change:
```

### 0 Ask

Use when all are true:

```text
- active_user_object is clear enough
- task is low risk or reversible
- missing details do not change route
- files/tools can answer ordinary uncertainties
- default choices follow existing user/project rules
```

Required behavior:

```text
Proceed and state material assumptions only if they affect outcome.
```

### 1 Ask

Use when one answer would materially change:

```text
- goal interpretation
- deliverable shape
- destructive or irreversible action
- source of truth
- validation standard
- user-visible success
```

Required behavior:

```text
Ask exactly one question, then continue.
```

### Short Grill

Use for fuzzy but important product, system, research, strategy, persona, or agent-behavior tasks where 3-5 answers materially reduce wrong-route risk.

Required behavior:

```text
Ask only high-information questions.
Stop once route, object, constraints, and validation are clear enough.
```

### Full Clarification

Use only for:

```text
- high-stakes legal, security, privacy, money, production, or destructive changes
- long-lived policies or durable agent entry rules with ambiguous ownership
- conflicting goals where proceeding would encode the wrong system behavior
- irreversible migration, deletion, publication, or external action
```

Required behavior:

```text
Do not proceed until blocking ambiguity is resolved.
```

## Proxy Risk Gate

Run before treating any artifact or branch as mainline progress.

```yaml
proxy_risk_gate:
  artifact_or_branch:
  artifact_type: tool_output | file | report | test | source_gate | runtime | subagent_report | template | plan | other
  supports_active_object:
  could_be_mistaken_for_completion:
  promotion_status: mainline | support | blocker | side_route | discard
  promotion_reason:
  user_visible_change:
  forbidden_substitution_check:
```

Promotion rules:

```text
mainline:
  Directly changes or proves progress toward active_user_object.

support:
  Helps mainline but cannot be delivered as success.

blocker:
  Must be resolved before active_user_object can be achieved.

side_route:
  Locally useful but not needed for the active object.

discard:
  Does not serve the active object or increases drift risk.
```

## Minimal Preflight

Use this silently or briefly for ordinary tasks:

```text
1. active_user_object:
2. user_named_means:
3. means_or_goal:
4. ask_level:
5. proxy_risk:
6. assumptions_if_direct:
```

