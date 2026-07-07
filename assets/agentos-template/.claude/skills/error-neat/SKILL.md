---
name: error-neat
description: "Use when the error memory system is unhealthy: oversized error files, oversized digests, long _INDEX rules, duplicate same-root errors, stale recent-error lists, or when the user explicitly asks to compress or clean error records."
---

# Error Neat

## Purpose

`error-neat` is the cleanup stage for `error-learning`. It compresses error memory without losing details.

It is not the normal entry point for new errors. Use `error-learning` first.

## Trigger

Run when any condition is true:
- single error file is over 30 lines
- `_DIGEST_NNN.md` is over 50 lines
- `_INDEX.md` high-priority rule is over 200 characters
- two or more files describe the same root failure
- archive links are missing or stale
- recent undigested errors include already digested items
- the user says "整理错误记录", "精简 errors", "index 太长了", "压缩错误日志", or "errors 该收一收了"

## Three Layers

Level 1: single error file
- at most 30 lines
- concrete "what went wrong" and "what to do"
- code details only when needed

Level 2: digest
- at most 50 lines
- pattern-level rule and action
- minimal code identifiers

Level 3: `_INDEX.md`
- behavior-level rules
- each high-priority rule at most 200 characters
- plain language

## Cleanup Flow

1. Audit counts and lengths.
2. Compress `_INDEX.md` first.
3. Compress digests second.
4. Merge or compress single error files last.
5. Move long details to `archive/` and link them.
6. Verify every layer still preserves "what went wrong" and "what to do".

## Same-Root Merge Rule

Same-root means one of:
- same violated high-priority rule
- same failure mode
- same user correction phrase
- same source-of-truth mistake
- same skipped tool or verification

When unsure, merge.

## Verification

Report actual numbers:
- longest single error file
- longest digest
- longest `_INDEX.md` high-priority rule
- same-root merge count
- new archive files
- missing archive links

Do not delete source data. Archive instead.
