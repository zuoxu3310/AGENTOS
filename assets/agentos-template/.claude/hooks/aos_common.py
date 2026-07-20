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
