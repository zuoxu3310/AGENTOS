#!/usr/bin/env python3
"""PreToolUse hook: enforce only deterministic Codex runtime boundaries."""
from __future__ import annotations

import json

import aos_common as aos


NATIVE_DELEGATION_TOOLS = {
    "Agent",
    "Task",
    "Workflow",
    "spawn_agent",
    "collab",
    "collaboration.spawn_agent",
}


def deny(reason: str) -> None:
    print(json.dumps({
        "hookSpecificOutput": {
            "hookEventName": "PreToolUse",
            "permissionDecision": "deny",
            "permissionDecisionReason": reason,
        }
    }, ensure_ascii=False))


def main() -> int:
    data = aos.hook_input()
    if aos.disabled():
        return 0
    tool = str(data.get("tool_name") or data.get("tool") or data.get("name") or "")
    if tool in NATIVE_DELEGATION_TOOLS:
        deny(
            "Codex delegation must use the vendored Dynamic Workflow runner; "
            "native collaboration workers are not a second execution backend."
        )
    return 0


if __name__ == "__main__":
    aos.run_guarded(main)
