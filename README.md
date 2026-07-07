# AgentOS — a repo-local operating system for AI coding agents

[![CI](https://github.com/zuoxu3310/AGENTOS/actions/workflows/ci.yml/badge.svg)](https://github.com/zuoxu3310/AGENTOS/actions/workflows/ci.yml)
[![License: Apache-2.0](https://img.shields.io/badge/License-Apache_2.0-blue.svg)](./LICENSE)
[![Runtimes: Claude Code · Codex · Agents](https://img.shields.io/badge/runtimes-Claude%20Code%20%C2%B7%20Codex%20%C2%B7%20Agents-6f42c1.svg)](#supported-runtimes)

**AgentOS is a repo-local governance kernel for AI coding agents.** You install one
`agent-os/` directory into any project, and every agent that works in that repo —
[Claude Code](https://docs.claude.com/en/docs/claude-code), [OpenAI Codex](https://openai.com/index/introducing-codex/),
or any `AGENTS.md`-aware runtime — inherits the same enforced discipline: a per-turn
audit trail, review gates against sycophancy and unsupported claims, task contracts,
route keeping, and a durable memory system. The rules live **once** in the kernel;
thin adapters project them into each runtime.

> **TL;DR** — `AGENTS.md` and `CLAUDE.md` tell an agent how to behave, but nothing
> checks that it did. AgentOS turns those instructions into a mechanism: hooks that
> **block a turn from ending until the agent has logged an audit entry**, a structural
> linter for the kernel, and a review-gate library the agent must route through before
> it claims something is done. It is runtime-agnostic, dependency-free, and installs in
> one command.

---

## Table of contents

- [Why AgentOS](#why-agentos)
- [What you get](#what-you-get)
- [Architecture: kernel vs. adapters](#architecture-kernel-vs-adapters)
- [Install](#install)
- [Supported runtimes](#supported-runtimes)
- [How per-turn enforcement works](#how-per-turn-enforcement-works)
- [The review gates](#the-review-gates)
- [Workflows](#workflows)
- [Memory and ledgers](#memory-and-ledgers)
- [Repository layout](#repository-layout)
- [Configuration](#configuration)
- [Verifying an install](#verifying-an-install)
- [FAQ](#faq)
- [Design principles](#design-principles)
- [Contributing](#contributing)
- [License](#license)

---

## Why AgentOS

Modern AI coding agents are steered by natural-language rule files (`AGENTS.md`,
`CLAUDE.md`, system prompts). Those files are **advisory**: the agent can read
"always verify before claiming done" and then claim done anyway, and nothing catches
it. As sessions get long, agents drift off the user's actual goal, agree too eagerly
with a flawed framing (sycophancy), promote a passing test into "the task is complete,"
and lose the thread across context compaction.

AgentOS treats agent reliability as an **operating-system problem**, not a prompting
problem:

- **A kernel** (`agent-os/`) holds the canonical rules once.
- **Adapters** project the kernel into each runtime so you don't maintain four copies.
- **Hooks** convert the highest-value invariants from prose into mechanism — a turn
  cannot finish until its audit entry exists and is well-formed.
- **Gates** give the agent an explicit checklist to route through before load-bearing
  claims (completion, causation, recommendation).

The result is a portable discipline layer you drop into any repository, so the way your
agents work stays consistent across projects and across models.

## What you get

| Capability | What it does | Enforcement |
|---|---|---|
| **Per-turn audit trail** | Every turn appends a structured entry to `agent-os/state/audit-log.md` and ends with a visible audit block | **Hook-enforced** (blocks at Stop) on Claude Code and Codex |
| **Kernel linter** | `aos-lint.py` proves the kernel's structure — required files, sections, no scaffolding residue | **Hook-enforced** (auto-runs after kernel edits) |
| **Enforcement-layer guard** | Edits to hooks/settings ask for approval; the script-owned metrics log can't be hand-edited | **Hook-enforced** (PreToolUse) |
| **Anti-sycophancy gate** | Steps outside the asker's framing on judgment/decision questions | Prompt-layer (routed by rules card) |
| **Minimal-code gate** | Reuse-before-generate ladder before writing code or adding a dependency | Prompt-layer |
| **Evidence-to-claim gate** | No "complete / proven / root cause" without matching evidence | Prompt-layer |
| **Reasoning & causality gate** | Derive backward from the target; re-verify borrowed conclusions | Prompt-layer |
| **Intent-contract gate** | Separate the user's goal from candidate means; pin a task contract | Prompt-layer |
| **Route-keeper / promotion gate** | Keep the active user object visible; don't let a support artifact replace the task | Prompt-layer |
| **Prompt-craft gate** | Structure every prompt you send to another model/agent (XML sections, materials-first, self-check) | Prompt-layer |
| **Workflows** | Non-small task lifecycle, a recoverable multi-worker dynamic workflow, and a blind multi-model fusion workflow | Prompt-layer |
| **Memory + ledgers** | A `wiki/` knowledge base plus `PLANS` / `PROGRESS` / `DECISIONS` / `HANDOFF` ledgers with routing rules | Prompt-layer |

> **Honest scope.** The hooks enforce the **existence, format, and numbering** of the
> audit trail and the **structure** of the kernel — not the truthfulness or quality of
> what the agent writes. AgentOS makes discipline mechanical where a mechanism is
> possible, and explicit (routed by the rules card) everywhere else. `aos-lint` proves
> structure only; it does not prove behavioral success.

## Architecture: kernel vs. adapters

AgentOS separates the **canonical rules** from the **runtime plumbing** that activates
them. You edit rules in one place; adapters carry them into each agent runtime.

```
your-project/
├── agent-os/                 ← THE KERNEL (canonical, runtime-agnostic)
│   ├── boot.md · router.md         entry + routing
│   ├── review/                     the gates (task-contract, anti-sycophancy, …)
│   ├── workflows/                  lifecycle, dynamic-workflow, fusion
│   ├── memory/                     routing, wiki-v2, error-learning, bootstrap
│   ├── adapters/                   runtime-visibility, skill-parity
│   ├── state/                      audit-log, current  (live, per-turn)
│   └── tools/aos-lint.py           structural linter
│
├── AGENTS.md                 ← adapter: Codex / generic entry point
├── CLAUDE.md                 ← adapter: Claude Code entry point
├── .claude/                  ← adapter: rules card, hooks, skill wrappers, settings
├── .codex/                   ← adapter: rules card, hooks, config
├── .agents/skills/           ← adapter: portable skill wrappers
│
├── PLANS.md · PROGRESS.md · DECISIONS.md · HANDOFF.md   ← ledgers (durable memory)
└── wiki/                     ← project knowledge base
```

**Golden rule:** `agent-os/` is the kernel; everything else points back to it and never
copies rule bodies into a competing kernel. Change a rule once, and every runtime sees
the change.

## Install

AgentOS ships as a self-contained installer skill — **no dependencies, Python 3 only.**

```bash
# 1. Get the installer (clone anywhere, or add it as an agent skill)
git clone https://github.com/zuoxu3310/AGENTOS.git

# 2. Install the kernel into your project
python3 AGENTOS/scripts/install-agentos.py /path/to/your/project

# 3. Validate the install
python3 AGENTOS/scripts/validate-agentos-install.py /path/to/your/project
python3 /path/to/your/project/agent-os/tools/aos-lint.py
```

The installer is **non-destructive by design**:

- `CLAUDE.md` and the four root ledgers **merge** by appending a marked AgentOS block —
  your existing content is preserved.
- `AGENTS.md` is a kernel projection: reinstalling syncs it and backs up the previous
  copy under `.agentos-backups/`.
- Live state under `agent-os/state/` and your `wiki/` are **seeded only on first
  install** and never reset by a reinstall — your audit log and knowledge base survive
  upgrades.
- Nothing is installed globally; no dependencies are added.

If you use Claude Code or Codex, the enforcement hooks activate on the **next session**
in that project (the first session may ask you to approve the new project hooks).

## Supported runtimes

| Runtime | Entry adapter | Enforcement |
|---|---|---|
| **Claude Code** | `CLAUDE.md` + `.claude/rules/agentos-local-rules.md` | Hooks wired via `.claude/settings.json` (SessionStart, UserPromptSubmit, Stop, PreToolUse, PostToolUse) |
| **OpenAI Codex** | `AGENTS.md` + `.codex/agentos-local-rules.md` | Hooks wired via `.codex/hooks.json` when the project `.codex/` layer is trusted |
| **Other `AGENTS.md`-aware agents** | `AGENTS.md` + `.agents/skills/` | Report-based (the rules card and gates apply; hook enforcement is runtime-specific) |

The gate and workflow library is identical across runtimes; only the activation plumbing
differs.

## How per-turn enforcement works

The core invariant: **no turn is complete without an audit entry.** Here is the loop on
a hook-enabled runtime:

1. **SessionStart** injects the static rules card plus dynamic state (the next audit
   number, the current active object).
2. **UserPromptSubmit** records the audit baseline for the turn.
3. The agent does the work and appends an entry to `agent-os/state/audit-log.md`:
   ```
   ## <n> (<sid>) — <one-line label>
   - object:
   - contract:
   - action+evidence:
   - status:
   - gates:
   - intent:
   ```
4. **Stop** verifies THIS session appended a well-formed entry: six fields present,
   the gates line disposes every review gate, the intent line quotes the user's own
   words verbatim (checked as a substring of the turn-opening message group), and
   long replies carry a zero-context restate line. Concurrent sessions share the log
   via the `(<sid>)` session tag — cross-session number collisions are legal; only a
   session's own numbers must increase, and the log is append-only. If not, it **blocks** and feeds the failure back to the agent (up to a
   bounded number of retries, then it fails open and records a `missed` row so the miss
   is measurable instead of silent).
5. **PostToolUse** re-runs `aos-lint` after any kernel edit; a structural failure is fed
   straight back.

Every hook is **fail-open**: a broken hook degrades to a no-op and never bricks a
session.

## The review gates

Gates are routed by the resident rules card. Each is a short decision procedure the
agent runs *before* a specific class of action:

- **intent-contract** — before non-small work: pin the active object, deliverable,
  boundaries, forbidden substitutions, evidence standard.
- **anti-sycophancy** — before judgment/decision/confirmation questions: step outside
  the asker's framing and give an un-anchored take.
- **minimal-code** — before writing code or adding a dependency: reuse before you
  generate.
- **reasoning-causality** — before guarantee / root-cause / "why" / selection claims:
  derive backward from the target.
- **evidence-to-claim** — before completion, causal, or recommendation wording: match
  the strength of the claim to the strength of the evidence.
- **route-keeper / promotion** — throughout: keep the user's real goal in view; don't
  let a passing test or a subagent report get promoted into "done."
- **prompt-craft** — before dispatching any prompt to another model or agent: structure
  it (XML sections, materials on top / question last, quote grounding, self-check).

## Workflows

- **Agent execution lifecycle** — the path non-small tasks follow: intake → reasoning
  base → intent gate → task contract → execution plan → route checkpoints →
  verification → evidence-to-claim gate → per-turn audit → final response → handoff.
- **Dynamic workflow** — a script-owned, multi-worker, recoverable workflow with a
  state board, worker monitor/reaper, and promotion-gated synthesis, for work that needs
  parallel agents with auditable visibility.
- **Fusion workflow** *(manual-only)* — fan one question out to a blind panel of models,
  judge the answers with an independent cold-start judge, and deliver one fused answer
  with full provenance. It only runs when you explicitly invoke it.

## Memory and ledgers

AgentOS keeps durable knowledge out of the chat and in versioned files:

- **Root ledgers** — `PLANS.md`, `PROGRESS.md`, `DECISIONS.md`, `HANDOFF.md` hold
  durable plans, verified progress, decisions with reasons, and the current
  active-object / route / next-safe-action handoff.
- **`wiki/`** — an Open-Knowledge-Format-style knowledge base (`knowledge/`, `docs/`,
  `errors/`, `raw/`, `CHATS/`, `TASKS/`) with YAML frontmatter carrying confidence and
  supersession, plus routing rules that decide where each kind of fact belongs.

## Repository layout

```
AGENTOS/                              this repo
├── SKILL.md                          the installer skill manifest
├── scripts/
│   ├── install-agentos.py            deterministic, non-destructive installer
│   └── validate-agentos-install.py   structural smoke validator
├── assets/agentos-template/          the full kernel that gets installed
├── docs/                             architecture & quickstart
├── .github/workflows/ci.yml          install → lint → validate → E2E on every push
├── LICENSE · NOTICE                  Apache-2.0
├── CITATION.cff                      how to cite AgentOS
└── llms.txt                          machine-readable summary for AI crawlers
```

## Configuration

AgentOS ships **persona-neutral**. Two policy slots are yours to set per project; they
live in the entry adapters and the rules cards:

- **Owner tag** *(optional)* — an identity string to prefix every answer with. Unset by
  default. Configure it in `AGENTS.md` and `.codex/agentos-local-rules.md` (the line
  "Start every user-facing answer with …").
- **Output language** — the single language for user-facing output. Set it in the
  "Language and reader policy" block of `AGENTS.md`, `.claude/rules/agentos-local-rules.md`,
  and `.codex/agentos-local-rules.md`.

Everything else — the gates, the audit invariant, the workflows — is general-purpose and
needs no configuration.

To temporarily disable the hooks (for debugging), set `AOS_HOOK_DISABLE=1` in the
environment; hooks degrade to no-ops.

## Verifying an install

```bash
# structure of the kernel
python3 agent-os/tools/aos-lint.py

# files, directories, and hook wiring of an installed project
python3 /path/to/AGENTOS/scripts/validate-agentos-install.py .

# end-to-end: runs the real Codex SessionStart hook and gate checks
node work/e2e-pressure-tests/agentos-e2e-pressure-test.mjs
```

The same three checks run in CI on every push (`.github/workflows/ci.yml`).

## FAQ

**What is AgentOS?**
A repo-local operating system for AI coding agents. It installs a canonical `agent-os/`
kernel of rules, review gates, workflows, and memory, plus runtime adapters that
activate those rules inside Claude Code, OpenAI Codex, and other `AGENTS.md`-aware
agents. Its signature mechanism is a hook-enforced per-turn audit trail.

**How is AgentOS different from `AGENTS.md` or `CLAUDE.md`?**
Those files are instructions an agent *may* follow. AgentOS keeps a single canonical
copy of the rules in `agent-os/`, projects it into every runtime via thin adapters, and
converts the top invariants into **hooks that block a turn until they are satisfied** —
so the discipline is mechanical, not just advisory.

**Is it tied to Anthropic or OpenAI?**
No. The kernel is runtime-agnostic. Claude Code and Codex get full hook enforcement
today; any agent that reads `AGENTS.md` inherits the rules card, gates, and workflows.

**Does it require dependencies or network access?**
No. The installer is Python 3 only, adds nothing globally, installs no packages, and
runs offline.

**Will it overwrite my existing `CLAUDE.md` or ledgers?**
No. It merges into them by appending a marked block, and backs up anything it replaces
under `.agentos-backups/`. Live state and your `wiki/` survive reinstalls.

**Does AgentOS guarantee the agent tells the truth?**
No — and it doesn't claim to. The hooks enforce that an audit trail *exists* and is
*well-formed*, and that the kernel is *structurally* intact. Truthfulness and quality
are what the prompt-layer gates push toward, but they are not mechanically provable.

**Can I use only part of it?**
Yes. The kernel is modular — run only the audit invariant, or add the gates and
workflows incrementally. The gates are routed, not forced, so you adopt them at your own
pace.

## Design principles

1. **One kernel, many adapters** — never maintain the same rule in four places.
2. **Mechanize what you can, make the rest explicit** — hooks for provable invariants;
   routed gates for judgment.
3. **Evidence before claims** — completion, causation, and root-cause wording must match
   the evidence.
4. **Fail open** — enforcement must never brick a working session.
5. **Non-destructive** — never silently discard user state; back up and merge.
6. **Honest scope** — say what is proven (structure, format) and what is not (behavior,
   truth).

## Contributing

Issues and pull requests are welcome. Please run the three verification checks above
before opening a PR; CI runs them automatically. See [CONTRIBUTING.md](./CONTRIBUTING.md).

## License

[Apache-2.0](./LICENSE). If you use AgentOS in research or a product, see
[CITATION.cff](./CITATION.cff) for how to cite it.

---

*AgentOS: install one kernel, and your AI coding agents work the same disciplined way in
every repo — with an audit trail that a hook, not a hope, keeps honest.*
