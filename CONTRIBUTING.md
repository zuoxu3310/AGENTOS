# Contributing to AgentOS

Thanks for your interest in improving AgentOS. This project values small, verifiable
changes and honest scope.

## Ground rules

- **The kernel is `agent-os/`.** Rules live there once. `AGENTS.md`, `CLAUDE.md`,
  `.claude/`, `.codex/`, and `.agents/` are adapters — they point back to the kernel and
  must not copy rule bodies into a competing kernel.
- **Keep it dependency-free.** The installer and hooks are Python 3 standard library
  only; the pressure test is Node standard library only. Do not add third-party
  dependencies.
- **Non-destructive.** Anything that touches a user's project must merge or back up, never
  silently overwrite.
- **Honest scope.** Enforce mechanically what can be proven (existence, format,
  structure); route the rest as gates. Do not describe a routed gate as a hard guarantee.

## Before you open a PR

Run the three verification checks and make sure they pass:

```bash
# 1. Kernel structure
python3 assets/agentos-template/agent-os/tools/aos-lint.py

# 2. Install into a scratch dir, then validate it
python3 scripts/install-agentos.py /tmp/aos-contrib-check
python3 scripts/validate-agentos-install.py /tmp/aos-contrib-check

# 3. End-to-end (runs the real Codex SessionStart hook + gate checks)
( cd /tmp/aos-contrib-check && node work/e2e-pressure-tests/agentos-e2e-pressure-test.mjs )
```

CI runs the same checks on every push and pull request.

## If you edit the kernel

- `aos-lint.py` asserts required files, directories, and section patterns. If you rename
  a file or a section, update `aos-lint.py`'s `REQUIRED_FILES` / `PATTERNS` in the same
  change, or lint will fail.
- Some invariants are asserted in more than one place (for example, the greeting-rule
  text is checked by both `aos-lint.py` and the E2E pressure test). Move coupled
  assertions together.
- After editing any `agent-os/**` file, re-run `aos-lint.py`.

## Reporting issues

Open a GitHub issue describing what you expected, what happened, and the runtime (Claude
Code / Codex / other) and OS you were on. For anything security-sensitive, see
[SECURITY.md](./SECURITY.md).
