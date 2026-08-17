"""Chain gate: the three-departments order is enforced on hook-provided identity
and the task ledger, never on model self-report. One module, shared byte-for-byte
by the Claude and Codex hook directories."""
from __future__ import annotations

import importlib.util
import json
import tempfile
import time
import unittest
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


def load(runtime: str):
    path = ROOT / f".{runtime}" / "hooks" / "aos_chain_gate.py"
    spec = importlib.util.spec_from_file_location(f"aos_chain_gate_{runtime}", path)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


GATE = load("claude")
SESSION = "sess-1"
TASK = "demo-task"


class GateCase(unittest.TestCase):
    def setUp(self) -> None:
        temporary = tempfile.TemporaryDirectory(prefix="agentos-gate-")
        self.addCleanup(temporary.cleanup)
        self.root = Path(temporary.name)
        (self.root / "agent-os" / "state" / "tasks").mkdir(parents=True)
        (self.root / "agent-os" / "tools").mkdir(parents=True)
        self.transcript = self.root / "transcript.jsonl"
        self.transcript.write_text("", encoding="utf-8")
        manifest = json.loads((ROOT / "agent-os/skills/seat-skills.json").read_text(encoding="utf-8"))
        manifest_path = self.root / "agent-os/skills/seat-skills.json"
        manifest_path.parent.mkdir(parents=True)
        manifest_path.write_text(json.dumps(manifest), encoding="utf-8")
        for runtime_root in (".agents", ".claude"):
            for names in manifest.values():
                for name in names:
                    path = self.root / runtime_root / "skills" / name / "SKILL.md"
                    path.parent.mkdir(parents=True, exist_ok=True)
                    path.write_text(f"# {name}\n", encoding="utf-8")

    # ---- helpers -----------------------------------------------------------
    def ledger(self, *events: tuple[str, str, str], runtime: str = "claude",
               skills: bool = True, goal: str = "g") -> None:
        path = self.root / "agent-os" / "state" / "tasks" / f"{TASK}.jsonl"
        lines = [json.dumps({"kind": "header", "task_id": TASK, "goal": goal, "done_when": []})]
        if skills:
            for role in ("zhongshu", "menxia", "shangshu", "executor", "yushi"):
                evidence = GATE.expected_skill_evidence(self.root, role, runtime)
                lines.append(json.dumps({"role": role, "kind": "skill_load", "status": "ok",
                                         "text": role, "evidence": evidence}))
        for index, (role, kind, status) in enumerate(events):
            lines.append(json.dumps({"role": role, "kind": kind, "status": status, "text": "t",
                                     "ts": f"2026-08-17T00:00:{index:02d}+00:00"}))
        path.write_text("\n".join(lines) + "\n", encoding="utf-8")
        GATE.bind_session(self.root, runtime, SESSION, TASK)
        if runtime == "codex" and skills:
            GATE.record_seat_thread(self.root, SESSION, "agentos-zhongshu", TASK,
                                    GATE.seat_thread_title(self.root, "agentos-zhongshu", TASK))

    def mapping(self, seat: str, task: str = TASK) -> None:
        path = self.root / "agent-os" / "state" / "sessions" / f"codex-{SESSION}.json"
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps({"seat": seat, "task_id": task}), encoding="utf-8")

    def title(self, seat: str, task: str = TASK) -> str:
        return GATE.seat_thread_title(self.root, seat, task)

    def data(self, event: str, agent_type: str | None = "agentos-zhongshu", **extra) -> dict:
        payload = {
            "hook_event_name": event,
            "session_id": SESSION,
            "cwd": str(self.root),
            "transcript_path": str(self.transcript),
        }
        if agent_type is not None:
            payload["agent_type"] = agent_type
            payload["agent_id"] = "a1"
        payload.update(extra)
        return payload

    def relay(self, runtime: str = "claude", task: str = TASK) -> None:
        GATE.bind_relay(self.root, runtime, SESSION, task)

    def relay_create(self, task: str, goal: str = "帮我看看这个项目", extra: str = "") -> str:
        return f"python3 agent-os/tools/aos_task_record.py create --task {task} --goal '{goal}'{extra}"

    def decide(self, data: dict, runtime: str = "claude"):
        return GATE.decide(data, self.root, runtime)

    def spawn(self, subagent_type: str, caller: str | None) -> dict:
        return self.data("PreToolUse", caller, tool_name="Agent",
                         tool_input={"subagent_type": subagent_type, "prompt": "<a></a><b></b><c></c>"})

    def bash(self, command: str, caller: str | None) -> dict:
        return self.data("PreToolUse", caller, tool_name="Bash", tool_input={"command": command})

    def edit(self, path: str, caller: str | None) -> dict:
        return self.data("PreToolUse", caller, tool_name="Edit",
                         tool_input={"file_path": str(self.root / path), "old_string": "a", "new_string": "b"})

    def create_thread(self, title: str, caller: str | None, event: str = "PreToolUse",
                      response: dict | None = None, environment: str = "local",
                      prompt: str | None = None) -> dict:
        target, task = GATE.seat_from_title(title)
        role = GATE.SEAT_TITLES.get(target, "席位").removesuffix("省")
        if target == "agentos-yushi":
            role = "御史"
        valid_prompt = (f"你是{role}，任务 {task}；读取 .codex/agents/{target}.toml、"
                        "agent-os/skills/seat-skills.json，随后运行 aos_skill_receipt.py。")
        extra = {"tool_name": "codex_app__create_thread",
                 "tool_input": {"title": title, "prompt": prompt or valid_prompt,
                                "target": {"type": "project", "projectId": "project-1",
                                           "environment": {"type": environment}}}}
        if response is not None:
            extra["tool_response"] = response
        return self.data(event, caller, **extra)

    def send_thread(self, thread_id: str, caller: str | None) -> dict:
        return self.data("PreToolUse", caller, tool_name="codex_app__send_message_to_thread",
                         tool_input={"threadId": thread_id, "prompt": "work"})

    def archive_thread(self, thread_id: str, caller: str | None) -> dict:
        return self.data("PreToolUse", caller, tool_name="codex_app__set_thread_archived",
                         tool_input={"threadId": thread_id, "archived": True})

    def user_said(self, text: str) -> None:
        with self.transcript.open("a", encoding="utf-8") as fh:
            fh.write(json.dumps({"type": "user", "message": {"role": "user", "content": text}}) + "\n")

    @staticmethod
    def allowed(decision) -> bool:
        return decision is None or decision.get("hookSpecificOutput", {}).get("permissionDecision") == "allow"

    @staticmethod
    def denied(decision) -> bool:
        return bool(decision) and decision.get("hookSpecificOutput", {}).get("permissionDecision") == "deny"

    # ---- identity ------------------------------------------------------------
    def test_seat_comes_from_hook_agent_type_and_unbound_main_is_nobody(self) -> None:
        self.assertEqual(GATE.seat_of({"agent_type": "agentos-zhongshu", "agent_id": "x"}), "zhongshu")
        self.assertIsNone(GATE.seat_of({}, self.root, "claude"))
        self.assertIsNone(GATE.seat_of({"agent_type": "agentos-entry"}, self.root, "claude"))
        self.assertEqual(GATE.seat_of({"agent_type": "agentos-menxia", "agent_id": "x"}), "menxia")
        self.assertIsNone(GATE.seat_of({"agent_type": "general-purpose", "agent_id": "x"}))
        self.relay()
        self.assertEqual(GATE.seat_of(self.data("PreToolUse", None), self.root, "claude"), "relay")
        self.assertEqual(GATE.current_task(self.root, "claude", SESSION), TASK)

    def test_codex_seat_comes_from_valid_session_mapping_and_unmapped_is_nobody(self) -> None:
        data = self.data("PreToolUse", None)
        self.assertIsNone(GATE.seat_of(data, self.root, "codex"))
        self.mapping("agentos-shangshu")
        self.assertEqual(GATE.seat_of(data, self.root, "codex"), "shangshu")
        self.assertEqual(GATE.current_task(self.root, "codex", SESSION), TASK)
        self.mapping("not-a-seat")
        self.assertIsNone(GATE.seat_of(data, self.root, "codex"))
        self.mapping("agentos-zhongshu")
        self.assertEqual(GATE.seat_of(data, self.root, "codex"), "zhongshu")
        self.relay("codex")
        self.assertEqual(GATE.seat_of(data, self.root, "codex"), "relay")

    def test_unbound_session_is_a_silent_noop_for_every_event(self) -> None:
        self.ledger(("menxia", "comparison", "pass"), ("shangshu", "dispatch", "ok"))
        # the ledger helper binds a task id without a seat: still not on the chain
        for runtime in ("claude", "codex"):
            self.assertIsNone(self.decide(self.edit("src/app.py", None), runtime))
            self.assertIsNone(self.decide(self.bash("echo x > src/app.py", None), runtime))
            self.assertIsNone(self.decide(self.spawn("agentos-menxia", None), runtime))
            self.assertIsNone(self.decide(self.data("Stop", None, stop_hook_active=False), runtime))
            self.assertIsNone(self.decide(self.data("SubagentStop", None, stop_hook_active=False), runtime))
            append = (f"python3 agent-os/tools/aos_task_record.py append --task {TASK} --role zhongshu "
                      "--kind delivery --status completed --text done")
            self.assertIsNone(self.decide(self.bash(append, None), runtime))
        self.assertIsNone(self.decide(self.create_thread(self.title("agentos-menxia"), None), "codex"))
        self.assertIsNone(self.decide(self.send_thread("thread-x", None), "codex"))

    def test_relay_creates_the_zhongshu_thread_on_codex_and_hook_registers_it(self) -> None:
        self.user_said("帮我看看这个项目")
        self.ledger(runtime="claude", goal="帮我看看这个项目")
        self.relay("codex", TASK)
        title = self.title("agentos-zhongshu")
        good = self.create_thread(title, None, prompt=f"你是中书，任务 {TASK}。用户说：帮我看看这个项目")
        self.assertIsNone(self.decide(good, "codex"))
        paraphrased = self.create_thread(title, None, prompt=f"你是中书，任务 {TASK}。用户想检查项目")
        self.assertTrue(self.denied(self.decide(paraphrased, "codex")))
        wrong_task = self.create_thread("中书省｜看看这个项目｜another-task", None, prompt="帮我看看这个项目")
        self.assertTrue(self.denied(self.decide(wrong_task, "codex")))
        post = dict(good, hook_event_name="PostToolUse", tool_response={"threadId": "thread-zhongshu"})
        self.assertIsNone(self.decide(post, "codex"))
        registry = json.loads((self.root / "agent-os/state/seats.json").read_text(encoding="utf-8"))
        self.assertEqual({"task": TASK, "thread": "thread-zhongshu", "title": title},
                         registry["agentos-zhongshu"])
        mapping = json.loads((self.root / "agent-os/state/sessions/codex-thread-zhongshu.json")
                             .read_text(encoding="utf-8"))
        self.assertEqual({"seat": "agentos-zhongshu", "task_id": TASK}, mapping)
        self.assertTrue(self.denied(self.decide(good, "codex")))  # duplicate
        # only the relay talks to 中书, and only in the user's words
        send = self.data("PreToolUse", None, tool_name="codex_app__send_message_to_thread",
                         tool_input={"threadId": "thread-zhongshu", "prompt": "用户补充：帮我看看这个项目"})
        self.assertIsNone(self.decide(send, "codex"))
        reworded = dict(send, tool_input={"threadId": "thread-zhongshu", "prompt": "用户想让你检查"})
        self.assertTrue(self.denied(self.decide(reworded, "codex")))
        self.assertTrue(self.denied(self.decide(self.send_thread("thread-zhongshu", "agentos-shangshu"), "codex")))
        # the relay never talks to other seats, never writes
        self.decide(self.create_thread(self.title("agentos-menxia"), None, "PostToolUse", {"threadId": "thread-menxia"}), "codex")
        self.mapping("agentos-zhongshu", TASK)
        self.decide(self.create_thread(self.title("agentos-menxia"), None, "PostToolUse", {"threadId": "thread-menxia"}), "codex")
        self.relay("codex", TASK)
        self.assertTrue(self.denied(self.decide(self.send_thread("thread-menxia", None), "codex")))
        self.assertTrue(self.denied(self.decide(self.edit("src/app.py", None), "codex")))
        self.assertTrue(self.denied(self.decide(self.bash("echo x > src/app.py", None), "codex")))
        self.assertIsNone(self.decide(self.data("Stop", None, stop_hook_active=False), "codex"))

    def test_relay_spawns_zhongshu_on_claude_with_the_users_words(self) -> None:
        self.user_said("帮我看看这个项目")
        self.ledger(goal="帮我看看这个项目")
        self.relay("claude", TASK)
        good = self.data("PreToolUse", None, tool_name="Agent",
                         tool_input={"subagent_type": "agentos-zhongshu", "prompt": "<a></a><b></b><c>帮我看看这个项目</c>"})
        decision = self.decide(good)
        self.assertTrue(self.allowed(decision))
        self.assertEqual(self.title("agentos-zhongshu"), decision["hookSpecificOutput"]["updatedInput"]["description"])
        bad = dict(good, tool_input={"subagent_type": "agentos-zhongshu", "prompt": "<a></a><b></b><c>检查项目</c>"})
        self.assertTrue(self.denied(self.decide(bad)))
        self.assertTrue(self.denied(self.decide(self.spawn("agentos-menxia", None))))
        self.assertTrue(self.denied(self.decide(self.spawn("agentos-zhongshu", "agentos-shangshu"))))

    def test_completed_delivery_post_hook_unbinds_relay_on_both_runtimes(self) -> None:
        for runtime in ("claude", "codex"):
            with self.subTest(runtime=runtime):
                self.ledger(runtime=runtime)
                GATE.bind_relay(self.root, runtime, "relay-main", TASK)
                delivery = (f"python3 agent-os/tools/aos_task_record.py append --task {TASK} "
                            "--role zhongshu --kind delivery --status completed --text done")
                post = self.data("PostToolUse", "agentos-zhongshu", tool_name="Bash",
                                 tool_input={"command": delivery}, tool_response={"ok": True})
                self.assertIsNone(self.decide(post, runtime))
                mapping = json.loads((self.root / "agent-os/state/sessions" /
                                      f"{runtime}-relay-main.json").read_text(encoding="utf-8"))
                self.assertFalse(mapping["bound"])

    # ---- ledger identity -----------------------------------------------------
    def test_ledger_append_with_foreign_role_is_denied(self) -> None:
        self.ledger()
        cmd = f"python3 agent-os/tools/aos_task_record.py append --task {TASK} --role menxia --kind comparison --status pass --text ok"
        self.assertTrue(self.denied(self.decide(self.bash(cmd, "agentos-zhongshu"))))

    def test_ledger_append_with_own_role_is_allowed_and_binds_session(self) -> None:
        self.ledger()
        cmd = f"python3 agent-os/tools/aos_task_record.py append --task {TASK} --role menxia --kind comparison --status pass --text ok"
        self.assertIsNone(self.decide(self.bash(cmd, "agentos-menxia")))
        self.assertEqual(GATE.current_task(self.root, "claude", SESSION), TASK)

    def test_relay_create_binds_the_session_and_carries_only_the_users_words(self) -> None:
        self.user_said("帮我看看这个项目")
        task = "t20260817-0930-health"
        self.assertTrue(self.denied(self.decide(self.bash(self.relay_create(task), "agentos-shangshu"))))
        self.assertTrue(self.denied(self.decide(self.bash(self.relay_create(task), "agentos-zhongshu"))))
        bad_id = self.decide(self.bash(self.relay_create("agentos-runtime-audit"), None))
        self.assertTrue(self.denied(bad_id))
        self.assertIn("t20260817", bad_id["hookSpecificOutput"]["permissionDecisionReason"])
        with_contract = self.bash(self.relay_create(task, extra=" --done-when 'a;;b'"), None)
        self.assertTrue(self.denied(self.decide(with_contract)))
        reworded = self.bash(self.relay_create(task, goal="检查项目健康"), None)
        self.assertTrue(self.denied(self.decide(reworded)))
        self.assertIsNone(GATE.seat_of(self.data("PreToolUse", None), self.root, "claude"))
        self.assertIsNone(self.decide(self.bash(self.relay_create(task), None)))
        self.assertEqual("relay", GATE.seat_of(self.data("PreToolUse", None), self.root, "claude"))
        self.assertEqual(task, GATE.current_task(self.root, "claude", SESSION))
        # relay ledger lines: only its four kinds, user_message verbatim
        base = f"python3 agent-os/tools/aos_task_record.py append --task {task} --role relay"
        self.assertIsNone(self.decide(self.bash(base + " --kind user_message --status ok --text '帮我看看这个项目'", None)))
        self.assertTrue(self.denied(self.decide(self.bash(base + " --kind user_message --status ok --text '检查项目'", None))))
        self.assertTrue(self.denied(self.decide(self.bash(base + " --kind delivery --status ok --text x", None))))
        forged = f"python3 agent-os/tools/aos_task_record.py append --task {task} --role zhongshu --kind delivery --status completed --text x"
        self.assertTrue(self.denied(self.decide(self.bash(forged, None))))
        # a subagent can never start or resume the chain
        self.assertTrue(self.denied(self.decide(self.bash(self.relay_create("t20260817-0931"), "general-purpose"))))

    def test_relay_pause_and_resume_unbind_and_rebind(self) -> None:
        self.user_said("帮我看看这个项目")
        task = "t20260817-0930"
        self.assertIsNone(self.decide(self.bash(self.relay_create(task), None)))
        (self.root / "agent-os/state/tasks" / f"{task}.jsonl").write_text(
            json.dumps({"kind": "header", "task_id": task}) + "\n", encoding="utf-8")
        base = f"python3 agent-os/tools/aos_task_record.py append --task {task} --role relay"
        self.assertIsNone(self.decide(self.bash(base + " --kind pause --status ok --text 用户喊停", None)))
        self.assertIsNone(GATE.seat_of(self.data("PreToolUse", None), self.root, "claude"))
        # unbound again: the session is plain chat
        self.assertIsNone(self.decide(self.edit("src/app.py", None)))
        self.assertTrue(self.denied(self.decide(self.bash(base + " --kind user_message --status ok --text '帮我看看这个项目'", None))))
        missing = self.decide(self.bash(base.replace(task, "t20260817-0000") + " --kind resume --status ok --text 继续", None))
        self.assertTrue(self.denied(missing))
        self.assertIsNone(self.decide(self.bash(base + " --kind resume --status ok --text 继续", None)))
        self.assertEqual("relay", GATE.seat_of(self.data("PreToolUse", None), self.root, "claude"))
        # delivery ends the binding; a later resume brings it back
        with (self.root / "agent-os/state/tasks" / f"{task}.jsonl").open("a", encoding="utf-8") as fh:
            fh.write(json.dumps({"role": "zhongshu", "kind": "delivery", "status": "completed",
                                 "ts": datetime.fromtimestamp(time.time(), timezone.utc).isoformat()}) + "\n")
        self.assertIsNone(GATE.seat_of(self.data("PreToolUse", None), self.root, "claude"))
        time.sleep(0.02)
        self.assertIsNone(self.decide(self.bash(base + " --kind resume --status ok --text 继续", None)))
        self.assertEqual("relay", GATE.seat_of(self.data("PreToolUse", None), self.root, "claude"))

    def test_phase_work_requires_hashed_role_skill_receipt(self) -> None:
        self.ledger(runtime="codex", skills=False)
        self.mapping("agentos-zhongshu")
        cmd = (f"python3 agent-os/tools/aos_task_record.py append --task {TASK} --role zhongshu "
               "--kind user_message --status ok --text hello")
        self.assertTrue(self.denied(self.decide(self.bash(cmd, None), "codex")))
        forged = cmd.replace("--kind user_message", "--kind skill_load")
        self.assertTrue(self.denied(self.decide(self.bash(forged, None), "codex")))
        receipt = (f"python3 agent-os/tools/aos_skill_receipt.py --task {TASK} "
                   "--role zhongshu --runtime codex")
        self.assertIsNone(self.decide(self.bash(receipt, None), "codex"))
        path = self.root / "agent-os/state/tasks" / f"{TASK}.jsonl"
        with path.open("a", encoding="utf-8") as stream:
            stream.write(json.dumps({"role": "zhongshu", "kind": "skill_load", "status": "ok",
                                     "evidence": GATE.expected_skill_evidence(
                                         self.root, "zhongshu", "codex")}) + "\n")
        self.assertIsNone(self.decide(self.bash(cmd, None), "codex"))

    def test_failed_or_blocked_terminal_records_do_not_require_a_skill_receipt(self) -> None:
        self.ledger(skills=False)
        kinds = {
            "agentos-zhongshu": ("zhongshu", "delivery"),
            "agentos-shangshu": ("shangshu", "integration"),
            "agentos-executor": ("executor", "execution_result"),
        }
        for actor, (role, kind) in kinds.items():
            for status in ("failed", "blocked"):
                with self.subTest(role=role, status=status):
                    command = (
                        "python3 agent-os/tools/aos_task_record.py append "
                        f"--task {TASK} --role {role} --kind {kind} "
                        f"--status {status} --text init-failed"
                    )
                    self.assertIsNone(self.decide(self.bash(command, actor)))

        completed = (
            "python3 agent-os/tools/aos_task_record.py append "
            f"--task {TASK} --role executor --kind execution_result "
            "--status completed --text done"
        )
        self.assertTrue(self.denied(self.decide(self.bash(completed, "agentos-executor"))))

        for actor, (role, kind) in kinds.items():
            self.ledger((role, kind, "blocked"), skills=False)
            event = "Stop" if role == "zhongshu" else "SubagentStop"
            self.assertIsNone(self.decide(self.data(event, actor, stop_hook_active=False)))

    def test_empty_phase_evidence_is_denied_but_empty_failure_terminal_still_lands(self) -> None:
        self.ledger()
        empty_review = (f"python3 agent-os/tools/aos_task_record.py append --task {TASK} "
                        "--role menxia --kind independent_review --status ok --text ''")
        decision = self.decide(self.bash(empty_review, "agentos-menxia"))
        self.assertTrue(self.denied(decision))
        self.assertIn("非空 --text", decision["hookSpecificOutput"]["permissionDecisionReason"])
        empty_failure = (f"python3 agent-os/tools/aos_task_record.py append --task {TASK} "
                         "--role executor --kind execution_result --status blocked --text ''")
        self.assertIsNone(self.decide(self.bash(empty_failure, "agentos-executor")))

    # ---- spawn order -------------------------------------------------------
    def test_shangshu_needs_menxia_pass(self) -> None:
        self.ledger(("menxia", "independent_review", "ok"))
        self.assertTrue(self.denied(self.decide(self.spawn("agentos-shangshu", "agentos-zhongshu"))))
        self.ledger(("menxia", "independent_review", "ok"), ("menxia", "comparison", "pass"))
        self.assertTrue(self.allowed(self.decide(self.spawn("agentos-shangshu", "agentos-zhongshu"))))

    def test_executor_is_spawned_by_shangshu_after_dispatch_only(self) -> None:
        self.ledger(("menxia", "comparison", "pass"))
        self.assertTrue(self.denied(self.decide(self.spawn("agentos-executor", "agentos-zhongshu"))))
        self.assertTrue(self.denied(self.decide(self.spawn("agentos-executor", "agentos-shangshu"))))
        self.ledger(("menxia", "comparison", "pass"), ("shangshu", "dispatch", "ok"))
        self.assertTrue(self.allowed(self.decide(self.spawn("agentos-executor", "agentos-shangshu"))))
        self.assertTrue(self.denied(self.decide(self.spawn("agentos-executor", "agentos-zhongshu"))))

    def test_menxia_and_yushi_are_spawned_by_zhongshu_only(self) -> None:
        self.ledger()
        self.assertTrue(self.allowed(self.decide(self.spawn("agentos-menxia", "agentos-zhongshu"))))
        self.assertTrue(self.denied(self.decide(self.spawn("agentos-menxia", "agentos-shangshu"))))
        self.assertTrue(self.allowed(self.decide(self.spawn("agentos-yushi", "agentos-zhongshu"))))

    def test_codex_create_thread_post_registers_seat_and_session(self) -> None:
        self.ledger(runtime="codex")
        title = self.title("agentos-menxia")
        self.assertIsNone(self.decide(self.create_thread(title, None), "codex"))
        post = self.create_thread(title, None, "PostToolUse",
                                  {"content": [{"text": json.dumps({"threadId": "thread-menxia"})}]})
        self.assertIsNone(self.decide(post, "codex"))
        registry = json.loads((self.root / "agent-os/state/seats.json").read_text(encoding="utf-8"))
        self.assertEqual({"task": TASK, "thread": "thread-menxia", "title": title},
                         registry["agentos-menxia"])
        mapping = json.loads((self.root / "agent-os/state/sessions/codex-thread-menxia.json")
                             .read_text(encoding="utf-8"))
        self.assertEqual({"seat": "agentos-menxia", "task_id": TASK}, mapping)

    def test_codex_seat_create_requires_local_environment_and_skill_prompt(self) -> None:
        self.ledger(runtime="codex")
        title = self.title("agentos-menxia")
        self.assertTrue(self.denied(self.decide(
            self.create_thread(title, None, environment="worktree"), "codex")))
        self.assertTrue(self.denied(self.decide(
            self.create_thread(title, None, prompt="你是门下，任务 demo-task"), "codex")))
        self.assertIsNone(self.decide(self.create_thread(title, None), "codex"))

    def test_codex_duplicate_create_thread_is_denied_with_existing_thread(self) -> None:
        self.ledger(runtime="codex")
        title = self.title("agentos-menxia")
        self.decide(self.create_thread(title, None, "PostToolUse", {"threadId": "thread-menxia"}), "codex")
        decision = self.decide(self.create_thread(title, None), "codex")
        self.assertTrue(self.denied(decision))
        reason = decision["hookSpecificOutput"]["permissionDecisionReason"]
        self.assertIn("thread-menxia", reason)
        self.assertIn("send_message_to_thread", reason)
        another = self.decide(self.create_thread("门下省｜另一个任务｜another-task", None), "codex")
        self.assertTrue(self.denied(another))
        self.assertIn("标题必须是", another["hookSpecificOutput"]["permissionDecisionReason"])

    def test_codex_send_message_to_thread_enforces_seat_order(self) -> None:
        self.ledger(runtime="codex")
        for title, thread_id in ((self.title("agentos-menxia"), "thread-menxia"),
                                 (self.title("agentos-shangshu"), "thread-shangshu"),
                                 (self.title("agentos-yushi"), "thread-yushi")):
            self.decide(self.create_thread(title, None, "PostToolUse", {"threadId": thread_id}), "codex")
        self.mapping("agentos-shangshu")
        self.decide(self.create_thread(self.title("agentos-executor"), None, "PostToolUse",
                                       {"threadId": "thread-executor"}), "codex")

        self.mapping("agentos-zhongshu")
        self.assertIsNone(self.decide(self.send_thread("thread-menxia", None), "codex"))
        self.assertTrue(self.denied(self.decide(self.send_thread("thread-shangshu", None), "codex")))
        self.ledger(("menxia", "comparison", "pass"), runtime="codex")
        self.assertIsNone(self.decide(self.send_thread("thread-shangshu", None), "codex"))

        self.mapping("agentos-shangshu")
        self.assertTrue(self.denied(self.decide(self.send_thread("thread-executor", None), "codex")))
        self.ledger(("menxia", "comparison", "pass"), ("shangshu", "dispatch", "ok"),
                    runtime="codex")
        self.mapping("agentos-shangshu")
        self.assertIsNone(self.decide(self.send_thread("thread-executor", None), "codex"))
        self.assertTrue(self.denied(self.decide(self.send_thread("thread-menxia", None), "codex")))

    def test_codex_archives_only_previous_delivered_task_by_zhongshu(self) -> None:
        self.ledger(("zhongshu", "delivery", "completed"), runtime="codex")
        self.decide(self.create_thread(self.title("agentos-menxia"), None, "PostToolUse",
                                       {"threadId": "thread-menxia"}), "codex")
        self.assertTrue(self.denied(self.decide(
            self.archive_thread("thread-menxia", None), "codex")))
        GATE.bind_session(self.root, "codex", SESSION, "next-task")
        self.assertTrue(self.denied(self.decide(
            self.archive_thread("thread-menxia", "agentos-shangshu"), "codex")))
        self.mapping("agentos-zhongshu", "next-task")
        self.assertIsNone(self.decide(self.archive_thread("thread-menxia", None), "codex"))

    # ---- writes ------------------------------------------------------------
    def test_project_writes_need_executor_identity_and_a_dispatch(self) -> None:
        self.ledger(("menxia", "comparison", "pass"))
        self.assertTrue(self.denied(self.decide(self.edit("src/app.py", "agentos-executor"))))
        self.ledger(("menxia", "comparison", "pass"), ("shangshu", "dispatch", "ok"))
        self.assertIsNone(self.decide(self.edit("src/app.py", "agentos-executor")))
        self.assertTrue(self.denied(self.decide(self.edit("src/app.py", "agentos-zhongshu"))))
        self.assertTrue(self.denied(self.decide(self.edit("src/app.py", "agentos-shangshu"))))
        self.assertTrue(self.denied(self.decide(self.edit("src/app.py", "agentos-menxia"))))
        mapping = self.root / "agent-os/state/sessions" / f"codex-{SESSION}.json"
        mapping.write_text(json.dumps({"seat": "agentos-executor"}), encoding="utf-8")
        self.assertIsNone(self.decide(self.edit("src/app.py", None), "codex"))

    def test_state_files_and_writable_task_yushi_memory_are_writable(self) -> None:
        self.ledger()
        self.assertIsNone(self.decide(self.edit("agent-os/state/active-work/x.json", "agentos-zhongshu")))
        self.assertIsNone(self.decide(self.edit("wiki/errors/2026-01-01_001.md", "agentos-yushi")))
        self.assertTrue(self.denied(self.decide(self.edit("src/app.py", "agentos-yushi"))))

    def test_read_only_task_keeps_yushi_silent_outside_state(self) -> None:
        self.ledger(goal="请只读检查，不要修改项目文件")
        self.assertTrue(self.denied(self.decide(
            self.edit("wiki/errors/2026-01-01_001.md", "agentos-yushi"))))
        self.assertTrue(self.denied(self.decide(
            self.bash("python3 agent-os/tools/aos-lint.py --fix-memory-views", "agentos-yushi"))))
        record = (f"python3 agent-os/tools/aos_task_record.py append --task {TASK} --role yushi "
                  "--kind error_record --status deferred --text 'read-only task'")
        self.assertIsNone(self.decide(self.bash(record, "agentos-yushi")))

    def test_bash_write_shapes_are_denied_for_non_executors_and_reads_never(self) -> None:
        self.ledger(("menxia", "comparison", "pass"), ("shangshu", "dispatch", "ok"))
        self.assertTrue(self.denied(self.decide(self.bash("echo x > src/app.py", "agentos-zhongshu"))))
        self.assertTrue(self.denied(self.decide(self.bash("sed -i '' 's/a/b/' src/app.py", "agentos-shangshu"))))
        self.assertIsNone(self.decide(self.bash("git status && grep -rn foo src", "agentos-zhongshu")))
        self.assertIsNone(self.decide(self.bash("echo x > src/app.py", "agentos-executor")))

    # ---- bypass ------------------------------------------------------------
    def test_bypass_is_menxias_call_with_a_verbatim_user_quote(self) -> None:
        self.ledger()
        cmd = (f"python3 agent-os/tools/aos_task_record.py append --task {TASK} --role zhongshu "
               f"--kind bypass --status ok --text '这个你自己直接弄一下'")
        self.user_said("好，这个你自己直接弄一下，不用走流程")
        # the actor (zhongshu) can never grant itself a bypass, even quoting the user
        self.assertTrue(self.denied(self.decide(self.bash(cmd, "agentos-zhongshu"))))
        cmd_menxia = cmd.replace("--role zhongshu", "--role menxia")
        # menxia may, but only with the user's verbatim words
        bad = cmd_menxia.replace("这个你自己直接弄一下", "帮我看看当前项目")
        self.assertTrue(self.denied(self.decide(self.bash(bad, "agentos-menxia"))))
        self.assertIsNone(self.decide(self.bash(cmd_menxia, "agentos-menxia")))
        self.ledger(("menxia", "bypass", "ok"))
        self.assertIsNone(self.decide(self.edit("src/app.py", "agentos-zhongshu")))
        self.assertIsNone(self.decide(self.bash("echo x > src/app.py", "agentos-zhongshu")))
        # even under a bypass 中书 records its round before ending the turn
        self.assertEqual("block", self.decide(self.data("Stop", "agentos-zhongshu", stop_hook_active=False)).get("decision"))
        self.ledger(("menxia", "bypass", "ok"), ("zhongshu", "delivery", "completed"))
        self.assertIsNone(self.decide(self.data("Stop", "agentos-zhongshu", stop_hook_active=False)))
        # a zhongshu-written bypass line in the ledger counts for nothing
        self.ledger(("zhongshu", "bypass", "ok"))
        self.assertTrue(self.denied(self.decide(self.edit("src/app.py", "agentos-zhongshu"))))

    # ---- stop --------------------------------------------------------------
    def test_zhongshu_cannot_stop_before_recording_the_latest_user_increment(self) -> None:
        self.assertIsNone(self.decide(self.data("Stop", "agentos-zhongshu", stop_hook_active=False)))  # no task
        self.ledger(("zhongshu", "candidate", "ok"), ("relay", "user_message", "ok"))
        for event in ("Stop", "SubagentStop"):
            decision = self.decide(self.data(event, "agentos-zhongshu", stop_hook_active=False))
            self.assertEqual("block", decision.get("decision"), event)
            self.assertIn("append --role zhongshu", decision.get("reason", ""))
        self.ledger(("relay", "user_message", "ok"), ("zhongshu", "candidate", "ok"))
        self.assertIsNone(self.decide(self.data("Stop", "agentos-zhongshu", stop_hook_active=False)))
        self.assertIsNone(self.decide(self.data("SubagentStop", "agentos-zhongshu", stop_hook_active=False)))
        self.ledger(("relay", "user_message", "ok"), ("zhongshu", "delivery", "completed"),
                    ("relay", "user_message", "ok"))
        self.assertIsNone(self.decide(self.data("Stop", "agentos-zhongshu", stop_hook_active=False)))
        # codex: the 中书 thread is identified by its registration, same rule
        self.ledger(("zhongshu", "candidate", "ok"), ("relay", "user_message", "ok"), runtime="codex")
        self.assertEqual("block", self.decide(self.data("Stop", None, stop_hook_active=False), "codex").get("decision"))

    def test_stop_never_loops_and_terminal_failure_releases(self) -> None:
        self.ledger(("menxia", "comparison", "pass"))
        self.assertIsNone(self.decide(self.data("Stop", "agentos-zhongshu", stop_hook_active=True)))
        self.ledger(("menxia", "comparison", "pass"), ("shangshu", "dispatch", "ok"),
                    ("shangshu", "execution_result", "blocked"))
        self.assertIsNone(self.decide(self.data("Stop", "agentos-zhongshu", stop_hook_active=False)))

    def test_executor_cannot_stop_without_terminal_record(self) -> None:
        self.ledger(("menxia", "comparison", "pass"), ("shangshu", "dispatch", "ok"))
        decision = self.decide(self.data("SubagentStop", "agentos-executor", stop_hook_active=False))
        self.assertEqual(decision.get("decision"), "block")
        self.assertIsNone(self.decide(self.data("SubagentStop", "agentos-executor", stop_hook_active=True)))
        self.ledger(("menxia", "comparison", "pass"), ("shangshu", "dispatch", "ok"),
                    ("executor", "execution_result", "completed"))
        self.assertIsNone(self.decide(self.data("SubagentStop", "agentos-executor", stop_hook_active=False)))

    def test_codex_executor_stop_uses_seat_terminal_gate(self) -> None:
        self.ledger(("menxia", "comparison", "pass"), ("shangshu", "dispatch", "ok"),
                    runtime="codex")
        self.mapping("agentos-executor")
        decision = self.decide(self.data("Stop", None, stop_hook_active=False), "codex")
        self.assertEqual("block", decision.get("decision"))
        self.assertIn("execution_result", decision.get("reason", ""))
        self.ledger(("menxia", "comparison", "pass"), ("shangshu", "dispatch", "ok"),
                    ("executor", "execution_result", "completed"), runtime="codex")
        self.mapping("agentos-executor")
        self.assertIsNone(self.decide(self.data("Stop", None, stop_hook_active=False), "codex"))

    def test_shangshu_cannot_integrate_or_stop_before_executor_result(self) -> None:
        self.ledger(("menxia", "comparison", "pass"), ("shangshu", "dispatch", "ok"))
        integrate = (f"python3 agent-os/tools/aos_task_record.py append --task {TASK} --role shangshu "
                     "--kind integration --status completed --text done")
        self.assertTrue(self.denied(self.decide(self.bash(integrate, "agentos-shangshu"))))
        decision = self.decide(self.data("SubagentStop", "agentos-shangshu", stop_hook_active=False))
        self.assertEqual("block", decision.get("decision"))
        self.assertIn("execution_result", decision.get("reason", ""))
        self.ledger(("menxia", "comparison", "pass"), ("shangshu", "dispatch", "ok"),
                    ("executor", "execution_result", "completed"))
        self.assertEqual("block", self.decide(
            self.data("SubagentStop", "agentos-shangshu", stop_hook_active=False)).get("decision"))
        self.assertIsNone(self.decide(self.bash(integrate, "agentos-shangshu")))

    def test_codex_apply_patch_and_native_spawn_shapes_are_gated(self) -> None:
        self.ledger(("menxia", "comparison", "pass"))
        patch = "*** Begin Patch\n*** Add File: src/new.py\n+x\n*** End Patch"
        data = self.data("PreToolUse", "agentos-executor", tool_name="apply_patch",
                         tool_input={"command": patch})
        self.assertTrue(self.denied(self.decide(data)))
        self.ledger(("menxia", "comparison", "pass"), ("shangshu", "dispatch", "ok"))
        self.assertIsNone(self.decide(data))
        self.mapping("agentos-zhongshu")
        for tool in ("spawn_agent", "collaborationspawn_agent"):
            spawn = self.data("PreToolUse", None, tool_name=tool,
                              tool_input={"agent_type": "agentos-executor", "message": "m"})
            decision = self.decide(spawn, "codex")
            self.assertTrue(self.denied(decision))
            self.assertEqual(decision["hookSpecificOutput"]["permissionDecisionReason"],
                             "[AgentOS chain] 席位用 codex_app create_thread / send_message_to_thread")
        spawn_by_shangshu = self.data("PreToolUse", "agentos-shangshu", tool_name="collaborationspawn_agent",
                                      tool_input={"agent_type": "agentos-executor", "message": "m"})
        self.assertTrue(self.denied(self.decide(spawn_by_shangshu, "codex")))

    def test_claude_agent_spawn_and_retitle_path_is_unchanged(self) -> None:
        self.ledger(("menxia", "comparison", "pass"), ("shangshu", "dispatch", "ok"))
        data = self.spawn("agentos-executor", "agentos-shangshu")
        decision = self.decide(data, "claude")
        self.assertTrue(self.allowed(decision))
        self.assertEqual(decision["hookSpecificOutput"]["updatedInput"]["description"],
                         self.title("agentos-executor"))

    def test_seat_spawns_show_role_readable_task_and_id(self) -> None:
        self.ledger(("menxia", "comparison", "pass"), ("shangshu", "dispatch", "ok"))
        codex = self.data("PreToolUse", "agentos-zhongshu", tool_name="collaborationspawn_agent",
                          tool_input={"agent_type": "agentos-menxia", "message": "m", "task_name": "review the file"})
        out = self.decide(codex)["hookSpecificOutput"]
        self.assertEqual("allow", out["permissionDecision"])
        # Codex agent names allow only [a-z0-9_]: role + task, ascii-safe
        self.assertEqual("menxia_demo_task", out["updatedInput"]["task_name"])
        already = dict(codex, tool_input={"agent_type": "agentos-menxia", "message": "m", "task_name": "menxia_demo_task"})
        self.assertIsNone(self.decide(already))
        claude = self.data("PreToolUse", "agentos-shangshu", tool_name="Agent",
                           tool_input={"subagent_type": "agentos-executor", "prompt": "<a></a><b></b><c></c>",
                                       "description": "write node 1"})
        out = self.decide(claude)["hookSpecificOutput"]
        self.assertEqual(self.title("agentos-executor"), out["updatedInput"]["description"])
        self.assertEqual("<a></a><b></b><c></c>", out["updatedInput"]["prompt"])

    def test_hook_copies_are_identical_across_runtimes(self) -> None:
        claude = (ROOT / ".claude" / "hooks" / "aos_chain_gate.py").read_bytes()
        codex = (ROOT / ".codex" / "hooks" / "aos_chain_gate.py").read_bytes()
        self.assertEqual(claude, codex)


if __name__ == "__main__":
    unittest.main()
