# Exemplar Library

## Purpose

User-accepted deliverables kept as first-class memory beside the error ledger;
form is imitated from them, never guessed from prohibitions.

## Admission Rule

```text
- Only deliverables the user actually accepted enter the library — verbatim,
  never edited, never paraphrased.
- Each exemplar carries frontmatter fields: type / date / context /
  acceptance / accepted_scope. Acceptance evidence is the user's accepting
  words, or the absence of correction on a type they normally correct.
- The agent never self-admits an exemplar, and never manufactures a draft to
  solicit acceptance. An empty library is a legal state, not a defect: the
  governing method gate (`agent-os/review/delivery-gate.md` for deliveries)
  operates alone until real accepted work accumulates.
```

## Location And Shape

```text
wiki/exemplars/<slug>-<date>.md          (per project; flat, no subdirectories)
  frontmatter: type / date / context / acceptance / accepted_scope
  body: the accepted deliverable, verbatim
wiki/exemplars/_INDEX.md                 (one line per exemplar with status)
wiki/exemplars/archive/                  (superseded or retired entries)
```

## Usage

```text
- Before producing a governed deliverable type, check `_INDEX.md`; if an
  accepted exemplar of that type exists, load it and match its FORM. Content
  comes from the task; shape comes from the exemplar. If none exists, the
  method gate alone governs.
- On conflict between an exemplar and a prose style rule, flag it to the user
  instead of silently picking one; the latest user message always wins.
- Health: keep <= 3 current exemplars per type; older ones move to archive/
  (never deleted — they remain evidence of what was once accepted).
```
