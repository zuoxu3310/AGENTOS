#!/usr/bin/env python3
"""Validate that an AgentOS scaffold was installed structurally."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path


REQUIRED_FILES = [
    "AGENTS.md",
    "CLAUDE.md",
    "PLANS.md",
    "PROGRESS.md",
    "DECISIONS.md",
    "HANDOFF.md",
    "agent-os/boot.md",
    "agent-os/router.md",
    "agent-os/review/reasoning-base.md",
    "agent-os/review/intent-causal-gate.md",
    "agent-os/review/task-contract.md",
    "agent-os/review/route-keeper-promotion-gate.md",
    "agent-os/review/evidence-to-claim-gate.md",
    "agent-os/review/completion-gate.md",
    "agent-os/review/per-turn-audit-gate.md",
    "agent-os/review/anti-sycophancy-gate.md",
    "agent-os/review/minimal-code-gate.md",
    "agent-os/review/prompt-craft-gate.md",
    "agent-os/workflows/fusion-workflow.md",
    ".claude/skills/prompt-craft-review/SKILL.md",
    ".agents/skills/prompt-craft-review/SKILL.md",
    ".agents/skills/prompt-craft-review/agents/openai.yaml",
    ".claude/skills/fusion-workflow/SKILL.md",
    ".claude/skills/fusion-workflow/scripts/run_gemini_cli.sh",
    ".claude/skills/fusion-workflow/scripts/run_codex_sandboxed.sh",
    ".claude/skills/fusion-workflow/references/panelist-prompt-template.md",
    ".claude/skills/fusion-workflow/references/judge-prompt-template.md",
    ".agents/skills/fusion-workflow/SKILL.md",
    ".agents/skills/fusion-workflow/agents/openai.yaml",
    "agent-os/state/audit-log.md",
    "agent-os/workflows/agent-execution-lifecycle.md",
    "agent-os/workflows/dynamic-workflow.md",
    "agent-os/memory/bootstrap.md",
    "agent-os/memory/routing.md",
    "agent-os/memory/wiki-v2.md",
    "agent-os/adapters/runtime-visibility.md",
    "agent-os/adapters/skill-parity.md",
    "agent-os/tools/aos-lint.py",
    ".claude/settings.json",
    ".codex/config.toml",
    ".codex/hooks.json",
    ".codex/agentos-local-rules.md",
    ".codex/hooks/aos_common.py",
    ".codex/hooks/aos_session_start.py",
    ".codex/hooks/aos_prompt_baseline.py",
    ".codex/hooks/aos_stop_gate.py",
    ".codex/hooks/aos_kernel_lint.py",
    ".codex/hooks/aos_guard_enforcer.py",
    ".claude/hooks/aos_common.py",
    ".claude/hooks/aos_session_start.py",
    ".claude/hooks/aos_prompt_baseline.py",
    ".claude/hooks/aos_stop_gate.py",
    ".claude/hooks/aos_kernel_lint.py",
    ".claude/hooks/aos_guard_enforcer.py",
    ".claude/rules/agentos-local-rules.md",
    ".agents/skills/dynamic-workflow/SKILL.md",
    ".agents/skills/dynamic-workflow/agents/openai.yaml",
    ".agents/skills/evidence-claim-review/SKILL.md",
    ".agents/skills/evidence-claim-review/agents/openai.yaml",
    ".agents/skills/intent-contract-review/SKILL.md",
    ".agents/skills/intent-contract-review/agents/openai.yaml",
    ".agents/skills/lifecycle-execution/SKILL.md",
    ".agents/skills/lifecycle-execution/agents/openai.yaml",
    ".agents/skills/memory-wiki-routing/SKILL.md",
    ".agents/skills/memory-wiki-routing/agents/openai.yaml",
    ".agents/skills/reasoning-causality-review/SKILL.md",
    ".agents/skills/reasoning-causality-review/agents/openai.yaml",
    ".agents/skills/route-promotion-review/SKILL.md",
    ".agents/skills/route-promotion-review/agents/openai.yaml",
    ".agents/skills/anti-sycophancy-review/SKILL.md",
    ".agents/skills/anti-sycophancy-review/agents/openai.yaml",
    ".agents/skills/minimal-code-review/SKILL.md",
    ".agents/skills/minimal-code-review/agents/openai.yaml",
    ".claude/skills/dynamic-workflow/SKILL.md",
    ".claude/skills/evidence-claim-review/SKILL.md",
    ".claude/skills/intent-contract-review/SKILL.md",
    ".claude/skills/lifecycle-execution/SKILL.md",
    ".claude/skills/memory-wiki-routing/SKILL.md",
    ".claude/skills/reasoning-causality-review/SKILL.md",
    ".claude/skills/route-promotion-review/SKILL.md",
    ".claude/skills/anti-sycophancy-review/SKILL.md",
    ".claude/skills/minimal-code-review/SKILL.md",
    "wiki/index.md",
    "wiki/log.md",
    "wiki/CHATS/README.md",
    "wiki/TASKS/README.md",
    "wiki/knowledge/agentos-wiki-v2-method.md",
    "wiki/ledgers/README.md",
    "wiki/raw/MANIFEST.md",
    "outputs/reasoning-base-v1-templates-2026-07-01.md",
    "outputs/agent-os-kernel-placement-map-v1-2026-07-01.md",
    "work/e2e-pressure-tests/agentos-e2e-pressure-test.mjs",
]

REQUIRED_DIRS = [
    "agent-os",
    ".agents/skills",
    ".claude/skills",
    ".codex/hooks",
    "wiki/CHATS",
    "wiki/TASKS",
    "wiki/docs",
    "wiki/errors",
    "wiki/knowledge",
    "wiki/ledgers",
    "wiki/raw",
    "work/e2e-pressure-tests",
]


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate an installed AgentOS scaffold.")
    parser.add_argument("target", nargs="?", default=".", help="Target project directory. Defaults to current directory.")
    args = parser.parse_args()
    target = Path(args.target).expanduser().resolve()

    missing_files = [p for p in REQUIRED_FILES if not (target / p).is_file()]
    missing_dirs = [p for p in REQUIRED_DIRS if not (target / p).is_dir()]
    unexpected_runs = [str(p.relative_to(target)) for p in (target / "work").glob("**/runs") if p.is_dir()]

    settings_path = target / ".claude" / "settings.json"
    if not settings_path.is_file():
        hook_wiring = "settings-json-missing"
    else:
        try:
            settings = json.loads(settings_path.read_text(encoding="utf-8"))
            stop_hooks = json.dumps(settings.get("hooks", {}).get("Stop", []))
            hook_wiring = "wired" if "aos_stop_gate.py" in stop_hooks else "stop-hook-not-wired"
        except Exception:
            hook_wiring = "settings-json-invalid"

    codex_hooks_path = target / ".codex" / "hooks.json"
    if not codex_hooks_path.is_file():
        codex_hook_wiring = "hooks-json-missing"
    else:
        try:
            codex_hooks = json.loads(codex_hooks_path.read_text(encoding="utf-8"))
            stop_hooks = json.dumps(codex_hooks.get("hooks", {}).get("Stop", []))
            codex_hook_wiring = "wired" if "aos_stop_gate.py" in stop_hooks else "stop-hook-not-wired"
        except Exception:
            codex_hook_wiring = "hooks-json-invalid"

    result = {
        "status": "passed" if not missing_files and not missing_dirs and hook_wiring == "wired" and codex_hook_wiring == "wired" else "failed",
        "target": str(target),
        "missing_files": missing_files,
        "missing_dirs": missing_dirs,
        "hook_wiring": hook_wiring,
        "codex_hook_wiring": codex_hook_wiring,
        "warnings": {
            "unexpected_historical_runs": unexpected_runs,
        },
    }
    print(json.dumps(result, indent=2, ensure_ascii=False))
    return 0 if result["status"] == "passed" else 1


if __name__ == "__main__":
    raise SystemExit(main())
