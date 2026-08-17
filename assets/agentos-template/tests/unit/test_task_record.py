from __future__ import annotations

import contextlib
import importlib.util
import io
import json
import os
import subprocess
import sys
import tempfile
import threading
import unittest
from datetime import datetime
from pathlib import Path
from unittest import mock


ROOT = Path(__file__).resolve().parents[2]
MODULE_PATH = ROOT / "agent-os" / "tools" / "aos_task_record.py"
SPEC = importlib.util.spec_from_file_location("aos_task_record_test", MODULE_PATH)
assert SPEC and SPEC.loader
AOS = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(AOS)


class TaskRecordTestCase(unittest.TestCase):
    """The record is a dumb append-only log: it must never refuse or lose a write."""

    def setUp(self) -> None:
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.root = Path(temporary.name)
        environment = mock.patch.dict(os.environ, {"AOS_ROOT": str(self.root)})
        environment.start()
        self.addCleanup(environment.stop)
        self.tasks = self.root / "agent-os" / "state" / "tasks"

    def cli(self, *argv: str) -> tuple[int, str]:
        stream = io.StringIO()
        with contextlib.redirect_stdout(stream):
            code = AOS.main(list(argv))
        return code, stream.getvalue()

    def lines(self, task_id: str) -> list[dict]:
        text = (self.tasks / f"{task_id}.jsonl").read_text(encoding="utf-8")
        return [json.loads(line) for line in text.splitlines() if line.strip()]

    def header(self, task_id: str) -> dict:
        headers = [line for line in self.lines(task_id) if line.get("kind") == "header"]
        self.assertTrue(headers, f"no header line in {task_id}")
        return headers[-1]

    def events(self, task_id: str) -> list[dict]:
        return [line for line in self.lines(task_id) if line.get("kind") != "header"]


class CreateTests(TaskRecordTestCase):
    def test_create_writes_the_record_header(self) -> None:
        code, _ = self.cli("create", "--task", "T-1", "--goal", "Fix order totals")
        self.assertEqual(0, code)
        header = self.header("T-1")
        self.assertEqual("T-1", header["task_id"])
        self.assertEqual("Fix order totals", header["title"])
        self.assertEqual("Fix order totals", header["goal"])
        self.assertEqual([], header["done_when"])
        self.assertEqual([], self.events("T-1"))
        datetime.fromisoformat(header["ts"])

    def test_title_is_short_readable_and_keeps_the_task_id_separate(self) -> None:
        goal = "$agentos 请帮我检查项目根目录是否存在 README.md；存在就报告首行"
        self.cli("create", "--task", "t20260817-0611", "--goal", goal)
        self.assertEqual("检查项目根目录是否存在 README.md", self.header("t20260817-0611")["title"])
        code, output = self.cli("title", "--task", "t20260817-0611")
        self.assertEqual(0, code)
        self.assertEqual("检查项目根目录是否存在 README.md\n", output)

    def test_title_truncation_is_deterministic(self) -> None:
        title = AOS.task_title("请" + "很长的任务" * 20)
        self.assertEqual(AOS.TITLE_LIMIT, len(title))
        self.assertTrue(title.endswith("…"))

    def test_done_when_splits_on_double_semicolon(self) -> None:
        self.cli(
            "create",
            "--task",
            "T-1",
            "--goal",
            "Ship it",
            "--done-when",
            "tests pass;;lint clean;;smoke run recorded",
        )
        self.assertEqual(
            ["tests pass", "lint clean", "smoke run recorded"],
            self.header("T-1")["done_when"],
        )

    def test_second_create_preserves_existing_events(self) -> None:
        """A repeated create appends another header; the latest one wins on read."""
        self.cli("create", "--task", "T-1", "--goal", "First goal")
        self.cli(
            "append",
            "--task",
            "T-1",
            "--role",
            "executor",
            "--kind",
            "execution_result",
            "--status",
            "done",
            "--text",
            "first pass finished",
        )
        code, _ = self.cli("create", "--task", "T-1", "--goal", "Second goal")
        self.assertEqual(0, code)
        events = self.events("T-1")
        self.assertEqual(1, len(events))
        self.assertEqual("first pass finished", events[0]["text"])
        self.assertEqual("Second goal", self.header("T-1")["goal"])
        _, output = self.cli("show", "--task", "T-1")
        self.assertIn("goal: Second goal", output)
        self.assertIn("first pass finished", output)


