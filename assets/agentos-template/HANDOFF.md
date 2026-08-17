# Handoff

## Current Snapshot

- Status: current
- Goal: AgentOS is opt-in — ordinary chat by default; the user invokes the `agentos` skill (`$agentos` / `/agentos`, "三省六部") and that session becomes the relay (太监) that carries exact words to `中书省｜<task>` and back; the chain inside (门下 raw review → compare → 尚书 → executor → integration → 中书 delivery) is unchanged and hook-enforced once a session is bound.
- Branch: `pristine-reset-20260812`; working tree uncommitted.
- Delivered 2026-08-17 (this snapshot): relay skill in both skill roots; 中书 seat prompts (`agentos-zhongshu`) replacing `agentos-entry`; neutral `.codex/config.toml` / `AGENTS.md` / `CLAUDE.md` entry text; rules card 18–19; zhongshu workflow (no create; no verdict hints; contract after pass); adapters, router, lint lists, capabilities C09, scenario tests; DECISIONS entry. Hook binding/silence rules, gate tests, installer template sync, and redistribution to the global installers and the 12 projects are the same-day companion deliveries — check DECISIONS/PROGRESS for their evidence before claiming them.
- Verification target: `aos-lint.py` PASS; `pytest tests` green; then the user's live run on each runtime: a plain session shows no AgentOS output; `$agentos`/`/agentos` on a real task opens `中书省｜<task>`, the exact words reach it, the delivery returns verbatim, the session is ordinary chat afterwards; pause/resume/stop work.
- Previous milestone (still true): Desktop-native `codex_app` seat threads, hook-owned seat registry, role-skill hash receipts, executor-owned results; the pilot project live chain `agentos-runtime-audit` completed with five visible seats; fixes synced to template and all 12 projects.
- Next actions: land hook binding + tests (companion worker), sync template, redistribute, user live acceptance on both runtimes. GitHub release repo NOT updated; AGENTOS working tree NOT committed.
- Boundaries: the gate never denies reads and keeps terminal/pause/stop records writable; the bypass is judged by 门下 and only quote-verified by the hook; unbound sessions are not gated by design.

## Historical Snapshot — AgentOS 2.0 rollout

- Status: historical; retained for evidence and recovery.
- Goal: maintain the released AgentOS 2.0 package and the 11 updated existing projects from one clean distribution source.
- Branch: `codex/agentos-control-loop-rebuild`.
- Recovery point: Git commit `cccf504` preserves the exact tracked state before the old engine was removed.
- Released: the pure repository at the release repository was pushed to `https://github.com/zuoxu3310/AGENTOS`; release commits `21721be` and `473b6f4` both passed GitHub Actions.
- Distributed: the `.agents`, `.claude`, and `.codex` global installer copies match the release bundle. Eleven active projects under `Downloads` were updated; backup-only directories were not treated as projects.
- Preserved: installer manifests report safe Wiki/state preservation. Existing Wiki files were byte-checked; only the four ledger symlinks reflect the intentionally merged root ledgers. Retired pseudo rules, referee files, audit gate, spokesperson contract, and Claude Dynamic Workflow adapter were backed up and removed.
- Verified: all 11 projects pass the structural validator. A real Codex PostToolUse payload for `agent-os/boot.md` returns silently in every project despite unrelated legacy Wiki failures, while an invalid edited ledger still returns its relevant failures.
- Next action: none for this rollout. Project-by-project Wiki/document migration is separate semantic work and must not be auto-applied.
- Boundaries: full `aos-lint.py` still reports each project's pre-existing document-format debt. Hook scripts changed, so a fresh runtime session may request trust again before activation can be claimed.
