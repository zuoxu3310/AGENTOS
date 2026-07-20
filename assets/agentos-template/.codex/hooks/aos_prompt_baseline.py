#!/usr/bin/env python3
"""UserPromptSubmit: bring the latest real user request back into attention."""
from __future__ import annotations

import json

import aos_common as aos


def main() -> int:
    data = aos.hook_input()
    if aos.disabled():
        return 0
    prompt = str(data.get("prompt") or "")
    if aos.is_stop_continuation(prompt, data):
        return 0
    root = aos.project_root(data)
    if not (root / "agent-os").is_dir():
        return 0
    _, path, active_work, problems = aos.active_work_state(root, "codex", data)
    state = json.dumps(active_work, ensure_ascii=False, separators=(",", ":")) if active_work else "none"
    error = "; ".join(problems) if problems else "none"
    context = (
        '<agentos_attention phase="user_message">\n'
        f"<state_path>{path}</state_path>\n"
        f"<current_active_work>{state}</current_active_work>\n"
        f"<mechanical_state_error>{error}</mechanical_state_error>\n"
        "<instruction>Re-read the real user message first. Decide whether it continues, "
        "corrects, replaces, or starts work unrelated to current_active_work. Reconstruct "
        "the result the user actually wants and its observable finish conditions. Ask only "
        "about a user-owned choice that truly blocks the next action. For a long task, keep "
        "the state file current. Before using tools, hold one work segment in current context: "
        "purpose, expected result, and stop condition. Several tools may serve that one segment; "
        "do not create a route event or repeat the reminder for each tool.</instruction>\n"
        "</agentos_attention>"
    )
    aos.emit_additional_context("UserPromptSubmit", context)
    return 0


if __name__ == "__main__":
    aos.run_guarded(main)
