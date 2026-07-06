#!/usr/bin/env python3
"""Shared helpers for AgentOS enforcement hooks (Codex adapter).

Canonical AgentOS rules live under agent-os/. The `.codex` hook adapter enforces mechanical
invariants only: existence, format, numbering, and protected-path prompts.
They do not judge truthfulness or quality.
"""
from __future__ import annotations

import json
import os
import re
import sys
import time
from pathlib import Path

DISABLE_ENV = "AOS_HOOK_DISABLE"
ENTRY_RE = re.compile(r"^## (\d+) — (.*)$", re.MULTILINE)
REQUIRED_FIELDS = ("- object:", "- contract:", "- action+evidence:", "- status:")


def hook_input() -> dict:
    try:
        return json.load(sys.stdin)
    except Exception:
        return {}


def disabled() -> bool:
    return os.environ.get(DISABLE_ENV, "") not in ("", "0")


def _candidate_paths(data: dict) -> list[str]:
    candidates: list[str] = []
    for key in ("CODEX_PROJECT_DIR", "CODEX_WORKSPACE_DIR", "CLAUDE_PROJECT_DIR", "PWD"):
        value = os.environ.get(key)
        if value:
            candidates.append(value)
    for key in ("cwd", "workspace", "workspace_dir", "project_dir", "root"):
        value = data.get(key)
        if isinstance(value, str) and value:
            candidates.append(value)
    candidates.append(str(Path.cwd()))
    return candidates


def project_root(data: dict) -> Path:
    """Walk up from each candidate so subdirectory sessions still find root."""
    for candidate in _candidate_paths(data):
        base = Path(candidate).expanduser()
        for path in (base, *base.parents):
            if (path / "agent-os").is_dir():
                return path
    return Path.cwd()


def audit_log_path(root: Path) -> Path:
    return root / "agent-os" / "state" / "audit-log.md"


def parse_entries(text: str) -> list[tuple[int, str]]:
    return [(int(m.group(1)), m.group(2).strip()) for m in ENTRY_RE.finditer(text)]


def max_entry(text: str) -> int:
    return max((n for n, _ in parse_entries(text)), default=0)


def entry_block(text: str, number: int) -> str:
    marker = re.search(rf"^## {number} — .*$", text, re.MULTILINE)
    if not marker:
        return ""
    rest = text[marker.end():]
    nxt = ENTRY_RE.search(rest)
    return rest[: nxt.start()] if nxt else rest


def entry_missing_fields(text: str, number: int) -> list[str]:
    block = entry_block(text, number)
    return [
        f for f in REQUIRED_FIELDS
        if not re.search(rf"^\s*{re.escape(f)}", block, re.MULTILINE)
    ]


def state_path(root: Path, session_id: str) -> Path:
    safe = re.sub(r"[^A-Za-z0-9_-]", "_", session_id or "unknown")
    return root / "agent-os" / "state" / "codex-hook-state" / f"{safe}.json"


def load_state(root: Path, session_id: str) -> dict:
    try:
        return json.loads(state_path(root, session_id).read_text(encoding="utf-8"))
    except Exception:
        return {}


def save_state(root: Path, session_id: str, state: dict) -> None:
    try:
        path = state_path(root, session_id)
        path.parent.mkdir(parents=True, exist_ok=True)
        tmp = path.with_suffix(".tmp")
        tmp.write_text(json.dumps(state, ensure_ascii=False), encoding="utf-8")
        os.replace(tmp, path)
    except Exception:
        pass


def log_compliance(root: Path, session_id: str, result: str, detail: str) -> None:
    try:
        path = root / "agent-os" / "state" / "compliance-log.tsv"
        if not path.exists():
            path.write_text("# ts\tsession\tevent\tresult\tdetail\n", encoding="utf-8")
        ts = time.strftime("%Y-%m-%dT%H:%M:%S")
        clean = detail.replace("\t", " ").replace("\n", " ")[:300]
        with path.open("a", encoding="utf-8") as f:
            f.write(f"{ts}\t{(session_id or 'unknown')[:8]}\tstop_gate\t{result}\t{clean}\n")
    except Exception:
        pass


def emit_block_decision(reason: str) -> None:
    print(json.dumps({
        "decision": "block",
        "reason": reason,
        "hookSpecificOutput": {
            "hookEventName": "Stop",
            "decision": "block",
            "reason": reason,
        },
    }, ensure_ascii=False))


def run_guarded(main) -> None:
    try:
        sys.exit(main())
    except SystemExit:
        raise
    except Exception as exc:
        print(f"[AgentOS] Codex hook degraded (fail-open): {exc}", file=sys.stderr)
        sys.exit(0)
