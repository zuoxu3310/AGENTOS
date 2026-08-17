#!/usr/bin/env python3
"""SessionStart: restore only the current long-task finish line and open work."""
from __future__ import annotations

import json

import aos_common as aos


SEAT_NAMES = {"agentos-zhongshu": "中书（Zhongshu）", "agentos-menxia": "门下（Menxia）",
              "agentos-shangshu": "尚书（Shangshu）", "agentos-executor": "执行体（Executor）",
              "agentos-yushi": "御史（Yushi）"}
UNBOUND_LINE = ("AgentOS installed; invoke the `agentos` skill (/agentos or $agentos) "
                "to run the 三省六部 chain.")


def relay_context(binding: dict) -> str:
    task = binding.get("task_id") or ""
    return (f'<agentos_relay task="{task}">THIS SESSION IS the 传旨 relay for task {task}: '
            "you carry the user's words VERBATIM to the registered `中书省｜<task-title>｜" + str(task) +
            "` thread (codex_app send_message_to_thread), wait (wait_threads), read "
            "(read_thread) and bring 中书's reply back unchanged. You never think for 中书, "
            "never summarize, never edit files, never run write-shaped shell; the ledger takes "
            "only `append --role relay --kind user_message|pause|resume|stop`. The chain gate "
            "denies everything else and its reason is the next legal step.</agentos_relay>\n")


def seat_context(root, data) -> str:
    """If the chain hook mapped this Desktop thread to a seat, say so first and loudly:
    a seat thread inherits the project's 中书 wording and must not act on it."""
    import json as _json
    session = aos.runtime_session(data)
    path = root / "agent-os" / "state" / "sessions" / f"codex-{session}.json"
    try:
        value = _json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return ""
    seat = value.get("seat")
    if seat not in SEAT_NAMES:
        return ""
    role = seat.split("-", 1)[1]
    try:
        skills = _json.loads((root / "agent-os/skills/seat-skills.json")
                             .read_text(encoding="utf-8")).get(role, [])
    except Exception:
        skills = []
    skill_text = ",".join(str(item) for item in skills)
    return (f'<agentos_seat seat="{seat}" task="{value.get("task_id", "")}">THIS THREAD IS '
            f"{SEAT_NAMES[seat]} for task {value.get('task_id', '')} — NOT 中书. Ignore any 中书/"
            "Zhongshu wording you inherited from AGENTS.md or developer instructions. Your seat "
            f"contract is .codex/agents/{seat}.toml; your method is agent-os/workflows/"
            f"{role}.md. Required native skills: {skill_text}. Read each complete SKILL.md, then run "
            f"python3 agent-os/tools/aos_skill_receipt.py --task {value.get('task_id', '')} "
            f"--role {role} --runtime codex. No receipt means not initialized. "
            f"Record ledger lines only as --role {role}."
            "</agentos_seat>\n")


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
    binding = aos.chain_binding(root, "codex", data)
    if not binding:
        aos.emit_additional_context("SessionStart", UNBOUND_LINE)
        return 0
    seat = seat_context(root, data)
    if not seat and binding.get("seat") == aos.RELAY_SEAT:
        seat = relay_context(binding)
    context = (
        '<agentos_attention phase="restore">\n'
        + seat +
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