class AppendTests(TaskRecordTestCase):
    def test_append_to_existing_task_lands_the_event(self) -> None:
        self.cli("create", "--task", "T-1", "--goal", "Fix order totals")
        code, _ = self.cli(
            "append",
            "--task",
            "T-1",
            "--role",
            "reviewer",
            "--kind",
            "review_verdict",
            "--status",
            "approved",
            "--text",
            "scope matches the request",
            "--evidence",
            "tests/unit/test_task_record.py",
        )
        self.assertEqual(0, code)
        event = self.events("T-1")[0]
        self.assertEqual("reviewer", event["role"])
        self.assertEqual("review_verdict", event["kind"])
        self.assertEqual("approved", event["status"])
        self.assertEqual("scope matches the request", event["text"])
        self.assertEqual("tests/unit/test_task_record.py", event["evidence"])
        stamp = datetime.fromisoformat(event["ts"])
        self.assertIsNotNone(stamp.tzinfo)
        self.assertEqual(0, stamp.utcoffset().total_seconds())

    def test_blocked_result_lands_on_a_missing_task(self) -> None:
        code, _ = self.cli(
            "append",
            "--task",
            "never-created",
            "--role",
            "executor",
            "--kind",
            "execution_result",
            "--status",
            "blocked",
            "--text",
            "cannot reach the database",
        )
        self.assertEqual(0, code)
        events = self.events("never-created")
        self.assertEqual(1, len(events))
        self.assertEqual("blocked", events[0]["status"])
        self.assertEqual("cannot reach the database", events[0]["text"])
        _, output = self.cli("show", "--task", "never-created")
        self.assertIn("task: never-created", output)
        self.assertIn("cannot reach the database", output)

    def test_append_without_evidence_keeps_a_null(self) -> None:
        self.cli(
            "append",
            "--task",
            "T-1",
            "--role",
            "executor",
            "--kind",
            "note",
            "--status",
            "info",
            "--text",
            "no evidence yet",
        )
        self.assertIsNone(self.events("T-1")[0]["evidence"])

    def test_unknown_kind_status_and_role_are_accepted_verbatim(self) -> None:
        code, _ = self.cli(
            "append",
            "--task",
            "T-1",
            "--role",
            "archivist-7",
            "--kind",
            "weather_report",
            "--status",
            "drizzling",
            "--text",
            "no enum policing here",
        )
        self.assertEqual(0, code)
        event = self.events("T-1")[0]
        self.assertEqual("archivist-7", event["role"])
        self.assertEqual("weather_report", event["kind"])
        self.assertEqual("drizzling", event["status"])

    def test_unicode_text_round_trips(self) -> None:
        self.cli(
            "append",
            "--task",
            "T-1",
            "--role",
            "executor",
            "--kind",
            "execution_result",
            "--status",
            "blocked",
            "--text",
            "数据库连接失败，无法继续执行",
        )
        self.assertEqual(
            "数据库连接失败，无法继续执行",
            self.events("T-1")[0]["text"],
        )

    def test_events_append_in_order(self) -> None:
        for index in range(3):
            self.cli(
                "append",
                "--task",
                "T-1",
                "--role",
                "executor",
                "--kind",
                "progress",
                "--status",
                "running",
                "--text",
                f"step {index}",
            )
        texts = [event["text"] for event in self.events("T-1")]
        self.assertEqual(["step 0", "step 1", "step 2"], texts)


