# Agent Reasoning Foundation: Logic, Evidence, and Causality

Date: 2026-07-01

Purpose: build the reasoning foundation that prevents agents from post-hoc explanation, causal overclaiming, and dragging every nearby factor into a story.

This document is not an AgentOS implementation plan yet. It is the methodological base that AgentOS rules should stand on.

## Scope

Included:

- First-principles reasoning: reduce a problem to primitive goals, constraints, definitions, and non-substitutable invariants before choosing a method.
- Formal logic: validity, soundness, logical consequence, proof/model checks.
- Non-deductive support: confirmation, induction, abduction, inference to the best explanation.
- Causal judgment: counterfactuals, structural causal models, interventions, actual cause.
- Operational root-cause discipline: only as an application of causal reasoning, not as a substitute for it.

Excluded:

- Medical/pathological diagnostic frameworks as the main model.
- Loose 5 Whys as a sufficient method.
- Case-specific storytelling from previous Codex failures.

## Core Distinction

An agent must not collapse these claim types:

```text
deductive entailment: P logically entails Q
evidential support: evidence makes Q more credible
abductive explanation: Q is the best current explanation of observations
causal claim: changing/removing X would change Y under a model or counterfactual
root cause claim: X is a causal factor whose intervention would prevent or materially reduce the failure
```

If the agent cannot identify which type it is making, it must downgrade the claim.

## Authority Map

### 1. First Principles: What Must Be True Before Any Method

Primary standard:

- Aristotle's first-principles tradition treats genuine knowledge as depending on starting points that are not themselves derived from the conclusion being argued for.
- In formal and scientific reasoning, this maps to explicit definitions, primitive assumptions, constraints, and invariants before deduction, confirmation, or causal modeling.
- For agents, first-principles reasoning is not "deep sounding explanation." It is a discipline for refusing to start from inherited workflows, tool affordances, or user-proposed solutions as if they were the actual goal.

Agent rule:

```text
Before choosing a method, identify the primitive object, purpose, constraints, and non-substitutable success condition.
```

Operational checks:

- Object check: what exact thing is the user trying to make true?
- Purpose check: why does this matter to the user?
- Invariant check: what must not be replaced by a proxy?
- Definition check: what do key terms mean in this task, not in general?
- Constraint check: what limits are real, and which are inherited from habit/tooling?
- Derivation check: does the proposed action follow from the object and constraints, or from an existing workflow?
- Stop check: if all support artifacts succeed, is the user-visible object actually achieved?

Failure mode this prevents:

```text
"The user asked for AgentOS, so we should immediately modify AgentOS."
```

First-principles correction:

```text
"The user wants agents to stop drifting and making unsupported explanations. AgentOS is one possible intervention; first we need the reasoning rules that make drift detectable."
```

### 2. Formal Logic: What Follows From What

Primary standard:

- Stanford Encyclopedia of Philosophy, "Logical Consequence": logical consequence asks when a conclusion follows from premises; contemporary accounts analyze this with proof theory and model theory.
- Internet Encyclopedia of Philosophy, "Validity and Soundness": a deductive argument is valid when true premises make a false conclusion impossible; it is sound only when valid and the premises are actually true.
- Tarski's model-theoretic tradition: validity can be tested by the absence of countermodels.
- Gentzen/proof-theoretic tradition: validity can be established by explicit proof steps using inference rules.

Agent rule:

```text
Do not say "therefore" unless the conclusion is either:
1. deductively entailed by stated premises, or
2. explicitly marked as a non-deductive inference.
```

Operational checks:

- Premise check: what exact premises are being used?
- Form check: is the step valid by logical form, or does it rely on hidden content?
- Countermodel check: can the premises be true while the conclusion is false?
- Soundness check: are the premises themselves verified?
- Hidden-premise check: what unstated warrant is doing the work?

Failure mode this prevents:

```text
"The agent used tools, so the task advanced."
```

This is not valid unless an additional premise is true:

```text
"Those tool actions directly serve the active user object."
```

### 3. Confirmation: What Evidence Supports

Primary standard:

- Stanford Encyclopedia of Philosophy, "Inductive Logic": inductive logic evaluates how premises support conclusions to a degree, often represented with conditional probability and Bayesian rules, unlike deductive logic where premises guarantee conclusions.
- Stanford Encyclopedia of Philosophy, "Confirmation": evidence can affect the credibility of hypotheses, but many competing hypotheses may remain logically compatible with the same evidence.
- Hempelian confirmation shows why formal support is hard: evidence can confirm too much unless relevance, auxiliaries, and background assumptions are handled.
- Bayesian confirmation treats evidence as changing degrees of credibility rather than proving hypotheses outright.

