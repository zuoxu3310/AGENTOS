---
name: fusion-workflow
description: Runs AgentOS Fusion Workflow — fan one question out to a blind panel of models (free web AIs via AgentChat, or codex/gemini/claude CLIs), judge all answers, deliver one fused answer with full provenance. MANUAL ONLY — use exclusively when the user explicitly invokes it (/fusion, "run Fusion", or names a panel). Never auto-initiate or suggest-trigger it.
---

# Fusion Workflow

Thin Claude adapter for the repo-local AgentOS kernel.

## Source

Read:

```text
agent-os/workflows/fusion-workflow.md          (contract: channels, cost gate, invariants)
vendor/fusion-fable/skills/fusion/SKILL.md     (cli-channel pipeline, steps 0-6)
vendor/fusion-fable/skills/fusion/references/judge_rubric.md
vendor/fusion-fable/skills/fusion/references/panel.md
vendor/AgentChat/skills/AgentChat-FreeSubAgent/SKILL.md   (free-channel pipeline)
.claude/skills/fusion-workflow/references/panelist-prompt-template.md
.claude/skills/fusion-workflow/references/judge-prompt-template.md
```

## Runtime Overrides (this machine, this project — they beat vendor text)

```text
panel detection : probe `command -v codex` and `command -v gemini` directly;
                  vendor detect_panel.sh probes `agy`, which is not installed.
gemini runner   : .claude/skills/fusion-workflow/scripts/run_gemini_cli.sh
                  (official gemini CLI one-shot), NOT vendor run_gemini.sh (agy).
codex runner    : .claude/skills/fusion-workflow/scripts/run_codex_sandboxed.sh
                  (default sandbox, empty scratch cwd, web search only).
                  Vendor run_codex.sh uses --dangerously-bypass-approvals-and-sandbox
                  and is blocked by the permission classifier — use it only when
                  the user explicitly approves an unsandboxed panelist run.
claude panelists: Agent tool, model: haiku unless the user names a bigger
                  model in the invocation (cost gate in the kernel contract).
judge           : a SEPARATE cold Agent-tool subagent per run — never the
                  orchestrator session (it packed the packet and has its own
                  lean; orchestrator-as-judge collapses independence). Default
                  model: inherit the session tier (each /fusion trigger carries
                  exactly one judge's cost; the user may name a tier). Give the judge ONLY: contract projection +
                  packet/question + anonymized A/B/C answers (+ artifact files
                  for Track A). The orchestrator holds the label mapping,
                  mediates any cross-exam round, and verifies the judge's
                  synthesis through the evidence gates before presenting.
free channel    : check `curl -s http://127.0.0.1:9222/json/version` first.
                  If Chrome CDP is down, report the launch command
                  (`bash vendor/AgentChat/scripts/start-chrome-debug.sh`) and
                  stop — do NOT silently fall through to the cli channel.
language        : answer in the question's language (the user's language);
                  ignore the vendor default of answering in French.
fusion mode on the free channel (default for execute/think tasks):
                  build the FreeSubAgent plan yourself — N nodes, IDENTICAL
                  question verbatim, depends_on all empty, one web provider per
                  node (prefer non-Claude providers: Gemini/ChatGPT/Kimi/
                  DeepSeek/Qwen; judge here is Claude). Do NOT let the DAG
                  decomposer rewrite the question. Panel size: 2 for small
                  checkable questions, 4 for consequential ones. Note: the
                  vendor arbitration brief's role-specific checks may be inert
                  in this mode; the judge's five-bucket synthesis is the load-
                  bearing comparison.
divergence mode : only for exploration tasks — use the vendor DAG decomposer
                  as shipped (roles, no two nodes on one sub-question).
context packet  : if the question depends on session/project context, first
                  compile ONE self-contained packet, identical for every
                  panelist. Skeleton = the active Task Contract projected for
                  cold readers — include ONLY: active object / deliverable /
                  boundaries / evidence standard / forbidden substitutions, then
                  add background facts / key file excerpts / original question
                  verbatim / expected output and language. EXCLUDE route, candidate
                  approaches, and any orchestrator hypothesis or lean (anchor
                  contamination). The same contract is later the judge's
                  yardstick and the completion gate. Keep <= ~10k chars (web
                  input limits); persist the packet in provenance. For
                  self-contained/public questions send the question verbatim
                  and let panelists research on their own.
anonymized judge: before judging, relabel answers A/B/C...; reveal the mapping
                  only inside the provenance file.
cross-exam round: only if the judge finds a load-bearing contradiction; free
                  channel by default, cli only with the user's approval; max 1 round.
prompt assembly : NEVER send a bare one-line role ("you are the judge"). Assemble the
                  panelist prompt and the judge prompt from the two templates
                  in references/ (official Anthropic/OpenAI practices baked
                  in: XML sections, long context on top + question at bottom,
                  quote grounding, evidence labels, coverage-first judging,
                  self-check). After assembly, scan the full prompt once for
                  contradictory directives before dispatch.
provenance      : run vendor save_run.sh, then move the printed file into
                  outputs/fusion-runs/ (mkdir -p first).
```

## Output Shape

```yaml
fusion_run:
  question_ref:
  channel: free | cli
  panel:                # who actually answered
  degradation_notes:
  judge_track: A_artifact | B_research
  provenance_path:      # outputs/fusion-runs/...
  fused_answer_ref:
  evidence_limits:
```

Raw panelist answers remain support artifacts; the fused answer passes the
Evidence-to-Claim Gate before any completion wording.
