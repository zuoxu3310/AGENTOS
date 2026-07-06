---
name: prompt-craft-review
description: Applies the AgentOS Prompt Craft Gate before writing or dispatching any prompt to another model or agent — subagent tasks, panel/judge prompts, worker prompts, DAG nodes, external CLI calls (codex/gemini/claude -p), web-AI dispatches. Use BEFORE composing such a prompt; a bare one-line role assignment violates the gate.
---

# Prompt Craft Review

Thin Codex adapter for the repo-local Agent OS kernel.

## Source

Read:

```text
agent-os/review/prompt-craft-gate.md
```

Worked examples:

```text
.claude/skills/fusion-workflow/references/panelist-prompt-template.md
.claude/skills/fusion-workflow/references/judge-prompt-template.md
```

## Trigger

Use before writing or sending any prompt destined for another model or agent.
Do not use for prompts the user writes themselves or for plain conversation.

## Output Shape

```yaml
prompt_craft_review:
  target: # which model/agent receives the prompt
  sections_present: # role / context / instructions / output_format / question
  long_context_order_ok: # materials top, question last
  evidence_labels_required: # yes/no
  contradiction_scan: # clean | fixed <n> conflicts
  zero_context_test: # pass | fixed
```

Do not copy kernel text into this wrapper.
