---
type: AgentOS Method
title: AgentOS Wiki v2 Method
description: Knowledge-format and lifecycle method for AgentOS project memory.
tags: [agentos, wiki, okf, memory, lifecycle]
timestamp: 2026-07-01T20:20:00+03:00
confidence: 0.78
status: active
last_confirmed: 2026-07-01
supersedes:
  - wiki/TASKS/2026-07-01-agentos-memory-visibility-base-v1.md
superseded_by:
sources:
  - https://cloud.google.com/blog/products/data-analytics/how-the-open-knowledge-format-can-improve-data-sharing
  - https://github.com/GoogleCloudPlatform/knowledge-catalog/tree/main/okf
  - https://gist.github.com/rohitg00/2067ab416f7bbe447c1977edaaa681e2
---

# AgentOS Wiki v2 Method

This concept turns the earlier scaffold-only wiki into a lifecycle-aware knowledge store.

It depends on [AgentOS Wiki v2](../../agent-os/memory/wiki-v2.md), [Memory Routing](../../agent-os/memory/routing.md), and [Memory Sync Audit](../../agent-os/memory/sync-audit.md).

## Method

Use one Markdown file per reusable concept. Treat the file path as the concept identity. Use YAML frontmatter for routing fields and Markdown body for human and agent reading.

Minimum AgentOS concept fields:

```yaml
type:
title:
description:
timestamp:
confidence:
status:
sources:
```

## Lifecycle

Knowledge moves through four tiers:

```text
working -> episodic -> semantic -> procedural
```

Only verified, reusable knowledge should become semantic memory under `wiki/knowledge/`. Procedural memory belongs in `agent-os/` or native runtime skills after validation.

## Supersession

When new evidence changes old memory, do not leave both claims as equally current. Mark the old concept stale or superseded, link the new concept, update `wiki/index.md`, and append `wiki/log.md`.

## Claim Boundary

This method is active but not yet fully automated. Current evidence supports the format and lifecycle rules; it does not prove hybrid search, automatic contradiction detection, or event-driven hooks.
