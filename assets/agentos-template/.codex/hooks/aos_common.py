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
# The seat a *main* session takes when the user invokes the `agentos` skill.
# Codex: a relay (太监) that carries exact words to the 中书省 Desktop thread.
# Claude: the session itself is 中书 and spawns the other seats as subagents.
MAIN_SEATS = {"codex": RELAY_SEAT, "claude": "agentos-zhongshu"}
MAIN_ROLES = {"codex": "relay", "claude": "zhongshu"}
SEAT_TYPES = ("agentos-zhongshu", "agentos-menxia", "agentos-shangshu",
              "agentos-executor", "agentos-yushi")


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


def spawn_agent_type(data: dict) -> str | None:
    """The seat type a Claude subagent was really spawned as, read from the
    runtime's own agent metadata (`agent-<id>.meta.json`, key customAgentType /
    agentType). Named or teamed spawns report the *name* as hook `agent_type`
    (seen 2026-08-18: `exec-pointer-truth` for an agentos-executor); this is the
    mechanical fallback. Fail-open: None when nothing readable."""
    agent_id = str(data.get("agent_id") or "")
    transcript = str(data.get("transcript_path") or "")
    if not agent_id or not transcript:
        return None
    base = Path(transcript)
    candidates = [
        base.with_suffix("") / "subagents" / f"agent-{agent_id}.meta.json",
        base.parent / f"agent-{agent_id}.meta.json",
        base.parent / "subagents" / f"agent-{agent_id}.meta.json",
    ]
    for path in candidates:
        try:
            meta = json.loads(path.read_text(encoding="utf-8"))
        except Exception:
            continue
        if not isinstance(meta, dict):
            continue
        for key in ("customAgentType", "agentType"):
            value = str(meta.get(key) or "")
            if value in SEAT_TYPES:
                return value
    return None


def seat_agent_type(data: dict) -> str | None:
    """Claude seat identity from hook input: `agent_type` when it names a seat,
    else the spawn metadata fallback. None for a non-seat subagent."""
    agent_type = str(data.get("agent_type") or "")
    if agent_type in SEAT_TYPES and data.get("agent_id"):
        return agent_type
    if data.get("agent_id"):
        return spawn_agent_type(data)
    return None


def chain_binding(root: Path, runtime: str, data: dict) -> dict | None:
    """The mechanical fact every hook keys on: is this session on the chain?
    Seat subagents/threads are bound by identity (agent_type or the session
    mapping the chain gate wrote); a main session is bound only while it is
    the runtime's main seat (Codex relay / Claude 中书) of a task that was
    started by the `agentos` skill and is not paused/stopped/delivered.
    None → the hook must be a silent no-op."""
    if data.get("agent_id"):
        seat_type = seat_agent_type(data)
        return {"seat": seat_type, "task_id": None} if seat_type else None
    path = root / "agent-os" / "state" / "sessions" / f"{runtime}-{_safe(runtime_session(data))}.json"
    try:
        mapping = json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return None
    if not isinstance(mapping, dict) or not mapping.get("seat"):
        return None
    seat = mapping.get("seat")
    if seat == RELAY_SEAT and runtime != "codex":
        return None  # legacy Claude relay binding: not a seat any more
    if seat in MAIN_SEATS.values() and ("bound" in mapping or seat == RELAY_SEAT):
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
