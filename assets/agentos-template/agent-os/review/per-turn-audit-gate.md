# Per-Turn Audit Gate

Date: 2026-07-02

## Purpose

Per-Turn Audit Gate makes audit non-optional. Every turn — including small,
short-path, and pure-conversation turns — must produce a minimal audit and
report it. This overrides any "small tasks may skip audit" allowance elsewhere
in the kernel.

The user-facing report remains mandatory even when runtime hooks exist: if the
Agent does not report the audit, that counts as the audit not done, and the user
can catch it on sight.

## Hard Rule

```text
Every turn, before the final answer, the Agent MUST:
1. Append one minimal audit entry to agent-os/state/audit-log.md.
2. Emit a short audit block in the answer, ending with the audit-log entry id.

No turn is complete without both.
A missing report means the audit was not done.
Small and pure-conversation turns shrink each field to one phrase; they never skip it.
```

## Minimal Audit Block (what to report in the answer)

```yaml
per_turn_audit:
  object:            # active user object, one line
  contract:          # deliverable / evidence standard / forbidden substitution, terse
  action_evidence:   # what was done + the file/command/observation that proves it
  status: complete | partial | support_only | blocked | not_started
  logged:            # agent-os/state/audit-log.md entry id
```

For small/chat turns the in-answer block may compress to four plain-language
lines — but never to a bare pointer like "audit #n logged", which carries no
catchable content. Minimum visible form:

```text
—— per-turn audit ——
did: <one line>
evidence: <file / command / observation, one line>
status: complete | partial | blocked
logged: agent-os/state/audit-log.md #<n>
```

The last line is mandatory and the block always ends with the entry id, so
the compact form and the full YAML form terminate identically and the log
pointer is never ambiguous.

## Audit Log Entry (what to append to the log)

Append to `agent-os/state/audit-log.md`:

```text
## <n> — <one-line turn label>
- object:
- contract:
- action+evidence:
- status:
```

Number entries by increment. Do not rewrite past entries except to close a
`partial` status to its final state.

## Enforcement Boundary

```text
- 2026-07-05: in the Claude Code runtime this gate is hook-enforced. A Stop hook
  (.claude/hooks/aos_stop_gate.py) verifies each turn that
  agent-os/state/audit-log.md gained a well-formed, uniquely numbered entry; a
  missing or malformed entry blocks the turn from finishing (max 2 forced
  retries, then the miss is recorded in agent-os/state/compliance-log.tsv so it
  is measurable instead of silent). The visible-block-in-answer scan is
  advisory only (logged, never blocking): transcript flushing races with the
  Stop event and twice produced false blocks on 2026-07-05.
- 2026-07-06: in Codex this gate is hook-enforced when the project `.codex/`
  layer is trusted. `.codex/hooks.json` wires the same SessionStart baseline,
  UserPromptSubmit baseline, Stop hook audit verification, kernel-edit lint, and
  enforcement-layer edit guard through `.codex/hooks/`.
- The hook enforces existence, format, and numbering — not truthfulness. A
  fabricated-but-well-formed entry still passes; catching that remains user
  spot-checks plus periodic external review of sampled turns.
- Other runtimes remain report-based until they have fresh runtime evidence for
  automatic triggering.
```
