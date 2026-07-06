---
name: fusion-workflow
description: Runs AgentOS Fusion Workflow — fan one question out to a blind panel of models (free web AIs via AgentChat, or codex/gemini/claude CLIs), judge all answers, deliver one fused answer with full provenance. MANUAL ONLY — use exclusively when the user explicitly invokes it (/fusion, "run Fusion", or names a panel). Never auto-initiate or suggest-trigger it.
---

# Fusion Workflow

Thin Codex adapter for the repo-local AgentOS kernel.

## Source

Read:

```text
agent-os/workflows/fusion-workflow.md          (contract: channels, cost gate, invariants)
agent-os/review/prompt-craft-gate.md           (every prompt passes this gate)
vendor/fusion-fable/skills/fusion/SKILL.md     (cli-channel pipeline)
vendor/fusion-fable/skills/fusion/references/judge_rubric.md
vendor/AgentChat/skills/AgentChat-FreeSubAgent/SKILL.md   (free-channel pipeline)
.claude/skills/fusion-workflow/references/panelist-prompt-template.md
.claude/skills/fusion-workflow/references/judge-prompt-template.md
```

## Runtime Rule (Codex)

The kernel contract governs unchanged: manual trigger only; free web channel
default; cli channel and any expensive-tier panelist need explicit the user
approval; panelists blind; judge is a separate cold worker — never the
orchestrating session; anonymized judging; provenance under outputs/fusion-runs/.

Codex-specific notes:

```text
runners  : use the adapter runners under .claude/skills/fusion-workflow/scripts/
           (run_gemini_cli.sh, run_codex_sandboxed.sh) — they are plain bash,
           not Claude-specific. The codex panelist runner spawns a SEPARATE
           codex exec, never reuses the orchestrating Codex session.
judge    : spawn as an independent Codex/Claude worker with ONLY the contract
           projection + packet + anonymized answers; per dynamic-workflow
           adapter rules, record a recoverable worker id for it.
templates: assemble panelist/judge prompts from the two templates above;
           a bare one-line role assignment violates the Prompt Craft Gate.
```

## Output Shape

```yaml
fusion_run:
  question_ref:
  channel: free | cli
  panel:
  degradation_notes:
  judge_track: A_artifact | B_research
  judge_worker_id:
  provenance_path:
  fused_answer_ref:
  evidence_limits:
```

Do not copy kernel text into this wrapper.
