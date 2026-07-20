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

    def set_lint(self, *, exit_code: int) -> None:
        body = (
            "import sys\n"
            + ("print('PASS test lint')\n" if exit_code == 0 else "print('FAIL broken document')\n")
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
            harness.write_state(done_work())
            for source in ("startup", "resume", "clear", "compact"):
                with self.subTest(runtime=harness.runtime, source=source):
                    result = harness.run("aos_session_start.py", {"source": source})
                    self.assertEqual(0, result.returncode, result.stderr)
                    context = additional_context(result)
                    self.assertIn('phase="restore"', context)
                    self.assertIn("Deliver the long-task result", context)
                    self.assertIn(str(harness.state_path()), context)
                    for word in forbidden:
                        self.assertNotIn(word, context)

    def test_user_prompt_reconsiders_every_real_message_but_skips_stop_continuation(self) -> None:
        for harness in self.harnesses:
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
                    "aos_guard_enforcer.py",
                    {"tool_name": "Bash", "tool_input": {"command": command}},
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

    def test_codex_blocks_native_delegation_and_allows_vendored_runner(self) -> None:
        codex = self.harnesses[0]
        native = codex.run(
            "aos_guard_enforcer.py",
            {"tool_name": "Agent", "tool_input": {"prompt": "unused"}},
        )
        decision = (payload(native).get("hookSpecificOutput") or {}).get("permissionDecision")
        self.assertEqual("deny", decision)
        self.assertNotIn('"ask"', native.stdout)

        runner = codex.run(
            "aos_guard_enforcer.py",
            {
                "tool_name": "Bash",
                "tool_input": {
                    "command": "node vendor/claude-dynamic-workflows-codex/runner/bin/run-workflow.js flow.js"
                },
            },
        )
        self.assertEqual("", runner.stdout.strip())

        claude_settings = (ROOT / ".claude" / "settings.json").read_text(encoding="utf-8")
        self.assertNotIn("aos_guard_enforcer.py", claude_settings)
        self.assertIn("Workflow", claude_settings)

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
                    "tool_input": {"command": "printf text > agent-os/boot.md"},
                },
            )
            self.assertEqual("", shell.stdout.strip())
            self.assertEqual("", shell.stderr.strip())

            harness.set_lint(exit_code=1)
            governed = harness.run(
                "aos_kernel_lint.py",
                {"tool_name": "Edit", "tool_input": {"file_path": "agent-os/boot.md"}},
            )
            self.assertEqual(2, governed.returncode)
            self.assertIn("broken document", governed.stderr)

    def test_many_tools_do_not_repeat_goal_attention(self) -> None:
        codex = self.harnesses[0]
        for index in range(5):
            before = codex.run(
                "aos_guard_enforcer.py",
                {"tool_name": "Bash", "tool_input": {"command": f"cat file-{index}"}},
            )
            after = codex.run(
                "aos_kernel_lint.py",
                {"tool_name": "Bash", "tool_input": {"command": f"cat file-{index}"}},
            )
            self.assertEqual("", before.stdout.strip())
            self.assertEqual("", after.stdout.strip())

    def test_pending_long_task_stops_once_then_marks_delivered(self) -> None:
        for harness in self.harnesses:
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
            result = harness.run("aos_stop_gate.py", {"stop_hook_active": False})
            self.assertEqual(0, result.returncode, result.stderr)
            self.assertEqual("", result.stdout.strip())


if __name__ == "__main__":
    unittest.main()
