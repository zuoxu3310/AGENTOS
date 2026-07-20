"""Repository contracts for attention, completion, and runtime ownership."""
from __future__ import annotations

import re
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


def read(relative: str) -> str:
    return (ROOT / relative).read_text(encoding="utf-8")


class InstructionStackContractTests(unittest.TestCase):
    def test_dynamic_workflow_remains_the_only_codex_delegation_backend(self) -> None:
        adapter = read("agent-os/adapters/codex-workflow.md").lower()
        skill = read(".agents/skills/dynamic-workflow/SKILL.md").lower()
        guard = read(".codex/hooks/aos_guard_enforcer.py")
        self.assertIn("no_delegation", adapter)
        self.assertIn("one delegated execution engine", adapter)
        self.assertIn("vendored dynamic workflow runner", guard.lower())
        self.assertIn("sole delegated execution command", skill)
        self.assertNotIn("spawn_agent", adapter)
        self.assertFalse((ROOT / ".claude/skills/dynamic-workflow/SKILL.md").exists())
        self.assertTrue(
            (ROOT / "vendor/claude-dynamic-workflows-codex/runner/bin/run-workflow.js").is_file()
        )

    def test_claude_keeps_native_workflow_without_codex_guard(self) -> None:
        claude = read("CLAUDE.md")
        settings = read(".claude/settings.json")
        self.assertIn("native Workflow", claude)
        self.assertIn("keeps Superpowers enabled", claude)
        self.assertNotIn("aos_guard_enforcer.py", settings)
        self.assertFalse((ROOT / ".claude/hooks/aos_guard_enforcer.py").exists())

    def test_resident_rules_are_one_exact_projection(self) -> None:
        rules = read("agent-os/rules-card.md")
        agents = read("AGENTS.md")
        managed = agents.split("<!-- BEGIN AGENTOS RESIDENT RULES -->", 1)[1].split(
            "<!-- END AGENTOS RESIDENT RULES -->", 1
        )[0].strip()
        self.assertEqual(rules.strip(), managed)
        self.assertEqual(
            (ROOT / ".claude/rules/agentos-local-rules.md").resolve(),
            (ROOT / "agent-os/rules-card.md").resolve(),
        )

    def test_rules_make_semantics_the_models_job_and_hooks_mechanical(self) -> None:
        rules = read("agent-os/rules-card.md").lower()
        compact = re.sub(r"\s+", " ", rules)
        self.assertIn("start from first principles", compact)
        self.assertIn("re-read every real user message", compact)
        self.assertIn("hooks only to restore attention or enforce deterministic", compact)
        self.assertIn("restored task state is context, never inherited execution permission", compact)

    def test_long_task_contract_has_a_falsifiable_finish_line(self) -> None:
        contract = read("agent-os/review/task-contract.md")
        compact_contract = re.sub(r"\s+", " ", contract)
        helper = read("agent-os/tools/aos_active_work.py")
        for field in (
            "goal",
            "done_when",
            "open_items",
            "next_action",
            "latest_user_delta",
            "status",
            "blocker",
            "report_state",
            "completion",
        ):
            self.assertIn(field, contract)
            self.assertIn(f'"{field}"', helper)
        self.assertIn("Several tools can belong to one work segment", compact_contract)
        self.assertIn("do not create persistent state merely because several tools", compact_contract.lower())

    def test_plain_language_is_default_without_fixed_length_scoring(self) -> None:
        rules = read("agent-os/rules-card.md").lower()
        compact_rules = re.sub(r"\s+", " ", rules)
        lifecycle = read("agent-os/workflows/agent-execution-lifecycle.md").lower()
        stop = read(".codex/hooks/aos_stop_gate.py").lower()
        for phrase in (
            "simple, natural, direct language",
            "if one sentence says it clearly, use one sentence",
            "simplicity must not hide",
        ):
            self.assertIn(phrase, compact_rules)
        self.assertIn("simple natural language", lifecycle)
        self.assertIn("simplest natural language", stop)
        for forbidden in ("min_judged_chars", "term density", "word count", "spokesperson"):
            self.assertNotIn(forbidden, stop)
            self.assertNotIn(forbidden, rules)

    def test_attention_hooks_exist_only_at_session_user_message_and_long_delivery(self) -> None:
        hooks = read(".codex/hooks.json")
        self.assertIn('"SessionStart"', hooks)
        self.assertIn('"UserPromptSubmit"', hooks)
        self.assertIn('"Stop"', hooks)
        prompt = read(".codex/hooks/aos_prompt_baseline.py")
        session = read(".codex/hooks/aos_session_start.py")
        stop = read(".codex/hooks/aos_stop_gate.py")
        self.assertIn('phase="user_message"', prompt)
        self.assertIn('phase="restore"', session)
        self.assertIn('report_state") != "pending"', stop)

    def test_pre_and_post_tool_hooks_do_not_classify_shell_intent(self) -> None:
        guard = read(".codex/hooks/aos_guard_enforcer.py")
        post = read(".codex/hooks/aos_kernel_lint.py")
        codex_hooks = read(".codex/hooks.json")
        claude_hooks = read(".claude/settings.json")
        for forbidden in ("READ_ONLY_SHELL", "SHELL_COMPOSITION", "WRITE_HINTS", "permissionDecision\": \"ask"):
            self.assertNotIn(forbidden, guard)
            self.assertNotIn(forbidden, post)
        self.assertNotIn('"matcher": "^(Bash|apply_patch|Edit|Write|MultiEdit)$"', codex_hooks)
        self.assertNotIn('"matcher": "^(Edit|Write|MultiEdit|Bash)$"', claude_hooks)

    def test_prompt_labels_remain_a_structure_check(self) -> None:
        gate = read("agent-os/review/prompt-craft-gate.md").lower()
        hook = read(".codex/hooks/aos_prompt_craft_guard.py").lower()
        self.assertIn("structure-only", gate)
        self.assertIn("does not guarantee", gate)
        self.assertIn("structure", hook)

    def test_questions_leave_only_real_user_owned_blockers(self) -> None:
        rules = read("agent-os/rules-card.md").lower()
        self.assertIn("the user owns decisions that change the requested outcome", rules)
        self.assertIn("ask only when a user-owned choice truly blocks the next action", rules)

    def test_minimal_mechanism_cannot_reduce_the_accepted_result(self) -> None:
        gate = read("agent-os/review/minimal-code-gate.md").lower()
        compact_gate = re.sub(r"\s+", " ", gate)
        contract = read("agent-os/review/task-contract.md").lower()
        self.assertIn("least mechanism", compact_gate)
        self.assertIn("minimal mechanism never means partial functionality", compact_gate)
        self.assertIn("do not add more work", contract)

    def test_old_route_engine_has_no_active_entry(self) -> None:
        forbidden = (
            "aos_" + "cognitive",
            "aos_" + "referee",
            "agency_" + "proposal_path",
            "turn_" + "admission",
            "route_" + "marker",
        )
        roots = (
            ROOT / ".codex",
            ROOT / ".claude",
            ROOT / "agent-os",
            ROOT / "tests",
            ROOT / "work/agentos-installer-candidate/scripts",
            ROOT / "work/agentos-installer-candidate/assets/agentos-template/.codex",
            ROOT / "work/agentos-installer-candidate/assets/agentos-template/.claude",
            ROOT / "work/agentos-installer-candidate/assets/agentos-template/agent-os",
            ROOT / "work/agentos-installer-candidate/assets/agentos-template/tests",
        )
        for root in roots:
            if not root.exists():
                continue
            for path in root.rglob("*"):
                if not path.is_file() or path.suffix not in {".py", ".md", ".json", ".toml"}:
                    continue
                if path.resolve() == Path(__file__).resolve():
                    continue
                if "agent-os/state/" in path.relative_to(ROOT).as_posix():
                    continue
                text = path.read_text(encoding="utf-8", errors="replace")
                for term in forbidden:
                    with self.subTest(path=path.relative_to(ROOT), term=term):
                        self.assertNotIn(term, text)

    def test_memory_uses_one_project_adapter_and_selective_recall(self) -> None:
        contract = read("agent-os/memory/routing.md").lower()
        for runtime in (".agents", ".claude"):
            skill = read(f"{runtime}/skills/memory-wiki-routing/SKILL.md").lower()
            self.assertIn("agent-os/memory/routing.md", skill)
            self.assertIn("at most three", skill)
        self.assertIn("single operating contract", contract)
        self.assertIn("do not preload the whole wiki or error library", contract)


if __name__ == "__main__":
    unittest.main()