class ResilienceTests(TaskRecordTestCase):
    def test_garbled_line_does_not_block_the_append(self) -> None:
        self.tasks.mkdir(parents=True, exist_ok=True)
        record = self.tasks / "T-1.jsonl"
        record.write_text("{ this is not json\n", encoding="utf-8")
        code, _ = self.cli(
            "append",
            "--task",
            "T-1",
            "--role",
            "executor",
            "--kind",
            "execution_result",
            "--status",
            "failed",
            "--text",
            "recorded past a broken line",
        )
        self.assertEqual(0, code)
        _, events, skipped = AOS.read_log(record)
        self.assertEqual(1, skipped)
        self.assertEqual(["recorded past a broken line"], [event["text"] for event in events])
        self.assertIn("{ this is not json", record.read_text(encoding="utf-8"))
        self.assertEqual(["T-1.jsonl"], sorted(path.name for path in self.tasks.iterdir()))

    def test_task_id_stays_inside_the_tasks_directory(self) -> None:
        code, _ = self.cli(
            "append",
            "--task",
            "../../escape",
            "--role",
            "executor",
            "--kind",
            "execution_result",
            "--status",
            "blocked",
            "--text",
            "path traversal is sanitized, not refused",
        )
        self.assertEqual(0, code)
        written = list(self.tasks.glob("*.jsonl"))
        self.assertEqual(1, len(written))
        self.assertEqual(self.tasks, written[0].parent)

    def test_no_stray_artifacts_remain(self) -> None:
        """The record is the only file the tool ever leaves behind."""
        self.cli("create", "--task", "T-1", "--goal", "Fix order totals")
        self.cli(
            "append",
            "--task",
            "T-1",
            "--role",
            "executor",
            "--kind",
            "execution_result",
            "--status",
            "done",
            "--text",
            "finished",
        )
        self.cli("show", "--task", "T-1")
        self.assertEqual(["T-1.jsonl"], sorted(path.name for path in self.tasks.iterdir()))

    def test_every_concurrent_thread_append_survives(self) -> None:
        """Eight executors reporting at once lose nothing: no writer reads or rewrites."""
        self.cli("create", "--task", "T-1", "--goal", "Fix order totals")
        failures: list[BaseException] = []
        start = threading.Barrier(8)

        def write(index: int) -> None:
            try:
                start.wait()
                AOS.append("T-1", "executor", "execution_result", "completed", f"writer {index}", None)
            except BaseException as exc:  # a record write may never fail on contention
                failures.append(exc)

        with contextlib.redirect_stdout(io.StringIO()):
            threads = [threading.Thread(target=write, args=(index,)) for index in range(8)]
            for thread in threads:
                thread.start()
            for thread in threads:
                thread.join()

        self.assertEqual([], [repr(failure) for failure in failures])
        texts = sorted(event["text"] for event in self.events("T-1"))
        self.assertEqual(sorted(f"writer {index}" for index in range(8)), texts)
        self.assertEqual(["T-1.jsonl"], sorted(path.name for path in self.tasks.iterdir()))

    def test_every_concurrent_process_append_survives(self) -> None:
        """The real chain writes from separate processes; every terminal record must land."""
        self.cli("create", "--task", "T-1", "--goal", "Fix order totals")
        environment = dict(os.environ, AOS_ROOT=str(self.root))
        processes = [
            subprocess.Popen(
                [
                    sys.executable, str(MODULE_PATH), "append",
                    "--task", "T-1",
                    "--role", "executor",
                    "--kind", "execution_result",
                    "--status", "completed",
                    "--text", f"process {index}",
                ],
                env=environment,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.PIPE,
            )
            for index in range(6)
        ]
        for process in processes:
            _, error = process.communicate(timeout=60)
            self.assertEqual(0, process.returncode, error.decode("utf-8", "replace"))

        texts = sorted(event["text"] for event in self.events("T-1"))
        self.assertEqual(sorted(f"process {index}" for index in range(6)), texts)
        self.assertEqual(["T-1.jsonl"], sorted(path.name for path in self.tasks.iterdir()))


