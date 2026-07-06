# Fusion Workflow

Date: 2026-07-06

## Purpose

Fusion Workflow is the Agent OS workflow for multi-model answer fusion: the same
question goes to several models in parallel and blind (no panelist sees another's
work), then a judge reads every answer and writes one fused answer grounded in a
structured comparison.

Use it for consequential questions that need execution, deep thought, or divergent
exploration, where being confidently wrong is expensive. A panel costs roughly N×
one answer and runs as slow as its slowest panelist — do not reach for it when one
model would obviously do.

## Kernel Classification

```text
kernel:
  this file, because it defines the canonical fusion contract.

adapter:
  .claude/skills/fusion-workflow/ (Claude wrapper + gemini CLI runner override).

extension:
  vendor/fusion-fable/ (blind panel + two-track judge, MIT, pinned clone)
  vendor/AgentChat/    (free web-AI channel via Chrome CDP, MIT, pinned clone)

verification:
  smoke runs recorded under outputs/fusion-runs/.
```

Vendor code is reused, not rewritten. Do not fork vendor internals into the kernel.

## Entry Criteria — Manual Only

Run Fusion ONLY when the latest user message explicitly invokes it (`/fusion`,
"run Fusion", or an equivalent direct request from the user).

```text
forbidden:
  - auto-initiating Fusion because a task looks hard
  - suggest-triggering ("this looks worth fusing, shall I?")
  - silently escalating any other workflow into a Fusion run
```

Decided by the user on 2026-07-06.

## Channels And Cost Gate

```yaml
channels:
  free:                       # default
    engine: vendor/AgentChat (Chrome CDP -> free web AIs)
    token_cost: zero
    precondition: Chrome debug session up and logged in (user-side)
  cli:                        # only when the user names it in the invocation
    panelists:
      gpt: codex CLI (vendor run_codex.sh, stdin prompt, subscription quota)
      gemini: gemini CLI (adapter run_gemini_cli.sh, free-tier quota)
      claude: in-session Agent subagents, model haiku by default
cost_gate:
  - free is the default; cli runs only when the invocation names it.
  - in-session panelists default to the cheapest model tier (haiku).
  - Fable/Opus-tier panelists require prior count+cost approval from the user
    (rule origin: wiki/errors/2026-07-06-expensive-subagents-without-approval.md).
  - the judge is a dedicated cold subagent, never the orchestrator session. It
    inherits the main-session model tier by default — one /fusion invocation
    carries the cost of exactly one judge; the user may name a different tier
    in the trigger.
  - never silently switch a failed free run to the cli channel; report instead.
```

## Modes (orthogonal to channels)

```yaml
modes:
  fusion:        # default — for execution and deep-reasoning tasks
    shape: the SAME question verbatim to every panelist, blind
    gain: independent runs expose each other's errors; contradictions surface
    free_channel_impl: pass FreeSubAgent a pre-built plan whose nodes all carry
      the identical question with empty depends_on (bypass the DAG decomposer;
      its role-specific arbitration checks may be inert in this mode — the
      judge's structured synthesis carries the load instead)
  divergence:    # for exploration / idea-generation tasks
    shape: role-decomposed angles (AgentChat DAG decomposer), no two panelists
      on the same sub-question
    gain: coverage breadth, not redundancy — do not sell it as cross-checking
mode_choice: by deliverable type (execute/think -> fusion; diverge -> divergence).
channel_choice: by the cost gate. Any mode runs on either channel.
```

## Context Packet (input regimes)

Panelists are cold: web-channel models see no session context, and the sandboxed
cli runners work in empty scratch dirs. Without equal input, answer divergence
is information asymmetry (noise), not independent reasoning (signal), and the
judge will misread missing-context gaps as contradictions.

```yaml
input_regimes:
  packet:        # for context-dependent questions (project files, prior findings)
    who_packs: the orchestrator (current main session — it already holds the
      context; no separate local model needed)
    skeleton: the active Task Contract, projected for cold readers. Whitelisted
      contract fields go in — active_user_object, deliverable, boundaries,
      evidence_standard (so panelists return checkable support), and
      forbidden_substitutions. Route, candidate approaches, and next-step plans
      are EXCLUDED — they encode the orchestrator's lean and would anchor the
      panel. The same contract later serves as the judge's yardstick and the
      completion gate: one standard from question to verdict.
    contents: contract projection + background facts, load-bearing file
      excerpts, the user's question VERBATIM, expected output shape and language
    hard_rules:
      - one identical packet to every panelist; no per-panelist tailoring
      - self-contained: assume the reader has zero context and cannot ask back
      - NEUTRALITY: the packet must contain no candidate answer, hypothesis,
        preliminary lean, or leading framing from the orchestrator — anchor
        contamination collapses panel independence
      - bounded size (web chat inputs have limits; keep load-bearing excerpts
        only, target <= ~10k chars)
      - the full packet is persisted in the provenance file for audit
  direct:        # for self-contained / public-knowledge questions
    send the question verbatim; let tool-capable panelists gather their own
    sources (independent research is part of the diversity being harvested)
regime_choice: does answering require information that exists only in this
  session/project? yes -> packet; no -> direct.
```

## Invariants

