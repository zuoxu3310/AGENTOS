#!/usr/bin/env python3
"""SessionStart hook: inject the AgentOS DYNAMIC state digest.

Static invariants live in .claude/rules/agentos-local-rules.md, which the
harness injects natively every session (verified 2026-07-05, project-level
rules dir is a forced-injection channel). This hook adds what a static file
cannot: the next audit entry number, the current-state digest, and the
high-priority rules distilled from the project error ledger (wiki/errors/
_INDEX.md) — recorded lessons must enter every session, not wait to be
looked up (owner ruling 2026-07-06).
"""
from __future__ import annotations

import re
import time

import aos_common as aos

MAX_ERROR_RULES = 10
MAX_UNDIGESTED = 8          # newest undigested error records force-read at start
MAX_LESSON_CHARS = 320      # per-record cap so the injection stays bounded


def digest_line(text: str, key: str) -> str:
    m = re.search(rf"{key}:\s*>?\s*(\S.*)", text)
    return m.group(1).strip()[:120] if m else "(not found)"


def error_rules(root) -> list[str]:
    """High-priority rules section of wiki/errors/_INDEX.md (Chinese or English header)."""
    idx = root / "wiki" / "errors" / "_INDEX.md"
    if not idx.is_file():
        return []
    text = idx.read_text(encoding="utf-8", errors="replace")
    m = re.search(r"^##\s*(?:高优规则|High[- ]?priority rules?)\s*$(.*?)(?=^##\s|\Z)",
                  text, re.MULTILINE | re.DOTALL | re.IGNORECASE)
    if not m:
        return []
    rules = [l.strip() for l in m.group(1).splitlines() if l.strip().startswith("- ")]
    return rules[:MAX_ERROR_RULES]


def undigested_errors(root) -> list[str]:
    """Force-read digest of every undigested error RECORD (not just distilled rules).

    Reads each _INDEX entry marked 未消化/undigested, opens the record file, and
    injects `title — What happened (1 line) — Rule` capped per record. Once
    error-digest compresses a record, it drops out of this list and lives on as
    a high-priority rule — the injection stays bounded by construction.
    """
    idx = root / "wiki" / "errors" / "_INDEX.md"
    if not idx.is_file():
        return []
    text = idx.read_text(encoding="utf-8", errors="replace")
    entries = re.findall(r"^- .*?\[([^\]]+)\]\(([^)]+)\).*?(?:未消化|undigested).*$",
                         text, re.MULTILINE)
    sec = re.search(r"^##\s*(?:Recent Undigested[^\n]*|未消化[^\n]*)$(.*?)(?=^##\s|\Z)",
                    text, re.MULTILINE | re.DOTALL | re.IGNORECASE)
    if sec:
        entries += re.findall(r"^- .*?\[([^\]]+)\]\(([^)]+)\)", sec.group(1), re.MULTILINE)
    seen = set()
    entries = [e for e in entries if not (e[1] in seen or seen.add(e[1]))]
    out = []
    for title, fname in entries[-MAX_UNDIGESTED:]:
        f = root / "wiki" / "errors" / fname
        if not f.is_file():
            continue
        body = f.read_text(encoding="utf-8", errors="replace")

        def section(name: str) -> str:
            m = re.search(rf"^##\s*{name}\s*$(.*?)(?=^##\s|\Z)", body,
                          re.MULTILINE | re.DOTALL)
            return re.sub(r"\s+", " ", m.group(1)).strip() if m else ""

        def bullet(names: str) -> str:
            m = re.search(rf"^-\s*(?:{names})\s*[:：]\s*(.+)$", body, re.MULTILINE)
            return m.group(1).strip() if m else ""

        happened = (section("What happened") or bullet("错误|What happened"))[:140]
        rule = section("Rule") or bullet("规则|Rule|教训")
        lesson = f"- {title}: {happened} → RULE: {rule}"[:MAX_LESSON_CHARS]
        out.append(lesson)
    return out


def main() -> int:
    data = aos.hook_input()
    if aos.disabled():
        return 0
    root = aos.project_root(data)
    log = aos.audit_log_path(root)
    if not log.is_file():
        print("[AgentOS] Found agent-os/ but state/audit-log.md is missing; "
              "restore it per agent-os/boot.md before running the per-turn audit.")
        return 0

    text = log.read_text(encoding="utf-8")
    nxt = aos.max_entry(text) + 1
    session_id = data.get("session_id", "")
    sid = aos.sid_of(session_id)
    # Re-injection after compaction must not reset the turn baseline,
    # or it would weaken the current turn's check
    if data.get("source") != "compact":
        state = aos.load_state(root, session_id)
        state.update({"last_n": max(aos.entries_for_sid(text, sid), default=0), "retries": 0})
        aos.save_state(root, session_id, state)

    current = root / "agent-os" / "state" / "current.md"
    cur_text = current.read_text(encoding="utf-8") if current.is_file() else ""

    lines = [
        f"[AgentOS | SessionStart injection | {time.strftime('%Y-%m-%d')}]",
        "Static rules: see the local rules card already injected with the session"
        " (.claude/rules/agentos-local-rules.md).",
        "Dynamic state:",
        f"- next audit entry this session: `## {nxt} ({sid}) — <label>` (Stop gate verifies per session; missing entries are bounced; append-only)",
        f"- active_user_object: {digest_line(cur_text, 'active_user_object')}",
        f"- next_safe_action: {digest_line(cur_text, 'next_safe_action')}",
    ]
    rules = error_rules(root)
    if rules:
        lines.append("Error-ledger high-priority rules (wiki/errors/_INDEX.md — lessons already paid for; violating one repeats a recorded mistake):")
        lines.extend(rules)
    undigested = undigested_errors(root)
    if undigested:
        lines.append(f"Undigested error RECORDS, force-read ({len(undigested)} newest — what happened + the rule; run error-digest when they pile up):")
        lines.extend(undigested)
    print("\n".join(lines))
    return 0


if __name__ == "__main__":
    aos.run_guarded(main)