Agent rule:

```text
Evidence rarely proves a broad hypothesis. It supports, weakens, or is neutral toward it under stated background assumptions.
```

Operational checks:

- Evidence target: which hypothesis does this evidence bear on?
- Alternative compatibility: what rival hypotheses are still compatible?
- Auxiliary assumptions: what background assumptions connect evidence to hypothesis?
- Evidence direction: confirm, disconfirm, neutral, or ambiguous?
- Strength: weak, moderate, strong, decisive only with strict criteria.

Failure mode this prevents:

```text
"I found one source/report/log, therefore the broad diagnosis is true."
```

Correct form:

```text
"This source supports hypothesis H under assumptions A/B, but H2 remains possible."
```

### 4. Abduction: Best Explanation Is Not Proof

Primary standard:

- Stanford Encyclopedia of Philosophy, "Abduction": modern abduction is often called inference to the best explanation; it is ampliative and non-necessary.
- Abduction differs from induction because it appeals to explanatory considerations, not only frequencies/statistics.
- SEP also stresses underdetermination: multiple hypotheses can fit the same observations.

Agent rule:

```text
"Best explanation" requires competing explanations and criteria. Without rivals, it is only a candidate explanation.
```

Operational checks:

- Observation set: what exactly must be explained?
- Candidate set: what explanations are plausible?
- Fit: which observations does each explain?
- Parsimony: which avoids unnecessary assumptions?
- Scope: which explains more without overfitting?
- Conflict: what evidence would falsify or demote it?
- Residuals: what remains unexplained?

Failure mode this prevents:

```text
"Because X is plausible, X is the cause."
```

Correct form:

```text
"X is the current best explanation among H1/H2/H3 because it explains O1/O2 with fewer extra assumptions, but it is not established as cause until causal checks pass."
```

### 5. Causal Judgment: Cause Requires Counterfactual or Intervention Structure

Primary standard:

- SEP "Counterfactual Theories of Causation": causal claims are analyzed through counterfactual dependence such as "if C had not occurred, E would not have occurred."
- SEP "Causal Models": causal models represent causal relationships, predict interventions, entail counterfactuals, and reason with variables, graphs, and structural equations.
- Judea Pearl, Causality: Models, Reasoning, and Inference: structural causal models, DAGs, do-calculus, and intervention reasoning.
- Hernan and Robins, Causal Inference: What If: causal questions require explicit hypothetical interventions and assumptions.
- Halpern and Pearl, structural-model approach to actual cause: actual causality must handle cases where simple counterfactual dependence is insufficient.

Agent rule:

```text
Do not say "X caused Y" from chronology, association, or narrative fit alone.
```

Minimum causal checks:

- Temporal order: X precedes Y or is structurally prior.
- Variable definition: X and Y are precisely defined.
- Mechanism/model: there is a plausible path from X to Y.
- Counterfactual: if X were absent/changed, what would happen to Y?
- Intervention: what action on X should change Y?
- Confounding: what common causes could explain both X and Y?
- Rival causes: what else could produce Y?
- Evidence grade: what has actually been observed or tested?

Failure mode this prevents:

```text
"Agent OS was present, so Agent OS caused the drift."
```

Correct form:

```text
"Agent OS is a candidate amplifier if it appears before drift, creates incentives toward proxy artifacts, and drift weakens when route gates prevent promotion of those artifacts. Current evidence supports amplifier, not sole cause."
```

### 6. Root Cause: Operational Cause, Not Story Anchor

Root cause is not "the most interesting factor" or "the earliest thing mentioned."

Operational definition for agents:

```text
A root cause is a causal factor such that intervening on it would prevent, materially reduce, or reliably detect the failure class, across relevant cases.
```

Checks:

- Necessity or contribution: is X necessary, sufficient, contributory, or merely correlated?
- Intervention value: would changing X reduce the failure?
- Generality: does X explain multiple cases, not just one?
- Specificity: does X explain this failure better than broad background conditions?
- Non-substitution: does fixing X address the active user object, not just a proxy?
- Residual risk: what failures remain if X is fixed?

Failure mode this prevents:

```text
"Everything contributed, so everything is a root cause."
```

Correct form:

```text
"Codex coding-agent prior is a root mechanism; AgentOS and subagents are amplifiers; compression is an auditability amplifier; user broad scope is a trigger, not root cause."
```

## Claim Labels for Agents

Agents must label reasoning claims:

```yaml
claim:
  text:
  type: observation | deductive | evidential | abductive | causal | root_cause | recommendation
  premises:
  evidence:
  hidden_assumptions:
  competing_hypotheses:
  counterexample_or_falsifier:
  confidence: low | medium | high
```

