#!/usr/bin/env python3
"""Shared helpers for AgentOS enforcement hooks (Claude Code adapter).

Enforcement layer, not kernel: canonical rules live under agent-os/.
These hooks enforce existence, format, and numbering of mechanical
invariants only; they cannot judge truthfulness or quality.
Fail-open policy: a broken hook must never brick a session.
"""
from __future__ import annotations

import json
import os
import re
import sys
import time
from pathlib import Path

DISABLE_ENV = "AOS_HOOK_DISABLE"
# Heading: `## <n> (<sid>) — <label>`. The (<sid>) session tag is what lets
# concurrent sessions share one audit-log without number collisions being an
# error (2026-07-07); legacy entries without a tag still parse.
ENTRY_RE = re.compile(r"^## (\d+)(?: \(([A-Za-z0-9_-]{2,12})\))? — (.*)$", re.MULTILINE)
REQUIRED_FIELDS = ("- object:", "- contract:", "- action+evidence:", "- status:", "- gates:", "- intent:")
# Leading markers meaning "this turn carries no real user instruction"
# (notification/slash-command turns are exempt from the verbatim-quote check)
NOTIFY_MARKERS = (
    "<teammate-message", "<agent-message", "<task-notification",
    "<command-name>", "<local-command", "[SYSTEM NOTIFICATION",
    "Stop hook feedback:",  # retry turns are hook-triggered, not new user instructions
)


def hook_input() -> dict:
    try:
        return json.load(sys.stdin)
    except Exception:
        return {}


def disabled() -> bool:
    return os.environ.get(DISABLE_ENV, "") not in ("", "0")


def project_root(data: dict) -> Path:
    """Walk up from each candidate so a subdirectory cwd still finds the root."""
    for candidate in (os.environ.get("CLAUDE_PROJECT_DIR"), data.get("cwd"), str(Path.cwd())):
        if not candidate:
            continue
        base = Path(candidate)
        for p in (base, *base.parents):
            if (p / "agent-os").is_dir():
                return p
    return Path.cwd()


def audit_log_path(root: Path) -> Path:
    return root / "agent-os" / "state" / "audit-log.md"


def parse_entries(text: str) -> list[tuple[int, str, str]]:
    """(number, sid, label) per entry, in file order; sid is "" on legacy entries."""
    return [(int(m.group(1)), m.group(2) or "", m.group(3).strip()) for m in ENTRY_RE.finditer(text)]


def max_entry(text: str) -> int:
    return max((n for n, _, _ in parse_entries(text)), default=0)


def sid_of(session_id: str) -> str:
    """Short session tag for entry headings; stable within a session."""
    clean = re.sub(r"[^A-Za-z0-9]", "", session_id or "")
    return clean[:4] or "anon"


def entries_for_sid(text: str, sid: str) -> list[int]:
    """This session's entry numbers, in file order (append order)."""
    return [n for n, s, _ in parse_entries(text) if s == sid]


def entry_block(text: str, number: int, sid: str = "") -> str:
    tag = rf" \({re.escape(sid)}\)" if sid else ""
    marker = re.search(rf"^## {number}{tag} — .*$", text, re.MULTILINE)
    if not marker:
        return ""
    rest = text[marker.end():]
    nxt = ENTRY_RE.search(rest)
    return rest[: nxt.start()] if nxt else rest


def entry_missing_fields(text: str, number: int, sid: str = "") -> list[str]:
    """Fields must each exist as their own line, not as substrings in prose."""
    block = entry_block(text, number, sid)
    return [
        f for f in REQUIRED_FIELDS
        if not re.search(rf"^\s*{re.escape(f)}", block, re.MULTILINE)
    ]


def _norm(s: str) -> str:
    return re.sub(r"\s+", "", s)


def turn_user_texts(transcript_path: str) -> list[str]:
    """Texts of the turn-opening user message GROUP, oldest first.

    The turn's real instruction may be any of several queued user records
    (a substantive message followed by a one-letter option answer burned the
    single-record pick on 2026-07-07), so the whole contiguous group is the
    comparison corpus, not one record. Harness injections never speak for the
    user: records stamped isMeta (skill bodies, workflow expansions, Stop-hook
    bounces, image stub records) are skipped without closing the group, as are
    tool_result receipts and non-message record types. Once the group has
    started, an assistant record or a receipt marks the previous turn — stop.
    User messages flush at turn start, so this read has no Stop-event race.
    """
    try:
        lines = Path(transcript_path).read_text(encoding="utf-8", errors="replace").splitlines()
    except Exception:
        return []
    collected: list[str] = []
    for line in reversed(lines[-600:]):
        try:
            obj = json.loads(line)
        except Exception:
            continue
        rtype = obj.get("type")
        if rtype == "assistant":
            if collected:
                break
            continue
        if rtype != "user":
            continue  # attachment/system/mode records neither open nor close the group
        if obj.get("isMeta"):
            continue
        content = (obj.get("message") or {}).get("content")
        if isinstance(content, str):
            text = content
        else:
            blocks = [p for p in content or [] if isinstance(p, dict)]
            if any(p.get("type") == "tool_result" for p in blocks):
                # Mid-turn receipt (system reminders often ride along in this
                # shape): before the group it is this turn's work — skip;
                # after the group opened it belongs to the previous turn — stop.
                if collected:
                    break
                continue
            texts = [p.get("text", "") for p in blocks if p.get("type") == "text"]
            text = "\n".join(
                t for t in texts if t.strip() and not t.lstrip().startswith("<system-reminder")
            )
        # Belt over isMeta for harness versions that do not stamp skill bodies.
        if text.lstrip().startswith("Base directory for this skill"):
            continue
        if text.strip():
            collected.append(text)
    collected.reverse()
    return collected


