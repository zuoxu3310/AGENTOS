#!/usr/bin/env python3
"""Black-box behavior tests for the staged AgentOS installer."""

from __future__ import annotations

import importlib.util
import json
import re
import shutil
import subprocess
import sys
import tempfile
import tomllib
import unittest
from pathlib import Path


CANDIDATE_ROOT = Path(__file__).resolve().parents[1]
INSTALLER_PATH = CANDIDATE_ROOT / "scripts" / "install-agentos.py"
VALIDATOR_PATH = CANDIDATE_ROOT / "scripts" / "validate-agentos-install.py"
TEMPLATE = CANDIDATE_ROOT / "assets" / "agentos-template"
AGENTOS_HOOK_RE = re.compile(r"\baos_[A-Za-z0-9_-]+\.py\b")


def load_script(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Cannot load {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


installer = load_script("staged_agentos_installer", INSTALLER_PATH)
validator = load_script("staged_agentos_validator", VALIDATOR_PATH)


def write_json(path: Path, value: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2) + "\n", encoding="utf-8")


def hook_commands(document: dict, event: str) -> list[str]:
    return [
        hook["command"]
        for group in document.get("hooks", {}).get(event, [])
        for hook in group.get("hooks", [])
        if isinstance(hook.get("command"), str)
    ]


def agentos_stop_commands(document: dict) -> list[str]:
    return [command for command in hook_commands(document, "Stop") if AGENTOS_HOOK_RE.search(command)]


class InstallerBehaviorTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory(prefix="agentos-installer-test-")
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name)

    def test_fresh_install_has_one_agentos_stop_handler_per_runtime(self) -> None:
        target = self.root / "fresh"
        manifest = installer.install(TEMPLATE, target, dry_run=False)

        self.assertEqual("ok", manifest["status"], manifest["failures"])
        claude = json.loads((target / ".claude/settings.json").read_text(encoding="utf-8"))
        codex = json.loads((target / ".codex/hooks.json").read_text(encoding="utf-8"))
        for document in (claude, codex):
            commands = agentos_stop_commands(document)
            self.assertEqual(1, len(commands), commands)
            self.assertIn("aos_stop_gate.py", commands[0])
        config_text = (target / ".codex/config.toml").read_text(encoding="utf-8")
        config = tomllib.loads(config_text)
        self.assertIs(config["features"]["hooks"], True)
        self.assertIn(installer.AGENTOS_DEV_BEGIN, config["developer_instructions"])
        self.assertEqual(1, config_text.count("[features]"))
        self.assertTrue((target / ".agents/skills/dynamic-workflow/SKILL.md").is_file())
        self.assertFalse((target / ".claude/skills/dynamic-workflow/SKILL.md").exists())
        self.assertFalse((target / ".codex/agentos-local-rules.md").exists())
        self.assertTrue((target / "agent-os/artifact-contracts.toml").is_file())
        agents = (target / "AGENTS.md").read_text(encoding="utf-8")
        managed = agents.split(installer.AGENTOS_RULES_BEGIN, 1)[1].split(
            installer.AGENTOS_RULES_END, 1
        )[0].strip()
        self.assertEqual(
            (target / "agent-os/rules-card.md").read_text(encoding="utf-8").strip(),
            managed,
        )
        self.assertTrue((target / "agent-os/adapters/codex-workflow.md").is_file())
        self.assertTrue((target / "vendor/claude-dynamic-workflows-codex/runner/bin/run-workflow.js").is_file())
        self.assertTrue((target / "vendor/claude-dynamic-workflows-codex/LICENSE").is_file())
        self.assertTrue((target / "vendor/claude-dynamic-workflows-codex.AGENTOS.md").is_file())
        workflow = (target / "agent-os/adapters/codex-workflow.md").read_text(encoding="utf-8").lower()
        self.assertIn("one delegated execution engine", workflow)
        self.assertNotIn("optional external runner", workflow)
        self.assertNotIn("spawn_agent", workflow)
        self.assertFalse((target / "agent-os/workflows/dynamic-workflow.md").exists())
        self.assertIn("native Workflow", (target / "CLAUDE.md").read_text(encoding="utf-8"))
        self.assertIn("keeps Superpowers enabled", (target / "CLAUDE.md").read_text(encoding="utf-8"))
        self.assertIn(
            "/agent-os/state/active-work/",
            (target / ".gitignore").read_text(encoding="utf-8"),
        )

    def test_existing_user_json_toml_and_entry_docs_survive_merge(self) -> None:
        target = self.root / "merge"
        target.mkdir()
        (target / "AGENTS.md").write_text("USER ENTRY RULE\n", encoding="utf-8")
        (target / ".gitignore").write_text("USER IGNORE RULE\n", encoding="utf-8")
        ledger_paths = [target / name for name in ("PLANS.md", "PROGRESS.md", "DECISIONS.md", "HANDOFF.md")]
        for path in ledger_paths:
            path.write_text(f"USER {path.stem} LEDGER\n", encoding="utf-8")
        user_wiki = target / "wiki/user-owned-note.md"
        user_wiki.parent.mkdir(parents=True, exist_ok=True)
        user_wiki.write_bytes(b"USER WIKI\x00\xfe")
        user_state = target / "agent-os/state/user-owned-state.md"
        user_state.parent.mkdir(parents=True, exist_ok=True)
        user_state.write_bytes(b"USER STATE\x00\xff")
        user_stop = {"type": "command", "command": "python3 tools/user_stop.py"}
        obsolete_stop = {"type": "command", "command": "python3 .hooks/aos_stop_gate.py --old"}
        obsolete_agentos_stop = {"type": "command", "command": "python3 .hooks/aos_guard_enforcer.py --old-stop"}
        user_pretool = {"type": "command", "command": "python3 tools/user_guard.py"}

        for path in (target / ".claude/settings.json", target / ".codex/hooks.json"):
            write_json(
                path,
                {
                    "userKey": {"keep": True},
                    "hooks": {
                        "Stop": [{"hooks": [user_stop, obsolete_stop, obsolete_agentos_stop]}],
                        "PreToolUse": [{"matcher": "UserTool", "hooks": [user_pretool]}],
                    },
                },
            )
        config_path = target / ".codex/config.toml"
        config_path.parent.mkdir(parents=True, exist_ok=True)
        config_path.write_text(
            'model = "user-model"\n'
            'developer_instructions = "KEEP USER INSTRUCTION" # KEEP DEV COMMENT\n\n'
            '[features]\n'
            'experimental = true\n'
            'hooks = false # KEEP HOOK COMMENT\n\n'
            '[user_table]\n'
            'value = 7\n',
            encoding="utf-8",
        )

        manifest = installer.install(TEMPLATE, target, dry_run=False)
        self.assertEqual("ok", manifest["status"], manifest["failures"])
        self.assertIn("USER ENTRY RULE", (target / "AGENTS.md").read_text(encoding="utf-8"))
        self.assertIn("BEGIN AGENTOS RESIDENT RULES", (target / "AGENTS.md").read_text(encoding="utf-8"))
        self.assertIn("USER IGNORE RULE", (target / ".gitignore").read_text(encoding="utf-8"))
        self.assertIn("BEGIN AGENTOS LOCAL STATE", (target / ".gitignore").read_text(encoding="utf-8"))
        for path in ledger_paths:
            self.assertIn(f"USER {path.stem} LEDGER", path.read_text(encoding="utf-8"))
            self.assertIn("BEGIN AGENTOS LEDGER BOOTSTRAP", path.read_text(encoding="utf-8"))
        self.assertEqual(b"USER WIKI\x00\xfe", user_wiki.read_bytes())
        self.assertEqual(b"USER STATE\x00\xff", user_state.read_bytes())

        for path in (target / ".claude/settings.json", target / ".codex/hooks.json"):
            document = json.loads(path.read_text(encoding="utf-8"))
            self.assertEqual({"keep": True}, document["userKey"])
            self.assertIn("python3 tools/user_stop.py", hook_commands(document, "Stop"))
            self.assertIn("python3 tools/user_guard.py", hook_commands(document, "PreToolUse"))
            agentos_commands = agentos_stop_commands(document)
            self.assertEqual(1, len(agentos_commands), agentos_commands)
            self.assertIn("aos_stop_gate.py", agentos_commands[0])

        config_text = config_path.read_text(encoding="utf-8")
        config = tomllib.loads(config_text)
        self.assertEqual("user-model", config["model"])
        self.assertIn("KEEP USER INSTRUCTION", config["developer_instructions"])
        self.assertIn(installer.AGENTOS_DEV_BEGIN, config["developer_instructions"])
        self.assertIs(config["features"]["experimental"], True)
        self.assertIs(config["features"]["hooks"], True)
        self.assertEqual(7, config["user_table"]["value"])
        self.assertEqual(1, config_text.count("[features]"))
        self.assertIn("# KEEP DEV COMMENT", config_text)
        self.assertIn("# KEEP HOOK COMMENT", config_text)

        stable_files = {
            path: path.read_bytes()
            for path in (
                target / ".claude/settings.json",
                target / ".codex/hooks.json",
                target / ".codex/config.toml",
                target / "AGENTS.md",
                target / ".gitignore",
                *ledger_paths,
                user_wiki,
                user_state,
            )
        }
        reinstalled = installer.install(TEMPLATE, target, dry_run=False)
        self.assertEqual("ok", reinstalled["status"])
        for path, expected in stable_files.items():
            self.assertEqual(expected, path.read_bytes(), f"reinstall changed {path}")
        self.assertEqual(1, config_path.read_text(encoding="utf-8").count("[features]"))
        self.assertEqual(
            1,
            tomllib.loads(config_path.read_text(encoding="utf-8"))["developer_instructions"].count(
                installer.AGENTOS_DEV_BEGIN
            ),
        )

    def test_reinstall_preserves_existing_state_and_wiki_bytes(self) -> None:
        target = self.root / "reinstall"
        first = installer.install(TEMPLATE, target, dry_run=False)
        self.assertEqual("ok", first["status"])
        protected = {
            target / "agent-os/state/active-work/codex-session.json": b"STATE SENTINEL\x00\xff",
            target / "agent-os/state/user-owned-state.md": b"USER STATE SENTINEL\x00\xfd",
            target / "wiki/index.md": b"WIKI SENTINEL\x00\xfe",
            target / "wiki/knowledge/agentos-wiki-v2-method.md": b"KNOWLEDGE SENTINEL\x00\xfc",
        }
        for path, sentinel in protected.items():
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(sentinel)

        second = installer.install(TEMPLATE, target, dry_run=False)
        self.assertEqual("ok", second["status"], second["failures"])
        for path, sentinel in protected.items():
            self.assertEqual(sentinel, path.read_bytes())
        actions = {item["path"]: item["action"] for item in second["actions"]}
        self.assertNotIn("agent-os/state/active-work/codex-session.json", actions)
        self.assertNotIn("agent-os/state/user-owned-state.md", actions)
        self.assertEqual("preserved-existing-wiki", actions["wiki/index.md"])
        self.assertEqual(
            "preserved-existing-wiki",
            actions["wiki/knowledge/agentos-wiki-v2-method.md"],
        )
        preservation = validator.preservation_report(target)
        self.assertEqual("safe", preservation["status"])
        self.assertIn("wiki/index.md", preservation["preserved"])
        self.assertIn("wiki/knowledge/agentos-wiki-v2-method.md", preservation["preserved"])

    def test_update_backs_up_and_removes_only_known_obsolete_agentos_paths(self) -> None:
        target = self.root / "obsolete"
        first = installer.install(TEMPLATE, target, dry_run=False)
        self.assertEqual("ok", first["status"])
        obsolete_file = target / ".codex/agentos-local-rules.md"
        obsolete_file.write_text("OLD PSEUDO ENTRY\n", encoding="utf-8")
        obsolete_directory = target / ".claude/skills/dynamic-workflow"
        obsolete_directory.mkdir(parents=True)
        (obsolete_directory / "SKILL.md").write_text(
            "OLD CLAUDE ADAPTER\n", encoding="utf-8"
        )
        user_state = target / "agent-os/state/audit-log.md"
        user_state.parent.mkdir(parents=True, exist_ok=True)
        user_state.write_text("PRESERVED HISTORY\n", encoding="utf-8")

        dry_run = installer.install(TEMPLATE, target, dry_run=True)
        dry_actions = {item["path"]: item for item in dry_run["actions"]}
        self.assertEqual(
            "backed-up-and-removed-obsolete",
            dry_actions[".codex/agentos-local-rules.md"]["action"],
        )
        self.assertTrue(obsolete_file.exists())
        self.assertTrue(obsolete_directory.exists())

        second = installer.install(TEMPLATE, target, dry_run=False)
        self.assertEqual("ok", second["status"])
        actions = {item["path"]: item for item in second["actions"]}
        for relative in (
            ".codex/agentos-local-rules.md",
            ".claude/skills/dynamic-workflow",
        ):
            self.assertEqual(
                "backed-up-and-removed-obsolete", actions[relative]["action"]
            )
            self.assertTrue(Path(actions[relative]["backup"]).exists())
            self.assertFalse((target / relative).exists())
        self.assertEqual("PRESERVED HISTORY\n", user_state.read_text(encoding="utf-8"))

    def test_invalid_existing_configs_are_byte_identical_and_cli_is_non_success(self) -> None:
        target = self.root / "invalid"
        invalid_values = {
            target / ".claude/settings.json": b'{"broken": ',
            target / ".codex/hooks.json": b'[invalid json',
            target / ".codex/config.toml": b'developer_instructions = """unterminated',
        }
        for path, value in invalid_values.items():
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(value)

        completed = subprocess.run(
            [sys.executable, str(INSTALLER_PATH), str(target)],
            check=False,
            capture_output=True,
            text=True,
        )
        self.assertEqual(2, completed.returncode, completed.stdout + completed.stderr)
        result = json.loads(completed.stdout)
        self.assertEqual("partial", result["status"])
        for path, value in invalid_values.items():
            self.assertEqual(value, path.read_bytes(), path)

        manifest = json.loads((target / ".agentos-install-manifest.json").read_text(encoding="utf-8"))
        self.assertEqual("partial", manifest["status"])
        failures = {item["path"]: item["action"] for item in manifest["failures"]}
        self.assertEqual("merge-failed-invalid-target-json", failures[".claude/settings.json"])
        self.assertEqual("merge-failed-invalid-target-json", failures[".codex/hooks.json"])
        self.assertEqual("merge-failed-invalid-target-toml", failures[".codex/config.toml"])

    def test_validator_accepts_current_attention_template_and_rejects_missing_layers(self) -> None:
        current_target = self.root / "current"
        manifest = installer.install(TEMPLATE, current_target, dry_run=False)
        self.assertEqual("ok", manifest["status"])
        current = validator.validate(current_target)
        self.assertEqual("passed", current["status"], json.dumps(current, indent=2))
        self.assertEqual("canonical", current["resident_rules"]["status"])

        broken_target = self.root / "broken"
        shutil.copytree(current_target, broken_target)
        (broken_target / "agent-os/tools/aos_active_work.py").unlink()
        shutil.rmtree(broken_target / "tests")
        for runtime in (".claude", ".codex"):
            (broken_target / runtime / "hooks/aos_common.py").write_text(
                "# intentionally missing active-work integration\n",
                encoding="utf-8",
            )
        (broken_target / "AGENTS.md").write_text("# broken projection\n", encoding="utf-8")

        broken = validator.validate(broken_target)
        self.assertEqual("failed", broken["status"])
        self.assertIn("agent-os/tools/aos_active_work.py", broken["missing_files"])
        self.assertEqual(
            "missing-task-state-test-layer", broken["task_state_tests"]["status"]
        )
        self.assertEqual(
            "runtime-attention-hook-missing", broken["attention_hooks"]["status"]
        )
        self.assertEqual("projection-mismatch", broken["resident_rules"]["status"])


if __name__ == "__main__":
    unittest.main(verbosity=2)
