# Handoff

## Current Snapshot

- Status: current
- Goal: AgentOS is opt-in — ordinary chat by default; the user invokes the `agentos` skill. Codex: the thread becomes the relay (太监) carrying exact words to `中书省｜<task>` and back. Claude: the session itself becomes 中书 (records the words, spawns 门下/尚书/executor/御史 as subagents, talks with the user, delivers once). Same kernel, transport-specific skills.
- Branch: `pristine-reset-20260812`; working tree uncommitted.
- Delivered 2026-08-18 (this snapshot): Claude 中书-main model (skill rewrite, `agentos-zhongshu.md` retired, hooks/session-start/prompt-baseline updated); shared gate hardening after the Cognition_AGENTOS lock-up — spawn-metadata identity fallback, seat-spawn normalization, sleep-poll denial, named exits, ledger-file guard, newline-safe verbatim parsing, frozen tasks on pause/stop, empty-invocation refusal; capabilities C09 rewritten + C10; tests 127 green; lint PASS. See DECISIONS 2026-08-18.
- Delivered 2026-08-17: relay skill in both skill roots; neutral `.codex/config.toml` / `AGENTS.md` / `CLAUDE.md` entry text; rules card 18–19; zhongshu workflow; adapters, router, lint lists, capabilities C09, scenario tests; hook binding/silence rules; installer template sync; redistribution to the global installers and the 12 projects; GitHub release repo updated (baf6e8c, cd34809).
- Verification target: `aos-lint.py` PASS; `pytest tests` green; installer behavior suite; then the user's live run on each runtime as in Next actions.
- Previous milestone (still true): Desktop-native `codex_app` seat threads, hook-owned seat registry, role-skill hash receipts, executor-owned results; RussianFlow live chain `agentos-runtime-audit` completed with five visible seats; fixes synced to template and all 12 projects.
- Next actions: sync installer template + global installer copies + 12 projects + release repo/GitHub with the 2026-08-18 change; then the user's live acceptance on Claude (`/agentos <real task>` from a plain session: 中书 answers directly, 门下/尚书/执行体 subagents carry the same title/id, executor's own `execution_result` lands, one delivery, session back to chat) and a Codex regression run.
- Boundaries: the gate never denies reads and keeps terminal/pause/stop records writable; the bypass is judged by 门下 and only quote-verified by the hook; unbound sessions are not gated by design.

## Historical Snapshot — AgentOS 2.0 rollout

- Status: historical; retained for evidence and recovery.
- Goal: AgentOS is opt-in — ordinary chat by default; the user invokes the `agentos` skill. Codex: the thread becomes the relay (太监) carrying exact words to `中书省｜<task>` and back. Claude: the session itself becomes 中书 (records the words, spawns 门下/尚书/executor/御史 as subagents, talks with the user, delivers once). Same kernel, transport-specific skills.
- Branch: `codex/agentos-control-loop-rebuild`.
- Recovery point: Git commit `cccf504` preserves the exact tracked state before the old engine was removed.
- Released: the pure repository at `/Users/zuoxu/Downloads/agentos-oss-release` was pushed to `https://github.com/zuoxu3310/AGENTOS`; release commits `21721be` and `473b6f4` both passed GitHub Actions.
- Distributed: the `.agents`, `.claude`, and `.codex` global installer copies match the release bundle. Eleven active projects under `Downloads` were updated; backup-only directories were not treated as projects.
- Preserved: installer manifests report safe Wiki/state preservation. Existing Wiki files were byte-checked; only the four ledger symlinks reflect the intentionally merged root ledgers. Retired pseudo rules, referee files, audit gate, spokesperson contract, and Claude Dynamic Workflow adapter were backed up and removed.
- Verified: all 11 projects pass the structural validator. A real Codex PostToolUse payload for `agent-os/boot.md` returns silently in every project despite unrelated legacy Wiki failures, while an invalid edited ledger still returns its relevant failures.
- Next action: none for this rollout. Project-by-project Wiki/document migration is separate semantic work and must not be auto-applied.
- Boundaries: full `aos-lint.py` still reports each project's pre-existing document-format debt. Hook scripts changed, so a fresh runtime session may request trust again before activation can be claimed.
