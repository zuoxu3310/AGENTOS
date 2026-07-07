#!/usr/bin/env python3
"""UserPromptSubmit hook: record the per-turn audit baseline + one-line reminder.

The baseline (current max audit entry) is what the Stop gate compares against;
the reminder keeps the expected entry number salient at generation time.
"""
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
    session_id = data.get("session_id", "")
    sid = aos.sid_of(session_id)
    state = aos.load_state(root, session_id)
    state.update({"last_n": max(aos.entries_for_sid(text, sid), default=0), "retries": 0})
    aos.save_state(root, session_id, state)

    print(
        f"[AgentOS] This turn's audit entry: `## {nxt} ({sid}) — <label>` -> agent-os/state/audit-log.md"
        " (APPEND only; the (sid) tag is how concurrent sessions share the log — if another session takes"
        f" #{nxt} first, any higher number is fine). Stop gate checks a six-line entry:"
        " four base fields + `- gates:` per-gate dispositions (intent= mandatory, >=3 total) + `- intent:` with a"
        " 「verbatim quote of this turn's user message」 (notification/slash-command turns exempt; queued messages all count);"
        f" replies >=1200 chars also need `- restate:` (zero-context restate test). End the visible answer with the audit block closing #{nxt}"
    )
    return 0


if __name__ == "__main__":
    aos.run_guarded(main)
