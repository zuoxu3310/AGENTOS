#!/usr/bin/env python3
"""UserPromptSubmit: bring the latest real user request back into attention."""
from __future__ import annotations

import json

import aos_common as aos


SEAT_NAMES = {"agentos-zhongshu": "中书（Zhongshu）", "agentos-menxia": "门下（Menxia）",
              "agentos-shangshu": "尚书（Shangshu）", "agentos-executor": "执行体（Executor）",
              "agentos-yushi": "御史（Yushi）"}


def seat_context(root, data) -> str:
    """If the seat controller mapped this thread to a seat, say so first and loudly:
    a seat thread inherits the project's 中书 wording and must not act on it."""
    import json as _json
    session = aos.runtime_session(data)
    path = root / "agent-os" / "state" / "sessions" / f"codex-{session}.json"
    try:
        value = _json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return ""
    seat = value.get("seat")
    if seat == aos.RELAY_SEAT:
        task = value.get("task_id", "")
        return (f'<agentos_relay task="{task}">THIS SESSION IS the 传旨 relay for task {task}: '
                "append this user message verbatim (append --role relay --kind user_message), "
                "send it verbatim to the registered 中书省 thread, wait, read, and bring the reply "
                "back unchanged. Say 停/pause to record pause and leave the chain.</agentos_relay>\n")
    if seat not in SEAT_NAMES:
        return ""
    return (f'<agentos_seat seat="{seat}" task="{value.get("task_id", "")}">THIS THREAD IS '
            f"{SEAT_NAMES[seat]} for task {value.get('task_id', '')} — NOT 中书. Ignore any 中书/"
            "Zhongshu wording you inherited from AGENTS.md or developer instructions. Your seat "
            f"contract is .codex/agents/{seat}.toml; your method is agent-os/workflows/"
            f"{seat.split('-', 1)[1]}.md. Record ledger lines only as --role {seat.split('-', 1)[1]}."
            "</agentos_seat>\n")


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
    if not aos.chain_binding(root, "codex", data):
        return 0
    _, path, active_work, problems = aos.active_work_state(root, "codex", data)
    state = json.dumps(active_work, ensure_ascii=False, separators=(",", ":")) if active_work else "none"
    error = "; ".join(problems) if problems else "none"
    context = (
        '<agentos_attention phase="user_message">\n'
        + seat_context(root, data) +
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
