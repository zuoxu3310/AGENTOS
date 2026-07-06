# Evidence-to-Claim Gate v1 Templates

Date: 2026-07-01

Use this after Route Keeper / Promotion Gate and before user-facing answers, final reports, intermediate summaries, handoff notes, and durable memory writes. It keeps the agent from saying more than the evidence allows.

## Purpose

Evidence-to-Claim Gate controls claim strength at the output boundary:

```text
- Classify important claims before writing them to the user, handoff, or memory.
- Bind each key claim to an evidence source.
- Match wording to evidence strength.
- Downgrade or remove claims when evidence is weak, missing, indirect, or unverified.
```

## Report Gate Mapping

Report Gate is the reporting-facing application of Evidence-to-Claim Gate. It is used when the agent writes final answers, intermediate summaries, reports, handoff notes, or durable memory. It is not a separate layer and should not duplicate Evidence-to-Claim Gate.

## When To Use

Use the full gate for:

```text
- completion claims
- causal claims
- root-cause claims
- recommendations
- final answers
- audit or review findings
- handoff and memory claims
- claims derived from subagents, tests, reports, source gates, or runtime checks
```

Use the micro gate for short low-risk answers. Do not write a long evidence table for every sentence; apply this to key conclusions and any sentence the user could reasonably act on.

## Micro Claim Gate

```yaml
claim_gate_micro:
  claim:
  claim_type:
  evidence_source:
  evidence_strength:
  allowed_wording:
```

## Evidence-to-Claim Gate

```yaml
evidence_to_claim_gate:
  claim:
  claim_type: observation | inference | explanation | causal | root_cause | recommendation | completion | handoff | memory | other
  evidence_source:
  evidence_strength: observed | supported | strongly_supported | best_current_explanation | proven | causal | root_cause | complete
  allowed_wording:
  forbidden_wording:
  uncertainty:
  user_visible_consequence:
```

## Claim Strength Ladder

```text
observed:
  Directly seen in a file, command output, source, UI, runtime, or user message.
  Allowed wording: "observed", "shows", "contains", "the command output says".

supported:
  Evidence makes the claim more likely, but does not eliminate important rivals.
  Allowed wording: "supports", "is consistent with", "suggests".

strongly_supported:
  Multiple relevant evidence sources support the claim and obvious rivals were checked.
  Allowed wording: "strongly supports", "the current evidence supports".

best_current_explanation:
  The claim is the strongest explanation after naming rival explanations and why they are weaker.
  Allowed wording: "best current explanation".

proven:
  Deductive proof, direct authoritative source, or complete verification establishes the claim in scope.
  Allowed wording: "proves", "establishes", only within the verified scope.

causal:
  Temporal order, defined variables, plausible mechanism, counterfactual or intervention logic, and rival-cause checks are satisfied.
  Allowed wording: "caused", only for the verified causal scope.

root_cause:
  A causal factor is shown to be an intervention point that would prevent, materially reduce, or reliably detect the failure class.
  Allowed wording: "root cause", only for the verified failure class.

complete:
  The task contract's active_user_object is achieved and required evidence satisfies the completion gate.
  Allowed wording: "complete", "done", "delivered", only for the contracted scope.
```

## Wording Rules

```text
- Do not say "complete" from test pass alone.
- Do not state a subagent report as fact until checked against source paths, commands, or files.
- Do not say "caused" from correlation, sequence, or plausibility alone.
- Do not say "task done" because a report was written unless the report is the contracted deliverable and the evidence standard is met.
- Do not say "source standard satisfied" because a source was found; check the requested standard.
- Do not turn partial evidence into a definitive conclusion.
- Do not write unverified claims into handoff or memory as settled facts.
```

## Known Exit-Pollution Triggers

```text
test pass:
  A passing test supports the tested property. It cannot authorize "complete" unless completion is exactly the tested property and the task contract agrees.

subagent report:
  A subagent report can supply leads. It cannot authorize "fact" wording without source verification.

correlation:
  Correlation can support a hypothesis. It cannot authorize "cause" wording without causal checks.

report written:
  A report file proves a report exists. It cannot authorize "task done" unless the report itself is the contracted deliverable and meets the evidence standard.

source found:
  Finding a source proves only that the source exists. It cannot authorize "source standard satisfied" unless authority, relevance, scope, and requested priority are checked.

partial evidence:
  Partial evidence can support or weaken a claim. It cannot authorize definitive conclusions.
```

## Output Review

Before final answer, summary, handoff, or memory write, check:

```yaml
output_review:
  key_claims:
    - claim:
      claim_type:
      evidence_source:
      evidence_strength:
      wording_allowed: yes | no
      revision_needed:
  claims_removed_or_downgraded:
  remaining_uncertainty:
```
