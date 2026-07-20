#!/usr/bin/env python3
"""Validate that an AgentOS scaffold was installed structurally."""

from __future__ import annotations

import argparse
import json
import re
import sys
import tomllib
from pathlib import Path


AGENTOS_HOOK_RE = re.compile(r"\baos_[A-Za-z0-9_-]+\.py\b")


REQUIRED_FILES = [
    "AGENTS.md",
    "CLAUDE.md",
    "PLANS.md",
    "PROGRESS.md",
    "DECISIONS.md",
    "HANDOFF.md",
    "agent-os/boot.md",
    "agent-os/router.md",
    "agent-os/artifact-contracts.toml",
    "agent-os/review/reasoning-base.md",
    "agent-os/review/intent-causal-gate.md",
    "agent-os/review/task-contract.md",
    "agent-os/review/route-keeper-promotion-gate.md",
    "agent-os/review/evidence-to-claim-gate.md",
    "agent-os/review/completion-gate.md",
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
    "agent-os/workflows/agent-execution-lifecycle.md",
    "agent-os/adapters/codex-workflow.md",
    "vendor/claude-dynamic-workflows-codex/runner/bin/run-workflow.js",
    "vendor/claude-dynamic-workflows-codex/runner/src/runtime.js",
    "vendor/claude-dynamic-workflows-codex/references/authoring.md",
    "vendor/claude-dynamic-workflows-codex/LICENSE",
    "vendor/claude-dynamic-workflows-codex.AGENTOS.md",
    "agent-os/memory/bootstrap.md",
    "agent-os/memory/routing.md",
    "agent-os/memory/wiki-v2.md",
    "agent-os/adapters/runtime-visibility.md",
    "agent-os/adapters/skill-parity.md",
    "agent-os/tools/aos-lint.py",
    "agent-os/tools/aos_active_work.py",
    ".claude/settings.json",
    ".codex/config.toml",
    ".codex/hooks.json",
    "agent-os/rules-card.md",
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
    "tests/capabilities.json",
    "tests/unit/test_active_work.py",
    "tests/integration/test_runtime_adapters.py",
    "tests/scenarios/test_instruction_stack_contract.py",
    "tests/scenarios/test_artifact_contracts.py",
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
    "tests/unit",
    "tests/integration",
    "tests/scenarios",
]


def _hook_commands(groups: object) -> list[str]:
    if not isinstance(groups, list):
        raise ValueError("hook-groups-must-be-a-list")
    commands = []
    for group in groups:
        if not isinstance(group, dict) or not isinstance(group.get("hooks", []), list):
            raise ValueError("hook-group-shape-invalid")
        for hook in group.get("hooks", []):
            if not isinstance(hook, dict):
                raise ValueError("hook-shape-invalid")
            command = hook.get("command")
            if isinstance(command, str):
                commands.append(command)
    return commands


def hook_config_report(path: Path) -> dict:
    if not path.is_file():
        return {"status": "missing", "agentos_stop_commands": [], "unrelated_stop_count": 0}
    try:
        document = json.loads(path.read_text(encoding="utf-8"))
        if not isinstance(document, dict) or not isinstance(document.get("hooks", {}), dict):
            raise ValueError("root-or-hooks-shape-invalid")
        stop_commands = _hook_commands(document.get("hooks", {}).get("Stop", []))
        agentos_stop = [command for command in stop_commands if AGENTOS_HOOK_RE.search(command)]
        valid = len(agentos_stop) == 1 and "aos_stop_gate.py" in agentos_stop[0]
        return {
            "status": "wired" if valid else "agentos-stop-handler-count-invalid",
            "agentos_stop_commands": agentos_stop,
            "unrelated_stop_count": len(stop_commands) - len(agentos_stop),
        }
    except Exception as exc:
        return {
            "status": "invalid-json-or-hook-shape",
            "error": str(exc),
            "agentos_stop_commands": [],
            "unrelated_stop_count": 0,
        }


def codex_toml_report(path: Path) -> dict:
    if not path.is_file():
        return {"status": "missing"}
    try:
        document = tomllib.loads(path.read_text(encoding="utf-8"))
        developer = document.get("developer_instructions")
        hooks = document.get("features", {}).get("hooks")
        valid = isinstance(developer, str) and "AgentOS" in developer and hooks is True
        return {
            "status": "wired" if valid else "agentos-values-missing",
            "features_hooks": hooks,
            "developer_instructions_present": isinstance(developer, str) and "AgentOS" in developer,
        }
    except Exception as exc:
        return {"status": "invalid-toml", "error": str(exc)}


def task_state_test_report(target: Path) -> dict:
    required = {
        "unit": "tests/unit/test_active_work.py",
        "integration": "tests/integration/test_runtime_adapters.py",
        "scenarios": "tests/scenarios/test_instruction_stack_contract.py",
    }
    files = {
        layer: relative
        for layer, relative in required.items()
        if (target / relative).is_file()
    }
    return {
        "status": "present" if len(files) == len(required) else "missing-task-state-test-layer",
        "files": files,
    }


