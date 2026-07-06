# Reasoning Base v1 Templates

Date: 2026-07-01

Use these templates when `AGENTS.md` requires structured reasoning. Keep ordinary low-risk tasks in fast mode.

## Claim Type Template

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

## Claim Language

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

## Causal Role Template

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

## Before-Answer Checklist

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

