#!/usr/bin/env python3
"""Stop hook: per-turn audit enforcer for Codex."""
from __future__ import annotations

import json
from pathlib import Path

import aos_common as aos

MAX_BLOCKS = 2


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
    cur_max = aos.max_entry(text)
    session_id = str(data.get("session_id") or data.get("conversation_id") or "")
    state = aos.load_state(root, session_id)
    baseline = state.get("baseline")
    if baseline is None:
        state.update({"baseline": cur_max, "retries": 0})
        aos.save_state(root, session_id, state)
        aos.log_compliance(root, session_id, "ok", f"no-baseline #{cur_max}")
        return 0
    retries = int(state.get("retries", 0))

    problems: list[str] = []
    if cur_max <= baseline:
        problems.append(f"Missing this turn's audit entry: expected a new #{baseline + 1}, but the audit-log max is still #{cur_max}")
    else:
        missing = aos.entry_missing_fields(text, cur_max)
        if missing:
            problems.append(f"Entry #{cur_max} is missing fields: {', '.join(missing)}")
        nums = [n for n, _ in aos.parse_entries(text)]
        dups = sorted({n for n in nums if nums.count(n) > 1})
        if dups:
            problems.append(f"Duplicate entry numbers: {dups} (parallel sessions must continue the numbering)")
        expected = set(range(baseline + 1, cur_max + 1))
        if not expected.issubset(set(nums)):
            problems.append(f"Entry numbers not contiguous: {baseline + 1}..{cur_max} must each exist")

    visible_note = ""
    if not problems:
        answer = last_assistant_text(data.get("transcript_path", ""))
        if answer and (f"#{cur_max}" not in answer and "per_turn_audit" not in answer):
            visible_note = " visible-block-unconfirmed"

    if not problems:
        state.update({"baseline": cur_max, "retries": 0})
        aos.save_state(root, session_id, state)
        aos.log_compliance(root, session_id, "ok" if retries == 0 else "forced_ok", f"#{cur_max}{visible_note}")
        return 0

    if retries >= MAX_BLOCKS:
        state["retries"] = 0
        aos.save_state(root, session_id, state)
        aos.log_compliance(root, session_id, "missed", "; ".join(problems))
        return 0

    state["retries"] = retries + 1
    aos.save_state(root, session_id, state)
    next_number = max(cur_max, baseline) + (0 if cur_max > baseline else 1)
    aos.emit_block_decision(
        "AgentOS per-turn audit failed: " + "; ".join(problems)
        + f". Append to agent-os/state/audit-log.md: `## {next_number} — <one-line label>`"
        + " entry (four lines - object: / - contract: / - action+evidence: / - status:), "
        + "and append an audit block at the end of your answer. Rule: agent-os/review/per-turn-audit-gate.md"
    )
    return 0


if __name__ == "__main__":
    aos.run_guarded(main)
