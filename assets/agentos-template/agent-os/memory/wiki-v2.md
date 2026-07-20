# AgentOS Wiki v2

## Purpose

Define the format and supersession rules for reusable knowledge under
`wiki/knowledge/`. All read/write timing, promotion, lifecycle ownership, and
conflict routing belong to the Memory Operating Contract.

The format follows the useful parts of Open Knowledge Format: Markdown concept
files, YAML frontmatter, path identity, explicit sources, and navigable links.

## Concept Document

Every `wiki/knowledge/*.md` concept except the collection `README.md` uses YAML frontmatter:

```yaml
---
type: AgentOS Concept
title:
description:
tags: []
timestamp:
confidence:
status: current | superseded | stale | archived
last_confirmed:
supersedes: []
superseded_by:
sources: []
---
```

Required fields are `type`, `title`, `description`, `timestamp`, `confidence`,
`status`, `last_confirmed`, `supersedes`, `superseded_by`, and `sources`.
Unknown `type` values may be retained during migration, but missing fields are
not valid.

## Identity And Links

The file path is the concept identity; do not rename it casually. Markdown
links create navigation, not evidence. State the relationship in prose and
keep primary evidence in `sources`.

## Confidence

```text
0.00-0.39  draft or weak
0.40-0.69  supported but incomplete
0.70-0.89  strongly supported in the current project
0.90-1.00  current canonical method with direct evidence
```

Confidence is claim strength, not a truth label.

## Supersession

When meaning changes, update both ends of the chain:

1. mark the old concept `superseded` and set `superseded_by`;
2. name the old concept in the replacement's `supersedes` list;
3. verify both paths exist;
4. add one lifecycle entry to `wiki/log.md`;
5. update the derived Wiki index view.

A broken or one-sided supersession chain is invalid. Unresolved contradiction
uses `stale`, not an invented replacement.
