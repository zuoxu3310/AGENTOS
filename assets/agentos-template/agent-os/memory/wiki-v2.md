# AgentOS Wiki v2

Date: 2026-07-01

## Purpose

AgentOS Wiki v2 upgrades `wiki/` from a directory scaffold into a knowledge format with lifecycle rules.

It is inspired by:

```text
- Open Knowledge Format: markdown concept files with YAML frontmatter, path identity, links as graph, optional index/log.
- LLM Wiki v2: confidence, supersession, retention, consolidation tiers, quality checks, audit trail.
```

Sources:

```text
https://cloud.google.com/blog/products/data-analytics/how-the-open-knowledge-format-can-improve-data-sharing
https://github.com/GoogleCloudPlatform/knowledge-catalog/tree/main/okf
https://gist.github.com/rohitg00/2067ab416f7bbe447c1977edaaa681e2
```

## Boundary

`agent-os/` remains the kernel. `wiki/` remains project memory storage.

Do not promote wiki pages over root ledgers:

```text
PLANS.md
PROGRESS.md
DECISIONS.md
HANDOFF.md
```

## Concept Document Minimum

Every reusable concept doc under `wiki/knowledge/` should use YAML frontmatter:

```yaml
---
type: AgentOS Concept
title:
description:
tags:
timestamp:
confidence:
status: active | draft | superseded | stale | archived
last_confirmed:
supersedes:
superseded_by:
sources:
---
```

Required for AgentOS Wiki v2 concept docs:

```text
type
title
description
timestamp
confidence
status
sources
```

`type` is the routing field. Unknown types are tolerated.

## Path Identity

The file path is the concept identity.

Example:

```text
wiki/knowledge/agentos-wiki-v2-method.md
```

Do not rename concept files casually. If a concept moves, preserve old links or record the move in `wiki/log.md`.

## Link Graph

Use normal Markdown links to create the knowledge graph.

Relationship meaning must be stated in surrounding prose:

```md
This method depends on [Memory Routing](../../agent-os/memory/routing.md).
It supersedes [the scaffold-only wiki method](../TASKS/2026-07-01-agentos-memory-visibility-base-v1.md).
```

Links support navigation; they do not prove claims.

## Confidence And Supersession

Confidence is a claim-strength signal, not a truth label.

Use:

```text
0.00-0.39 weak or draft
0.40-0.69 supported but incomplete
0.70-0.89 strongly supported for current project state
0.90-1.00 current canonical project method with direct evidence
```

When newer evidence changes a concept:

```text
1. Create or update the new concept.
2. Set old concept status to superseded or stale.
3. Fill `superseded_by` on old concept.
4. Fill `supersedes` on new concept.
5. Append `wiki/log.md`.
6. Downgrade final claims until the new state is verified.
```

## Consolidation Tiers

Route memory by maturity:

```text
working:
  current conversation and scratch state

episodic:
  wiki/CHATS/ and wiki/TASKS/ summaries

semantic:
  wiki/knowledge/ concept docs

procedural:
  agent-os/ kernel rules and local native skills after verification
```

Do not promote working or episodic observations into semantic/procedural memory without evidence and route checks.

## Quality Gate

Before writing or updating a concept doc:

```yaml
wiki_v2_quality_gate:
  source_checked:
  claim_type_separated:
  confidence_set:
  contradiction_checked:
  supersession_needed:
  index_updated:
  log_updated:
```

If contradiction is found and not resolved, set `status: draft` or `status: stale` and write the uncertainty plainly.

## Index And Log

`wiki/index.md` is the human-readable map. It must link durable concept docs.

`wiki/log.md` is the audit trail. It records memory operations, evidence, and next action.

Passing an index/log check does not prove the concept is true; it proves the memory operation is traceable.
