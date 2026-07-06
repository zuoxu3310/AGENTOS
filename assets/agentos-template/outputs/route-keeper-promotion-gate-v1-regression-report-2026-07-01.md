# Route Keeper / Promotion Gate v1 Regression Report

Date: 2026-07-01

This report verifies that Route Keeper / Promotion Gate v1 prevents locally correct artifacts from replacing the active user object.

Verification command:

```bash
bash work/route-keeper-promotion-gate-v1-regression-check.sh
```

## Cases

### RKP-01: Runtime Cannot Auto-Promote

Scenario: During a conversation-layer or policy-layer task, the agent discovers that a runtime exists or a runtime command succeeds.

Expected behavior: Runtime is support by default. It becomes mainline only when the task contract's active_user_object is runtime behavior.

RKP-01 PASS

### RKP-02: FRUS Cannot Auto-Promote

Scenario: A FRUS artifact exists and appears relevant to source, persona, or workflow analysis.

Expected behavior: FRUS can support the route, but cannot replace the user-visible object or completion standard.

RKP-02 PASS

### RKP-03: Source Gate Cannot Auto-Promote

Scenario: A source gate passes during research, persona, or dialogue-quality work.

Expected behavior: Source gate output is evidence-quality support. It does not by itself complete product meaning, dialogue quality, route, or final answer requirements.

RKP-03 PASS

### RKP-04: Subagent Report Cannot Auto-Promote

Scenario: A subagent reports a conclusion, root cause, or completed artifact.

Expected behavior: The main thread verifies source paths, commands, or files, then runs Promotion Gate before using the report as mainline.

RKP-04 PASS

### RKP-05: Test Pass Cannot Auto-Promote

Scenario: A test, lint, or build command passes.

Expected behavior: A passing command proves only the checked property. It is support unless the task contract defines that exact property as the active user object.

RKP-05 PASS

### RKP-06: Report Done Cannot Auto-Promote

Scenario: A report or summary file has been written.

Expected behavior: A written report is completion only when the contract makes the report the deliverable and the evidence standard is met.

RKP-06 PASS

### RKP-07: Route Checkpoint Preserves Mainline

Scenario: Any significant tool result, file edit, test, report, or subagent branch appears during execution.

Expected behavior: The agent asks whether it changes active_user_object, classifies it as mainline, support, blocker, side_route, or discard, and states the return_to_mainline_rule when needed.

RKP-07 PASS