def last_user_text(transcript_path: str) -> str:
    """Joined corpus of the turn-opening user group (see turn_user_texts)."""
    return "\n".join(turn_user_texts(transcript_path))


def turn_assistant_texts(transcript_path: str) -> list[str]:
    """Assistant text blocks since the last real user message, oldest first.

    Used by the mid-turn-delivery instrument: a long text early in this span
    with only a stub after the tool actions means the deliverable sat where
    the user may never see it. Queued user messages cut the span short, so
    this is a conservative bound — callers must treat it as advisory.
    """
    try:
        lines = Path(transcript_path).read_text(encoding="utf-8", errors="replace").splitlines()
    except Exception:
        return []
    collected: list[str] = []
    for line in reversed(lines[-600:]):
        try:
            obj = json.loads(line)
        except Exception:
            continue
        rtype = obj.get("type")
        if rtype == "assistant":
            content = (obj.get("message") or {}).get("content") or []
            texts = [p.get("text", "") for p in content if isinstance(p, dict) and p.get("type") == "text"]
            joined = "\n".join(t for t in texts if t.strip())
            if joined:
                collected.append(joined)
            continue
        if rtype != "user":
            continue
        if obj.get("isMeta"):
            continue
        content = (obj.get("message") or {}).get("content")
        if isinstance(content, str):
            if content.strip():
                break
            continue
        blocks = [p for p in content or [] if isinstance(p, dict)]
        if any(p.get("type") == "tool_result" for p in blocks):
            continue
        texts = [p.get("text", "") for p in blocks if p.get("type") == "text"]
        if any(t.strip() and not t.lstrip().startswith("<system-reminder") for t in texts):
            break
    collected.reverse()
    return collected


def is_notification_turn(user_text: str) -> bool:
    head = user_text.lstrip()[:200]
    return any(m in head for m in NOTIFY_MARKERS)


def intent_quote_problem(entry_block_text: str, user_text: str) -> str:
    """Content anchor: the intent line must quote the user verbatim inside 「…」,
    and the quote must be a literal substring of this turn's user message.

    One of the few anchors a script can verify for truth: a quote that does not
    match was invented. Empty return value = pass.
    """
    m = re.search(r"^\s*- intent:(.*)$", entry_block_text, re.MULTILINE)
    if not m:
        return "missing `- intent:` line"
    quotes = re.findall(r"「([^」]+)」", m.group(1))
    if not quotes:
        return "intent line lacks a 「verbatim user quote」"
    nu = _norm(user_text)
    # Minimum 4 chars to keep quotes non-trivial. The floor scales down for
    # short messages by their PUNCTUATION-STRIPPED length — otherwise a
    # trailing period forces the quote to include it ("收尾。" burned this).
    core_len = len(re.sub(r"[\W_]", "", user_text))
    need = min(4, core_len) or 1
    if any(len(_norm(q)) >= need and _norm(q) in nu for q in quotes):
        return ""
    return "the 「quote」 in the intent line is not a verbatim substring of this turn's user message"


def gates_line_problem(entry_block_text: str) -> str:
    """The gates line must dispose each gate: intent= mandatory, >=3 dispositions
    total (key=passed|n/a(short reason)).
    """
    m = re.search(r"^\s*- gates:(.*)$", entry_block_text, re.MULTILINE)
    if not m:
        return "missing `- gates:` line"
    line = m.group(1)
    if "intent=" not in line or line.count("=") < 3:
        return "gates line must dispose each gate (key=passed|n/a(short reason); keys: intent/syco/code/prompt/evidence/route), with intent= present and >=3 dispositions"
    return ""


def state_path(root: Path, session_id: str) -> Path:
    safe = re.sub(r"[^A-Za-z0-9_-]", "_", session_id or "unknown")
    return root / ".claude" / "hooks" / ".state" / f"{safe}.json"


def load_state(root: Path, session_id: str) -> dict:
    try:
        return json.loads(state_path(root, session_id).read_text(encoding="utf-8"))
    except Exception:
        return {}


def save_state(root: Path, session_id: str, state: dict) -> None:
    try:
        p = state_path(root, session_id)
        p.parent.mkdir(parents=True, exist_ok=True)
        tmp = p.with_suffix(".tmp")
        tmp.write_text(json.dumps(state, ensure_ascii=False), encoding="utf-8")
        os.replace(tmp, p)
    except Exception:
        pass


def log_compliance(root: Path, session_id: str, result: str, detail: str) -> None:
    """Append one measurement row. Script-written only; agents must not edit it."""
    try:
        p = root / "agent-os" / "state" / "compliance-log.tsv"
        if not p.exists():
            p.write_text("# ts\tsession\tevent\tresult\tdetail\n", encoding="utf-8")
        ts = time.strftime("%Y-%m-%dT%H:%M:%S")
        clean = detail.replace("\t", " ").replace("\n", " ")[:300]
        with p.open("a", encoding="utf-8") as f:
            f.write(f"{ts}\t{(session_id or 'unknown')[:8]}\tstop_gate\t{result}\t{clean}\n")
    except Exception:
        pass


def emit_block_decision(reason: str) -> None:
    print(json.dumps({"decision": "block", "reason": reason}, ensure_ascii=False))


def run_guarded(main) -> None:
    try:
        sys.exit(main())
    except SystemExit:
        raise
    except Exception as exc:
        print(f"[AgentOS] hook degraded (fail-open): {exc}", file=sys.stderr)
        sys.exit(0)
