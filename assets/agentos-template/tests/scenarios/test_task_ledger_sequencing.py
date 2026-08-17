"""Regression for wiki/errors/2026-08-13-delivery-preceded-mandated-independent-check:
a user-visible delivery must not precede its mandated independent check — in
each task ledger the first zhongshu delivery either follows a menxia
independent_review, carries an explicit retroactive/provisional marker, or has
a later append-only correction that targets it."""
from __future__ import annotations

import contextlib
import importlib.util
import io
import json
import tempfile
import unittest
from pathlib import Path


REPO = Path(__file__).resolve().parents[2]
LINTER_PATH = REPO / "agent-os/tools/aos-lint.py"
SPEC = importlib.util.spec_from_file_location("agentos_sequencing_lint", LINTER_PATH)
assert SPEC is not None and SPEC.loader is not None
LINTER = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(LINTER)


def event(role: str, kind: str, text: str = "x", **fields: object) -> str:
    payload = {"role": role, "kind": kind, "status": "ok", "text": text}
    payload.update(fields)
    return json.dumps(payload)


def correction(target_ts: str, **overrides: object) -> str:
    payload = {
        "target_delivery_ts": target_ts,
        "classification": "retroactive",
        "reason": "The chain could not obtain its independent review before reporting the blocker.",
    }
    payload.update(overrides.pop("payload", {}))
    fields = {"evidence": "task audit"}
    fields.update(overrides)
    return event(
        "executor",
        "delivery_correction",
        json.dumps(payload),
        **fields,
    )


class TaskLedgerSequencingTests(unittest.TestCase):
    def check(self, ledger_lines: list[str] | None) -> list[str]:
        temporary = tempfile.TemporaryDirectory(prefix="agentos-sequencing-")
        self.addCleanup(temporary.cleanup)
        root = Path(temporary.name)
        if ledger_lines is not None:
            tasks = root / "agent-os/state/tasks"
            tasks.mkdir(parents=True)
            (tasks / "case.jsonl").write_text("\n".join(ledger_lines) + "\n", encoding="utf-8")
        previous = LINTER.ROOT
        LINTER.ROOT = root
        failures: list[str] = []
        try:
            with contextlib.redirect_stdout(io.StringIO()):
                LINTER.lint_task_ledger_sequencing(failures)
        finally:
            LINTER.ROOT = previous
        return failures

    def test_review_before_first_delivery_passes(self) -> None:
        self.assertEqual([], self.check([
            event("zhongshu", "user_message"),
            event("menxia", "independent_review"),
            event("zhongshu", "delivery"),
        ]))

    def test_delivery_without_review_or_marker_fails(self) -> None:
        failures = self.check([
            event("zhongshu", "user_message"),
            event("zhongshu", "delivery", "shipped straight to the user channel"),
        ])
        self.assertEqual(1, len(failures))
        self.assertIn("delivery precedes independent review", failures[0])

    def test_marked_retroactive_delivery_passes(self) -> None:
        for marker in ("Retroactive (事后补记): shipped pre-chain", "provisional interim result"):
            with self.subTest(marker=marker):
                self.assertEqual([], self.check([
                    event("zhongshu", "user_message"),
                    event("zhongshu", "delivery", marker),
                ]))

    def test_later_append_only_correction_passes(self) -> None:
        target_ts = "2026-08-16T20:19:35.288708+00:00"
        self.assertEqual([], self.check([
            event("zhongshu", "user_message"),
            event("zhongshu", "delivery", "shipped pre-chain", ts=target_ts),
            correction(target_ts),
        ]))

    def test_correction_must_follow_and_target_first_delivery(self) -> None:
        target_ts = "2026-08-16T20:19:35.288708+00:00"
        cases = {
            "before": [
                correction(target_ts),
                event("zhongshu", "delivery", "shipped pre-chain", ts=target_ts),
            ],
            "wrong-target": [
                event("zhongshu", "delivery", "shipped pre-chain", ts=target_ts),
                correction("2026-08-16T20:20:00+00:00"),
            ],
        }
        for name, lines in cases.items():
            with self.subTest(name):
                failures = self.check(lines)
                self.assertEqual(1, len(failures))
                self.assertIn("delivery precedes independent review", failures[0])

    def test_invalid_correction_payload_does_not_clear_failure(self) -> None:
        target_ts = "2026-08-16T20:19:35.288708+00:00"
        cases = {
            "not-json": event(
                "executor", "delivery_correction", "not json", evidence="task audit"
            ),
            "bad-classification": correction(
                target_ts, payload={"classification": "final"}
            ),
            "missing-reason": correction(target_ts, payload={"reason": ""}),
            "missing-evidence": correction(target_ts, evidence=""),
            "bad-status": correction(target_ts, status="blocked"),
        }
        for name, invalid in cases.items():
            with self.subTest(name):
                failures = self.check([
                    event("zhongshu", "delivery", "shipped pre-chain", ts=target_ts),
                    invalid,
                ])
                self.assertEqual(1, len(failures))
                self.assertIn("invalid correction", failures[0])

    def test_no_ledgers_passes(self) -> None:
        self.assertEqual([], self.check(None))

    @unittest.skipUnless(
        (REPO / "wiki/raw/2026-08-13-skills-audit-ledger.jsonl").is_file(),
        "development-instance data absent: skills-audit durable copy",
    )
    def test_live_durable_copy_of_skills_audit_is_compliant(self) -> None:
        durable = REPO / "wiki/raw/2026-08-13-skills-audit-ledger.jsonl"
        self.assertTrue(durable.is_file(), "durable ledger copy missing")
        first_delivery = None
        for line in durable.read_text(encoding="utf-8").splitlines():
            try:
                entry = json.loads(line)
            except ValueError:
                continue
            if entry.get("role") == "zhongshu" and entry.get("kind") == "delivery":
                first_delivery = str(entry.get("text", ""))
                break
        assert first_delivery is not None
        self.assertTrue(
            any(term in first_delivery.lower() for term in ("retroactive", "provisional", "事后补记")),
            "first delivery in the audited ledger lacks its retroactive marker",
        )


if __name__ == "__main__":
    unittest.main()
