# Error Learning

Date: 2026-07-06

## Purpose

Record confirmed agent mistakes so the same failure class gets caught earlier next time.

This is the kernel rule. The global `error-learning` skill is a convenience adapter;
where it is absent, this file is sufficient to do the work by hand.

Fix the user-facing problem first. Record the error after the fix.

## Record / Do Not Record

Record when:

```text
- the user clearly corrected an agent mistake
- an explicit instruction was violated
- facts, evidence, progress, file state, or tool results were fabricated
- a required tool, verification, hook, or skill was skipped
- the same failure mode recurred
- the agent detected its own confirmed mistake
```

Do not record: new requirements, direction changes, preferences, exploratory pivots,
or diagnostic questions ("any problems here?" is a question, not a correction).

## Location

`wiki/errors/` (lint-required in AgentOS projects). Seed `_INDEX.md` when missing.

## Procedure

```text
1. Same-root check first: same violated rule, same failure mode, same correction
   phrase, same source-of-truth mistake, or same skipped verification
   -> append one Recurrence line to the existing file. When unsure, merge.
2. Otherwise create one concise file:
   - what went wrong (1-3 lines)
   - what to do next time (1-3 lines, one rule per line)
   - evidence anchor: the command, path, or output that proves the mistake
     (re-runnable; "I remember" is not an anchor)
3. Update _INDEX.md: high-priority rules, categories, recent-undigested list, counts.
4. Health limits: single file <= 30 lines; digest <= 50 lines; each high-priority
   index rule <= 200 characters. On breach: compress and archive with links.
   Never delete source data.
5. Digest when undigested errors reach 10, or 3+ share one pattern:
   pattern-level rules only, no case history, no meta-commentary.
```

## Output

One line in the user-facing reply:

```text
_(error logged: <one sentence>; new|recurrence; health ok|cleaned)_
```

## Probe Feed

Recorded errors are prime material for the user's wrong-premise probes
("the trap you fell into last time"). Keep titles one-sentence so each error
can be turned into a probe question directly.