def attention_hook_report(target: Path) -> dict:
    runtimes = {}
    required_hooks = (
        "aos_common.py",
        "aos_session_start.py",
        "aos_prompt_baseline.py",
        "aos_stop_gate.py",
    )
    for runtime in (".claude", ".codex"):
        hook_root = target / runtime / "hooks"
        valid = []
        for name in required_hooks:
            path = hook_root / name
            if not path.is_file():
                continue
            text = path.read_text(encoding="utf-8", errors="replace")
            if name == "aos_common.py":
                ok = "aos_active_work" in text
            else:
                ok = "active_work_state" in text
            if ok:
                valid.append(str(path.relative_to(target)))
        runtimes[runtime] = valid
    return {
        "status": "wired" if all(len(paths) == len(required_hooks) for paths in runtimes.values()) else "runtime-attention-hook-missing",
        "files": runtimes,
    }


def resident_rules_report(target: Path) -> dict:
    begin = "<!-- BEGIN AGENTOS RESIDENT RULES -->"
    end = "<!-- END AGENTOS RESIDENT RULES -->"
    try:
        card = (target / "agent-os/rules-card.md").read_text(encoding="utf-8").strip()
        agents = (target / "AGENTS.md").read_text(encoding="utf-8")
        managed = agents.split(begin, 1)[1].split(end, 1)[0].strip()
        claude_projection = target / ".claude/rules/agentos-local-rules.md"
        valid = (
            managed == card
            and claude_projection.resolve() == (target / "agent-os/rules-card.md").resolve()
            and not (target / ".codex/agentos-local-rules.md").exists()
        )
        return {"status": "canonical" if valid else "projection-mismatch"}
    except (FileNotFoundError, IndexError, OSError) as exc:
        return {"status": "projection-mismatch", "error": str(exc)}


def preservation_report(target: Path) -> dict:
    manifest_path = target / ".agentos-install-manifest.json"
    if not manifest_path.is_file():
        return {"status": "manifest-not-found", "preserved": [], "unsafe": []}
    try:
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        actions = manifest.get("actions", [])
        if not isinstance(actions, list):
            raise ValueError("actions-must-be-a-list")
        protected = [
            item for item in actions
            if isinstance(item, dict)
            and (
                str(item.get("path", "")).startswith("agent-os/state/")
                or str(item.get("path", "")).startswith("wiki/")
            )
        ]
        preserved = [
            item.get("path") for item in protected
            if str(item.get("action", "")).startswith("preserved-existing-")
        ]
        unsafe = [
            item for item in protected
            if item.get("action") in {"backed-up-and-replaced", "merged", "agentos-block-updated"}
        ]
        return {
            "status": "safe" if not unsafe else "unsafe-protected-replacement-recorded",
            "preserved": preserved,
            "unsafe": unsafe,
        }
    except Exception as exc:
        return {"status": "invalid-manifest", "error": str(exc), "preserved": [], "unsafe": []}


def validate(target: Path) -> dict:
    target = target.expanduser().resolve()

    missing_files = [p for p in REQUIRED_FILES if not (target / p).is_file()]
    missing_dirs = [p for p in REQUIRED_DIRS if not (target / p).is_dir()]
    unexpected_runs = [str(p.relative_to(target)) for p in (target / "work").glob("**/runs") if p.is_dir()]

    claude_hooks = hook_config_report(target / ".claude" / "settings.json")
    codex_hooks = hook_config_report(target / ".codex" / "hooks.json")
    codex_toml = codex_toml_report(target / ".codex" / "config.toml")
    task_state_tests = task_state_test_report(target)
    attention_hooks = attention_hook_report(target)
    resident_rules = resident_rules_report(target)
    preservation = preservation_report(target)

    passed = (
        not missing_files
        and not missing_dirs
        and claude_hooks["status"] == "wired"
        and codex_hooks["status"] == "wired"
        and codex_toml["status"] == "wired"
        and task_state_tests["status"] == "present"
        and attention_hooks["status"] == "wired"
        and resident_rules["status"] == "canonical"
        and preservation["status"] in {"safe", "manifest-not-found"}
    )

    result = {
        "status": "passed" if passed else "failed",
        "target": str(target),
        "missing_files": missing_files,
        "missing_dirs": missing_dirs,
        "claude_hook_wiring": claude_hooks,
        "codex_hook_wiring": codex_hooks,
        "codex_toml": codex_toml,
        "task_state_tests": task_state_tests,
        "attention_hooks": attention_hooks,
        "resident_rules": resident_rules,
        "state_wiki_preservation": preservation,
        "warnings": {
            "unexpected_historical_runs": unexpected_runs,
        },
    }
    return result


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate an installed AgentOS scaffold.")
    parser.add_argument("target", nargs="?", default=".", help="Target project directory. Defaults to current directory.")
    args = parser.parse_args()
    result = validate(Path(args.target))
    print(json.dumps(result, indent=2, ensure_ascii=False))
    return 0 if result["status"] == "passed" else 1


if __name__ == "__main__":
    raise SystemExit(main())
