# Intent-Causal Gate

## Purpose

Intent-Causal Gate decides what the user is really trying to make true before planning, implementation, delegation, or tool-heavy execution.

It prevents the Agent from treating AgentOS, tools, files, workflows, subagents, tests, or reports as the goal when they are only candidate means.

## Core Rules

```text
- Treat the latest user message as highest-priority evidence, not as a complete specification.
- Classify user content as goal, means, constraint, evidence, emotion, or ambiguity before acting.
- Treat named tools, files, workflows, AgentOS, subagents, tests, and reports as candidate means unless the user explicitly makes them the goal.
- Identify `active_user_object`: what the user is trying to make true and what cannot be replaced by support artifacts.
- Separate the user's goal from candidate means. A named tool, workflow, file, test, or implementation idea does not change the goal by itself.
- Distinguish information retrieval from judgment formation. Judgment formation requires an observable trigger: user request, expressed uncertainty, conflicting goals, or a user-owned tradeoff blocking the next action. AI-user disagreement alone never starts or prolongs exploration.
- Admit a question only when all six conditions hold: the answer is user-owned, unavailable from context or investigation, changes route or risk, has no safe reversible default, is necessary at the present stage, and blocks a named next top-level action.
- Preserve an unexpressed user view before exposing the AI recommendation. Otherwise answer AI-first with materially different alternatives, an independent recommendation with its basis, and permission to reject all options.
- Group questions by dependency, never by a fixed count. Ask sequentially when one answer can change or remove another; batch independent questions only when they jointly block the same next action. Recompute the remainder after a partial answer instead of demanding form completion.
- When questioning stops, expose what was resolved, remaining uncertainty, why plausible remaining branches do not change the current step, assumptions, residual risk, and the condition that would reopen questioning.
- A clear grounded authorization is an execution signal. A material goal change is a new current-goal version, not an inference from candidate means.
- Do not let "ask less" become guessing: investigate available facts, teach blind spots, build variants, request a reference, or state a safe reversible default. At high unknown density, guessing is not legitimized by stating assumptions.
- Run Proxy Risk Gate before promoting any tool/file/report/subagent result to mainline.
- Every substantive judgment already records an independent conclusion, basis,
  and change condition. Use `agent-os/review/anti-sycophancy-gate.md` only when
  the user explicitly requests adversarial framing review or when a contested,
  high-risk frame needs tools beyond that normal judgment record.
- Question shaping check before execution: if the question mixes emotional content with an analysis request, split them and handle separately; rewrite negation-style lookups ("which X are not Y") into positive form before searching; if the question's shape would systematically bias the answer, surface that to the user before proceeding.
```

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

means:
  Method, tool, process, or artifact the user mentioned.

constraint:
  Must or must-not boundary.

evidence:
  User-provided fact, file, thread, error, correction, or observation.

emotion:
  Frustration, urgency, distrust, preference, or concern that changes communication or verification needs.

ambiguity:
  Missing or conflicting meaning that could materially change route, scope, validation, or success.
```

## Ask Gate

Ask only after every admission condition passes; otherwise investigate, choose a
safe reversible default, propose a concrete route, or park the unknown.

```yaml
question_decision:
  mode: no_question | sequential | independent_batch
  purpose: information_retrieval | judgment_formation
  admission_conditions:
    user_owned:
    unavailable_from_context_or_investigation:
    changes_route_or_risk:
    no_safe_reversible_default:
    present_stage_necessary:
    blocked_top_level_action:
  observable_exploration_trigger:
  dependencies:
  plausible_answer_branches:
  presentation_order: user_first | ai_first
  partial_answer_reassessment:
  stop_support:
```

```text
no_question:
  Use when any admission condition fails. The AI retains ordinary investigation,
  synthesis, and safe reversible implementation choices.

sequential:
  Use when one answer can change, remove, or regenerate another question.

independent_batch:
  Use only for mutually independent questions that jointly block the same next
  top-level action. A partial answer triggers a fresh decision on the remainder.
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

Promotion classes:

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