class ShowTests(TaskRecordTestCase):
    def test_show_prints_goal_conditions_and_events(self) -> None:
        self.cli(
            "create",
            "--task",
            "T-1",
            "--goal",
            "Fix order totals",
            "--done-when",
            "tests pass;;lint clean",
        )
        self.cli(
            "append",
            "--task",
            "T-1",
            "--role",
            "executor",
            "--kind",
            "execution_result",
            "--status",
            "blocked",
            "--text",
            "cannot reach the database",
            "--evidence",
            "logs/db.txt",
        )
        code, output = self.cli("show", "--task", "T-1")
        self.assertEqual(0, code)
        self.assertIn("Fix order totals", output)
        self.assertIn("tests pass", output)
        self.assertIn("lint clean", output)
        self.assertIn("executor", output)
        self.assertIn("execution_result", output)
        self.assertIn("blocked", output)
        self.assertIn("cannot reach the database", output)
        self.assertIn("logs/db.txt", output)
        event_lines = [line for line in output.splitlines() if "execution_result" in line]
        self.assertEqual(1, len(event_lines))

    def test_show_on_a_missing_task_reports_instead_of_crashing(self) -> None:
        code, output = self.cli("show", "--task", "never-created")
        self.assertEqual(0, code)
        self.assertIn("never-created", output)

    def test_show_reads_past_a_garbled_line_without_touching_the_file(self) -> None:
        """Reading is read-only: a broken line is reported, never renamed or dropped."""
        self.cli("create", "--task", "T-1", "--goal", "Fix order totals")
        self.cli(
            "append",
            "--task",
            "T-1",
            "--role",
            "executor",
            "--kind",
            "execution_result",
            "--status",
            "completed",
            "--text",
            "the valid event",
        )
        record = self.tasks / "T-1.jsonl"
        with record.open("a", encoding="utf-8") as stream:
            stream.write("}{ half a line\n")
        before = record.read_bytes()

        errors = io.StringIO()
        with contextlib.redirect_stderr(errors):
            code, output = self.cli("show", "--task", "T-1")

        self.assertEqual(0, code)
        self.assertIn("Fix order totals", output)
        self.assertIn("the valid event", output)
        self.assertIn("skipped 1 unreadable line(s)", errors.getvalue())
        self.assertEqual(before, record.read_bytes())
        self.assertEqual(["T-1.jsonl"], sorted(path.name for path in self.tasks.iterdir()))


