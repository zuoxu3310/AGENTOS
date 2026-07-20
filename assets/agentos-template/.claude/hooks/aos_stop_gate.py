#!/usr/bin/env python3
"""Stop: give a finished or blocked long task one delivery review."""
from __future__ import annotations

import json

import aos_common as aos


def _truthy(value) -> bool:
    return value is True or str(value).lower() in {"1", "true", "yes"}


def continuation_prompt(active_work: dict, problems: list[str]) -> str:
    state = json.dumps(active_work, ensure_ascii=False, separators=(",", ":"))
    state_problems = "; ".join(problems) if problems else "none"
    return (
        f"{aos.STOP_CONTINUATION_MARKER}\n"
        "<role>Recheck one long-task delivery before it reaches the user.</role>\n"
        f"<context><active_work>{state}</active_work>"
        f"<mechanical_state_error>{state_problems}</mechanical_state_error></context>\n"
        "<instructions>Use the same main model. First confirm whether the task is done or "
        "blocked from the recorded conditions and evidence. Then rewrite the delivery in the "
        "simplest natural language that still tells the user: what happened, what they now "
        "have, what remains, and what they need to decide or do. Remove unnecessary jargon, "
        "translation-like phrasing, internal mechanism names, and work-log detail. Do not hide "
        "a boundary, risk, missing evidence, or unfinished item. If mechanical_state_error is "
        "not none, fix the state file before returning.</instructions>\n"
        "<output_format>Return only the normal user-facing answer.</output_format>\n"
        "<question>Recheck and deliver the result now.</question>"
    )


def main() -> int:
    data = aos.hook_input()
    if aos.disabled():
        return 0
    root = aos.project_root(data)
    if not (root / "agent-os").is_dir():
        return 0
    module, path, active_work, problems = aos.active_work_state(root, "claude", data)
    if not active_work or active_work.get("report_state") != "pending":
        return 0
    if not _truthy(data.get("stop_hook_active")):
        aos.emit_stop_block(continuation_prompt(active_work, problems))
        return 0
    if problems:
        print(json.dumps({
            "systemMessage": "AgentOS did not mark this long-task report delivered because "
            "its mechanical state is invalid: " + "; ".join(problems)
        }, ensure_ascii=False))
        return 0
    delivered_problems = module.mark_delivered(path)
    if delivered_problems:
        print(json.dumps({
            "systemMessage": "AgentOS could not mark the long-task report delivered: "
            + "; ".join(delivered_problems)
        }, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    aos.run_guarded(main)
