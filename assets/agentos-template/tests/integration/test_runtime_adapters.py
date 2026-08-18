"""Black-box contracts for the Codex and Claude attention hooks."""
from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
RUNTIMES = ("codex", "claude")
SESSION = "session-a"


def done_work() -> dict:
    return {
        "goal": "Deliver the long-task result",
        "done_when": ["result exists", "runtime behavior is verified"],
        "open_items": [],
        "next_action": "",
        "latest_user_delta": "finish and report",
        "status": "done",
        "blocker": "",
        "report_state": "pending",
        "completion": [
            {"condition": "result exists", "evidence": ["result.md"]},
            {
                "condition": "runtime behavior is verified",
                "evidence": ["live observation"],
            },
        ],
    }


class HookHarness:
    def __init__(self, runtime: str):
        self.runtime = runtime
        self._temporary = tempfile.TemporaryDirectory(prefix=f"agentos-{runtime}-")
        self.root = Path(self._temporary.name)
        (self.root / "agent-os" / "tools").mkdir(parents=True)
        shutil.copy2(
            ROOT / "agent-os" / "tools" / "aos_active_work.py",
            self.root / "agent-os" / "tools" / "aos_active_work.py",
        )
        hook_source = ROOT / f".{runtime}" / "hooks"
        hook_target = self.root / f".{runtime}" / "hooks"
        shutil.copytree(hook_source, hook_target)
        self.hooks = hook_target
        self.set_lint(exit_code=0)

    def close(self) -> None:
        self._temporary.cleanup()

    def set_lint(self, *, exit_code: int, message: str = "FAIL broken document") -> None:
        body = (
            "import sys\n"
            + ("print('PASS test lint')\n" if exit_code == 0 else f"print({message!r})\n")
            + f"raise SystemExit({exit_code})\n"
        )
        (self.root / "agent-os" / "tools" / "aos-lint.py").write_text(
            body, encoding="utf-8"
        )

    def state_path(self) -> Path:
        return (
            self.root
            / "agent-os"
            / "state"
            / "active-work"
            / f"{self.runtime}-{SESSION}.json"
        )

    def bind_relay(self, task: str = "t20260817-0930") -> None:
        """Put this session on the chain the way the `agentos` skill does: the chain gate
        binds the main session as the runtime's main seat of a task — the relay on
        Codex, 中书 itself on Claude."""
        seat = "agentos-relay" if self.runtime == "codex" else "agentos-zhongshu"
        path = self.root / "agent-os" / "state" / "sessions" / f"{self.runtime}-{SESSION}.json"
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps({"seat": seat, "task_id": task, "bound": True,
                                    "ts": 1.0}), encoding="utf-8")

    @property
    def main_tag(self) -> str:
        return "agentos_relay" if self.runtime == "codex" else "agentos_zhongshu"

    def write_state(self, active_work: dict) -> None:
        path = self.state_path()
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(
            json.dumps(
                {"schema_version": 1, "active_work": active_work},
                ensure_ascii=False,
                indent=2,
            )
            + "\n",
            encoding="utf-8",
        )

    def run(self, hook: str, payload: dict) -> subprocess.CompletedProcess[str]:
        data = {"cwd": str(self.root), "session_id": SESSION, **payload}
        env = os.environ.copy()
        env["PYTHONDONTWRITEBYTECODE"] = "1"
        env[f"{self.runtime.upper()}_PROJECT_DIR"] = str(self.root)
        return subprocess.run(
            [sys.executable, str(self.hooks / hook)],
            input=json.dumps(data, ensure_ascii=False),
            text=True,
            capture_output=True,
            cwd=self.root,
            env=env,
            timeout=30,
        )


def payload(process: subprocess.CompletedProcess[str]) -> dict:
    if not process.stdout.strip():
        return {}
    return json.loads(process.stdout.strip().splitlines()[-1])


def additional_context(process: subprocess.CompletedProcess[str]) -> str:
    return str((payload(process).get("hookSpecificOutput") or {}).get("additionalContext") or "")


