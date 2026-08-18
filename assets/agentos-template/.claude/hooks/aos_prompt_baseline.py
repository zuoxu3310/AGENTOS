#!/usr/bin/env python3
"""UserPromptSubmit: bring the latest real user request back into attention."""
from __future__ import annotations

import json
import os

import aos_common as aos

CONTEXT_ALARM_TOKENS = 400_000
# Below this transcript byte size the estimate cannot reach the alarm line.
_MIN_ALARM_BYTES = 1_200_000


def _estimated_context_tokens(data: dict) -> int:
    """Rough live-context estimate from the transcript (~4 ASCII chars or 1
    non-ASCII char per token), counted from the last compaction boundary."""
    path = data.get("transcript_path")
    if not isinstance(path, str) or not path or not os.path.isfile(path):
        return 0
    if os.path.getsize(path) < _MIN_ALARM_BYTES:
        return 0
    with open(path, "r", encoding="utf-8", errors="ignore") as fh:
        lines = fh.readlines()
    start = 0
    boundary_markers = (
        '"isCompactSummary":true', '"isCompactSummary": true',
        '"subtype":"compact_boundary"', '"subtype": "compact_boundary"',
    )
    for index, line in enumerate(lines):
        if any(marker in line for marker in boundary_markers):
            start = index
    ascii_chars = other_chars = 0
    for line in lines[start:]:
        try:
            event = json.loads(line)
        except Exception:
            continue
        message = event.get("message")
        if not isinstance(message, dict):
            continue
        content = message.get("content")
        texts: list[str] = []
        if isinstance(content, str):
            texts.append(content)
        elif isinstance(content, list):
            for block in content:
                if isinstance(block, dict):
                    for key in ("text", "thinking", "content"):
                        value = block.get(key)
                        if isinstance(value, str):
                            texts.append(value)
        for text in texts:
            for char in text:
                if ord(char) < 128:
                    ascii_chars += 1
                else:
                    other_chars += 1
    return ascii_chars // 4 + other_chars


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
    binding = aos.chain_binding(root, "claude", data)
    if not binding:
        return 0
    _, path, active_work, problems = aos.active_work_state(root, "claude", data)
    state = json.dumps(active_work, ensure_ascii=False, separators=(",", ":")) if active_work else "none"
    error = "; ".join(problems) if problems else "none"
    task = binding.get("task_id") or ""
    relay = (
        f'<agentos_zhongshu task="{task}">THIS SESSION IS 中书省 for task {task}: '
        "append this user message verbatim (append --role zhongshu --kind user_message, newlines "
        "kept), then work by agent-os/workflows/zhongshu.md — 门下 sees the raw words before any "
        "candidate of yours; a seat running in the background wakes you when it finishes, so end "
        "the turn instead of sleeping. If the user says 停/pause or 关掉/stop: TaskStop the running "
        "seats, then record pause/stop and leave the chain.</agentos_zhongshu>\n"
    ) if binding.get("seat") == aos.MAIN_SEATS.get("claude") else ""
    context = (
        '<agentos_attention phase="user_message">\n'
        + relay +
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
    try:
        estimate = _estimated_context_tokens(data)
    except Exception:
        estimate = 0
    payload: dict = {
        "hookSpecificOutput": {
            "hookEventName": "UserPromptSubmit",
            "additionalContext": context,
        }
    }
    if estimate >= CONTEXT_ALARM_TOKENS:
        payload["systemMessage"] = (
            f"[AgentOS] context estimate ~{estimate:,} tokens (>= {CONTEXT_ALARM_TOKENS:,}): "
            "persist conclusions to the ledgers and consider a fresh session. Estimate from "
            "the transcript, not a billing fact."
        )
        payload["hookSpecificOutput"]["additionalContext"] = context + (
            f'\n<context_cost_alarm estimated_tokens="{estimate}">Estimated live context has '
            f"crossed {CONTEXT_ALARM_TOKENS} tokens. State this plainly to the user in the next "
            "reply, persist conclusions to the ledgers, and recommend continuing in a fresh "
            "session when the current task allows a clean handoff.</context_cost_alarm>"
        )
    print(json.dumps(payload, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    aos.run_guarded(main)
