#!/usr/bin/env python3
"""Append-only task record for AgentOS. The tool records; roles judge.

One task is one JSONL file. Every action appends one line with a single
`os.write` on an `O_APPEND` descriptor: no read-modify-write, so concurrent
writers cannot lose each other's records, and terminal results (completed,
failed, blocked) land in any state, including on a task id never created.
"""
from __future__ import annotations

import argparse
import json
import os
import re
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


TERMINAL_KINDS = ("delivery", "execution_result")
TITLE_LIMIT = 32


def root() -> Path:
    override = os.environ.get("AOS_ROOT")
    return Path(override) if override else Path(__file__).resolve().parents[2]


def safe_id(value: str) -> str:
    return re.sub(r"[^A-Za-z0-9._-]", "_", value or "anonymous")[:160]


def record_path(task_id: str) -> Path:
    return root() / "agent-os" / "state" / "tasks" / f"{safe_id(task_id)}.jsonl"


def now() -> str:
    return datetime.now(timezone.utc).isoformat()


def task_title(goal: str) -> str:
    """A deterministic, readable title fragment derived from the user's words."""
    text = re.sub(r"^\s*(?:[$/]agentos)\b\s*", "", goal or "", flags=re.I)
    text = re.sub(r"\s+", " ", text).strip()
    for prefix in ("麻烦帮我", "请帮我", "麻烦", "帮我", "请"):
        if text.startswith(prefix):
            text = text[len(prefix):].lstrip(" ，,:：")
            break
    text = re.split(r"[\n。；;！？!?]", text, maxsplit=1)[0]
    text = text.replace("｜", "-").strip(" ，,:：.-") or "未命名任务"
    if len(text) > TITLE_LIMIT:
        text = text[: TITLE_LIMIT - 1].rstrip() + "…"
    return text


def emit(path: Path, line: dict[str, Any]) -> None:
    """Append one line. O_CREAT makes a missing record a non-event, O_APPEND makes
    the write land after whatever any other writer just appended."""
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = (json.dumps(line, ensure_ascii=False) + "\n").encode("utf-8")
    descriptor = os.open(path, os.O_APPEND | os.O_CREAT | os.O_WRONLY, 0o644)
    try:
        os.write(descriptor, payload)
    finally:
        os.close(descriptor)


def read_log(path: Path) -> tuple[dict[str, Any], list[dict[str, Any]], int]:
    """Latest header, events in order, unreadable line count. Reading never writes:
    a garbled line is skipped and left exactly where it is."""
    header: dict[str, Any] = {}
    events: list[dict[str, Any]] = []
    skipped = 0
    for raw in path.read_text(encoding="utf-8", errors="replace").splitlines():
        if not raw.strip():
            continue
        try:
            line = json.loads(raw)
        except ValueError:
            line = None
        if not isinstance(line, dict):
            skipped += 1
            continue
        if line.get("kind") == "header" and "task_id" in line:
            header = line
        else:
            events.append(line)
    return header, events, skipped


def create(task_id: str, goal: str, done_when: str | None) -> int:
    path = record_path(task_id)
    conditions = [part.strip() for part in (done_when or "").split(";;") if part.strip()]
    emit(path, {"kind": "header", "task_id": task_id, "title": task_title(goal), "goal": goal,
                "done_when": conditions, "ts": now()})
    print(f"created {task_id} -> {path}")
    return 0


def append(task_id: str, role: str, kind: str, status: str, text: str, evidence: str | None) -> int:
    path = record_path(task_id)
    emit(path, {"ts": now(), "role": role, "kind": kind, "status": status,
                "text": text, "evidence": evidence})
    print(f"recorded {kind}/{status} on {task_id}")
    return 0


def show(task_id: str) -> int:
    path = record_path(task_id)
    if not path.exists():
        print(f"no record for {task_id}")
        return 0
    header, events, skipped = read_log(path)
    if skipped:
        print(f"skipped {skipped} unreadable line(s)", file=sys.stderr)
    print(f"task: {header.get('task_id') or task_id}")
    print(f"title: {header.get('title') or task_title(str(header.get('goal', '')))}")
    print(f"goal: {header.get('goal', '')}")
    for condition in header.get("done_when") or ():
        print(f"done_when: {condition}")
    for event in events:
        evidence = f" [{event.get('evidence')}]" if event.get("evidence") else ""
        head = f"{event.get('ts')} {event.get('role')} {event.get('kind')}/{event.get('status')}"
        print(f"{head}: {event.get('text')}{evidence}")
    return 0


def title(task_id: str) -> int:
    path = record_path(task_id)
    if not path.exists():
        print(f"no record for {task_id}", file=sys.stderr)
        return 1
    header, _, _ = read_log(path)
    print(header.get("title") or task_title(str(header.get("goal", ""))))
    return 0


def board() -> int:
    """A derived read-only view over the same files `show` folds: no new state and
    no second source of truth. The status is the last terminal event's own word;
    conflicting events are not reconciled, because that is a role's judgment."""
    directory = root() / "agent-os" / "state" / "tasks"
    rows: list[tuple[str, str, str, str]] = []
    skipped = 0
    for path in sorted(directory.glob("*.jsonl")) if directory.is_dir() else ():
        header, events, unreadable = read_log(path)
        skipped += unreadable
        terminal = [event for event in events if event.get("kind") in TERMINAL_KINDS]
        if terminal:
            status = str(terminal[-1].get("status", ""))
        else:
            status = "active" if events else "empty"
        stamp = events[-1].get("ts") if events else header.get("ts")
        rows.append((status, str(header.get("task_id") or path.stem),
                     str(stamp or ""), str(header.get("goal", ""))[:80]))
    if skipped:
        print(f"skipped {skipped} unreadable line(s)", file=sys.stderr)
    for row in sorted(rows, key=lambda entry: (entry[2], entry[1]), reverse=True):
        print("\t".join(row))
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Append-only AgentOS task record.")
    commands = parser.add_subparsers(dest="command", required=True)

    maker = commands.add_parser("create", help="append the record header")
    maker.add_argument("--goal", required=True)
    maker.add_argument("--done-when", help='finish conditions joined by ";;"')
    writer = commands.add_parser("append", help="append one event; never refused")
    for flag in ("--role", "--kind", "--status", "--text"):
        writer.add_argument(flag, required=True)
    writer.add_argument("--evidence")
    reader = commands.add_parser("show", help="print the record for a human")
    titler = commands.add_parser("title", help="print the deterministic display title")
    commands.add_parser("board", help="derived read-only view of every record")
    for command in (maker, writer, reader, titler):
        command.add_argument("--task", required=True)

    args = parser.parse_args(argv)
    try:
        if args.command == "create":
            return create(args.task, args.goal, args.done_when)
        if args.command == "append":
            return append(args.task, args.role, args.kind, args.status, args.text, args.evidence)
        if args.command == "board":
            return board()
        if args.command == "title":
            return title(args.task)
        return show(args.task)
    except OSError as exc:
        print(f"record write failed: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