```text
- Panelists are blind: never paste one panelist's output into another's prompt.
- In fusion mode panelists get the user's question verbatim; no personas, no
  assigned lenses (divergence-mode roles are division of labor, not personas).
- Anonymized judging: during the judge phase answers are labeled A/B/C...; the
  label-to-model mapping is revealed only in the provenance file. This blocks
  judge self-preference (llm-council pattern).
- Family diversity: when the judge is a Claude session, prefer non-Claude
  panelists; same-family agreement never outranks cross-family consensus.
- Prompt discipline: every prompt passes the Prompt Craft Gate
  (agent-os/review/prompt-craft-gate.md); panelist and judge prompts are
  assembled from the engineered templates in the adapter's references/. A
  bare one-line role assignment is a contract violation.
- The judge is the only place the answers meet.
- Judge separation: the judge is NOT the orchestrator. It is spawned cold per
  run and receives ONLY the contract projection, the packet (or verbatim
  question), and the anonymized answers — never the session conversation, the
  label-to-model mapping, or any orchestrator lean. Its verdict must be
  reproducible from the provenance file alone.
- The orchestrator (main session) owns the route: it packs, dispatches,
  monitors, anonymizes, and afterwards verifies the judge's synthesis through
  the Promotion and Evidence-to-Claim gates. It never writes the verdict.
- Raw panelist answers are support artifacts until the judge weighs them; the
  judge's synthesis is itself a worker product until the orchestrator verifies.
- Every run persists full provenance before the fused answer is presented.
```

## Optional Cross-Examination Round (gated)

Only when the judge reports a load-bearing contradiction: the ORCHESTRATOR
dispatches the round (the judge cannot spawn agents) — each surviving panelist
gets the OTHERS' anonymized answers and gives a short critique/defense of the
disputed point only (not a rewrite); replies go back to the judge. Free
channel: allowed by default (zero token cost, adds latency). CLI channel: needs
the user's go-ahead (extra spend). Never loop more than one extra round.

## Execution Model

```text
1. Write the question verbatim to a per-run temp dir. Pick the input regime:
   context-dependent -> build the Context Packet (neutrality rules above);
   self-contained -> question verbatim only.
2. Select channel by the cost gate above.
3. Select mode by deliverable type (fusion = same question to all; divergence =
   role-decomposed DAG), then fan out all panelists in parallel, blind.
   free: AgentChat FreeSubAgent — pre-built same-question plan (fusion) or
         decomposer DAG (divergence); prefer non-Claude web providers when the
         judge is Claude; panel size 2 for small checkable questions, 4 for
         consequential ones.
   cli:  fusion-fable pattern via the adapter runners.
4. Degradation: a failed/empty/timed-out panelist is dropped with a one-line
   note; the run needs >=2 surviving independent answers, else report failure.
5. Anonymize: the orchestrator relabels surviving answers A/B/C...; it alone
   holds the mapping (provenance only) — the judge never sees it.
6. Spawn the judge: one cold subagent (main-session model tier by default),
   input = contract projection + packet/question + anonymized answers (+ the
   candidate artifact files for Track A; the judge has bash to run them). The
   judge classifies the deliverable, then runs one track
   (vendor/fusion-fable/skills/fusion/references/judge_rubric.md):
   Track A artifact: run every candidate, decide by observed behavior, graft
   working parts onto the stronger base, run the merged result until it passes.
   Track B research: Consensus / Contradictions / Partial coverage / Unique
   insights / Blind spots, then a grounded answer.
7. Persist provenance to outputs/fusion-runs/ (question, every raw answer with
   the label-to-model mapping, analysis or arbitration brief, fused answer,
   degradation notes).
8. The orchestrator verifies the judge's synthesis through the Promotion and
   Evidence-to-Claim gates, then presents: fused answer first, audit trail
   beneath, name the panel actually used, the judge agent, and any degradation.
```

## Promotion Rules

```text
Promote without extra verification: panel composition, per-panelist exit status,
provenance file path.

Do not promote without verification: factual/causal/completion claims inside any
panelist answer. The fused answer passes Evidence-to-Claim Gate like any other
deliverable; a panelist that ran code or read a primary source outranks one
reasoning from memory; a dropped panelist is absent, never silent agreement.
```

## Completion Evidence

```text
- provenance file exists under outputs/fusion-runs/ and names the panel
- >=2 independent raw answers recorded (or an explicit failure report)
- degradation notes recorded for every dropped panelist
- the judge was a separate cold agent; its full input set is contained in the
  provenance file (verdict reproducible without the session)
- fused answer cites which panelists ground each load-bearing point
- the orchestrator verified the judge's synthesis through the gates
- Evidence-to-Claim Gate allows the final wording
```

## Handoff Minimum

```yaml
fusion_handoff:
  question_ref:
  channel_and_panel:
  provenance_path:
  surviving_panelists:
  degradation_notes:
  judge_track:
  next_safe_action:
```

## Claim Boundary

```text
allowed:
  "The fused answer is grounded in N independent panelist answers; provenance
   at <path>."

forbidden without stronger evidence:
  "The fused answer is correct."
  "The panel covered all blind spots."
  "The free channel is verified" (until a real logged-in run has been recorded).
```
