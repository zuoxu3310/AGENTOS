#!/usr/bin/env python3
"""Stop hook: the per-turn audit enforcer.

Verifies, before the turn is allowed to finish, that:
1. agent-os/state/audit-log.md gained a new `## <n> (<sid>) — …` entry for THIS
   session (2026-07-07: numbering is per-session — concurrent sessions share one
   log, so cross-session number collisions are legal and only this session's
   numbers must strictly increase; repairs are append-only, never renumber);
2. the newest entry is well-formed (header + object/contract/action+evidence/status
   + gates/intent — 2026-07-06 gate hardening);
3. the gates line disposes each gate explicitly (intent= mandatory, >=3 dispositions);
4. on real-instruction turns the intent line quotes the user's words verbatim
   (substring-checked against the CORPUS of the turn-opening user message group —
   queued messages and option answers all count; harness injections never do);
5. long deliverable replies (>=1200 chars) carry a `- restate:` line proving the
   zero-context restate test ran (reply text handed to a fresh cheap reader that
   must restate mechanism + decisions; fail -> rewrite before delivering).

The visible-audit-block scan of the transcript is ADVISORY ONLY (recorded in
the compliance log, never blocking): transcript flushing races with the Stop
event and produced false blocks (2026-07-05, twice). File-based checks are
race-free and stay blocking.

Blocks at most MAX_BLOCKS times per turn, then fails open and records a
`missed` row in agent-os/state/compliance-log.tsv so misses are measurable
instead of silent. Enforces existence and format only — never truthfulness.
"""
from __future__ import annotations

import json
import re
from pathlib import Path

import aos_common as aos

MAX_BLOCKS = 2
LONG_REPLY_CHARS = 1200

# Translation-shell / boilerplate seed list (Tier-1 seed, 2026-07-07). ADVISORY ONLY — counted and logged, never blocking: the
# field survey showed naive semantic word-gates misfire badly (>70% FP on
# open detectors), so this instrument measures recurrence instead of gating.
SHELL_TERMS = (
    "值得注意的是", "综上所述", "总而言之", "不难发现", "深入探讨",
    "全方位", "一站式", "无缝", "赋能", "抓手", "闭环", "颗粒度",
    "底层逻辑", "本质上而言", "至关重要", "显著提升", "进行了",
    "零假设", "鲁棒", "显著高于",
)
SHELL_WARN_AT = 3  # distinct terms in one reply

# Final-message pointer phrases (2026-07-07 field incident: a 3221-char
# deliverable sat mid-turn, the final message said "已在上方交付" — and the
# user saw nothing). Text written before tool actions may never reach the
# user, so a final message that POINTS at it instead of carrying it is a
# delivery failure. Narrow list on purpose: precision over recall.
POINTER_PHRASES = (
    "已在上方", "已在上面", "见上文", "上面已交付", "上方已交付", "上文已给出",
)


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
        if obj.get("type") != "assistant":
            continue
        content = (obj.get("message") or {}).get("content") or []
        texts = [p.get("text", "") for p in content if isinstance(p, dict) and p.get("type") == "text"]
        if texts:
            return "\n".join(texts)
    return ""


def pointer_hit(answer: str) -> str | None:
    """First pointer phrase USED (not merely mentioned) in the answer.

    A quoted occurrence (「已在上方」-style examples when DISCUSSING this very
    gate) is a mention, not a pointing act — the gate's own launch reply
    tripped on this within the hour (2026-07-07). A match immediately preceded
    by a quote character is therefore exempt.
    """
    for p in POINTER_PHRASES:
        i = answer.find(p)
        while i != -1:
            prev = answer[i - 1] if i > 0 else ""
            if prev not in "「『\"'“‘（(":
                return p
            i = answer.find(p, i + 1)
    return None


def style_warnings(answer: str) -> list[str]:
    """Countable style checks — ADVISORY ONLY (logged, never blocking).

    The final-answer text races the Stop event (false blocks 2026-07-05), so
    these follow the visible-scan precedent: measure, do not block.

    Deliberately NOT checked here (owner ruling 2026-07-06):
    - any owner-side canary phrase (a diagnostic signal the user checks by eye);
      enforcing one mechanically would silence the very signal it exists to give;
    - coined-term (codename) violations — not string-checkable; the restate
      test covers them via the zero-context reader.
    """
    warns = []
    if not answer:
        return warns
    if len(re.findall(r"^#{1,6}\s", answer, re.MULTILINE)) > 3:
        warns.append("more than 3 markdown headers in a chat reply (report-tone signal, per error-ledger rule 2026-07-06)")
    shell_hits = [t for t in SHELL_TERMS if t in answer]
    if len(shell_hits) >= SHELL_WARN_AT:
        warns.append("translation-shell/boilerplate terms in reply: " + "、".join(shell_hits[:8]))
    return warns


