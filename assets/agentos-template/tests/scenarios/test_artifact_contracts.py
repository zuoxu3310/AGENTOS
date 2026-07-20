from __future__ import annotations

import contextlib
import importlib.util
import io
import shutil
import tempfile
import unittest
from pathlib import Path


REPO = Path(__file__).resolve().parents[2]
LINTER_PATH = REPO / "agent-os/tools/aos-lint.py"
SPEC = importlib.util.spec_from_file_location("agentos_artifact_lint", LINTER_PATH)
assert SPEC is not None and SPEC.loader is not None
LINTER = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(LINTER)


class ArtifactContractScenarios(unittest.TestCase):
    def workspace(self) -> Path:
        temporary = tempfile.TemporaryDirectory(prefix="agentos-artifacts-")
        self.addCleanup(temporary.cleanup)
        root = Path(temporary.name)
        for directory in (
            "agent-os", "outputs", "wiki", ".agents/skills", ".claude/skills"
        ):
            shutil.copytree(REPO / directory, root / directory, symlinks=True)
        for relative in (
            "AGENTS.md", "CLAUDE.md", "PLANS.md", "PROGRESS.md",
            "DECISIONS.md", "HANDOFF.md", ".codex/config.toml",
            ".codex/hooks/aos_stop_gate.py",
            ".codex/hooks/aos_prompt_baseline.py",
            ".claude/hooks/aos_stop_gate.py",
            ".claude/hooks/aos_prompt_baseline.py",
        ):
            destination = root / relative
            destination.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(REPO / relative, destination)
        rules = root / ".claude/rules"
        rules.mkdir(parents=True)
        (rules / "agentos-local-rules.md").symlink_to(
            "../../agent-os/rules-card.md"
        )
        return root

    def problems(self, root: Path) -> list[str]:
        previous = LINTER.ROOT
        LINTER.ROOT = root
        failures: list[str] = []
        try:
            with contextlib.redirect_stdout(io.StringIO()):
                LINTER.lint_artifact_contracts(failures)
        finally:
            LINTER.ROOT = previous
        return failures

    def memory_problems(self, root: Path) -> list[str]:
        previous = LINTER.ROOT
        LINTER.ROOT = root
        failures: list[str] = []
        try:
            with contextlib.redirect_stdout(io.StringIO()):
                LINTER.lint_memory_contracts(failures)
        finally:
            LINTER.ROOT = previous
        return failures

    def test_clean_publication_contract_has_exactly_one_type_per_document(self) -> None:
        root = self.workspace()
        self.assertEqual([], self.problems(root))
        self.assertEqual([], self.memory_problems(root))

    def test_structure_dead_projection_and_duplicate_source_are_rejected(self) -> None:
        mutations = {
            "stable-date": lambda root: (root / "agent-os/boot.md").write_text(
                (root / "agent-os/boot.md").read_text(encoding="utf-8")
                .replace("# AgentOS Boot\n", "# AgentOS Boot\n\nDate: 2099-01-01\n", 1),
                encoding="utf-8",
            ),
            "missing-structure": lambda root: (root / "agent-os/review/minimal-code-gate.md").write_text(
                (root / "agent-os/review/minimal-code-gate.md").read_text(encoding="utf-8")
                .replace("## Purpose", "## Intent", 1),
                encoding="utf-8",
            ),
            "untyped-document": lambda root: (root / "agent-os/orphan.md").write_text(
                "# Orphan\n", encoding="utf-8"
            ),
            "dead-projection": lambda root: (root / ".codex/agentos-local-rules.md").symlink_to(
                "../agent-os/rules-card.md"
            ),
            "duplicate-source": lambda root: (root / ".codex/hooks/aos_prompt_baseline.py").write_text(
                (root / ".codex/hooks/aos_prompt_baseline.py").read_text(encoding="utf-8")
                + "\n# <executive_intake>Start every new goal from first principles\n",
                encoding="utf-8",
            ),
        }
        for name, mutate in mutations.items():
            with self.subTest(name=name):
                root = self.workspace()
                mutate(root)
                self.assertTrue(self.problems(root), f"{name} escaped artifact lint")

    def test_memory_contract_rejects_unregistered_source_and_invalid_current_state(self) -> None:
        mutations = {
            "raw-unregistered": lambda root: (root / "wiki/raw/2026-01-01-example.md").write_text(
                "# Example raw source\n", encoding="utf-8"
            ),
            "second-handoff": lambda root: (root / "HANDOFF.md").write_text(
                (root / "HANDOFF.md").read_text(encoding="utf-8")
                + "\n## Current Snapshot\n\n- Status: current\n",
                encoding="utf-8",
            ),
            "broken-supersession": lambda root: (root / "wiki/knowledge/agentos-wiki-v2-method.md").write_text(
                (root / "wiki/knowledge/agentos-wiki-v2-method.md").read_text(encoding="utf-8")
                .replace("supersedes: []", "supersedes: [wiki/knowledge/missing.md]", 1),
                encoding="utf-8",
            ),
        }
        for name, mutate in mutations.items():
            with self.subTest(name=name):
                root = self.workspace()
                mutate(root)
                self.assertTrue(self.memory_problems(root), f"{name} escaped memory lint")

    def test_fix_memory_views_is_idempotent_and_preserves_semantic_files(self) -> None:
        root = self.workspace()
        semantic_paths = (
            "DECISIONS.md",
            "PROGRESS.md",
            "wiki/knowledge/agentos-wiki-v2-method.md",
        )
        before = {relative: (root / relative).read_bytes() for relative in semantic_paths}
        previous = LINTER.ROOT
        LINTER.ROOT = root
        try:
            self.assertFalse(LINTER.fix_memory_views())
            self.assertFalse(LINTER.fix_memory_views())
        finally:
            LINTER.ROOT = previous
        after = {relative: (root / relative).read_bytes() for relative in semantic_paths}
        self.assertEqual(before, after)


if __name__ == "__main__":
    unittest.main()
