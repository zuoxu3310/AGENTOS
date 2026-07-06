---
name: minimal-code-review
description: Runs the minimal-code decision ladder before writing code, adding a dependency, or adding a feature — reuse before generation. Use before generating any new code in this Agent OS project.
---

# Minimal Code Review

Thin Claude adapter for the repo-local Agent OS kernel.

## Source

Read:

```text
agent-os/boot.md
agent-os/router.md
agent-os/review/minimal-code-gate.md
```

## Trigger

Use before writing code, adding a dependency, or adding a feature. Not for pure conversation, docs, or analysis.

## Output Shape

```yaml
minimal_code_review:
  ladder_stop_rung:
  reuse_target:
  generated_scope:
```

Do not copy kernel text into this wrapper.
