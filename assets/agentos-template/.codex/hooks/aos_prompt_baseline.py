#!/usr/bin/env python3
"""UserPromptSubmit hook: record the per-turn audit baseline for Codex."""
from __future__ import annotations

import aos_common as aos


def main() -> int:
    data = aos.hook_input()
    if aos.disabled():
        return 0
    root = aos.project_root(data)
    log = aos.audit_log_path(root)
    if not log.is_file():
        return 0

    text = log.read_text(encoding="utf-8")
    nxt = aos.max_entry(text) + 1
    session_id = str(data.get("session_id") or data.get("conversation_id") or "")
    sid = aos.sid_of(session_id)
    state = aos.load_state(root, session_id)
    state.update({"last_n": max(aos.entries_for_sid(text, sid), default=0), "retries": 0})
    aos.save_state(root, session_id, state)

    print(
        f"[AgentOS] This turn's audit entry: `## {nxt} ({sid}) — <label>` -> agent-os/state/audit-log.md"
        " (APPEND only; concurrent sessions share the log — if another session takes"
        f" #{nxt} first, any higher number is fine). Codex Stop gate checks a six-line entry:"
        " four base fields + `- gates:` per-gate dispositions (intent= mandatory, >=3 total) + `- intent:` with a"
        " 「verbatim quote of this turn's user message」 when a transcript is available."
        f" End the visible answer with the audit block closing #{nxt}"
    )
    return 0


if __name__ == "__main__":
    aos.run_guarded(main)
