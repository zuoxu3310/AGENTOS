#!/usr/bin/env python3
"""SessionStart hook: inject the AgentOS static rules and dynamic state for Codex.

Also force-reads the project error ledger (parity with the Claude adapter,
2026-07-06): high-priority rules plus every undigested error record enter the
session at start — recorded lessons must not wait to be looked up.
"""
from __future__ import annotations

import re
import time

import aos_common as aos

STATIC_RULE_CARD = ".codex/agentos-local-rules.md"
MAX_ERROR_RULES = 10
MAX_UNDIGESTED = 8
MAX_LESSON_CHARS = 320


def digest_line(text: str, key: str) -> str:
    match = re.search(rf"{key}:\s*>?\s*(\S.*)", text)
    return match.group(1).strip()[:120] if match else "(not found)"


def read_static_rules(root):
    path = root / STATIC_RULE_CARD
    if not path.is_file():
        return None, ""
    return path, path.read_text(encoding="utf-8").strip()


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
    """Force-read digest of every undigested error RECORD (what happened + rule)."""
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
        out.append(f"- {title}: {happened} → RULE: {rule}"[:MAX_LESSON_CHARS])
    return out


def resident_bodies(root) -> list[str]:
    """Full text of the every-turn method bodies (owner ruling 2026-07-12).

    The rules card carries triggers and constraints (the what-not); these
    files carry method (the how). Measured 2026-07-12: 10 review gates +
    lifecycle ≈ 50 KB ≈ 6% of a 200k window — cheap enough to reside.
    Rare-path bodies (fusion/dynamic workflows, memory/, adapters/) stay
    on-demand via router.md.
    """
    files = sorted((root / "agent-os" / "review").glob("*.md"))
    files.append(root / "agent-os" / "workflows" / "agent-execution-lifecycle.md")
    out = []
    for f in files:
        if not f.is_file():
            continue
        rel = f.relative_to(root).as_posix()
        body = f.read_text(encoding="utf-8", errors="replace").strip()
        out.append(f"\n===== RESIDENT METHOD BODY: {rel} =====\n{body}")
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
    sid = aos.sid_of(str(data.get("session_id") or data.get("conversation_id") or ""))
    session_id = str(data.get("session_id") or data.get("conversation_id") or "")
    if data.get("source") != "compact":
        state = aos.load_state(root, session_id)
        state.update({"last_n": max(aos.entries_for_sid(text, sid), default=0), "retries": 0})
        aos.save_state(root, session_id, state)

    current = root / "agent-os" / "state" / "current.md"
    cur_text = current.read_text(encoding="utf-8") if current.is_file() else ""
    rule_path, rule_card = read_static_rules(root)

    if rule_card:
        print(f"""[AgentOS | Codex Static Rules Card | {rule_path.relative_to(root).as_posix()}]
{rule_card}
[AgentOS | Codex Static Rules Card End]""")
    else:
        print(f"[AgentOS] {STATIC_RULE_CARD} is missing; Codex still reads AGENTS.md, "
              "but the full discipline card was not injected.")

    lines = [
        f"[AgentOS | Codex SessionStart injection | {time.strftime('%Y-%m-%d')}]",
        "The static discipline card above was injected by the SessionStart hook; "
        "AGENTS.md remains the durable project entry point.",
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
    bodies = resident_bodies(root)
    if bodies:
        lines.append(
            "Resident method bodies (owner ruling 2026-07-12): full text of every"
            " review gate + the execution lifecycle — the HOW behind the rules card's"
            " triggers. Apply these when walking gates; re-read the files only when"
            " editing them. Rare-path bodies (fusion/dynamic workflows, memory/,"
            " adapters/) remain on-demand via router.md.")
        lines.extend(bodies)
    print("\n".join(lines))
    return 0


if __name__ == "__main__":
    aos.run_guarded(main)
