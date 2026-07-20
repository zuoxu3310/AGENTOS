#!/usr/bin/env python3
"""Minimal per-session state for long AgentOS tasks."""
from __future__ import annotations

import argparse
import json
import os
import re
import tempfile
from pathlib import Path
from typing import Any


SCHEMA_VERSION = 1
STATUSES = {"active", "blocked", "done"}
REPORT_STATES = {"not_due", "pending", "delivered"}
FIELDS = (
    "goal",
    "done_when",
    "open_items",
    "next_action",
    "latest_user_delta",
    "status",
    "blocker",
    "report_state",
    "completion",
)


def safe_id(value: str) -> str:
    return re.sub(r"[^A-Za-z0-9._-]", "_", value or "anonymous")[:160]


def state_path(root: Path, runtime: str, session_id: str) -> Path:
    return (
        root
        / "agent-os"
        / "state"
        / "active-work"
        / f"{safe_id(runtime)}-{safe_id(session_id)}.json"
    )


def _text(value: Any) -> bool:
    return isinstance(value, str) and bool(value.strip())


def _text_list(value: Any, *, allow_empty: bool) -> bool:
    return (
        isinstance(value, list)
        and (allow_empty or bool(value))
        and all(_text(item) for item in value)
    )


def validate(active_work: Any) -> list[str]:
    problems: list[str] = []
    if not isinstance(active_work, dict):
        return ["active_work must be an object"]
    missing = [field for field in FIELDS if field not in active_work]
    if missing:
        problems.append("missing fields: " + ", ".join(missing))

    goal = active_work.get("goal")
    done_when = active_work.get("done_when")
    open_items = active_work.get("open_items")
    next_action = active_work.get("next_action")
    status = active_work.get("status")
    blocker = active_work.get("blocker")
    report_state = active_work.get("report_state")
    completion = active_work.get("completion")

    if not _text(goal):
        problems.append("goal must be non-empty")
    if not _text_list(done_when, allow_empty=False):
        problems.append("done_when must contain at least one finish condition")
        done_when = []
    elif len(set(done_when)) != len(done_when):
        problems.append("done_when contains duplicate conditions")
    if not _text_list(open_items, allow_empty=True):
        problems.append("open_items must be a list of non-empty strings")
        open_items = []
    elif len(set(open_items)) != len(open_items):
        problems.append("open_items contains duplicates")
    if not isinstance(next_action, str):
        problems.append("next_action must be a string")
        next_action = ""
    if not isinstance(active_work.get("latest_user_delta"), str):
        problems.append("latest_user_delta must be a string")
    if status not in STATUSES:
        problems.append("status must be active, blocked, or done")
    if not isinstance(blocker, str):
        problems.append("blocker must be a string")
        blocker = ""
    if report_state not in REPORT_STATES:
        problems.append("report_state must be not_due, pending, or delivered")

    if status == "active":
        if not open_items:
            problems.append("active work must have an open item")
        if next_action not in open_items:
            problems.append("next_action must be one of open_items")
        if blocker.strip():
            problems.append("active work cannot carry a blocker")
        if report_state != "not_due":
            problems.append("active work report_state must be not_due")
    elif status == "blocked":
        if not blocker.strip():
            problems.append("blocked work must explain the blocker")
        if next_action and next_action not in open_items:
            problems.append("blocked next_action must be empty or one of open_items")
        if report_state not in {"pending", "delivered"}:
            problems.append("blocked work must be pending or delivered for reporting")
    elif status == "done":
        if open_items:
            problems.append("done work cannot have open_items")
        if next_action:
            problems.append("done work must have an empty next_action")
        if blocker.strip():
            problems.append("done work cannot carry a blocker")
        if report_state not in {"pending", "delivered"}:
            problems.append("done work must be pending or delivered for reporting")

    if not isinstance(completion, list):
        problems.append("completion must be a list")
        completion = []
    seen: set[str] = set()
    for index, item in enumerate(completion):
        if not isinstance(item, dict):
            problems.append(f"completion[{index}] must be an object")
            continue
        condition = item.get("condition")
        evidence = item.get("evidence")
        if not _text(condition):
            problems.append(f"completion[{index}].condition must be non-empty")
            continue
        if condition in seen:
            problems.append(f"completion condition repeated: {condition}")
        seen.add(condition)
        if condition not in done_when:
            problems.append(f"completion condition is not in done_when: {condition}")
        if not _text_list(evidence, allow_empty=False):
            problems.append(f"completion evidence missing for: {condition}")
    if status == "done" and set(seen) != set(done_when):
        problems.append("done work needs evidence for every done_when condition exactly once")
    return problems


def load(path: Path) -> tuple[dict[str, Any] | None, list[str]]:
    if not path.exists():
        return None, []
    try:
        document = json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:
        return None, [f"state file is not valid JSON: {exc}"]
    if not isinstance(document, dict):
        return None, ["state document must be an object"]
    if document.get("schema_version") != SCHEMA_VERSION:
        return None, [f"schema_version must be {SCHEMA_VERSION}"]
    active_work = document.get("active_work")
    problems = validate(active_work)
    return active_work if isinstance(active_work, dict) else None, problems


def save(path: Path, active_work: dict[str, Any]) -> None:
    problems = validate(active_work)
    if problems:
        raise ValueError("; ".join(problems))
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = json.dumps(
        {"schema_version": SCHEMA_VERSION, "active_work": active_work},
        ensure_ascii=False,
        indent=2,
        sort_keys=False,
    ) + "\n"
    handle, temporary = tempfile.mkstemp(prefix=path.name + ".", dir=path.parent)
    try:
        with os.fdopen(handle, "w", encoding="utf-8") as stream:
            stream.write(payload)
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary, path)
    finally:
        try:
            os.unlink(temporary)
        except FileNotFoundError:
            pass


def mark_delivered(path: Path) -> list[str]:
    active_work, problems = load(path)
    if problems or active_work is None:
        return problems or ["active_work is missing"]
    if active_work.get("report_state") != "pending":
        return ["report_state is not pending"]
    updated = dict(active_work)
    updated["report_state"] = "delivered"
    save(path, updated)
    return []


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("state_file", type=Path)
    args = parser.parse_args()
    _, problems = load(args.state_file)
    if problems:
        for problem in problems:
            print("FAIL", problem)
        return 1
    print("PASS active_work")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
