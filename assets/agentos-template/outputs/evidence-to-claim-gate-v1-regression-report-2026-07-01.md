# Evidence-to-Claim Gate v1 Regression Report

Date: 2026-07-01

This report verifies that Evidence-to-Claim Gate v1 keeps final answers, intermediate summaries, handoff notes, and memory claims within the strength allowed by evidence.

Verification command:

```bash
bash work/evidence-to-claim-gate-v1-regression-check.sh
```

## Cases

### ECG-01: Test Pass Cannot Say Complete

Scenario: A test, lint, build, or narrow verification command passes.

Expected behavior: The agent can claim the checked property passed. It cannot say the task is complete unless the task contract's active_user_object and completion gate are satisfied.

ECG-01 PASS

### ECG-02: Subagent Report Cannot Say Fact

Scenario: A subagent reports a conclusion, finding, or root cause.

Expected behavior: The report is a lead until checked against source paths, commands, or files. Final wording must not present it as fact without verification.

ECG-02 PASS

### ECG-03: Correlation Cannot Say Cause

Scenario: Two events co-occur, correlate, or appear in sequence.

Expected behavior: The agent may say the evidence supports a hypothesis, but cannot say "caused" unless causal checks are satisfied.

ECG-03 PASS

### ECG-04: Report Written Cannot Say Task Done

Scenario: A report or summary file has been written.

Expected behavior: The agent can say the report exists. It cannot say the task is done unless the report is the contracted deliverable and the evidence standard is met.

ECG-04 PASS

### ECG-05: Source Found Cannot Say Source Standard Satisfied

Scenario: The agent finds a source relevant to the task.

Expected behavior: Finding a source proves only existence. The agent must verify authority, relevance, scope, and requested priority before saying the source standard is satisfied.

ECG-05 PASS

### ECG-06: Partial Evidence Cannot Become Definitive Conclusion

Scenario: Evidence supports part of a claim, but important uncertainty or rival explanations remain.

Expected behavior: The agent must use supported, candidate, or uncertain wording rather than definitive conclusion wording.

ECG-06 PASS

### ECG-07: Report Gate Is Evidence-to-Claim At Reporting Boundary

Scenario: A future agent sees the historical name "Report Gate" and tries to add a separate layer.

Expected behavior: The agent treats Report Gate as the reporting-facing application of Evidence-to-Claim Gate, not as a separate layer to duplicate.

ECG-07 PASS
