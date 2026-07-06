# AgentOS Architecture

AgentOS is built on one idea: **keep the rules in a single canonical kernel, and let thin
adapters activate them inside each agent runtime.** This document explains the layers.

## The three layers

```
┌─────────────────────────────────────────────────────────────┐
│ ENFORCEMENT LAYER  (mechanical)                              │
│   .claude/hooks/  ·  .codex/hooks/  ·  agent-os/tools/aos-lint│
│   SessionStart · UserPromptSubmit · Stop · PreToolUse · Post  │
└─────────────────────────────────────────────────────────────┘
             ▲ activates / verifies
┌─────────────────────────────────────────────────────────────┐
│ ADAPTER LAYER  (projection)                                  │
│   AGENTS.md · CLAUDE.md · rules cards · skill wrappers        │
│   .claude/ · .codex/ · .agents/                              │
└─────────────────────────────────────────────────────────────┘
             ▲ points back to
┌─────────────────────────────────────────────────────────────┐
│ KERNEL LAYER  (canonical, runtime-agnostic)                  │
│   agent-os/  — rules · routing · review · workflows ·         │
│               memory · state · tools                         │
└─────────────────────────────────────────────────────────────┘
```

### 1. Kernel layer — `agent-os/`

The single source of truth. Nothing in the kernel is runtime-specific.

| Path | Role |
|---|---|
| `boot.md` | Minimum startup: what an agent reads first |
| `router.md` | Routes a task to the right gates, workflows, and skills |
| `review/` | The decision procedures (gates): task-contract, intent-causal, anti-sycophancy, minimal-code, reasoning-base, evidence-to-claim, route-keeper/promotion, prompt-craft, per-turn-audit, completion |
| `workflows/` | Agent execution lifecycle, dynamic (multi-worker) workflow, fusion (multi-model) workflow |
| `memory/` | Routing rules, wiki-v2 method, error-learning, bootstrap, sync-audit |
| `adapters/` | Cross-runtime standards: runtime-visibility, skill-parity |
| `state/` | Live per-turn state: `audit-log.md`, `current.md` (seeded once, then owned by the project) |
| `tools/aos-lint.py` | Structural linter for the kernel |

### 2. Adapter layer — projections

Each runtime has an entry file and a resident "rules card" that point back into the
kernel instead of duplicating it.

- **Claude Code:** `CLAUDE.md` + `.claude/rules/agentos-local-rules.md` (auto-injected
  each session) + `.claude/skills/` wrappers.
- **Codex / generic:** `AGENTS.md` + `.codex/agentos-local-rules.md` + `.agents/skills/`
  wrappers (with Codex `agents/openai.yaml` metadata where needed).

The **skill-parity** standard keeps the same capability available under each runtime's
skill format; the **runtime-visibility** standard defines when a workflow worker is
visible enough to be auditable.

### 3. Enforcement layer — hooks + lint

Hooks turn the highest-value invariants from prose into mechanism. They are **fail-open**
(a broken hook becomes a no-op) and enforce existence/format/structure only.

| Hook event | File | What it does |
|---|---|---|
| SessionStart | `aos_session_start.py` | Injects the rules card + dynamic state (next audit number, current object) |
| UserPromptSubmit | `aos_prompt_baseline.py` | Records the per-turn audit baseline |
| Stop | `aos_stop_gate.py` | Blocks the turn until a well-formed, uniquely-numbered audit entry exists beyond the baseline |
| PreToolUse | `aos_guard_enforcer.py` | Asks before edits to the enforcement layer; denies edits to the script-owned metrics log |
| PostToolUse | `aos_kernel_lint.py` | Re-runs `aos-lint` after any `agent-os/**` edit and feeds failures back |

Claude Code wires these via `.claude/settings.json`; Codex wires them via
`.codex/hooks.json` when the project `.codex/` layer is trusted.

## The per-turn audit invariant

The load-bearing guarantee AgentOS *can* make mechanically:

> A turn cannot finish until `agent-os/state/audit-log.md` has gained a well-formed,
> uniquely-numbered entry beyond the turn's baseline.

An entry is:

```
## <n> — <one-line label>
- object:
- contract:
- action+evidence:
- status:
```

The Stop hook checks: (1) the log gained at least one entry beyond the baseline; (2) the
newest entry has all four fields; (3) entry numbers are unique and contiguous. It blocks
up to a bounded number of retries, then fails open and records a `missed` row in the
script-owned `compliance-log.tsv` so misses are **measurable instead of silent**.

The transcript scan that checks for a *visible* audit block is advisory only (recorded,
never blocking) because transcript flushing races the Stop event.

## What is enforced vs. routed

| Concern | Mechanism |
|---|---|
| Audit trail exists and is well-formed | **Hook-enforced** (Stop) |
| Kernel structure is intact | **Hook-enforced** (`aos-lint` on edit) + CI |
| Enforcement layer isn't edited by accident | **Hook-enforced** (PreToolUse guard) |
| Anti-sycophancy, minimal-code, evidence-to-claim, reasoning, intent, route, prompt-craft | **Routed** by the rules card (prompt layer) |

This split is deliberate: mechanize what can be proven, and make the rest explicit and
routed rather than pretending a judgment gate is a hard guarantee.

## Design invariants

- **One kernel, many adapters.** Never maintain a rule in more than one place.
- **Fail open.** Enforcement must never brick a working session.
- **Non-destructive install.** Merge or back up; never silently overwrite user state.
- **Seed-once live state.** `agent-os/state/` and `wiki/` are seeded on first install and
  preserved forever after, so upgrades never wipe the audit log or knowledge base.
- **Honest scope.** `aos-lint` proves structure only; the hooks prove format and
  existence — not truthfulness.
