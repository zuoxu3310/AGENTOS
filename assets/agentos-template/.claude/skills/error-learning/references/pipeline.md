# Error Learning Pipeline

## 1. Classify

Record only confirmed agent mistakes.

Must record:
- violated explicit user instruction
- fabricated state, evidence, cost, source, or tool output
- skipped required tool, skill, verification, or subagent
- repeated failure mode
- self-detected confirmed mistake

Do not record:
- new requirement
- changed preference
- exploration pivot
- normal design iteration
- diagnostic question

## 2. Locate

Use this order:

1. `<project-root>/wiki/errors/` when the project uses the memory scaffold.
2. `memory/errors/` inside Claude project memory.
3. Existing `<project-root>/errors/` only when it is an older real directory or a symlink to `wiki/errors/`.
4. Create `<project-root>/wiki/errors/` if neither exists and the current project root is clear.

Seed `_INDEX.md` when missing.

## 3. Merge First

Before creating a file, inspect existing error files.

Same-root means one of:
- same violated high-priority rule
- same failure mode
- same user correction phrase
- same source-of-truth mistake
- same skipped required tool or verification

When unsure, append recurrence instead of creating a new file.

## 4. Write Concisely

Single error files must be at most 30 lines.

Keep only:
- what went wrong
- what to do next time
- one-line recurrence entries

Avoid case history, digest cross-links, pattern numbering, and long code detail.

## 5. Update Index

Update:
- high-priority rules when digest changed them
- category summary
- recent undigested errors
- digest log
- total counts and date

## 6. Health Check

Run after every write:

```bash
find wiki/errors -maxdepth 1 -type f -name '*.md' ! -name '_INDEX.md' ! -name '_DIGEST_*.md' -exec wc -l {} +
find wiki/errors -maxdepth 1 -type f -name '_DIGEST_*.md' -exec wc -l {} +
```

Check:
- single error files <= 30 lines
- digest files <= 50 lines
- `_INDEX.md` high-priority rules <= 200 characters
- no same-root error split across two files
- archive links exist
- "what went wrong" and "what to do" remain findable

## 7. Auto Digest

When recent undigested errors reach 10, or there are 3+ obvious same-pattern errors:

1. Create `_DIGEST_NNN.md` first.
2. Update `_INDEX.md` second.
3. Move digested source files to `archive/` last.
4. Run health check again.

## 8. Auto Neat

Run the cleanup stage automatically when:
- single error file > 30 lines
- digest > 50 lines
- `_INDEX.md` rule > 200 characters
- same-root errors are split across files
- recent errors are already digested but still listed

Cleanup may archive and relink details. It must not delete source data.
