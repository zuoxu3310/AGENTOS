# Per-Turn Audit Gate

Date: 2026-07-02

## Purpose

Per-Turn Audit Gate makes audit non-optional. Every turn — including small,
short-path, and pure-conversation turns — must produce a minimal audit and
report it. This overrides any "small tasks may skip audit" allowance elsewhere
in the kernel.

The enforcement the user chose is report-based, not hook-based: if the Agent
does not report the audit, that counts as the audit not done, and the user can
catch it on sight.

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
what was done: <one line>
evidence: <file/command/observation, one line>
status: complete | partial | blocked
logged: agent-os/state/audit-log.md #<n>
```

The last line is mandatory and the block always ends with the entry id, so
the compact form and the full YAML form terminate identically and the log
pointer is never ambiguous.

## Audit Log Entry (what to append to the log)

Append to `agent-os/state/audit-log.md`:

```text
## <n> (<sid>) — <one-line turn label>
- object:
- contract:
- action+evidence:
- status:
- gates: intent=passed|n/a(short reason); syco=…; code=…; prompt=…; evidence=…; route=…
- intent: quote「<verbatim substring of this turn's user message>」→ goal=… deliverable=… not-doing=…
- restate: passed(<zero-context reader>/one-line gist) | rewritten(reason)   # only on replies >=1200 chars
```

Field values may be written in the working language of the session (the quote
inside 「」 is always the user's own words untranslated); the six field KEYS and
this format definition are English-only — the system must stay unambiguous.

Numbering (2026-07-07): `<sid>` is the short session tag the hooks
announce each turn — it is what lets CONCURRENT sessions share one log. Take the
announced number (global max + 1); if another session takes it first, any higher
number is fine — same number under different session tags is legal, only your own
session's numbers must strictly increase. The log is APPEND-ONLY: never renumber
or edit past entries (concurrent editing corrupts the shared file; concurrent-session
collisions burned this, 2026-07-06), except to close a `partial` status to
its final state. Entries without a tag are legacy and stay untouched.

Why the three extra lines (2026-07-06 owner ruling: every gate must be walked
and leave a trace):

```text
- gates: no gate may be skipped silently. Every gate gets a disposition —
  passed, or not-applicable with a reason. Skipping becomes a written lie
  instead of an invisible omission; that is what makes it auditable.
- intent: the quote inside 「」 must be a verbatim substring of this turn's
  user message. This is a CONTENT anchor a script can verify — field presence
  can be performed, a matching verbatim quote cannot be invented. Notification
  and slash-command turns are exempt from the quote check.
- restate: long deliverables must survive a zero-context restate test — hand
  the reply text (nothing else) to a cheap fresh reader; if it cannot restate
  the mechanism and the pending decisions, the clarity was performative and
  the reply must be rewritten before delivery. Since 2026-07-07 the reader
  answers a second question too: does the reply hold a LINE — swapping two
  body paragraphs must break it (a swap-immune reply is a list of points, not
  an argument; rewrite). Rule body for writing the line: the line-drawing
  protocol on the local rules card (fix the from→to question, given→new
  chaining per paragraph, terms pay a story-first entry fee, qualifiers
  bundled after the line).
```

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
- 2026-07-06 hardening: the Stop hook additionally verifies
  (a) the gates line disposes >=3 gates and always disposes intent=;
  (b) on real-instruction turns the intent quote is a verbatim substring of the
  turn's user message (read from the transcript; user messages flush at turn
  start, so this read has no Stop-event race);
  (c) replies >=1200 chars carry a restate line evidencing the zero-context
  restate test. The restate check reads the last assistant message and thus
  shares the flush race — it can misfire once; MAX_BLOCKS + fail-open bounds
  the damage and the miss lands in compliance-log.tsv.
- 2026-07-07 (from a field audit): (a) numbering went
  per-session — entries carry a `(<sid>)` tag, the gate only requires that THIS
  session appended a new, strictly-increasing entry; cross-session number
  collisions are legal and the global-contiguity check is gone (concurrent
  sessions sharing one log made collisions a designed-in failure); (b) the
  quote check compares against the CORPUS of the turn-opening user message
  group — queued messages and option answers all count, harness injections
  (isMeta records: skill bodies, workflow expansions, bounce feedback, image
  stubs) never do. Regression set: real bounce turns from field
  transcripts, per the fixtures-from-real-data rule.
- The hook enforces existence, format, numbering, and the verbatim-quote
  content anchor — not full truthfulness. A fabricated-but-well-formed gates or
  restate line still passes; catching that remains user spot-checks plus
  periodic external review of sampled turns.
- Non-Claude runtimes (Codex included) remain report-based: a missing report
  means the audit was not done, and the user can catch it on sight.
```
