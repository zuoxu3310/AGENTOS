#!/usr/bin/env python3
"""SessionStart hook: inject the AgentOS DYNAMIC state digest.

Static invariants live in .claude/rules/agentos-local-rules.md, which the
harness injects natively every session (verified 2026-07-05, project-level
rules dir is a forced-injection channel). This hook only adds what a static
file cannot: the next audit entry number and the current-state digest.
"""
from __future__ import annotations

import re
import time

import aos_common as aos


def digest_line(text: str, key: str) -> str:
    m = re.search(rf"{key}:\s*>?\s*(\S.*)", text)
    return m.group(1).strip()[:120] if m else "(unavailable)"


def main() -> int:
    data = aos.hook_input()
    if aos.disabled():
        return 0
    root = aos.project_root(data)
    log = aos.audit_log_path(root)
    if not log.is_file():
        print("[AgentOS] Detected agent-os/ but state/audit-log.md is missing; complete it per agent-os/boot.md before running the per-turn audit.")
        return 0

    nxt = aos.max_entry(log.read_text(encoding="utf-8")) + 1
    session_id = data.get("session_id", "")
    # Re-injection after compaction must not reset this turn's baseline, to avoid weakening the current check
    if data.get("source") != "compact":
        state = aos.load_state(root, session_id)
        state.update({"baseline": nxt - 1, "retries": 0})
        aos.save_state(root, session_id, state)

    current = root / "agent-os" / "state" / "current.md"
    cur_text = current.read_text(encoding="utf-8") if current.is_file() else ""

    print(f"""[AgentOS | SessionStart injection | {time.strftime('%Y-%m-%d')}]
Static rules come from the session-injected local rules card (.claude/rules/agentos-local-rules.md).
Dynamic state:
- Next audit entry this session: #{nxt} (checked by the Stop gate; a miss is blocked)
- active_user_object: {digest_line(cur_text, "active_user_object")}
- next_safe_action: {digest_line(cur_text, "next_safe_action")}""")
    return 0


if __name__ == "__main__":
    aos.run_guarded(main)