class RuntimeAdapterContractTests(unittest.TestCase):
    def setUp(self) -> None:
        self.harnesses = [HookHarness(runtime) for runtime in RUNTIMES]

    def tearDown(self) -> None:
        for harness in self.harnesses:
            harness.close()

    def test_session_start_restores_only_minimal_long_task_state(self) -> None:
        forbidden = (
            "turn_" + "admission",
            "proposal",
            "route_" + "marker",
            "authorization",
        )
        for harness in self.harnesses:
            harness.bind_relay()
            harness.write_state(done_work())
            for source in ("startup", "resume", "clear", "compact"):
                with self.subTest(runtime=harness.runtime, source=source):
                    result = harness.run("aos_session_start.py", {"source": source})
                    self.assertEqual(0, result.returncode, result.stderr)
                    context = additional_context(result)
                    self.assertIn('phase="restore"', context)
                    self.assertIn(harness.main_tag, context)
                    self.assertIn("Deliver the long-task result", context)
                    self.assertIn(str(harness.state_path()), context)
                    for word in forbidden:
                        self.assertNotIn(word, context)

    def test_unbound_session_gets_one_line_and_every_other_hook_is_silent(self) -> None:
        for harness in self.harnesses:
            with self.subTest(runtime=harness.runtime):
                start = harness.run("aos_session_start.py", {"source": "startup"})
                self.assertEqual(0, start.returncode, start.stderr)
                context = additional_context(start)
                self.assertIn("agentos", context)
                self.assertNotIn("Zhongshu seat", context)
                self.assertNotIn("<agentos_attention", context)
                harness.write_state(done_work())
                for hook, extra in (
                    ("aos_prompt_baseline.py", {"prompt": "随便聊聊"}),
                    ("aos_stop_gate.py", {"stop_hook_active": False}),
                    ("aos_prompt_craft_guard.py", {"tool_name": "Agent",
                                                   "tool_input": {"subagent_type": "general-purpose",
                                                                  "prompt": "bare prompt"}}),
                    ("aos_chain_gate.py", {"hook_event_name": "PreToolUse", "tool_name": "Edit",
                                           "tool_input": {"file_path": str(harness.root / "src/app.py")}}),
                    ("aos_chain_gate.py", {"hook_event_name": "Stop", "stop_hook_active": False}),
                ):
                    result = harness.run(hook, extra)
                    self.assertEqual(0, result.returncode, result.stderr)
                    self.assertEqual("", result.stdout.strip(), (hook, extra))

    def test_codex_seat_thread_gets_its_seat_context(self) -> None:
        codex = self.harnesses[0]
        path = codex.root / "agent-os" / "state" / "sessions" / f"codex-{SESSION}.json"
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps({"seat": "agentos-zhongshu", "task_id": "t20260817-0930"}), encoding="utf-8")
        result = codex.run("aos_session_start.py", {"source": "startup"})
        context = additional_context(result)
        self.assertIn('seat="agentos-zhongshu"', context)
        self.assertIn("NOT 中书", context) if False else self.assertIn("agent-os/workflows/zhongshu.md", context)

    def test_user_prompt_reconsiders_every_real_message_but_skips_stop_continuation(self) -> None:
        for harness in self.harnesses:
            harness.bind_relay()
            with self.subTest(runtime=harness.runtime):
                result = harness.run(
                    "aos_prompt_baseline.py",
                    {"prompt": "把最新修正合进去，然后继续原任务"},
                )
                context = additional_context(result)
                self.assertIn('phase="user_message"', context)
                self.assertIn("continues, corrects, replaces", context)
                self.assertIn("Several tools may serve that one segment", context)

                skipped = harness.run(
                    "aos_prompt_baseline.py",
                    {"prompt": "<agentos_stop_continuation> recheck delivery"},
                )
                self.assertEqual("", skipped.stdout.strip())

    def test_shell_read_probes_are_never_semantically_classified(self) -> None:
        codex = self.harnesses[0]
        probes = (
            "cat README.md",
            "test -e README.md",
            'rg "A|B" README.md',
            "sed -n '1,10p' README.md | head -n 2",
            "pwd && git status --short",
        )
        for command in probes:
            with self.subTest(command=command):
                result = codex.run(
                    "aos_chain_gate.py",
                    {"hook_event_name": "PreToolUse", "tool_name": "Bash",
                     "tool_input": {"command": command}},
                )
                self.assertEqual(0, result.returncode, result.stderr)
                self.assertEqual("", result.stdout.strip())

    def test_prompt_guard_ignores_codex_exec_help(self) -> None:
        for harness in self.harnesses:
            tool_name = "exec_command" if harness.runtime == "codex" else "Bash"
            field = "cmd" if harness.runtime == "codex" else "command"
            result = harness.run(
                "aos_prompt_craft_guard.py",
                {"tool_name": tool_name, "tool_input": {field: "codex exec --help"}},
            )
            self.assertEqual(0, result.returncode, result.stderr)
            self.assertEqual("", result.stdout.strip())

    def test_both_runtimes_wire_the_chain_gate_and_no_runner_guard_remains(self) -> None:
        for runtime in RUNTIMES:
            self.assertFalse((ROOT / f".{runtime}" / "hooks" / "aos_guard_enforcer.py").exists())
            self.assertTrue((ROOT / f".{runtime}" / "hooks" / "aos_chain_gate.py").is_file())
        codex_hooks = (ROOT / ".codex" / "hooks.json").read_text(encoding="utf-8")
        claude_settings = (ROOT / ".claude" / "settings.json").read_text(encoding="utf-8")
        for text in (codex_hooks, claude_settings):
            self.assertIn("aos_chain_gate.py", text)
            self.assertIn("SubagentStop", text)
        # Codex uses Desktop codex_app threads; native AgentOS seat spawning is retired.
        codex = self.harnesses[0]
        mapping = codex.root / "agent-os" / "state" / "sessions" / f"codex-{SESSION}.json"
        mapping.parent.mkdir(parents=True, exist_ok=True)
        mapping.write_text(json.dumps({"seat": "agentos-zhongshu", "task_id": "contract"}), encoding="utf-8")
        create_thread = {
            "hook_event_name": "PreToolUse",
            "tool_name": "codex_app__create_thread",
            "tool_input": {"title": "门下省｜未命名任务｜contract", "prompt": "你是门下，任务 contract"},
        }
        incomplete = payload(codex.run("aos_chain_gate.py", create_thread))
        self.assertEqual("deny", incomplete["hookSpecificOutput"]["permissionDecision"])
        self.assertIn("environment.type=local", incomplete["hookSpecificOutput"]["permissionDecisionReason"])
        native = {"hook_event_name": "PreToolUse", "tool_name": "spawn_agent",
                  "tool_input": {"agent_type": "agentos-menxia", "prompt": "work"}}
        decision = (payload(codex.run("aos_chain_gate.py", native)).get("hookSpecificOutput") or {})
        self.assertEqual("deny", decision.get("permissionDecision"))
        self.assertEqual(
            "[AgentOS chain] 席位用 codex_app create_thread / send_message_to_thread",
            decision.get("permissionDecisionReason"),
        )

    def test_post_tool_is_silent_except_for_structured_governed_edits(self) -> None:
        for harness in self.harnesses:
            ordinary = harness.run(
                "aos_kernel_lint.py",
                {"tool_name": "Edit", "tool_input": {"file_path": "README.md"}},
            )
            self.assertEqual("", ordinary.stdout.strip())
            self.assertEqual("", ordinary.stderr.strip())

            shell = harness.run(
                "aos_kernel_lint.py",
                {
                    "tool_name": "Bash",
                    "tool_input": {"command": "printf text > agent-os/router.md"},
                },
            )
            self.assertEqual("", shell.stdout.strip())
            self.assertEqual("", shell.stderr.strip())

            harness.set_lint(
                exit_code=1,
                message="FAIL agent-os/router.md missing router structure",
            )
            governed = harness.run(
                "aos_kernel_lint.py",
                {"tool_name": "Edit", "tool_input": {"file_path": "agent-os/router.md"}},
            )
            self.assertEqual(2, governed.returncode)
            self.assertIn("agent-os/router.md", governed.stderr)

            harness.set_lint(
                exit_code=1,
                message="FAIL wiki/legacy-note.md has an old project format",
            )
            unrelated = harness.run(
                "aos_kernel_lint.py",
                {"tool_name": "Edit", "tool_input": {"file_path": "agent-os/router.md"}},
            )
            self.assertEqual(0, unrelated.returncode, unrelated.stderr)
            self.assertEqual("", unrelated.stderr.strip())

    def test_many_tools_do_not_repeat_goal_attention(self) -> None:
        codex = self.harnesses[0]
        for index in range(5):
            before = codex.run(
                "aos_chain_gate.py",
                {"hook_event_name": "PreToolUse", "tool_name": "Bash",
                 "tool_input": {"command": f"cat file-{index}"}},
            )
            after = codex.run(
                "aos_kernel_lint.py",
                {"tool_name": "Bash", "tool_input": {"command": f"cat file-{index}"}},
            )
            self.assertEqual("", before.stdout.strip())
            self.assertEqual("", after.stdout.strip())

    def test_pending_long_task_stops_once_then_marks_delivered(self) -> None:
        for harness in self.harnesses:
            harness.bind_relay()
            harness.write_state(done_work())
            first = harness.run("aos_stop_gate.py", {"stop_hook_active": False})
            first_payload = payload(first)
            self.assertEqual("block", first_payload.get("decision"))
            self.assertEqual({"decision", "reason"}, set(first_payload))
            self.assertIn("<agentos_stop_continuation>", first_payload.get("reason", ""))
            self.assertIn("simplest natural language", first_payload.get("reason", ""))

            second = harness.run("aos_stop_gate.py", {"stop_hook_active": True})
            self.assertEqual(0, second.returncode, second.stderr)
            document = json.loads(harness.state_path().read_text(encoding="utf-8"))
            self.assertEqual("delivered", document["active_work"]["report_state"])

            third = harness.run("aos_stop_gate.py", {"stop_hook_active": False})
            self.assertEqual("", third.stdout.strip())

    def test_short_reply_has_no_forced_second_generation(self) -> None:
        for harness in self.harnesses:
            harness.bind_relay()
            result = harness.run("aos_stop_gate.py", {"stop_hook_active": False})
            self.assertEqual(0, result.returncode, result.stderr)
            self.assertEqual("", result.stdout.strip())


if __name__ == "__main__":
    unittest.main()
