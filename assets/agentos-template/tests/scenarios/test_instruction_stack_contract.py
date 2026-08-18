"""Repository contracts for attention, completion, and runtime ownership."""
from __future__ import annotations

import re
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


def read(relative: str) -> str:
    return (ROOT / relative).read_text(encoding="utf-8")


class InstructionStackContractTests(unittest.TestCase):
    def test_codex_seats_use_desktop_threads_and_native_spawn_is_retired(self) -> None:
        adapter = read("agent-os/adapters/codex-workflow.md").lower()
        self.assertIn("spawn_agent", adapter)
        self.assertIn("codex_app.create_thread", adapter)
        self.assertIn("codex_app.send_message_to_thread", adapter)
        self.assertNotIn("no_delegation", adapter)
        for seat in ("agentos-zhongshu", "agentos-menxia", "agentos-shangshu", "agentos-executor", "agentos-yushi"):
            toml = read(f".codex/agents/{seat}.toml")
            self.assertIn(f'name = "{seat}"', toml)
            self.assertIn("developer_instructions", toml)
        self.assertFalse((ROOT / ".codex/hooks/aos_guard_enforcer.py").exists())
        self.assertFalse((ROOT / ".claude/skills/dynamic-workflow/SKILL.md").exists())

    def test_every_seat_has_native_skill_binding_and_hashed_runtime_receipt(self) -> None:
        manifest = read("agent-os/skills/seat-skills.json")
        receipt = read("agent-os/tools/aos_skill_receipt.py")
        gate = read(".codex/hooks/aos_chain_gate.py")
        for role in ("zhongshu", "menxia", "shangshu", "executor", "yushi"):
            self.assertIn(f'"{role}"', manifest)
        for name in (
            "intent-contract-review", "reasoning-causality-review",
            "anti-sycophancy-review", "prompt-craft-review",
            "route-promotion-review", "evidence-claim-review", "delivery-review",
            "engineering-plan-review", "minimal-code-review", "lifecycle-execution",
            "memory-wiki-routing",
        ):
            self.assertIn(f'"{name}"', manifest)
            self.assertTrue((ROOT / f".agents/skills/{name}/SKILL.md").is_file())
            self.assertTrue((ROOT / f".claude/skills/{name}/SKILL.md").is_file())
        self.assertIn("hashlib.sha256", receipt)
        self.assertIn('"skill_load"', receipt)
        self.assertIn("valid_skill_receipt", gate)

    def test_codex_visual_seats_are_main_titled_local_and_not_archived_early(self) -> None:
        config = read(".codex/config.toml")
        adapter = read("agent-os/adapters/codex-workflow.md")
        shangshu = read("agent-os/workflows/shangshu.md")
        skill = read(".agents/skills/agentos/SKILL.md")
        for text in (config, adapter, skill):
            normalized = text.replace("<id>", "<task-id>").replace("<task>", "<task-id>")
            self.assertIn("中书省｜<task-title>｜<task-id>", normalized)
        for text in (adapter, skill):
            self.assertIn("environment.type=local", text)
        for text in (adapter, read(".codex/agents/agentos-zhongshu.toml")):
            self.assertIn("seat-skills.json", text)
            self.assertIn("aos_skill_receipt.py", text)
        self.assertIn("Do not archive", shangshu)
        self.assertIn("next task", adapter)

    def test_visible_seat_titles_include_readable_task_and_stable_id(self) -> None:
        recorder = read("agent-os/tools/aos_task_record.py")
        gate = read(".claude/hooks/aos_chain_gate.py")
        skill = read(".agents/skills/agentos/SKILL.md")
        self.assertIn("def task_title", recorder)
        self.assertIn('commands.add_parser("title"', recorder)
        self.assertIn("def seat_thread_title", gate)
        self.assertIn("角色｜任务简称｜任务号", gate)
        self.assertIn("aos_task_record.py title --task <id>", skill)

    def test_chain_is_opt_in_through_one_skill_per_runtime_with_one_kernel(self) -> None:
        """Same kernel, two transports: on Codex the invoking thread is a relay and
        中书 is a Desktop thread; on Claude the invoking session IS 中书 (the shape
        the user had before 2026-08-17 — a courier session on Claude hid the
        chain for an hour on 2026-08-18)."""
        codex_skill = read(".agents/skills/agentos/SKILL.md")
        claude_skill = read(".claude/skills/agentos/SKILL.md")
        self.assertNotEqual(codex_skill, claude_skill)
        for skill in (codex_skill, claude_skill):
            self.assertIn("name: agentos", skill)
            self.assertIn("ONLY when the user explicitly invokes", skill)
            for phrase in ("No payload, no chain", "t<YYYYMMDD-HHMM>", "--kind pause", "--kind stop",
                           "aos_task_record.py title --task <id>", "freeze the ledger"):
                self.assertIn(phrase, skill)
        for phrase in ("--role relay --kind resume", "never summarizes", "codex_app.create_thread",
                       "中书省｜<task-title>｜<id>"):
            self.assertIn(phrase, codex_skill)
        self.assertNotIn("Agent(agentos-zhongshu)", codex_skill)
        for phrase in ("this session is 中书", "--role zhongshu --kind resume",
                       "--role zhongshu --kind user_message", "Agent(agentos-menxia)",
                       "Agent(agentos-shangshu)", "TaskStop", "my call failed", "strongest rival",
                       "never suggest a verdict", "Never `sleep`-poll", "END THE TURN",
                       "`name`, `team_name`, or `isolation`", "Read `agent-os/workflows/zhongshu.md`"):
            self.assertIn(phrase, claude_skill)
        self.assertNotIn("codex_app", claude_skill.split("## Who you are")[1])
        settings = read(".claude/settings.json")
        self.assertNotIn('"agent"', settings)
        self.assertFalse((ROOT / ".claude/agents/agentos-entry.md").exists())
        self.assertFalse((ROOT / ".claude/agents/agentos-zhongshu.md").exists())
        config = read(".codex/config.toml")
        self.assertIn("Ordinary chat is the default", config)
        self.assertIn("`agentos` skill", config)
        rules = read("agent-os/rules-card.md")
        self.assertIn("The chain is opt-in", rules)
        for entry in (read("AGENTS.md"), read("CLAUDE.md")):
            self.assertIn("ordinary chat is the default", entry)
            self.assertNotIn("every request runs the three-departments", entry)
        workflow = read("agent-os/workflows/zhongshu.md")
        self.assertIn("never suggests one", workflow)
        self.assertIn("On Claude you ARE the", workflow)
        self.assertIn("An invocation with no task content opens nothing", workflow)

    def test_claude_keeps_native_workflow_without_codex_guard(self) -> None:
        claude = read("CLAUDE.md")
        settings = read(".claude/settings.json")
        self.assertIn("native Workflow", claude)
        self.assertIn("keeps Superpowers enabled", claude)
        self.assertNotIn("aos_guard_enforcer.py", settings)
        self.assertFalse((ROOT / ".claude/hooks/aos_guard_enforcer.py").exists())
        self.assertIn('"matcher": "^Bash$"', settings)
        self.assertIn('"PostToolUse"', settings)

    def test_claude_seats_use_synchronous_agent_results_not_idle_team_messages(self) -> None:
        menxia = read(".claude/agents/agentos-menxia.md")
        shangshu = read(".claude/agents/agentos-shangshu.md")
        executor = read(".claude/agents/agentos-executor.md")
        for text in (menxia, shangshu, executor):
            tools = text.split("---", 2)[1]
            self.assertNotIn("SendMessage", tools)
        self.assertIn("Each spawn handles exactly the phase named", menxia)
        self.assertIn("Agent(agentos-executor)", shangshu)
        for phrase in ("run_in_background=false", "never `name`, `team_name`, or\n`isolation`",
                       "never `sleep`-poll", "integration --status blocked"):
            self.assertIn(phrase, shangshu)
        self.assertIn("synchronous Agent result", executor)
        workflow = read("agent-os/workflows/zhongshu.md")
        self.assertIn("two separate synchronous `Agent(agentos-menxia)`", workflow)
        self.assertIn("never use `SendMessage` to an ended Claude agent", workflow)
        self.assertIn("never `sleep`-poll", workflow)

    def test_pause_and_stop_have_fixed_non_inferential_replies_on_both_runtimes(self) -> None:
        for path in (".claude/skills/agentos/SKILL.md", ".agents/skills/agentos/SKILL.md"):
            skill = read(path)
            self.assertIn("已暂停任务 <id>；席位保留", skill)
            self.assertIn("已停止任务 <id>；本会话回到普通聊天", skill)
            self.assertIn("Do not add a diagnosis, execution history", skill)

    def test_main_seat_preserves_invocation_and_yushi_respects_read_only_contracts(self) -> None:
        skill = " ".join(read(".claude/skills/agentos/SKILL.md").split())
        self.assertIn('"Exact words" includes the invocation token', skill)
        self.assertIn("reconstruct the full line as `/agentos`", skill)
        codex = " ".join(read(".agents/skills/agentos/SKILL.md").split())
        self.assertIn("preserve the user's full `$agentos ...` message", codex)
        yushi_agent = read(".claude/agents/agentos-yushi.md")
        yushi_workflow = read("agent-os/workflows/yushi.md")
        for text in (yushi_agent, yushi_workflow):
            self.assertIn("read-only", text)
            self.assertIn("error_record", text)
            self.assertNotIn("--kind error_learning", text)

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
        self.assertIn("hooks restore attention or enforce deterministic facts", compact)
        self.assertIn("restored task state is context, never inherited permission", compact)

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
            "plain language",
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

    def test_chain_gate_denies_on_facts_only_and_never_asks(self) -> None:
        gate = read(".codex/hooks/aos_chain_gate.py")
        post = read(".codex/hooks/aos_kernel_lint.py")
        for forbidden in ("permissionDecision\": \"ask", "\"ask\""):
            self.assertNotIn(forbidden, gate)
            self.assertNotIn(forbidden, post)
        self.assertIn("agent_type", gate)          # identity from the runtime
        self.assertIn("ledger_events", gate)       # phase from the ledger
        self.assertIn("quoted_by_user", gate)      # bypass = verbatim user quote

    def test_prompt_labels_remain_a_structure_check(self) -> None:
        gate = read("agent-os/review/prompt-craft-gate.md").lower()
        hook = read(".codex/hooks/aos_prompt_craft_guard.py").lower()
        self.assertIn("structure-only", gate)
        self.assertIn("does not guarantee", gate)
        self.assertIn("structure", hook)

    def test_questions_leave_only_real_user_owned_blockers(self) -> None:
        rules = read("agent-os/rules-card.md").lower()
        self.assertIn("the user owns decisions that change the requested outcome", rules)
        self.assertIn("ask only when a user-owned choice blocks", rules)

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
                if path.name == "install-agentos.py":
                    # Retired names may exist only as exact cleanup tombstones.
                    text = re.sub(
                        r"OBSOLETE_AGENTOS_PATHS\s*=\s*\(.*?\)\n\n",
                        "",
                        text,
                        flags=re.DOTALL,
                    )
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

    def test_role_contracts_order_method_reads_by_path(self) -> None:
        """A method reference is not a method: every chain role contract must
        order concrete Reads of kernel gate paths at the moment of use, not
        name skills or capabilities in the abstract (wiki/errors
        root-named-is-not-possessed, recurrence 3)."""
        for contract in (
            ".claude/skills/agentos/SKILL.md",
            ".claude/agents/agentos-menxia.md",
            ".claude/agents/agentos-shangshu.md",
            ".claude/agents/agentos-executor.md",
            ".claude/agents/agentos-yushi.md",
        ):
            body = read(contract)
            self.assertRegex(
                body, r"Read[^.\n]*`agent-os/(review|memory|workflows)/[a-z-]+\.md`",
                f"{contract} lacks a concrete method-read order",
            )


if __name__ == "__main__":
    unittest.main()
