---
name: memory-wiki-routing
description: The sole project adapter for AgentOS memory routing, selective loading, Wiki maintenance, stage closeout, and error recall or landing.
---

# Memory Wiki Routing

## Source

Read `agent-os/memory/routing.md` completely. Read only the relevant supporting
format or checklist:

```text
initial scaffold       agent-os/memory/bootstrap.md
knowledge concept      agent-os/memory/wiki-v2.md
stage closeout         agent-os/memory/sync-audit.md
error record           agent-os/memory/error-learning.md
```

## Route

Classify the event, load only the current artifacts named by the operating
contract, and write only destinations whose meaning changed. Before a related
high-risk action, match explicit error `triggers` and load at most three active
rules with verified landing targets.

Global `wiki-maintenance`, `neat-freak`, `error-learning`, and `error-neat`
skills may assist maintenance when available. They are not installed-project
dependencies and do not own policy. Claude still uses native Workflow and
Superpowers for execution.

## Completion

At explicit closeout, return the transaction's `memory_disposition`. Use
`not_needed` when no durable artifact changed; do not write every ledger merely
to demonstrate that routing ran.
