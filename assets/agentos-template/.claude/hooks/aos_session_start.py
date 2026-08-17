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
    binding = aos.chain_binding(root, "claude", data)
    if not binding:
        aos.emit_additional_context(
            "SessionStart",
            "AgentOS installed; invoke the `agentos` skill (/agentos or $agentos) "
            "to run the 三省六部 chain.")
        return 0
    _, path, active_work, problems = aos.active_work_state(root, "claude", data)
    state = json.dumps(active_work, ensure_ascii=False, separators=(",", ":")) if active_work else "none"
    error = "; ".join(problems) if problems else "none"
    task = binding.get("task_id") or ""
    entry = (
        f'<agentos_relay task="{task}">THIS SESSION IS the 传旨 relay for task {task}: '
        "carry the user's words VERBATIM to the agentos-zhongshu agent (Agent tool, "
        f"description 中书省｜<task-title>｜{task}), bring its reply back unchanged; never think for 中书, "
        "never edit files, never run write-shaped shell; the ledger takes only "
        "`append --role relay --kind user_message|pause|resume|stop`.</agentos_relay>\n"
    ) if binding.get("seat") == aos.RELAY_SEAT else ""
    context = (
        '<agentos_attention phase="restore">\n'
        + entry +
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
