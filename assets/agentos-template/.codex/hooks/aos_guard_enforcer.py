#!/usr/bin/env python3
"""PreToolUse hook: guard AgentOS enforcement-layer files in Codex."""
from __future__ import annotations

import json
import re
from pathlib import Path

import aos_common as aos

ASK_FILE_PREFIXES = (
    ".codex/hooks/",
    ".codex/hooks.json",
    ".codex/config.toml",
    ".codex/agentos-local-rules.md",
    ".claude/hooks/",
    ".claude/settings",
)
DENY_PATHS = ("agent-os/state/compliance-log.tsv",)
WRITE_HINTS = ("rm ", "mv ", "cp ", "sed -i", "tee ", "chmod", "truncate", "apply_patch")
REDIRECT_PROTECTED = re.compile(r">>?\s*\S*(\.codex/(hooks|config\.toml|hooks\.json)|\.claude/(hooks|settings))")
REDIRECT_METRICS = re.compile(r">>?\s*\S*compliance-log\.tsv")


def decide(decision: str, reason: str) -> None:
    print(json.dumps({
        "hookSpecificOutput": {
            "hookEventName": "PreToolUse",
            "permissionDecision": decision,
            "permissionDecisionReason": reason,
        }
    }, ensure_ascii=False))


def _tool_input(data: dict) -> dict:
    value = data.get("tool_input") or data.get("input") or data.get("arguments") or {}
    return value if isinstance(value, dict) else {}


def _payload_text(data: dict) -> str:
    try:
        return json.dumps(data, ensure_ascii=False)
    except Exception:
        return str(data)


def main() -> int:
    data = aos.hook_input()
    if aos.disabled():
        return 0
    tool = str(data.get("tool_name") or data.get("tool") or data.get("name") or "")
    tool_input = _tool_input(data)
    payload = _payload_text(data)

    if tool in ("Bash", "shell", "exec_command"):
        cmd = str(tool_input.get("command") or tool_input.get("cmd") or "")
        writes = any(h in cmd for h in WRITE_HINTS)
        if "compliance-log.tsv" in cmd and (writes or REDIRECT_METRICS.search(cmd)):
            decide("deny", "compliance-log.tsv may only be written by the hook; this command appears to modify the metrics file.")
            return 0
        touches_layer = any(prefix in cmd for prefix in ASK_FILE_PREFIXES)
        if touches_layer and (writes or REDIRECT_PROTECTED.search(cmd)):
            decide("ask", "This command appears to modify an AgentOS enforcement-layer file; ask the user to confirm.")
            return 0
        return 0

    if "compliance-log.tsv" in payload:
        decide("deny", "compliance-log.tsv is a hook-only metrics file; an agent editing it would distort the compliance data.")
        return 0

    root = aos.project_root(data)
    for key in ("file_path", "path", "target_file", "file"):
        file_path = tool_input.get(key)
        if not isinstance(file_path, str) or not file_path:
            continue
        try:
            rel = Path(file_path).resolve().relative_to(root.resolve()).as_posix()
        except ValueError:
            continue
        if any(rel.startswith(path) for path in DENY_PATHS):
            decide("deny", "compliance-log.tsv is a hook-only metrics file; an agent editing it would distort the compliance data.")
            return 0
        if any(rel.startswith(prefix) for prefix in ASK_FILE_PREFIXES):
            decide("ask", f"{rel} belongs to the AgentOS enforcement layer; changes need explicit confirmation from the user.")
            return 0

    if any(prefix in payload for prefix in ASK_FILE_PREFIXES):
        decide("ask", "This tool call appears to modify an AgentOS enforcement-layer file; ask the user to confirm.")
    return 0


if __name__ == "__main__":
    aos.run_guarded(main)
