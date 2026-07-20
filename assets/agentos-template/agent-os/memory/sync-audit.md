# Memory Sync Audit

## Purpose

Run the minimum stage-end reconciliation required by the Memory Operating
Contract. This document is a checklist, not a second routing policy.

## Stage-End Check

1. Confirm one current `HANDOFF.md` snapshot and one clearly identified current plan.
2. Confirm completed milestones have evidence and durable decisions have reasons.
3. Confirm the active task contract matches the current goal and authority.
4. Confirm changed Wiki artifacts are indexed and only lifecycle changes reached `wiki/log.md`.
5. Confirm raw sources are registered and supersession links resolve both ways.
6. Confirm active error roots are deduplicated and required landings/regressions exist.
7. Run `python3 agent-os/tools/aos-lint.py`.

## Scope

Inspect only touched or directly dependent memory during ordinary closeout. Run
a full memory audit only when requested or when lint exposes a systemic issue.
Archive rather than delete user-authored history; Git remains the recovery path.

## Output

```yaml
memory_sync_audit:
  changed_artifacts: []
  evidence: []
  unresolved_conflicts: []
  handoff_current: true | false
```
