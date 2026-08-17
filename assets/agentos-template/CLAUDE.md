# Claude Code Adapter

<!-- BEGIN AGENTOS ENTRY CONTRACT -->
## 开机简报 — Claude Session Briefing

AgentOS is installed here; ordinary chat is the default. The three-departments
chain runs only when the user explicitly invokes the `agentos` skill
(`/agentos`, "三省六部", "走链"); until then no seat, no ledger, no hook applies.
Resident rules load via `.claude/rules/agentos-local-rules.md`.

What exists:
- Kernel: `agent-os/` — seat methods in `agent-os/workflows/*.md`; route by
  `agent-os/router.md`.
- Seats: relay (the invoking session, `.claude/skills/agentos/SKILL.md` — a
  courier that carries the user's exact words and never thinks in their place)
  · 中书 `agentos-zhongshu` (spawned by the relay as `中书省｜<task>`; understanding
  + the one final delivery) · 门下 `agentos-menxia` · 尚书 `agentos-shangshu` ·
  one-shot `agentos-executor` (spawned by 尚书 only) · 御史 `agentos-yushi`
  (background). The roster is CLOSED — invent no roles.
- Instruments: Claude uses native Workflow and keeps Superpowers enabled,
  both serving inside the chain; the Codex adapter is never loaded here.
  `.claude/skills/` holds thin method shells; hooks restore attention, lint
  documents, and the chain gate (`.claude/hooks/aos_chain_gate.py`) is silent
  for unbound sessions and enforces the seat order mechanically once bound —
  its deny reason is the next legal step.

Once invoked, in this order:
1. Relay records the user's exact words (`aos_task_record.py create` /
   `append --role relay`) and spawns 中书 with them, nothing more.
2. 中书 spawns 门下 with the RAW increment; the goal is fixed only by comparison.
3. 中书 hands 尚书 the approved package once; it executes through one-shot
   executors and returns one integrated result.
4. 中书 verifies against `done_when`, delivers ONE reply, records it; the relay
   returns it verbatim; confirmed mistakes go to 御史 in the background.

The user's explicit instruction outranks everything, including the hooks —
only 门下 records the bypass, quoting the user's exact words.
<!-- END AGENTOS ENTRY CONTRACT -->

<!-- gitnexus:start -->
# GitNexus — Code Intelligence

This project is indexed by GitNexus as **AGENTOS** (3298 symbols, 4948 relationships, 51 execution flows). Use the GitNexus MCP tools to understand code, assess impact, and navigate safely.

> If any GitNexus tool warns the index is stale, run `npx gitnexus analyze` in terminal first.

## Always Do

- **MUST run impact analysis before editing any symbol.** Before modifying a function, class, or method, run `gitnexus_impact({target: "symbolName", direction: "upstream"})` and report the blast radius (direct callers, affected processes, risk level) to the user.
- **MUST run `gitnexus_detect_changes()` before committing** to verify your changes only affect expected symbols and execution flows.
- **MUST warn the user** if impact analysis returns HIGH or CRITICAL risk before proceeding with edits.
- When exploring unfamiliar code, use `gitnexus_query({query: "concept"})` to find execution flows instead of grepping. It returns process-grouped results ranked by relevance.
- When you need full context on a specific symbol — callers, callees, which execution flows it participates in — use `gitnexus_context({name: "symbolName"})`.

## Never Do

- NEVER edit a function, class, or method without first running `gitnexus_impact` on it.
- NEVER ignore HIGH or CRITICAL risk warnings from impact analysis.
- NEVER rename symbols with find-and-replace — use `gitnexus_rename` which understands the call graph.
- NEVER commit changes without running `gitnexus_detect_changes()` to check affected scope.

## Resources

| Resource | Use for |
|----------|---------|
| `gitnexus://repo/AGENTOS/context` | Codebase overview, check index freshness |
| `gitnexus://repo/AGENTOS/clusters` | All functional areas |
| `gitnexus://repo/AGENTOS/processes` | All execution flows |
| `gitnexus://repo/AGENTOS/process/{name}` | Step-by-step execution trace |

## CLI

| Task | Read this skill file |
|------|---------------------|
| Understand architecture / "How does X work?" | `.claude/skills/gitnexus/gitnexus-exploring/SKILL.md` |
| Blast radius / "What breaks if I change X?" | `.claude/skills/gitnexus/gitnexus-impact-analysis/SKILL.md` |
| Trace bugs / "Why is X failing?" | `.claude/skills/gitnexus/gitnexus-debugging/SKILL.md` |
| Rename / extract / split / refactor | `.claude/skills/gitnexus/gitnexus-refactoring/SKILL.md` |
| Tools, resources, schema reference | `.claude/skills/gitnexus/gitnexus-guide/SKILL.md` |
| Index, status, clean, wiki CLI commands | `.claude/skills/gitnexus/gitnexus-cli/SKILL.md` |

<!-- gitnexus:end -->
