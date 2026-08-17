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


# The canonical presence list is parsed from the TARGET's own aos-lint.py so
# the validator can never drift from the product's single source of truth.
FALLBACK_CORE_FILES = [
    "AGENTS.md",
    "CLAUDE.md",
    "agent-os/rules-card.md",
    "agent-os/router.md",
    "agent-os/architecture.md",
    "agent-os/artifact-contracts.toml",
    "agent-os/tools/aos-lint.py",
]

EXTRA_REQUIRED_FILES = [
    ".codex/agents/agentos-zhongshu.toml",
    ".claude/agents/agentos-zhongshu.md",
    ".claude/skills/agentos/SKILL.md",
    ".agents/skills/agentos/SKILL.md",
    ".codex/agents/agentos-menxia.toml",
    ".codex/agents/agentos-shangshu.toml",
    ".codex/agents/agentos-executor.toml",
    ".codex/agents/agentos-yushi.toml",
    ".codex/hooks/aos_chain_gate.py",
    ".claude/hooks/aos_chain_gate.py",
    "agent-os/skills/seat-skills.json",
    "agent-os/tools/aos_skill_receipt.py",
    "tests/unit/test_skill_receipt.py",
    ".claude/skills/fusion-workflow/scripts/run_gemini_cli.sh",
    ".claude/skills/fusion-workflow/scripts/run_codex_sandboxed.sh",
    ".claude/skills/fusion-workflow/references/panelist-prompt-template.md",
    ".claude/skills/fusion-workflow/references/judge-prompt-template.md",
]


# Third-party add-ons vendored as their own git checkouts (git-ignored in the
# published template). Missing copies are reported, never a failure.
OPTIONAL_VENDOR_FILES = [
    "vendor/fusion-fable/skills/fusion/SKILL.md",
    "vendor/AgentChat/skills/AgentChat-FreeSubAgent/SKILL.md",
]


def target_lint_required_files(target: Path) -> list[str]:
    try:
        lint_text = (target / "agent-os/tools/aos-lint.py").read_text(encoding="utf-8")
        begin = lint_text.index("REQUIRED_FILES = [")
        finish = lint_text.index("]", begin)
        return re.findall(r'"([^"]+)"', lint_text[begin:finish])
    except Exception:
        return []

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
        gate = [c for c in agentos_stop if "aos_stop_gate.py" in c]
        known_extra = [c for c in agentos_stop if "aos_chain_gate.py" in c]
        valid = len(gate) == 1 and len(gate) + len(known_extra) == len(agentos_stop)
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


def role_skill_report(target: Path) -> dict:
    try:
        manifest = json.loads((target / "agent-os/skills/seat-skills.json").read_text(encoding="utf-8"))
        roles = ("zhongshu", "menxia", "shangshu", "executor", "yushi")
        configured = all(isinstance(manifest.get(role), list) and manifest[role] for role in roles)
        receipt = (target / "agent-os/tools/aos_skill_receipt.py").read_text(encoding="utf-8")
        hook = (target / ".codex/hooks/aos_chain_gate.py").read_text(encoding="utf-8")
        valid = configured and "sha256" in receipt and "valid_skill_receipt" in hook
        return {"status": "enforced" if valid else "role-skill-contract-incomplete",
                "roles": {role: manifest.get(role, []) for role in roles}}
    except Exception as exc:
        return {"status": "role-skill-contract-incomplete", "error": str(exc)}


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

    required_files = target_lint_required_files(target) or FALLBACK_CORE_FILES
    required_files = list(dict.fromkeys([*required_files, *EXTRA_REQUIRED_FILES]))
    missing_files = [p for p in required_files if not (target / p).is_file()]
    missing_optional_vendor = [p for p in OPTIONAL_VENDOR_FILES if not (target / p).is_file()]
    missing_dirs = [p for p in REQUIRED_DIRS if not (target / p).is_dir()]
    unexpected_runs = [str(p.relative_to(target)) for p in (target / "work").glob("**/runs") if p.is_dir()]

    claude_hooks = hook_config_report(target / ".claude" / "settings.json")
    codex_hooks = hook_config_report(target / ".codex" / "hooks.json")
    codex_toml = codex_toml_report(target / ".codex" / "config.toml")
    task_state_tests = task_state_test_report(target)
    attention_hooks = attention_hook_report(target)
    resident_rules = resident_rules_report(target)
    role_skills = role_skill_report(target)
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
        and role_skills["status"] == "enforced"
        and preservation["status"] in {"safe", "manifest-not-found"}
    )

    result = {
        "status": "passed" if passed else "failed",
        "target": str(target),
        "missing_files": missing_files,
        "missing_optional_vendor": missing_optional_vendor,
        "missing_dirs": missing_dirs,
        "claude_hook_wiring": claude_hooks,
        "codex_hook_wiring": codex_hooks,
        "codex_toml": codex_toml,
        "task_state_tests": task_state_tests,
        "attention_hooks": attention_hooks,
        "resident_rules": resident_rules,
        "role_skills": role_skills,
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
