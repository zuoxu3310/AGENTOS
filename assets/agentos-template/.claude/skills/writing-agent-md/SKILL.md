---
name: writing-agent-md
description: Use when editing or auditing CLAUDE.md, AGENTS.md, or deciding whether a rule belongs in an entry doc, skill, hook, prompt, or project memory file.
---

## Shared Agent Boundary

- Claude Code may edit `CLAUDE.md`, `AGENTS.md`, and imported entry-doc files directly.
- Codex should propose patches for `CLAUDE.md`, `AGENTS.md`, and imports unless the user explicitly asks it to edit them.
- Both agents may read freely.

# Writing Agent Entry Docs

## Purpose

This skill only owns agent entry documents:
- `CLAUDE.md`
- `AGENTS.md`
- canonical entry docs such as `wiki/AGENTS.md`
- imported entry-doc fragments
- entry-doc placement decisions

It does not maintain project memory files. Use the routing table below.

## Routing

- Full project memory scaffold -> `project-memory-bootstrap`
- `wiki/`, `raw/`, `CHATS/`, `index.md`, `log.md` ingest/query/lint/promote -> `wiki-maintenance`
- Stage-end doc and memory reconciliation -> `neat-freak`
- Confirmed agent mistakes -> `error-learning`
- Error record compression -> `error-neat`
- Skill authoring -> `skill-creator` or `writing-skills`
- Hooks/settings/permissions -> configuration-specific tools, not entry docs
- One-time task requirements -> current prompt or `TASKS/`

## Entry Doc Rules

Entry docs should contain durable rules that agents need at session start:
- project structure and important paths
- build, test, lint, run commands that are not obvious
- non-default coding conventions
- safety rules and do-not-touch areas
- source-of-truth order
- completion and verification rules
- routing to project memory files and skills

Do not put these in entry docs:
- current progress
- chat transcripts
- temporary task scope
- detailed API docs
- long tutorials
- file-by-file explanations
- facts an agent can read from code or package metadata
- anything better enforced by hook, CI, pre-commit, or script

## Claude vs AGENTS

Claude Code reads `CLAUDE.md`. Codex and many other agents read `AGENTS.md`.

Preferred project bridge:

```text
wiki/AGENTS.md          # single source of truth
AGENTS.md -> wiki/AGENTS.md
CLAUDE.md -> wiki/AGENTS.md
```

This gives byte-identical entry docs without `cp + diff`.

If a repo cannot use symlinks, fallback order is:
1. `CLAUDE.md` imports `@AGENTS.md`
2. byte mirror with `cp` + `diff -q`

If mirroring is used, verify with:

```bash
diff -q CLAUDE.md AGENTS.md
```

## Placement Decision

Ask what the information is:

- Stable cross-session agent rule -> `AGENTS.md` / `CLAUDE.md`
- Current state for next agent -> `HANDOFF.md`
- Active or recent plan -> `PLANS.md`
- Actual progress with evidence -> `PROGRESS.md`
- Durable decision and reason -> `DECISIONS.md`
- Non-trivial task contract -> `TASKS/`
- Key chat intent -> `CHATS/`
- Compiled project knowledge -> `wiki/`
- Raw source material -> `raw/`
- Confirmed repeated mistake -> `errors/`
- Reusable workflow -> skill
- Mandatory mechanical action -> hook/CI/script
- One-time instruction -> prompt

## Quality Bar

Keep entry docs short, concrete, and verifiable.

Before adding a rule, ask:
- Would removing this likely cause a future agent mistake?
- Is this stable across sessions?
- Is this more appropriate as a skill, hook, memory file, or prompt?
- Can the rule be checked by a command, path, or observable behavior?

## Verification

For any edit:

```bash
wc -l CLAUDE.md AGENTS.md 2>/dev/null
wc -c AGENTS.md 2>/dev/null
rg -n "today|yesterday|recently|刚刚|最近|今天|昨天" CLAUDE.md AGENTS.md 2>/dev/null
```

If `CLAUDE.md` imports `AGENTS.md`, verify the import path exists.

If symlink single-truth is required, verify:

```bash
readlink AGENTS.md
readlink CLAUDE.md
test -f wiki/AGENTS.md
```

If byte mirroring is required, run `diff -q CLAUDE.md AGENTS.md`.

## References

Read only when needed:
- [references/claude-md-spec.md](references/claude-md-spec.md)
- [references/agents-md-spec.md](references/agents-md-spec.md)
- [references/checklist.md](references/checklist.md)
- [references/sources.md](references/sources.md)