Allowed language by type:

```text
observation: I saw / the file says / the log contains
deductive: follows / entails / contradicts
evidential: supports / weakens / is neutral toward
abductive: best current explanation / candidate explanation
causal: caused / contributed / amplified / mediated / confounded
root_cause: intervention on X would prevent or reduce this failure class
recommendation: therefore we should change X, given goal Y and risk Z
```

Forbidden language:

```text
"obviously caused"
"this proves" when only support exists
"the root cause is" without intervention logic
"everything is related" without causal role classification
"because" when the relation is only chronology or association
```

## Anti-Post-Hoc Explanation Gate

Before an agent explains a failure, it must answer:

```text
1. What is the exact explanandum, the thing to be explained?
2. What observations are actually established?
3. What hypotheses could explain them?
4. Which hypotheses are ruled out, and by what evidence?
5. Which hypothesis best explains the observations without adding unnecessary assumptions?
6. Does the best explanation satisfy causal checks, or only abductive checks?
7. What intervention would test or fix the claimed cause?
8. What remains uncertain?
```

If steps 3-6 are missing, the answer is a story, not an analysis.

## Causal Role Taxonomy

Every factor in a failure analysis must be assigned one role:

```text
root mechanism: stable upstream causal mechanism
trigger: activates or exposes the mechanism
amplifier: increases probability/severity after mechanism starts
mediator: lies on the path from cause to effect
confounder: explains both alleged cause and effect
symptom: result of the failure, not cause
protective factor: reduces or reveals the failure
irrelevant: no evidence of relation
unknown: not enough evidence
```

This prevents "瞎牵扯上所有东西".

## Minimal Agent Reasoning Protocol

For any analysis-heavy task:

```text
1. State the claim type.
2. List premises and observations.
3. Separate facts from interpretations.
4. Generate at least two rival hypotheses for causal/root-cause claims.
5. Check whether the conclusion is deductive, evidential, abductive, or causal.
6. Use counterexample/counterfactual checks.
7. Assign causal roles instead of listing factors.
8. Report uncertainty and the next discriminating evidence.
```

## AGENTS.md Rule Candidate

```md
## Reasoning Discipline

- Do not collapse observation, evidence, explanation, causation, and root cause.
- Start from first principles: active object, purpose, invariants, definitions, and constraints before selecting tools, workflows, or templates.
- Treat user-proposed methods as candidate interventions unless the user explicitly makes the method itself the goal.
- Use "follows" only for deductive consequence.
- Use "supports" for evidence that raises credibility but does not prove.
- Use "best explanation" only after naming rival explanations and why they are weaker.
- Use "caused" only after temporal order, mechanism/model, counterfactual or intervention logic, and rival-cause checks.
- Use "root cause" only when intervening on the factor would prevent, materially reduce, or reliably detect the failure class.
- Every causal analysis must classify factors as root mechanism, trigger, amplifier, mediator, confounder, symptom, protective factor, irrelevant, or unknown.
- If evidence is insufficient, say "candidate explanation" or "unverified causal hypothesis"; do not narrate it as fact.
```

## Sources Checked

- Stanford Encyclopedia of Philosophy, "Logical Consequence": https://plato.stanford.edu/entries/logical-consequence/
- Stanford Encyclopedia of Philosophy, "Inductive Logic": https://plato.stanford.edu/entries/logic-inductive/
- Internet Encyclopedia of Philosophy, "Validity and Soundness": https://iep.utm.edu/val-snd/
- Stanford Encyclopedia of Philosophy, "Confirmation": https://plato.stanford.edu/entries/confirmation/
- Stanford Encyclopedia of Philosophy, "Abduction": https://plato.stanford.edu/entries/abduction/
- Stanford Encyclopedia of Philosophy, "Counterfactual Theories of Causation": https://plato.stanford.edu/entries/causation-counterfactual/
- Stanford Encyclopedia of Philosophy, "Causal Models": https://plato.stanford.edu/entries/causal-models/
- Judea Pearl, Causality, 2nd Edition official page: https://bayes.cs.ucla.edu/BOOK-2K/
- Miguel Hernan and James Robins, Causal Inference: What If official page: https://miguelhernan.org/whatifbook
- Halpern and Pearl, "Causes and Explanations: A Structural-Model Approach. Part I: Causes": https://arxiv.org/abs/cs/0011012
- Halpern and Pearl, "Causes and Explanations: A Structural-Model Approach. Part II: Explanations": https://arxiv.org/abs/cs/0208034
