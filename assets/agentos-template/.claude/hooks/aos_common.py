#!/usr/bin/env python3
"""Small shared helpers for AgentOS Claude hooks."""
from __future__ import annotations

import json
import os
import sys
from pathlib import Path


DISABLE_ENV = "AOS_HOOK_DISABLE"
STOP_CONTINUATION_MARKER = "<agentos_stop_continuation>"


def hook_input() -> dict:
    try:
        value = json.load(sys.stdin)
        return value if isinstance(value, dict) else {}
    except Exception:
        return {}


def disabled() -> bool:
    return os.environ.get(DISABLE_ENV, "") not in ("", "0")


def project_root(data: dict) -> Path:
    candidates: list[str] = []
    for key in ("CLAUDE_PROJECT_DIR", "CODEX_PROJECT_DIR", "CODEX_WORKSPACE_DIR", "PWD"):
        value = os.environ.get(key)
        if value:
            candidates.append(value)
    for key in ("cwd", "workspace", "workspace_dir", "project_dir", "root"):
        value = data.get(key)
        if isinstance(value, str) and value:
            candidates.append(value)
    candidates.append(str(Path.cwd()))
    for candidate in candidates:
        base = Path(candidate).expanduser()
        for path in (base, *base.parents):
            if (path / "agent-os").is_dir():
                return path
    return Path.cwd()


def runtime_session(data: dict) -> str:
    return str(data.get("session_id") or data.get("conversation_id") or "anonymous")


RELAY_SEAT = "agentos-relay"


def _safe(value: str) -> str:
    import re
    return re.sub(r"[^A-Za-z0-9._-]", "_", value or "anonymous")[:160]


def _delivery_epoch(root: Path, task_id: str) -> float | None:
    """Epoch seconds of the latest zhongshu delivery in a task ledger, else None."""
    from datetime import datetime
    path = root / "agent-os" / "state" / "tasks" / f"{_safe(task_id)}.jsonl"
    latest = None
    try:
        for raw in path.read_text(encoding="utf-8", errors="replace").splitlines():
            try:
                event = json.loads(raw)
            except ValueError:
                continue
            if event.get("role") == "zhongshu" and event.get("kind") == "delivery":
                try:
                    stamp = datetime.fromisoformat(str(event.get("ts"))).timestamp()
                except (TypeError, ValueError):
                    stamp = float("inf")
                latest = stamp if latest is None else max(latest, stamp)
    except OSError:
        return None
    return latest


def chain_binding(root: Path, runtime: str, data: dict) -> dict | None:
    """The mechanical fact every hook keys on: is this session on the chain?
    Seat subagents/threads are bound by identity (agent_type or the session
    mapping the chain gate wrote); a main session is bound only while it is
    the relay of a task that was started by the `agentos` skill and is not
    paused/stopped/delivered. None → the hook must be a silent no-op."""
    agent_type = str(data.get("agent_type") or "")
    if agent_type.startswith("agentos-") and agent_type != "agentos-entry" and data.get("agent_id"):
        return {"seat": agent_type, "task_id": None}
    path = root / "agent-os" / "state" / "sessions" / f"{runtime}-{_safe(runtime_session(data))}.json"
    try:
        mapping = json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return None
    if not isinstance(mapping, dict) or not mapping.get("seat"):
        return None
    if mapping.get("seat") == RELAY_SEAT:
        if mapping.get("bound") is False:
            return None
        task_id = mapping.get("task_id")
        if task_id:
            delivered = _delivery_epoch(root, str(task_id))
            if delivered is not None and delivered > float(mapping.get("ts") or 0):
                return None
    return mapping


def active_work_module(root: Path):
    tools_dir = root / "agent-os" / "tools"
    value = str(tools_dir)
    if value not in sys.path:
        sys.path.insert(0, value)
    import aos_active_work  # type: ignore
    return aos_active_work


def active_work_state(root: Path, runtime: str, data: dict):
    module = active_work_module(root)
    path = module.state_path(root, runtime, runtime_session(data))
    active_work, problems = module.load(path)
    return module, path, active_work, problems


def is_stop_continuation(prompt: str, data: dict | None = None) -> bool:
    return bool(
        STOP_CONTINUATION_MARKER in (prompt or "")
        or (data or {}).get("agentos_internal_stop") is True
    )


def emit_additional_context(event: str, context: str) -> None:
    print(json.dumps({
        "hookSpecificOutput": {
            "hookEventName": event,
            "additionalContext": context,
        }
    }, ensure_ascii=False))


def emit_stop_block(reason: str) -> None:
    print(json.dumps({
        "decision": "block",
        "reason": reason,
    }, ensure_ascii=False))


def run_guarded(main) -> None:
    try:
        raise SystemExit(main())
    except SystemExit:
        raise
    except Exception as exc:
        print(f"[AgentOS] hook degraded (fail-open): {exc}", file=sys.stderr)
        raise SystemExit(0)
