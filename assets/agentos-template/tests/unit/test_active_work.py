from __future__ import annotations

import importlib.util
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
MODULE_PATH = ROOT / "agent-os" / "tools" / "aos_active_work.py"
SPEC = importlib.util.spec_from_file_location("aos_active_work_test", MODULE_PATH)
assert SPEC and SPEC.loader
AOS = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(AOS)


def active_state() -> dict:
    return {
        "goal": "Deliver the requested long-task result",
        "done_when": ["result exists", "runtime behavior is verified"],
        "open_items": ["build result", "run runtime check"],
        "next_action": "build result",
        "latest_user_delta": "implement the accepted plan",
        "status": "active",
        "blocker": "",
        "report_state": "not_due",
        "completion": [],
    }


def done_state() -> dict:
    state = active_state()
    state.update(
        open_items=[],
        next_action="",
        status="done",
        report_state="pending",
        completion=[
            {"condition": "result exists", "evidence": ["result.md"]},
            {
                "condition": "runtime behavior is verified",
                "evidence": ["live thread observation"],
            },
        ],
    )
    return state


class ActiveWorkContractTests(unittest.TestCase):
    def test_active_long_task_is_valid(self) -> None:
        self.assertEqual([], AOS.validate(active_state()))

    def test_missing_finish_conditions_fails(self) -> None:
        state = active_state()
        state["done_when"] = []
        self.assertTrue(any("done_when" in item for item in AOS.validate(state)))

    def test_next_action_must_be_open(self) -> None:
        state = active_state()
        state["next_action"] = "unrelated optimization"
        self.assertIn("next_action must be one of open_items", AOS.validate(state))

    def test_done_task_needs_each_condition_exactly_once_with_evidence(self) -> None:
        state = done_state()
        state["completion"].pop()
        problems = AOS.validate(state)
        self.assertTrue(any("every done_when condition" in item for item in problems))

        state = done_state()
        state["completion"][0]["evidence"] = []
        problems = AOS.validate(state)
        self.assertTrue(any("evidence missing" in item for item in problems))

    def test_done_task_cannot_keep_or_add_work(self) -> None:
        state = done_state()
        state["open_items"] = ["nice-to-have cleanup"]
        state["next_action"] = "nice-to-have cleanup"
        self.assertIn("done work cannot have open_items", AOS.validate(state))

    def test_blocked_task_needs_a_real_blocker(self) -> None:
        state = active_state()
        state.update(status="blocked", blocker="", report_state="pending")
        self.assertIn("blocked work must explain the blocker", AOS.validate(state))

    def test_state_round_trip_and_delivery_transition(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "state.json"
            AOS.save(path, done_state())
            loaded, problems = AOS.load(path)
            self.assertEqual([], problems)
            self.assertEqual("pending", loaded["report_state"])
            self.assertEqual([], AOS.mark_delivered(path))
            delivered, problems = AOS.load(path)
            self.assertEqual([], problems)
            self.assertEqual("delivered", delivered["report_state"])

    def test_runtime_sessions_have_distinct_paths(self) -> None:
        root = Path("/project")
        codex = AOS.state_path(root, "codex", "session-a")
        claude = AOS.state_path(root, "claude", "session-a")
        other = AOS.state_path(root, "codex", "session-b")
        self.assertEqual(3, len({codex, claude, other}))


if __name__ == "__main__":
    unittest.main()
