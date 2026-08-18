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
        f'<agentos_zhongshu task="{task}">THIS SESSION IS 中书省 (Zhongshu) for task {task}: '
        "the user invoked the `agentos` skill and this main session is the bound 中书 seat. "
        "Work by `.claude/skills/agentos/SKILL.md` and `agent-os/workflows/zhongshu.md`: record "
        "each user message VERBATIM (`append --role zhongshu --kind user_message`), give 门下 the raw "
        "words first (Agent agentos-menxia), 尚书 only after 门下's pass, ONE delivery recorded as "
        "`delivery`; never edit project files or run write-shaped shell yourself, never sleep-poll a "
        "seat — say what is happening and end the turn, the completion notification wakes you. "
        "Pause/stop: TaskStop every running seat, then `append --role zhongshu --kind pause|stop`."
        "</agentos_zhongshu>\n"
    ) if binding.get("seat") == aos.MAIN_SEATS.get("claude") else ""
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
