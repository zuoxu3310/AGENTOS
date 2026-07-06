#!/usr/bin/env python3
"""SessionStart hook: inject the AgentOS static rules and dynamic state for Codex."""
from __future__ import annotations

import re
import time

import aos_common as aos

STATIC_RULE_CARD = ".codex/agentos-local-rules.md"


def digest_line(text: str, key: str) -> str:
    match = re.search(rf"{key}:\s*>?\s*(\S.*)", text)
    return match.group(1).strip()[:120] if match else "(unavailable)"


def read_static_rules(root):
    path = root / STATIC_RULE_CARD
    if not path.is_file():
        return None, ""
    return path, path.read_text(encoding="utf-8").strip()


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
    session_id = str(data.get("session_id") or data.get("conversation_id") or "")
    if data.get("source") != "compact":
        state = aos.load_state(root, session_id)
        state.update({"baseline": nxt - 1, "retries": 0})
        aos.save_state(root, session_id, state)

    current = root / "agent-os" / "state" / "current.md"
    cur_text = current.read_text(encoding="utf-8") if current.is_file() else ""
    rule_path, rule_card = read_static_rules(root)

    if rule_card:
        print(f"""[AgentOS | Codex Static Rules Card | {rule_path.relative_to(root).as_posix()}]
{rule_card}
[AgentOS | Codex Static Rules Card End]""")
    else:
        print(f"[AgentOS] Missing {STATIC_RULE_CARD}; Codex still reads AGENTS.md, but the full discipline card was not injected.")

    print(f"""[AgentOS | Codex SessionStart injection | {time.strftime('%Y-%m-%d')}]
The Codex static discipline card was injected by the SessionStart hook; AGENTS.md remains the durable project entry point.
Dynamic state:
- Next audit entry this session: #{nxt} (checked by the Stop hook; a miss is blocked)
- active_user_object: {digest_line(cur_text, "active_user_object")}
- next_safe_action: {digest_line(cur_text, "next_safe_action")}""")
    return 0


if __name__ == "__main__":
    aos.run_guarded(main)