def main() -> int:
    data = aos.hook_input()
    if aos.disabled():
        return 0
    root = aos.project_root(data)
    log = aos.audit_log_path(root)
    if not log.is_file():
        return 0

    text = log.read_text(encoding="utf-8")
    session_id = data.get("session_id", "")
    sid = aos.sid_of(session_id)
    state = aos.load_state(root, session_id)
    baseline = state.get("last_n")
    mine = aos.entries_for_sid(text, sid)
    newest = mine[-1] if mine else 0
    if baseline is None:
        # No baseline (hook attached/upgraded mid-session etc.): degrade gracefully — log, never block
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
        else:
            block = aos.entry_block(text, newest, sid)
            gp = aos.gates_line_problem(block)
            if gp:
                problems.append(gp)
            user_texts = aos.turn_user_texts(data.get("transcript_path", ""))
            user_text = "\n".join(user_texts)
            if user_text and not any(aos.is_notification_turn(t) for t in user_texts):
                ip = aos.intent_quote_problem(block, user_text)
                if ip:
                    problems.append(ip + " (intent-gate trace: `- intent: quote「<verbatim substring of the user message>」→ goal / deliverable / not-doing`)")
            answer_now = last_assistant_text(data.get("transcript_path", ""))
            if len(answer_now) >= LONG_REPLY_CHARS and not re.search(r"^\s*- restate:", block, re.MULTILINE):
                problems.append(
                    f"long deliverable turn (>= {LONG_REPLY_CHARS} chars) lacks a `- restate:` line: run the zero-context"
                    " restate test first (hand ONLY the reply text to a cheap fresh reader; it must restate the"
                    " core mechanism and the pending decisions; if it cannot, rewrite before delivering),"
                    " then add `- restate: passed(<reader>/one-line gist)` or `rewritten(reason)` to the entry"
                )

    final_answer = last_assistant_text(data.get("transcript_path", ""))
    hit = pointer_hit(final_answer)
    if hit:
        problems.append(
            f"the final message points at mid-turn text (「{hit}」) instead of carrying the answer —"
            " text written before tool actions may never reach the user; re-send the COMPLETE"
            " answer as the final message (audit first, then the full answer last)"
        )

    visible_note = ""
    if not problems:
        answer = final_answer
        if answer and (f"#{newest}" not in answer and "per_turn_audit" not in answer):
            # Log-only, never block: transcript flushing races the Stop event; blocking misfires
            visible_note = " visible-block-unconfirmed"

    if not problems:
        warns = style_warnings(final_answer)
        turn_texts = aos.turn_assistant_texts(data.get("transcript_path", ""))
        if len(turn_texts) >= 2:
            prior_max = max(len(t) for t in turn_texts[:-1])
            if prior_max >= 600 and len(turn_texts[-1]) < min(300, prior_max // 3):
                warns.append(
                    f"possible mid-turn delivery: a {prior_max}-char text sits before tool actions"
                    f" while the final message is only {len(turn_texts[-1])} chars"
                )
        if warns:
            aos.log_compliance(root, session_id, "style_warn", "; ".join(warns))
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
    suggested = aos.max_entry(text) + 1
    aos.emit_block_decision(
        "AgentOS per-turn audit failed: " + "; ".join(problems)
        + f". APPEND (never edit past entries) `## {suggested} ({sid}) — <one-line label>`"
        + " to agent-os/state/audit-log.md (six lines: - object: / - contract: / - action+evidence: / - status: /"
        + " - gates: per-gate dispositions / - intent: 「verbatim user quote」; one short phrase per line suffices on small turns),"
        + " and end the visible answer with the audit block. Rule: agent-os/review/per-turn-audit-gate.md"
    )
    return 0


if __name__ == "__main__":
    aos.run_guarded(main)
