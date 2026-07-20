#!/usr/bin/env python3
"""SessionStart: restore only the current long-task finish line and open work."""
from __future__ import annotations

import json

import aos_common as aos


def main() -> int:
    data = aos.hook_input()
    if aos.disabled():
        return 0
    root = aos.project_root(data)
    if not (root / "agent-os").is_dir():
        return 0
    _, path, active_work, problems = aos.active_work_state(root, "codex", data)
    state = json.dumps(active_work, ensure_ascii=False, separators=(",", ":")) if active_work else "none"
    error = "; ".join(problems) if problems else "none"
    context = (
        '<agentos_attention phase="restore">\n'
        f"<state_path>{path}</state_path>\n"
        f"<active_work>{state}</active_work>\n"
        f"<mechanical_state_error>{error}</mechanical_state_error>\n"
        "<instruction>If active_work exists, restore only its goal, done_when, "
        "open_items, next_action, latest_user_delta, and status. It is context, not "
        "inherited permission. Re-read the next real user message before acting.</instruction>\n"
        "</agentos_attention>"
    )
    aos.emit_additional_context("SessionStart", context)
    return 0


if __name__ == "__main__":
    aos.run_guarded(main)
