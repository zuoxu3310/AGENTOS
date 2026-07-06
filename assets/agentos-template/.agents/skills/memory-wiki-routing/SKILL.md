---
name: memory-wiki-routing
description: Routes AgentOS durable memory, wiki, ledger, handoff, chat distillation, raw-source ingest, OKF-style concept docs, and stage sync. Use before writing project memory, updating wiki/index/log, promoting findings into PLANS/PROGRESS/DECISIONS/HANDOFF, or applying AgentOS Wiki v2 lifecycle rules.
---

# Memory Wiki Routing

Thin Codex adapter for the repo-local AgentOS memory kernel.

## Source

Read:

```text
agent-os/boot.md
agent-os/router.md
agent-os/memory/bootstrap.md
agent-os/memory/routing.md
agent-os/memory/sync-audit.md
```

If the task mentions Wiki v2, OKF, concept docs, confidence, supersession, graph links, or lifecycle memory, also read:

```text
agent-os/memory/wiki-v2.md
```

## Trigger

Use before durable memory writes, wiki routing, task contracts, chat notes, reusable knowledge pages, raw-source manifests, index/log updates, stage-end sync, or handoff updates.

## Routing Rule

Keep canonical current state in root ledgers:

```text
PLANS.md
PROGRESS.md
DECISIONS.md
HANDOFF.md
```

Use `wiki/knowledge/` for reusable concept knowledge and methodology. Use OKF-style frontmatter for concept docs, but do not move root ledgers into wiki pages.

## Output Shape

```yaml
memory_wiki_routing:
  active_user_object:
  content_classification:
  destination:
  concept_doc_required:
  ledgers_updated:
  wiki_index_updated:
  wiki_log_updated:
  evidence:
  handoff_state:
```

Do not treat wiki summaries as code evidence. Do not treat subagent reports as facts until checked.
