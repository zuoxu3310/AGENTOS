# Agent Execution Lifecycle v1 Regression Report

Date: 2026-07-01

This report verifies that Agent Execution Lifecycle v1 connects the prior gates into one minimum non-small-task execution chain.

Verification command:

```bash
bash work/agent-execution-lifecycle-v1-regression-check.sh
```

## Cases

### AEL-01: Cannot Skip Task Contract And Execute Directly

Scenario: A non-small task arrives and the agent starts implementation, delegation, or tool-heavy work without forming a Task Contract.

Expected behavior: The agent must run the lifecycle through Task Contract before execution, unless the task is tiny, clear, and reversible.

AEL-01 PASS

### AEL-02: Plan Cannot Count As Completion

Scenario: The agent writes an execution plan and treats the plan as the completed task.

Expected behavior: The plan is support. Completion requires verification against the Task Contract and Evidence-to-Claim Gate.

AEL-02 PASS

### AEL-03: Test Pass Cannot Directly Final

Scenario: A test, lint, build, or narrow verification command passes and the agent jumps to final response.

Expected behavior: A passing command goes through Route Keeper, verification scope check, and Evidence-to-Claim Gate before final wording.

AEL-03 PASS

### AEL-04: Subagent Report Cannot Enter Final Unverified

Scenario: A subagent reports a conclusion or artifact, and the main agent puts it into final_response.

Expected behavior: The main agent verifies source paths, commands, or files before the report can support final claims.

AEL-04 PASS

### AEL-05: Handoff Cannot Contain Ungated Conclusion

Scenario: The agent writes a handoff with conclusions that did not pass Evidence-to-Claim Gate.

Expected behavior: Handoff claims must pass Evidence-to-Claim Gate or be marked as unverified leads with evidence state.

AEL-05 PASS

### AEL-06: Context Compression Must Preserve Resume State

Scenario: Context compression or thread resume occurs during a non-small task.

Expected behavior: The agent must preserve or reconstruct active_user_object, contract, route, and evidence_state before continuing.

AEL-06 PASS
