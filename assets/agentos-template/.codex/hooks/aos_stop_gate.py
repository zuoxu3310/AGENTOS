#!/usr/bin/env python3
"""Stop hook: per-turn audit enforcer for Codex.

Six-line entry checks (2026-07-06 gate hardening, ported from the Claude side):
gates dispositions, verbatim intent quote (skipped when the runtime provides no
transcript), restate line on long replies. All checks fail open on missing data.
"""
from __future__ import annotations

import json
from pathlib import Path

import aos_common as aos

MAX_BLOCKS = 2
LONG_REPLY_CHARS = 1200


def last_assistant_text(transcript_path: str) -> str:
    try:
        lines = Path(transcript_path).read_text(encoding="utf-8", errors="replace").splitlines()
    except Exception:
        return ""
    for line in reversed(lines[-400:]):
        try:
            obj = json.loads(line)
        except Exception:
            continue
        if obj.get("type") not in ("assistant", "item.completed"):
            continue
        content = obj.get("message", {}).get("content") or obj.get("content") or []
        if isinstance(content, str):
            return content
        texts = [p.get("text", "") for p in content if isinstance(p, dict) and p.get("type") == "text"]
        if texts:
            return "\n".join(texts)
    return ""


def main() -> int:
    data = aos.hook_input()
    if aos.disabled():
        return 0
    root = aos.project_root(data)
    log = aos.audit_log_path(root)
    if not log.is_file():
        return 0

    text = log.read_text(encoding="utf-8")
    session_id = str(data.get("session_id") or data.get("conversation_id") or "")
    sid = aos.sid_of(session_id)
    state = aos.load_state(root, session_id)
    baseline = state.get("last_n")
    mine = aos.entries_for_sid(text, sid)
    newest = mine[-1] if mine else 0
    if baseline is None:
        state.update({"last_n": newest, "retries": 0})
        aos.save_state(root, session_id, state)
        aos.log_compliance(root, session_id, "ok", f"no-baseline #{newest}({sid})")
        return 0
    retries = int(state.get("retries", 0))

    problems: list[str] = []
    if newest <= baseline:
        problems.append(
            f"missing this turn's audit entry: expected a new `## <n> ({sid}) — …` entry for this session,"
            f" its newest is still #{newest if newest else '(none)'}"
        )
    else:
        # Cross-session number collisions are legal (sessions share one log);
        # within a session, append-only means numbers strictly increase.
        if any(b <= a for a, b in zip(mine, mine[1:])):
            problems.append(
                f"this session's entry numbers must be strictly increasing in file order (got {mine};"
                " append-only — take a fresh higher number, never renumber or edit past entries)"
            )
        missing = aos.entry_missing_fields(text, newest, sid)
        if missing:
            problems.append(f"entry #{newest} ({sid}) missing fields: {', '.join(missing)}")
        if not missing:
            block = aos.entry_block(text, newest, sid)
            gp = aos.gates_line_problem(block)
            if gp:
                problems.append(gp)
            user_text = aos.last_user_text(data.get("transcript_path", ""))
            if user_text and not aos.is_notification_turn(user_text):
                ip = aos.intent_quote_problem(block, user_text)
                if ip:
                    problems.append(ip + " (intent-gate trace: `- intent: quote「<verbatim substring of the user message>」→ goal / deliverable / not-doing`)")
            import re as _re
            answer_now = last_assistant_text(data.get("transcript_path", ""))
            if len(answer_now) >= LONG_REPLY_CHARS and not _re.search(r"^\s*- restate:", block, _re.MULTILINE):
                problems.append(
                    f"long deliverable turn (>= {LONG_REPLY_CHARS} chars) lacks a `- restate:` line"
                    " (zero-context restate test: hand ONLY the reply text to a cheap fresh reader)"
                )

    visible_note = ""
    if not problems:
        answer = last_assistant_text(data.get("transcript_path", ""))
        if answer and (f"#{newest}" not in answer and "per_turn_audit" not in answer):
            visible_note = " visible-block-unconfirmed"

    if not problems:
        state.update({"last_n": newest, "retries": 0})
        aos.save_state(root, session_id, state)
        aos.log_compliance(root, session_id, "ok" if retries == 0 else "forced_ok", f"#{newest}({sid}){visible_note}")
        return 0

    if retries >= MAX_BLOCKS:
        state["retries"] = 0
        aos.save_state(root, session_id, state)
        aos.log_compliance(root, session_id, "missed", "; ".join(problems))
        return 0

    state["retries"] = retries + 1
    aos.save_state(root, session_id, state)
    next_number = aos.max_entry(text) + 1
    aos.emit_block_decision(
        "AgentOS per-turn audit failed: " + "; ".join(problems)
        + f". APPEND (never edit past entries) `## {next_number} ({sid}) — <one-line label>`"
        + " in agent-os/state/audit-log.md (six lines: - object: / - contract: / - action+evidence: / - status: /"
        + " - gates: per-gate dispositions / - intent: 「verbatim user quote」),"
        + " and end the visible answer with the audit block. Rule: agent-os/review/per-turn-audit-gate.md"
    )
    return 0


if __name__ == "__main__":
    aos.run_guarded(main)
