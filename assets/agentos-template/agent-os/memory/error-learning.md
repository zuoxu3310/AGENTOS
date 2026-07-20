# Error Learning

## Purpose

Turn a confirmed agent mistake into a smaller probability of the same future
failure. Fix the user-visible problem first. A record is useful only when it
can be recalled by a real trigger and points to a protection that can be
checked.

## Record Boundary

Record a user correction, violated instruction, fabricated claim, skipped
required verification, repeated failure, or self-confirmed mistake. Do not
record a new requirement, preference, exploratory change, or unanswered
diagnostic question as an error.

## Same-Root Rule

Before creating a file, compare violated rule, failure mode, correction,
source-of-truth mistake, and skipped verification. If any load-bearing root is
the same, update the existing root and increment `recurrence`. When uncertain,
merge and make the broader trigger explicit.

## Machine Header

Every active error record starts with YAML frontmatter:

```yaml
---
error_id:
root_id:
status: observed | landed | verified | recurring | superseded
recurrence: 1
triggers: []
landing_level: 0
landing_target:
regression:
---
```

`error_id` and `root_id` are stable and unique. `triggers` are concrete terms
or action conditions, not broad topics. A landing target or regression anchor
must resolve to a real repository path; an optional `::test_name` suffix names
a test inside that file.

## Landing Rule

Choose the first level the correction can support:

```text
1. artifact shape     schema or required deliverable field
2. external check     test, lint, hook, or other independent guard
3. positive exemplar  user-accepted artifact to imitate
4. narrower contract  remove the unsafe decision surface
5. prose rule         only with a written reason levels 1-4 do not fit
```

For `recurrence >= 2`, Level 1 or 2 plus a real regression anchor is mandatory,
unless the error file records an explicit user waiver. Landing happens in the
same turn as the fix; an experiment may verify it but may not defer it.

After a landing is verified, use `verified`. If it happens again, use
`recurring`: the protection failed and must be strengthened rather than adding
another essay.

## Recall

Before a related high-risk action, `memory-wiki-routing` matches explicit
`triggers`, retrieves at most three non-superseded rules, and verifies their
landing targets. Do not preload the entire error library and do not use vector
search for this bounded collection.

## Derived Views And Health

`wiki/errors/_INDEX.md` has a semantic high-priority rule section and a derived
record/metric section. `--fix-memory-views` may regenerate only the derived
section. It tracks:

```text
recurrences after landing
active errors without regression protection
stale, duplicate, or conflicting rules
```

An active record is invalid if its machine header is incomplete, its landing
target is missing, the same `root_id` is split across files, or a recurrence
of two or more lacks Level 1/2 protection and regression. Keep each record at
or below 45 lines including its machine header; archive or digest source detail
without deleting it.

## Minimal Body

After the header, keep only:

```text
# concise failure title
## What happened
## Correction
## Landing
## Evidence Anchor
```

The body explains the root and evidence; the header enables recall and checks.
