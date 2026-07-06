#!/usr/bin/env python3
"""PreToolUse hook: the guard for the guards.

Honest boundary: this is an anti-accident bar, not an anti-adversary one.
It screens Edit/Write file paths and does a heuristic scan of Bash commands;
an intentionally obfuscated command can evade it. True adversarial protection
would need OS-level permissions outside the agent's user (external review
2026-07-05, finding F1).

Scope:
- Edit/Write to .claude/hooks/ or .claude/settings* -> ask the user;
- Bash commands that look like writes into those paths -> ask;
- agent-os/state/compliance-log.tsv -> deny (script-written metrics file).
"""
from __future__ import annotations

import json
import re
from pathlib import Path

import aos_common as aos

ASK_FILE_PREFIXES = (".claude/hooks/", ".claude/settings")
DENY_PATHS = ("agent-os/state/compliance-log.tsv",)
WRITE_HINTS = ("rm ", "mv ", "cp ", "sed -i", "tee ", "chmod", "truncate")
REDIRECT_PROTECTED = re.compile(r">>?\s*\S*\.claude/(hooks|settings)")
REDIRECT_METRICS = re.compile(r">>?\s*\S*compliance-log\.tsv")


def decide(decision: str, reason: str) -> None:
    print(json.dumps({
        "hookSpecificOutput": {
            "hookEventName": "PreToolUse",
            "permissionDecision": decision,
            "permissionDecisionReason": reason,
        }
    }, ensure_ascii=False))


def main() -> int:
    data = aos.hook_input()
    if aos.disabled():
        return 0
    tool = data.get("tool_name") or ""
    tool_input = data.get("tool_input") or {}

    if tool == "Bash":
        cmd = tool_input.get("command") or ""
        writes = any(h in cmd for h in WRITE_HINTS)
        if "compliance-log.tsv" in cmd and (writes or REDIRECT_METRICS.search(cmd)):
            decide("deny", "compliance-log.tsv may only be written by the hook; this command appears to modify the metrics file.")
            return 0
        touches_layer = ".claude/hooks" in cmd or ".claude/settings" in cmd
        if touches_layer and (writes or REDIRECT_PROTECTED.search(cmd)):
            decide("ask", "This command appears to modify an AgentOS enforcement-layer file (heuristic, may be a false positive); ask the user to confirm.")
            return 0
        return 0

    file_path = tool_input.get("file_path") or ""
    if not file_path:
        return 0
    root = aos.project_root(data)
    try:
        rel = Path(file_path).resolve().relative_to(root.resolve()).as_posix()
    except ValueError:
        return 0
    if rel in DENY_PATHS:
        decide("deny", "compliance-log.tsv is a hook-only metrics file; an agent editing it would distort the compliance data.")
        return 0
    if any(rel.startswith(p) for p in ASK_FILE_PREFIXES):
        decide("ask", f"{rel} belongs to the AgentOS enforcement layer (the enforcement mechanism itself); changes need explicit approval from the user.")
        return 0
    return 0


if __name__ == "__main__":
    aos.run_guarded(main)
