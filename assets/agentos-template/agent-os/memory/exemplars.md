# Exemplar Library

## Purpose

User-accepted deliverables kept as first-class memory beside the error ledger;
form is imitated from them, never guessed from prohibitions.

## Admission Rule

```text
- Only deliverables Master ZX actually accepted enter the library — verbatim,
  never edited, never paraphrased.
- Each exemplar carries: date, deliverable type, the task context in one line,
  and the acceptance evidence (Master ZX's accepting words or the absence of
  correction on a type he normally corrects).
- The agent never self-admits an exemplar. No acceptance evidence, no entry.
- Seeding: an EMPTY library for a governed type is a defect, not a waiting state.
  When a type has no exemplar, draft one WITH the user in the current session
  (shape rules + a live sample) and ask for acceptance on the spot. Waiting for
  acceptances to accumulate is not a seeding plan. A mechanism shipped with an
  empty library is unfinished work.
```

## Location and Shape

```text
wiki/exemplars/<type>/<date>-<slug>.md   (per project)
  frontmatter: type / date / context / acceptance-evidence
  body: the accepted deliverable, verbatim
wiki/exemplars/_INDEX.md                 (one line per exemplar, per-type sections)
```

## Usage

```text
- Before producing any governed deliverable type (report to ZX, decision brief,
  work order, PI-style writeup, handoff), load that type's exemplars and match
  their FORM. Content comes from the task; shape comes from the exemplar.
- On conflict between an exemplar and a prose style rule, flag it to Master ZX
  instead of silently picking one; the latest user message always wins.
- Health: keep <= 3 current exemplars per type; older ones move to archive/
  (never deleted — they remain evidence of what was once accepted).
```
