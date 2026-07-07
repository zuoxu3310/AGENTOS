---
name: error-learning
description: "Use after fixing a confirmed agent mistake: user correction, violated instruction, fabricated claim, repeated failure, or self-detected error. Do not use for new requirements, preference changes, exploration pivots, or diagnostic questions."
---

# Error Learning

## AgentOS Coordination

In projects with `agent-os/`, the kernel law `agent-os/memory/error-learning.md`
governs and this skill executes it. AgentOS addition: every error file carries an
evidence anchor — the re-runnable command, path, or output that proves the mistake.

## Purpose

`error-learning` is the single entry point for the error memory system. It records confirmed mistakes and keeps the error index healthy without waiting for the user to ask for cleanup.

Fix the user-facing problem first. Record the error after the fix.

## Record

Record when:
- The user clearly corrected an agent mistake.
- The agent violated an explicit instruction.
- The agent fabricated facts, evidence, progress, file state, costs, or tool results.
- The agent skipped a required tool, verification, subagent, hook, or skill.
- The same failure mode recurred.
- The agent detects its own confirmed mistake.

Do not record when:
- The user adds a new requirement.
- The user changes direction.
- The user gives an aesthetic preference.
- The conversation is exploratory.
- The user asks a diagnostic question such as "有什么问题", "有没有问题", or "我有什么问题".

## Pipeline

Follow [references/pipeline.md](references/pipeline.md):

1. Fix the current issue.
2. Locate the error directory.
3. Check for same-root existing errors.
4. Append recurrence or create one concise error file.
5. Update `_INDEX.md`.
6. Run the health check.
7. If needed, digest and clean automatically.
8. Verify again.

## Location

Prefer the current project's scaffolded `wiki/errors/` directory when present. Root `errors/` may be a symlink to it for compatibility. Otherwise use Claude auto-memory `memory/errors/`. If neither exists and the current project root is clear, create `wiki/errors/` and seed `_INDEX.md`.

## Output

Keep user-facing output to one line:

```text
_(error logged: <one sentence>; <new|recurrence>; health <ok|cleaned>)_
```

## Digest and Cleanup

Digest and cleanup are internal stages of this skill:
- `error-digest`: when undigested errors reach 10 or patterns are obvious.
- `error-neat`: when files exceed size limits, same-root errors split across files, or `_INDEX.md` gets too long.

Do not ask before digesting or cleaning unless the action would delete data. Archiving with links is allowed; destructive deletion is not.

## Verification

Before claiming success, check:
- Error file exists or recurrence was appended.
- `_INDEX.md` was updated.
- Single error files are at most 30 lines.
- Digest files are at most 50 lines.
- `_INDEX.md` high-priority rules are at most 200 characters each.
- Archive links point to existing files when details were moved.
