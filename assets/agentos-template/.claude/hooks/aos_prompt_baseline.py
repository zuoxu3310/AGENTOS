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

    nxt = aos.max_entry(log.read_text(encoding="utf-8")) + 1
    session_id = data.get("session_id", "")
    state = aos.load_state(root, session_id)
    state.update({"baseline": nxt - 1, "retries": 0})
    aos.save_state(root, session_id, state)

    print(f"[AgentOS] This turn's audit entry: #{nxt} → agent-os/state/audit-log.md (the Stop hook will verify it; end your answer with an audit block closing on #{nxt})")
    return 0


if __name__ == "__main__":
    aos.run_guarded(main)