class BoardTests(TaskRecordTestCase):
    """The board is derived, not stored: it folds the same files `show` folds."""

    def record(self, filename: str, *lines: str) -> Path:
        self.tasks.mkdir(parents=True, exist_ok=True)
        path = self.tasks / filename
        path.write_text("".join(f"{line}\n" for line in lines), encoding="utf-8")
        return path

    def header_line(self, task_id: str, goal: str, ts: str) -> str:
        return json.dumps(
            {"kind": "header", "task_id": task_id, "goal": goal, "done_when": [], "ts": ts}
        )

    def event_line(self, ts: str, kind: str, status: str, text: str = "note") -> str:
        return json.dumps(
            {"ts": ts, "role": "executor", "kind": kind, "status": status,
             "text": text, "evidence": None}
        )

    def board(self) -> tuple[int, list[list[str]], str]:
        errors = io.StringIO()
        with contextlib.redirect_stderr(errors):
            code, output = self.cli("board")
        rows = [line.split("\t") for line in output.splitlines()]
        return code, rows, errors.getvalue()

    def test_board_lists_tasks_most_recently_updated_first(self) -> None:
        self.record(
            "T-old.jsonl",
            self.header_line("T-old", "Fix order totals", "2026-08-10T09:00:00+00:00"),
            self.event_line("2026-08-10T10:00:00+00:00", "progress", "running"),
        )
        self.record(
            "T-new.jsonl",
            self.header_line("T-new", "Ship the board", "2026-08-12T08:00:00+00:00"),
            self.event_line("2026-08-12T11:00:00+00:00", "delivery", "completed"),
        )
        self.record(
            "T-mid.jsonl",
            self.header_line("T-mid", "Rebuild the index", "2026-08-11T09:00:00+00:00"),
            self.event_line("2026-08-11T09:30:00+00:00", "execution_result", "blocked"),
        )
        code, rows, errors = self.board()
        self.assertEqual(0, code)
        self.assertEqual("", errors)
        self.assertEqual(["T-new", "T-mid", "T-old"], [row[1] for row in rows])
        self.assertEqual(
            ["completed", "2026-08-12T11:00:00+00:00", "Ship the board"],
            [rows[0][0], rows[0][2], rows[0][3]],
        )
        self.assertEqual(["blocked", "active"], [rows[1][0], rows[2][0]])

    def test_last_terminal_event_wins_over_earlier_ones(self) -> None:
        """Latest delivery or execution_result decides; later chatter does not."""
        self.record(
            "T-1.jsonl",
            self.header_line("T-1", "Fix order totals", "2026-08-12T08:00:00+00:00"),
            self.event_line("2026-08-12T09:00:00+00:00", "execution_result", "completed"),
            self.event_line("2026-08-12T09:30:00+00:00", "delivery", "failed"),
            self.event_line("2026-08-12T10:00:00+00:00", "note", "info"),
        )
        _, rows, _ = self.board()
        self.assertEqual(1, len(rows))
        self.assertEqual("failed", rows[0][0])
        self.assertEqual("2026-08-12T10:00:00+00:00", rows[0][2])

    def test_header_only_task_shows_empty(self) -> None:
        self.cli("create", "--task", "T-1", "--goal", "Fix order totals")
        _, rows, _ = self.board()
        self.assertEqual(1, len(rows))
        self.assertEqual("empty", rows[0][0])
        self.assertEqual("T-1", rows[0][1])
        self.assertEqual("Fix order totals", rows[0][3])

    def test_event_only_task_uses_the_filename_stem(self) -> None:
        """An auto-created record has no header; the board still names and rates it."""
        self.cli(
            "append",
            "--task",
            "never-created",
            "--role",
            "executor",
            "--kind",
            "execution_result",
            "--status",
            "blocked",
            "--text",
            "cannot reach the database",
        )
        _, rows, _ = self.board()
        self.assertEqual(1, len(rows))
        self.assertEqual("blocked", rows[0][0])
        self.assertEqual("never-created", rows[0][1])
        self.assertEqual("", rows[0][3])

    def test_garbled_lines_are_counted_once_across_files(self) -> None:
        first = self.record(
            "T-1.jsonl",
            "{ this is not json",
            self.event_line("2026-08-12T09:00:00+00:00", "delivery", "completed"),
        )
        second = self.record(
            "T-2.jsonl",
            self.header_line("T-2", "Ship it", "2026-08-12T08:00:00+00:00"),
            "}{ half a line",
        )
        before = (first.read_bytes(), second.read_bytes())

        code, rows, errors = self.board()
        self.assertEqual(0, code)
        self.assertEqual(["T-1", "T-2"], sorted(row[1] for row in rows))
        self.assertEqual(["skipped 2 unreadable line(s)"], errors.splitlines())
        self.assertEqual(before, (first.read_bytes(), second.read_bytes()))
        self.assertEqual(
            ["T-1.jsonl", "T-2.jsonl"], sorted(path.name for path in self.tasks.iterdir())
        )

    def test_non_jsonl_files_are_ignored(self) -> None:
        self.record("T-1.jsonl", self.header_line("T-1", "Fix order totals", "2026-08-12T08:00:00+00:00"))
        (self.tasks / "notes.txt").write_text("not a record\n", encoding="utf-8")
        (self.tasks / "T-1.jsonl.bak").write_text("{ nonsense\n", encoding="utf-8")
        code, rows, errors = self.board()
        self.assertEqual(0, code)
        self.assertEqual("", errors)
        self.assertEqual([["empty", "T-1", "2026-08-12T08:00:00+00:00", "Fix order totals"]], rows)

    def test_empty_directory_prints_nothing(self) -> None:
        self.tasks.mkdir(parents=True, exist_ok=True)
        code, output = self.cli("board")
        self.assertEqual(0, code)
        self.assertEqual("", output)

    def test_missing_tasks_directory_prints_nothing(self) -> None:
        code, output = self.cli("board")
        self.assertEqual(0, code)
        self.assertEqual("", output)
        self.assertFalse(self.tasks.exists())

    def test_long_goal_is_truncated_to_eighty_characters(self) -> None:
        goal = "g" * 200
        self.cli("create", "--task", "T-1", "--goal", goal)
        _, rows, _ = self.board()
        self.assertEqual("g" * 80, rows[0][3])


if __name__ == "__main__":
    unittest.main()
