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
            "agent-os", "wiki", ".agents/skills", ".claude/skills",
            ".claude/agents", "tests/scenarios",
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

    def require_instance(self, relative: str) -> None:
        """Skip when the development repo's instance data is absent (fresh install)."""
        if not (REPO / relative).is_file():
            self.skipTest(f"development-instance data absent: {relative}")

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
        self.assertEqual([], self.problems(self.workspace()))

    def test_fresh_project_may_start_with_empty_memory_collections(self) -> None:
        root = self.workspace()
        for relative in (
            "wiki/CHATS/2026-07-11-self-evolving-agents-harvest.md",
            "wiki/TASKS/2026-07-20-agentos-global-convergence.md",
        ):
            (root / relative).unlink(missing_ok=True)
        for path in (root / "wiki/raw").glob("20*"):
            path.unlink()
        for directory in (
            "wiki/archive", "wiki/errors/archive", "wiki/exemplars",
        ):
            shutil.rmtree(root / directory, ignore_errors=True)
        for path in (root / "wiki/errors").glob("20*.md"):
            path.unlink()
        for path in (root / "wiki/errors").glob("_DIGEST_*.md"):
            path.unlink()
        error_index = root / "wiki/errors/_INDEX.md"
        error_index.write_text(
            "\n".join(
                line
                for line in error_index.read_text(encoding="utf-8").splitlines()
                if "_DIGEST_" not in line
            )
            + "\n",
            encoding="utf-8",
        )
        index = root / "wiki/index.md"
        index.write_text(
            index.read_text(encoding="utf-8").replace(
                "- [Current task](TASKS/2026-07-20-agentos-global-convergence.md)\n",
                "- [Task notes](TASKS/README.md)\n",
            ),
            encoding="utf-8",
        )
        manifest = root / "wiki/raw/MANIFEST.md"
        manifest.write_text(
            "# Raw Source Manifest\n\n## Sources\n\n"
            "| Source path | Recorded | Owner | Status | Promotion |\n"
            "|---|---|---|---|---|\n",
            encoding="utf-8",
        )
        previous = LINTER.ROOT
        LINTER.ROOT = root
        try:
            LINTER.fix_memory_views()
        finally:
            LINTER.ROOT = previous
        self.assertEqual([], self.problems(root))
        self.assertEqual([], self.memory_problems(root))

    def test_date_structure_dead_projection_and_duplicate_source_are_rejected(self) -> None:
        mutations = {
            "stable-date": lambda root: (root / "agent-os/router.md").write_text(
                (root / "agent-os/router.md").read_text(encoding="utf-8")
                .replace("# AgentOS Router\n", "# AgentOS Router\n\nDate: 2099-01-01\n", 1),
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
            "exemplar-missing-accepted-scope": lambda root: (root / "wiki/exemplars/spokesperson-tldr-2026-07-16.md").write_text(
                "\n".join(
                    line
                    for line in (root / "wiki/exemplars/spokesperson-tldr-2026-07-16.md")
                    .read_text(encoding="utf-8").splitlines()
                    if not line.startswith("accepted_scope:")
                )
                + "\n",
                encoding="utf-8",
            ),
            "exemplar-dead-contract": lambda root: (root / "wiki/exemplars/spokesperson-tldr-2026-07-16.md").write_text(
                (root / "wiki/exemplars/spokesperson-tldr-2026-07-16.md").read_text(encoding="utf-8")
                + "\ncontract_ref: agent-os/review/missing-report-contract.md\n",
                encoding="utf-8",
            ),
        }
        instance_preconditions = {
            "exemplar-missing-accepted-scope": "wiki/exemplars/spokesperson-tldr-2026-07-16.md",
            "exemplar-dead-contract": "wiki/exemplars/spokesperson-tldr-2026-07-16.md",
        }
        for name, mutate in mutations.items():
            with self.subTest(name=name):
                if name in instance_preconditions:
                    self.require_instance(instance_preconditions[name])
                root = self.workspace()
                mutate(root)
                self.assertTrue(self.problems(root), f"{name} escaped artifact lint")

    def test_memory_contract_rejects_broken_views_lifecycle_and_error_landings(self) -> None:
        def rewrite(root: Path, relative: str, old: str, new: str) -> None:
            path = root / relative
            path.write_text(path.read_text(encoding="utf-8").replace(old, new, 1), encoding="utf-8")

        mutations = {
            "missing-index": lambda root: rewrite(
                root, "wiki/index.md", "- [TASKS/README.md](TASKS/README.md)\n", ""
            ),
            "raw-unregistered": lambda root: rewrite(
                root, "wiki/raw/MANIFEST.md", "| `wiki/raw/2026-07-11-工作汇报向上管理-抖音转写.md`", "| `wiki/raw/missing.md`"
            ),
            "second-handoff": lambda root: (root / "HANDOFF.md").write_text(
                (root / "HANDOFF.md").read_text(encoding="utf-8")
                + "\n## Current Snapshot\n\n- Status: current\n",
                encoding="utf-8",
            ),
            "broken-supersession": lambda root: rewrite(
                root,
                "wiki/knowledge/agentos-wiki-v2-method.md",
                "supersedes: []",
                "supersedes: [wiki/knowledge/missing.md]",
            ),
            "invalid-landing": lambda root: rewrite(
                root,
                "wiki/errors/2026-07-11-hollow-gates-dispositions.md",
                "landing_target: agent-os/rules-card.md",
                "landing_target: agent-os/tools/missing.py",
            ),
            "recurrence-without-regression": lambda root: rewrite(
                root,
                "wiki/errors/2026-07-12-scolding-diagnosis-left-unanswered.md",
                "regression: tests/scenarios/test_instruction_stack_contract.py",
                "regression:",
            ),
            "duplicate-root": lambda root: shutil.copy2(
                root / "wiki/errors/2026-07-11-hollow-gates-dispositions.md",
                root / "wiki/errors/2026-07-20-duplicate-root.md",
            ),
        }
        instance_preconditions = {
            "raw-unregistered": "wiki/raw/2026-07-11-工作汇报向上管理-抖音转写.md",
            "invalid-landing": "wiki/errors/2026-07-11-hollow-gates-dispositions.md",
            "recurrence-without-regression": "wiki/errors/2026-07-12-scolding-diagnosis-left-unanswered.md",
            "duplicate-root": "wiki/errors/2026-07-11-hollow-gates-dispositions.md",
        }
        for name, mutate in mutations.items():
            with self.subTest(name=name):
                if name in instance_preconditions:
                    self.require_instance(instance_preconditions[name])
                root = self.workspace()
                mutate(root)
                self.assertTrue(self.memory_problems(root), f"{name} escaped memory lint")

    def test_fix_memory_views_is_idempotent_and_does_not_edit_semantic_files(self) -> None:
        root = self.workspace()
        semantic_paths = (
            "DECISIONS.md",
            "PROGRESS.md",
            "wiki/knowledge/agentos-wiki-v2-method.md",
            "wiki/errors/2026-07-11-hollow-gates-dispositions.md",
        )
        semantic_paths = tuple(
            relative for relative in semantic_paths if (root / relative).is_file()
        )
        before = {
            relative: (root / relative).read_bytes() for relative in semantic_paths
        }
        previous = LINTER.ROOT
        LINTER.ROOT = root
        try:
            self.assertFalse(LINTER.fix_memory_views())
            self.assertFalse(LINTER.fix_memory_views())
        finally:
            LINTER.ROOT = previous
        after = {
            relative: (root / relative).read_bytes() for relative in semantic_paths
        }
        self.assertEqual(before, after)


if __name__ == "__main__":
    unittest.main()
