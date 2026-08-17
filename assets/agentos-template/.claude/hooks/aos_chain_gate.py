#!/usr/bin/env python3
"""Chain gate: enforce the three-departments ORDER on mechanically provided facts.

Two facts only, never semantics:
  * who is calling  — the runtime's hook input `agent_type` (Claude seats) or the
    session mapping this gate wrote (Codex seat threads, and the relay: a main
    session bound to a task by the `agentos` skill). An unbound main session is
    NOT on the chain: every hook is a silent no-op for it.
  * where the task is — the task ledger under agent-os/state/tasks/, whose role
    field this same gate makes trustworthy (a seat may only append as itself).

Rules (deny = tell the caller the next legal step; reads are never denied;
terminal records are always writable; unknown → fail-open):
  create/send shangshu : 中书 only, send after menxia `comparison/pass` (or bypass)
  create/send executor : 尚书 only, send after its own `dispatch` record
  create/send menxia/yushi: 中书 only
  project writes   : executor (or any dispatched worker) after a dispatch;
                     御史 only under wiki/; 中书 only under a user bypass;
                     agent-os/state/ always
  ledger           : `create` by the relay (task id tNNNNNNNN-NNNN…, goal = the
                     user's verbatim words, no done_when) — that binds the session;
                     `append --role X` only when X is the caller; relay appends only
                     user_message (verbatim quote) / pause / resume / stop;
                     `--kind bypass` only with a verbatim quote from a real user
                     message of this session
  relay            : creates/talks to the `中书省｜<task-title>｜<task-id>` thread (Codex) or the
                     agentos-zhongshu agent (Claude) only, always carrying a real
                     user message verbatim; never writes; its Stop is never blocked
  Stop (中书)      : blocked once when no zhongshu record is newer than the latest
                     relay user_message of the task; delivery ends the task
  SubagentStop     : a seat may not end before its own record exists (once)
Same file in .claude/hooks and .codex/hooks; runtime differences are data.
"""
from __future__ import annotations

import json
import os
import re
import shlex
import sys
import time
from pathlib import Path

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import aos_common as aos  # noqa: E402

SEATS = {
    "agentos-relay": "relay",
    "agentos-zhongshu": "zhongshu",
    "agentos-menxia": "menxia",
    "agentos-shangshu": "shangshu",
    "agentos-executor": "executor",
    "agentos-yushi": "yushi",
}
SPAWN_TOOLS = {"Agent", "Task", "spawn_agent", "collab", "collaboration.spawn_agent",
               "collaborationspawn_agent"}
SEAT_TITLES = {"agentos-zhongshu": "中书省", "agentos-menxia": "门下省", "agentos-shangshu": "尚书省",
               "agentos-executor": "执行体", "agentos-yushi": "御史台"}
SHELL_TOOLS = {"Bash", "shell", "exec_command", "exec", "local_shell", "shell_command", "container.exec"}
WRITE_TOOLS = {"Edit", "Write", "MultiEdit", "NotebookEdit", "apply_patch", "write_file",
               "create_file", "edit_file", "str_replace_editor"}
LEDGER_RE = re.compile(r"aos_task_record\.py\b([^;&|\n]*)")
SKILL_RECEIPT_RE = re.compile(r"aos_skill_receipt\.py\b([^;&|\n]*)")
MUTATION = re.compile(
    r"(?:^|[\s;&|(\"'`:=])(?:"
    r"git\s+(?:init|add|commit|rm|mv|checkout|restore|reset|apply|merge|rebase|push)\b"
    r"|rm\s|mv\s|cp\s|mkdir\b|touch\b|chmod\b|chown\b|ln\s"
    r"|sed\s+-i|tee\s|truncate\b|npm\s+(?:install|i)\b|pip3?\s+install\b|apply_patch\b"
    r"|python3?\s+-\s*<<|python3?\s+-c\b|node\s+-e\b"
    r")"
)
REDIRECT = re.compile(r"(?<!\d)>{1,2}\s*(?!&|/dev/)\S")
STATE_PREFIX = "agent-os/state/"
RELAY_SEAT = "agentos-relay"
RELAY_TASK_RE = re.compile(r"^t\d{8}-\d{4}[a-z0-9-]*$")
TITLE_LIMIT = 32
RELAY_KINDS = {"user_message", "pause", "resume", "stop"}
TERMINAL_FAILURE_KINDS = {
    "zhongshu": "delivery",
    "shangshu": "integration",
    "executor": "execution_result",
}
EVIDENCE_KINDS = {
    "user_message", "independent_review", "comparison", "dispatch",
    "execution_result", "integration", "delivery", "bypass", "error_record",
    "error_learning",
}


# ---------------------------------------------------------------- identity --
def seat_of(data: dict, root: Path | None = None, runtime: str | None = None) -> str | None:
    """Caller identity. Claude seats: hook `agent_type`. Codex seat threads and the
    relay (either runtime): the session mapping written by this gate. Anything
    else — an unbound main session, a legacy `agentos-entry` main, a non-seat
    subagent — is None."""
    agent_type = str(data.get("agent_type") or "")
    if agent_type:
        seat = SEATS.get(agent_type)
        if seat or data.get("agent_id"):
            return seat
    if root is None or runtime is None:
        return None
    mapping = aos.chain_binding(root, runtime, data)
    if not mapping:
        return None
    seat_type = str(mapping.get("seat") or "")
    if seat_type == RELAY_SEAT:
        return "relay"
    if runtime == "codex" and seat_type in SEAT_TITLES:
        return SEATS[seat_type]
    return None


def is_unbound_main(data: dict, root: Path, runtime: str) -> bool:
    """A session that is neither a seat nor a bound relay: not on the chain."""
    return seat_of(data, root, runtime) is None and not data.get("agent_id")


def bind_relay(root: Path, runtime: str, session: str, task_id: str) -> None:
    path = sessions_dir(root) / f"{runtime}-{aos_safe(session)}.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps({"seat": RELAY_SEAT, "task_id": task_id, "bound": True,
                                "ts": time.time()}, ensure_ascii=False), encoding="utf-8")


def unbind_relay(root: Path, runtime: str, session: str) -> None:
    session_flag(root, runtime, session, "bound", False)


def unbind_relays_for_task(root: Path, runtime: str, task_id: str) -> None:
    """Unbind every relay carrying a delivered task, regardless of seat session."""
    for path in sessions_dir(root).glob(f"{runtime}-*.json"):
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
        except Exception:
            continue
        if (data.get("seat") == RELAY_SEAT and data.get("task_id") == task_id
                and data.get("bound") is not False):
            data["bound"] = False
            data["ts"] = time.time()
            path.write_text(json.dumps(data, ensure_ascii=False), encoding="utf-8")


def prompt_quotes_user(prompt: str, transcript_path: str | None) -> bool:
    """True when the prompt carries some real user message of this session verbatim
    (whitespace-insensitive). The relay is a pipe: it may add wrapping, never replace."""
    haystack = re.sub(r"\s+", "", prompt or "")
    for text in user_texts(transcript_path):
        needle = re.sub(r"\s+", "", text)
        if len(needle) >= 4 and needle in haystack:
            return True
    return False


# ------------------------------------------------------------------ ledger --
def sessions_dir(root: Path) -> Path:
    return root / "agent-os" / "state" / "sessions"


def bind_session(root: Path, runtime: str, session: str, task_id: str) -> None:
    path = sessions_dir(root) / f"{runtime}-{aos_safe(session)}.json"
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        data = {}
    data.update({"task_id": task_id, "ts": time.time()})
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False), encoding="utf-8")


def session_flag(root: Path, runtime: str, session: str, key: str, value=None):
    """Read (value is None) or set a small per-session flag beside the task binding."""
    path = sessions_dir(root) / f"{runtime}-{aos_safe(session)}.json"
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        data = {}
    if value is None:
        return data.get(key)
    data[key] = value
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False), encoding="utf-8")
    return value


def seats_path(root: Path) -> Path:
    return root / "agent-os" / "state" / "seats.json"


def seat_registry(root: Path) -> dict:
    try:
        value = json.loads(seats_path(root).read_text(encoding="utf-8"))
    except Exception:
        return {}
    return value if isinstance(value, dict) else {}


def write_seat_registry(root: Path, value: dict) -> None:
    path = seats_path(root)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def seat_from_title(title: str) -> tuple[str | None, str | None]:
    for seat_type, prefix in SEAT_TITLES.items():
        if title.startswith(prefix):
            remainder = title[len(prefix):].lstrip("｜|:：—- ").strip()
            task_id = remainder.rsplit("｜", 1)[-1].strip()
            return seat_type, task_id or None
    return None, None


def registered_seat(root: Path, thread_id: str) -> tuple[str | None, dict | None]:
    for seat_type, record in seat_registry(root).items():
        if isinstance(record, dict) and str(record.get("thread") or "") == thread_id:
            return seat_type, record
    return None, None


def response_thread_id(value) -> str | None:
    if isinstance(value, dict):
        for key in ("threadId", "thread_id"):
            if isinstance(value.get(key), str) and value[key]:
                return value[key]
        for nested in value.values():
            found = response_thread_id(nested)
            if found:
                return found
    elif isinstance(value, list):
        for nested in value:
            found = response_thread_id(nested)
            if found:
                return found
    elif isinstance(value, str):
        try:
            parsed = json.loads(value)
        except ValueError:
            match = re.search(r'["\']threadId["\']\s*:\s*["\']([^"\']+)', value)
            return match.group(1) if match else None
        return response_thread_id(parsed)
    return None


def record_seat_thread(root: Path, thread_id: str, seat_type: str,
                       task_id: str, title: str) -> None:
    registry = seat_registry(root)
    registry[seat_type] = {"task": task_id, "thread": thread_id, "title": title}
    write_seat_registry(root, registry)
    path = sessions_dir(root) / f"codex-{aos_safe(thread_id)}.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps({"seat": seat_type, "task_id": task_id},
                               ensure_ascii=False) + "\n", encoding="utf-8")


def current_task(root: Path, runtime: str, session: str) -> str | None:
    path = sessions_dir(root) / f"{runtime}-{aos_safe(session)}.json"
    try:
        return json.loads(path.read_text(encoding="utf-8")).get("task_id") or None
    except Exception:
        return None


def aos_safe(value: str) -> str:
    return re.sub(r"[^A-Za-z0-9._-]", "_", value or "anonymous")[:160]


def ledger_events(root: Path, task_id: str) -> list[dict]:
    path = root / "agent-os" / "state" / "tasks" / f"{aos_safe(task_id)}.jsonl"
    events: list[dict] = []
    try:
        for raw in path.read_text(encoding="utf-8", errors="replace").splitlines():
            try:
                line = json.loads(raw)
            except ValueError:
                continue
            if isinstance(line, dict) and line.get("kind") != "header":
                events.append(line)
    except OSError:
        pass
    return events


def task_header(root: Path, task_id: str | None) -> dict:
    path = root / "agent-os" / "state" / "tasks" / f"{aos_safe(task_id or '')}.jsonl"
    try:
        for raw in path.read_text(encoding="utf-8", errors="replace").splitlines():
            parsed = json.loads(raw)
            if isinstance(parsed, dict) and parsed.get("kind") == "header":
                return parsed
    except (OSError, ValueError):
        pass
    return {}


def display_task_label(goal: str) -> str:
    text = re.sub(r"^\s*(?:[$/]agentos)\b\s*", "", goal or "", flags=re.I)
    text = re.sub(r"\s+", " ", text).strip()
    for prefix in ("麻烦帮我", "请帮我", "麻烦", "帮我", "请"):
        if text.startswith(prefix):
            text = text[len(prefix):].lstrip(" ，,:：")
            break
    text = re.split(r"[\n。；;！？!?]", text, maxsplit=1)[0]
    text = text.replace("｜", "-").strip(" ，,:：.-") or "未命名任务"
    return text if len(text) <= TITLE_LIMIT else text[: TITLE_LIMIT - 1].rstrip() + "…"


def task_label(root: Path, task_id: str | None) -> str:
    header = task_header(root, task_id)
    return str(header.get("title") or display_task_label(str(header.get("goal") or "")))


def seat_thread_title(root: Path, seat_type: str, task_id: str | None) -> str:
    return f"{SEAT_TITLES[seat_type]}｜{task_label(root, task_id)}｜{task_id or 'no-task'}"


def task_forbids_project_writes(root: Path, task_id: str | None,
                                events: list[dict] | None = None) -> bool:
    """Whether the approved task boundary forbids teardown memory writes."""
    events = events if events is not None else ledger_events(root, task_id or "")
    header = task_header(root, task_id)
    goal = str(header.get("goal") or "")
    contracts = [str(e.get("text") or "") for e in events
                 if e.get("role") == "zhongshu" and e.get("kind") == "contract"]
    contract = contracts[-1] if contracts else ""
    explicit_goal_markers = (
        "不要修改项目文件", "不得修改项目文件", "不修改项目文件",
        "do not modify project files", "no project writes",
    )
    if any(marker in goal.lower() for marker in explicit_goal_markers):
        return True
    return bool(re.search(r"权限边界.{0,24}(?:只读|read[- ]only)", contract, re.I | re.S))


def phase(events: list[dict]) -> dict:
    def has(role: str, kind: str, status: str | None = None) -> bool:
        return any(e.get("role") == role and e.get("kind") == kind
                   and (status is None or e.get("status") == status) for e in events)
    return {
        "menxia_pass": has("menxia", "comparison", "pass"),
        "dispatched": has("shangshu", "dispatch"),
        "executed": has("executor", "execution_result"),
        "integrated": has("shangshu", "integration"),
        "bypass": has("menxia", "bypass"),
        "delivered": has("zhongshu", "delivery"),
        "skill_roles": {e.get("role") for e in events
                         if e.get("kind") == "skill_load" and e.get("status") == "ok"},
        "terminal_failure": any(e.get("kind") in ("execution_result", "delivery", "integration")
                                and e.get("status") in ("failed", "blocked") for e in events),
        "seat_records": {e.get("role") for e in events},
    }


def required_skills(root: Path, role: str) -> list[str]:
    path = root / "agent-os" / "skills" / "seat-skills.json"
    try:
        value = json.loads(path.read_text(encoding="utf-8")).get(role)
    except Exception:
        return []
    return [str(item) for item in value] if isinstance(value, list) else []


def expected_skill_evidence(root: Path, role: str, runtime: str) -> str | None:
    import hashlib
    parts: list[str] = []
    skill_root = ".agents" if runtime == "codex" else ".claude"
    for name in required_skills(root, role):
        path = root / skill_root / "skills" / name / "SKILL.md"
        try:
            digest = hashlib.sha256(path.read_bytes()).hexdigest()
        except OSError:
            return None
        parts.append(f"{name}:{digest}")
    return f"{runtime}|" + ";".join(parts) if parts else None


def valid_skill_receipt(root: Path, task_id: str | None, role: str | None, runtime: str) -> bool:
    if not task_id or not role:
        return False
    expected = expected_skill_evidence(root, role, runtime)
    if not expected:
        return False
    return any(e.get("role") == role and e.get("kind") == "skill_load"
               and e.get("status") == "ok" and e.get("evidence") == expected
               for e in ledger_events(root, task_id))


def active_dispatched_task(root: Path) -> str | None:
    tasks = root / "agent-os" / "state" / "tasks"
    for path in sorted(tasks.glob("*.jsonl"), reverse=True) if tasks.is_dir() else ():
        state = phase(ledger_events(root, path.stem))
        if state["dispatched"] and not state["integrated"]:
            return path.stem
    return None


# ---------------------------------------------------------------- transcript --
def user_texts(transcript_path: str | None) -> list[str]:
    """Every string a real user typed in this session, from the runtime transcript.
    Claude: {"type":"user","message":{"role":"user","content":str|[{"type":"text"}]}};
    Codex rollout: payload.role == "user" with content[].text / input_text.
    tool_result blocks are never user text."""
    texts: list[str] = []
    if not transcript_path or not os.path.isfile(transcript_path):
        return texts
    try:
        with open(transcript_path, "r", encoding="utf-8", errors="ignore") as fh:
            for raw in fh:
                try:
                    event = json.loads(raw)
                except ValueError:
                    continue
                _collect_user(event, texts)
    except OSError:
        return texts
    return texts


def _collect_user(node, texts: list[str]) -> None:
    if isinstance(node, dict):
        if node.get("role") == "user":
            content = node.get("content")
            if isinstance(content, str):
                texts.append(content)
            elif isinstance(content, list):
                for block in content:
                    if isinstance(block, dict) and block.get("type") in ("text", "input_text"):
                        value = block.get("text")
                        if isinstance(value, str):
                            texts.append(value)
            return
        for value in node.values():
            _collect_user(value, texts)
    elif isinstance(node, list):
        for value in node:
            _collect_user(value, texts)


def quoted_by_user(quote: str, transcript_path: str | None) -> bool:
    needle = re.sub(r"\s+", "", quote or "")
    if len(needle) < 2:
        return False
    return any(needle in re.sub(r"\s+", "", text) for text in user_texts(transcript_path))


# ------------------------------------------------------------------ helpers --
def deny(reason: str) -> dict:
    return {"hookSpecificOutput": {"hookEventName": "PreToolUse",
                                   "permissionDecision": "deny",
                                   "permissionDecisionReason": "[AgentOS chain] " + reason}}


def retitle(tool: str, tool_input: dict, target: str, root: Path, task_id: str | None) -> dict | None:
    """Every visible seat says role, readable task label, and stable task id."""
    seat_title = SEAT_TITLES.get(target)
    if not seat_title:
        return None
    if tool in ("Agent", "Task"):
        key, title = "description", seat_thread_title(root, target, task_id)
    else:
        # Codex derives the child's agent_name from task_name and accepts only
        # lowercase letters, digits and underscores (verified 2026-08-16).
        key = "task_name"
        task_ascii = re.sub(r"[^a-z0-9]+", "_", (task_id or "no_task").lower()).strip("_") or "no_task"
        title = f"{SEATS[target]}_{task_ascii}"[:64]
    if str(tool_input.get(key) or "").strip() == title:
        return None
    updated = dict(tool_input)
    updated[key] = title
    return {"hookSpecificOutput": {"hookEventName": "PreToolUse",
                                   "permissionDecision": "allow",
                                   "updatedInput": updated}}


def block(reason: str) -> dict:
    return {"decision": "block", "reason": "[AgentOS chain] " + reason}


def command_text(tool_input: dict) -> str:
    value = tool_input.get("command")
    if isinstance(value, list):
        return " ".join(str(part) for part in value)
    if isinstance(value, str):
        return value
    for key in ("cmd", "script", "commandLine"):
        if isinstance(tool_input.get(key), str):
            return tool_input[key]
    return ""


def relative_path(root: Path, value: str) -> str | None:
    try:
        path = Path(value).expanduser()
        if not path.is_absolute():
            path = root / path
        return path.resolve().relative_to(root.resolve()).as_posix()
    except Exception:
        return None


def write_targets(root: Path, tool_input: dict) -> list[str]:
    values: list[str] = []
    for key in ("file_path", "path", "target_file", "file", "notebook_path"):
        value = tool_input.get(key)
        if isinstance(value, str) and value:
            values.append(value)
    patch = tool_input.get("patch") or tool_input.get("input") or tool_input.get("command")
    if isinstance(patch, str) and "*** " in patch:
        values.extend(re.findall(r"^\*\*\* (?:Add|Update|Delete) File: (.+)$", patch, re.MULTILINE))
    return [p for p in (relative_path(root, v) for v in values) if p is not None]


def ledger_calls(command: str) -> list[dict]:
    calls: list[dict] = []
    for match in LEDGER_RE.finditer(command):
        try:
            argv = shlex.split(match.group(1))
        except ValueError:
            argv = match.group(1).split()
        call: dict = {"sub": argv[0] if argv else ""}
        for index, token in enumerate(argv):
            if token.startswith("--") and index + 1 < len(argv):
                call[token[2:]] = argv[index + 1]
        calls.append(call)
    return calls


def skill_receipt_calls(command: str) -> list[dict]:
    calls: list[dict] = []
    for match in SKILL_RECEIPT_RE.finditer(command):
        try:
            argv = shlex.split(match.group(1))
        except ValueError:
            argv = match.group(1).split()
        call: dict = {}
        for index, token in enumerate(argv):
            if token.startswith("--") and index + 1 < len(argv):
                call[token[2:]] = argv[index + 1]
        calls.append(call)
    return calls


# ------------------------------------------------------------------- gates --
def relay_ledger_gate(call: dict, seat: str | None, data: dict, root: Path,
                      runtime: str, session: str) -> dict | None:
    """Ledger commands a main session may run as the relay. `create` and `resume`
    are the chain's start/restart: they bind an unbound session; pause/stop unbind."""
    sub = call.get("sub")
    if seat is None and data.get("agent_id") and (sub == "create" or call.get("role") == "relay"):
        return deny("子代理不能启动或续接链：任务由用户会话（传旨）创建和恢复。")
    if sub == "create":
        if seat not in (None, "relay"):
            return deny("任务记录由传旨会话（relay）创建；席位线程不建任务。")
        task = str(call.get("task") or "")
        if not RELAY_TASK_RE.match(task):
            return deny("任务号格式：t + 8 位日期 + '-' + 4 位时间（如 t20260817-0930，可带 -后缀，"
                        "只用小写字母数字连字符）；传旨会话机械起号，不带框架。")
        if "done-when" in call:
            return deny("create 不写 --done-when：目标与完成条件在门下 pass 之后由中书契约固定，传旨会话不预设。")
        if not quoted_by_user(str(call.get("goal") or ""), data.get("transcript_path")):
            return deny("create 的 --goal 必须是用户在本会话说过的原话（一字不差），传旨会话不改写用户的话。")
        bind_relay(root, runtime, session, task)
        return None
    if sub != "append" or call.get("role") != "relay":
        return None
    if seat not in (None, "relay"):
        return deny(f"你是 {seat}，账本只接受 --role {seat}；角色由 hook 认定，不由自报。")
    kind = str(call.get("kind") or "")
    task = str(call.get("task") or current_task(root, runtime, session) or "")
    if kind not in RELAY_KINDS:
        return deny("传旨会话只记录 user_message / pause / resume / stop 四种事件。")
    if kind == "resume":
        if not task or not (root / "agent-os" / "state" / "tasks" / f"{aos_safe(task)}.jsonl").is_file():
            return deny("resume 需要 --task <已存在的任务号>；先用 aos_task_record.py board 查看未完成任务。")
        bind_relay(root, runtime, session, task)
        return None
    if seat is None:
        return deny("会话未绑定任务：先 create 新任务，或 append --role relay --kind resume --task <任务号>。")
    if kind == "user_message" and not quoted_by_user(str(call.get("text") or ""), data.get("transcript_path")):
        return deny("user_message 的 --text 必须是用户在本会话说过的原话（一字不差）。")
    if kind in ("pause", "stop"):
        unbind_relay(root, runtime, session)
    return None


def gate_pretool(data: dict, root: Path, runtime: str) -> dict | None:
    seat = seat_of(data, root, runtime)
    tool = str(data.get("tool_name") or "")
    tool_input = data.get("tool_input") or {}
    session = aos.runtime_session(data)
    unbound_main = seat is None and not data.get("agent_id")
    if unbound_main:
        # Not on the chain: the only thing examined is a chain start/restart.
        if tool in SHELL_TOOLS:
            for call in ledger_calls(command_text(tool_input)):
                decision = relay_ledger_gate(call, None, data, root, runtime, session)
                if decision:
                    return decision
        return None
    task_id = current_task(root, runtime, session)
    state = phase(ledger_events(root, task_id)) if task_id else phase([])

    if runtime == "codex" and tool.endswith("set_thread_title"):
        title = str(tool_input.get("title") or "")
        target, title_task = seat_from_title(title)
        if target != "agentos-zhongshu":
            return None
        if seat not in ("relay", "zhongshu"):
            return deny("只有传旨会话或中书能命名中书省线程。")
        expected = seat_thread_title(root, "agentos-zhongshu", task_id)
        if not task_id or title_task != task_id or title != expected:
            return deny(f"中书省线程标题必须是 {expected}。")
        return None

    if runtime == "codex" and tool.endswith("create_thread"):
        title = str(tool_input.get("title") or "")
        target, title_task = seat_from_title(title)
        if target is None:
            return None
        environment = (((tool_input.get("target") or {}).get("environment") or {}).get("type"))
        prompt = str(tool_input.get("prompt") or "")
        existing = seat_registry(root).get(target)
        call_task = title_task or task_id
        if target == "agentos-zhongshu":
            if seat != "relay":
                return deny("中书省线程由传旨会话创建：先 aos_task_record.py create 建任务并读取 title，"
                            "再 create_thread 中书省｜<任务简称>｜<任务号>。")
            expected = seat_thread_title(root, target, task_id)
            if not task_id or title_task != task_id or title != expected:
                return deny(f"标题必须是 {expected}（角色｜任务简称｜任务号）。")
            if environment != "local":
                return deny("AgentOS 可视席位必须在当前项目使用 environment.type=local；禁止 worktree 排队路径。")
            if not prompt_quotes_user(prompt, data.get("transcript_path")):
                return deny("发给中书的首条消息必须原样包含用户说过的话（一字不差）；传旨会话不转述。")
            if (isinstance(existing, dict) and existing.get("task") == call_task and existing.get("thread")):
                return deny(f"任务 {call_task} 已有中书省线程 {existing['thread']}：用 send_message_to_thread 继续。")
            return None
        required = "shangshu" if target == "agentos-executor" else "zhongshu"
        if seat != required:
            return deny(f"只有{SEATS[required]}能创建 {SEATS[target]} 席位线程。")
        expected = seat_thread_title(root, target, call_task)
        if title != expected:
            return deny(f"标题必须是 {expected}（所有席位共用同一任务简称和任务号）。")
        if environment != "local":
            return deny("AgentOS 可视席位必须在当前项目使用 environment.type=local；禁止 worktree 排队路径。")
        if not valid_skill_receipt(root, call_task, seat, runtime):
            return deny(f"{seat} 先完整读取 agent-os/skills/seat-skills.json 为本席位列出的 SKILL.md，"
                        f"再运行 aos_skill_receipt.py --task {call_task} --role {seat} --runtime {runtime}。")
        if seat == "zhongshu":
            main = seat_registry(root).get("agentos-zhongshu")
            if not (isinstance(main, dict) and main.get("task") == call_task and main.get("thread")):
                return deny(f"{seat_thread_title(root, 'agentos-zhongshu', call_task)} 线程尚未登记；"
                            "只有传旨会话创建的中书省线程能开其他席位。")
        prefix = SEAT_TITLES[target].removesuffix("省") if target != "agentos-yushi" else "御史"
        required_prompt_parts = (
            f"你是{prefix}，任务 {call_task}",
            f".codex/agents/{target}.toml",
            "agent-os/skills/seat-skills.json",
            "aos_skill_receipt.py",
        )
        if any(part not in prompt for part in required_prompt_parts):
            return deny("席位首条消息必须包含身份+任务、对应 .codex/agents TOML、"
                        "seat-skills.json 和 aos_skill_receipt.py 技能回执指令。")
        if (call_task and isinstance(existing, dict)
                and existing.get("task") == call_task and existing.get("thread")):
            return deny(f"任务 {call_task} 已有 {SEATS[target]} 线程 {existing['thread']}："
                        "用 codex_app send_message_to_thread 继续该线程。")
        return None

    if runtime == "codex" and tool.endswith("send_message_to_thread"):
        thread_id = str(tool_input.get("threadId") or tool_input.get("thread_id") or "")
        target, record = registered_seat(root, thread_id)
        if target is None or record is None:
            return None
        call_task = str(record.get("task") or task_id or "")
        call_state = phase(ledger_events(root, call_task)) if call_task else phase([])
        if target == "agentos-zhongshu":
            if seat != "relay":
                return deny("只有传旨会话能给中书省线程发消息。")
            if call_task != task_id:
                return deny(f"这条中书省线程属于任务 {call_task}；先 append --role relay --kind resume --task {call_task}。")
            if not prompt_quotes_user(str(tool_input.get("prompt") or ""), data.get("transcript_path")):
                return deny("发给中书的消息必须原样包含用户说过的话（一字不差）；传旨会话不转述。")
            return None
        if seat == "relay":
            return deny("传旨会话只和中书省线程说话；门下、尚书、执行体由链上席位驱动。")
        if not valid_skill_receipt(root, call_task, seat, runtime):
            return deny(f"{seat} 尚无有效技能加载回执；先读取本席位 SKILL.md 并运行 aos_skill_receipt.py。")
        if target in ("agentos-menxia", "agentos-yushi"):
            if seat != "zhongshu":
                return deny(f"只有中书能给 {SEATS[target]} 发消息。")
        elif target == "agentos-shangshu":
            if seat != "zhongshu":
                return deny("只有中书能给尚书发消息。")
            if not (call_state["menxia_pass"] or call_state["bypass"]):
                return deny("门下还没有 comparison/pass 记录：先完成门下审议再给尚书发任务。")
        elif target == "agentos-executor":
            if seat != "shangshu":
                return deny("只有尚书能给执行体发消息。")
            if not call_state["dispatched"]:
                return deny("尚书先记录 dispatch 再给执行体发任务。")
        return None

    if runtime == "codex" and tool.endswith("set_thread_archived"):
        thread_id = str(tool_input.get("threadId") or tool_input.get("thread_id") or "")
        target, record = registered_seat(root, thread_id)
        if target is None or record is None:
            return None
        old_task = str(record.get("task") or "")
        old_state = phase(ledger_events(root, old_task))
        if seat not in ("relay", "zhongshu"):
            return deny("席位归档由传旨会话或中书管理；尚书不得提前隐藏执行体。")
        if not old_state["delivered"]:
            return deny("任务尚未记录 delivery，不能归档可视席位。")
        if seat == "zhongshu" and task_id == old_task:
            return deny("用户尚未看到本轮最终交付；席位保持可见，到下一任务开始时再归档。")
        return None

    if tool in SHELL_TOOLS:
        command = command_text(tool_input)
        receipts = skill_receipt_calls(command)
        if receipts:
            for call in receipts:
                call_task = call.get("task")
                call_role = call.get("role")
                call_runtime = call.get("runtime")
                if not call_task or not call_role or not call_runtime:
                    return deny("aos_skill_receipt.py 必须提供 --task、--role 和 --runtime。")
                if call_role != seat:
                    return deny(f"你是 {seat}，技能回执只接受 --role {seat}。")
                if call_runtime != runtime:
                    return deny(f"当前运行时是 {runtime}，技能回执必须使用 --runtime {runtime}。")
                if not required_skills(root, call_role):
                    return deny(f"seat-skills.json 没有 {call_role} 的技能清单。")
                bind_session(root, runtime, session, call_task)
            return None
        calls = ledger_calls(command)
        if calls:
            for call in calls:
                if call["sub"] == "create" or call.get("role") == "relay":
                    decision = relay_ledger_gate(call, seat, data, root, runtime, session)
                    if decision:
                        return decision
                    continue
                if call["sub"] == "append":
                    if seat is None:
                        return deny("你不是链上的席位，不能写任务账本。")
                    if seat == "relay":
                        return deny("传旨会话只以 --role relay 记录 user_message / pause / resume / stop。")
                    if call.get("role") != seat:
                        return deny(f"你是 {seat}，账本只接受 --role {seat}；角色由 hook 认定，不由自报。")
                    if call.get("kind") == "skill_load":
                        return deny("skill_load 不能自报；完整读取本席位 SKILL.md 后运行 aos_skill_receipt.py 生成哈希回执。")
                    call_task = call.get("task") or task_id
                    terminal_failure = (
                        call.get("kind") == TERMINAL_FAILURE_KINDS.get(seat)
                        and call.get("status") in ("failed", "blocked")
                    )
                    if (call.get("kind") in EVIDENCE_KINDS and not terminal_failure
                            and not str(call.get("text") or "").strip()):
                        return deny(f"{call.get('kind')} 必须包含非空 --text；空事件不能充当阶段证据。")
                    if not terminal_failure and not valid_skill_receipt(root, call_task, seat, runtime):
                        return deny(f"{seat} 先读取本席位 SKILL.md，并运行 aos_skill_receipt.py 生成技能加载回执。")
                    if call.get("kind") == "integration" and seat == "shangshu" and not terminal_failure:
                        call_state = phase(ledger_events(root, call_task))
                        if not call_state["executed"]:
                            return deny("执行体尚未用 --role executor 写 execution_result；尚书不能提前写 integration。")
                    if call.get("kind") == "bypass":
                        if seat != "menxia":
                            return deny("放行（bypass）只能由门下在读过用户原话后记录；中书不能给自己放行。")
                        if not quoted_by_user(call.get("text", ""), data.get("transcript_path")):
                            return deny("bypass 的 --text 必须是用户在本会话说过的原话（一字不差），"
                                        "hook 在用户消息里没有找到这句话。")
                for call_task in (call.get("task"),):
                    if call_task and seat != "relay":
                        bind_session(root, runtime, session, call_task)
            return None
        if seat == "yushi" and task_forbids_project_writes(root, task_id):
            return deny("本任务权限边界是只读：御史只能读证据并写 agent-os/state/ 账本，"
                        "不得运行其他 shell、写 wiki 或刷新 memory views；记录 error_record/deferred 后结束。")
        if seat in ("relay", "zhongshu", "menxia", "shangshu") and (MUTATION.search(command) or REDIRECT.search(command)):
            if seat == "zhongshu" and state["bypass"]:
                return None
            if seat == "relay":
                return deny("传旨会话不做任何工作：只把用户原话交给中书省线程，再把结果带回。")
            if seat == "zhongshu":
                return deny("中书不亲自改动工作区：写形状的命令交给尚书派出的执行体；"
                            "用户明确让你直接做时，把原话发给门下，由门下记录 bypass（引用用户原话）。")
            return deny(f"{seat} 不改动工作区（只读、记账本）。")
        return None

    if tool in SPAWN_TOOLS:
        target = str(tool_input.get("subagent_type") or tool_input.get("agent_type")
                     or tool_input.get("role") or tool_input.get("agent") or "")
        if target not in SEATS:
            return None
        if runtime == "codex":
            return deny("席位用 codex_app create_thread / send_message_to_thread")
        if target == "agentos-zhongshu":
            if seat != "relay":
                return deny("中书由传旨会话派出：先 aos_task_record.py create 建任务（绑定会话）。")
            if not task_id:
                return deny("先用 aos_task_record.py create 建任务记录，再派中书。")
            if not prompt_quotes_user(str(tool_input.get("prompt") or ""), data.get("transcript_path")):
                return deny("发给中书的提示必须原样包含用户说过的话（一字不差）；传旨会话不转述。")
            return retitle(tool, tool_input, target, root, task_id)
        if seat == "relay":
            return deny("传旨会话只派中书；门下、尚书、执行体、御史由链上席位派出。")
        if target in ("agentos-menxia", "agentos-yushi"):
            if seat != "zhongshu":
                return deny(f"只有中书能派 {SEATS[target]}。")
            return retitle(tool, tool_input, target, root, task_id)
        if target == "agentos-shangshu":
            if seat != "zhongshu":
                return deny("只有中书能派尚书。")
            if not task_id:
                return deny("任务尚未绑定：等传旨会话 create 后再走门下审议。")
            if not (state["menxia_pass"] or state["bypass"]):
                return deny("门下还没有 comparison/pass 记录：先把用户原始增量发给门下，等它记录 pass 再派尚书。")
            return retitle(tool, tool_input, target, root, task_id)
        if target == "agentos-executor":
            if seat != "shangshu":
                return deny("执行体只能由尚书派出。")
            if not state["dispatched"]:
                return deny("尚书先记录 dispatch（append --role shangshu --kind dispatch）再派执行体。")
            return retitle(tool, tool_input, target, root, task_id)
        return None

    if tool in WRITE_TOOLS:
        targets = write_targets(root, tool_input)
        if targets and all(t.startswith(STATE_PREFIX) for t in targets):
            return None
        if seat == "relay":
            return deny("传旨会话不改文件：只把用户原话交给中书省线程，再把结果带回。")
        if seat == "yushi":
            if task_forbids_project_writes(root, task_id):
                return deny("本任务权限边界是只读：御史不得写 wiki；只记 error_record/deferred 到任务账本。")
            if targets and all(t.startswith("wiki/") for t in targets):
                return None
            return deny("御史只写 wiki/ 下的错误记忆。")
        if seat == "zhongshu":
            return None if state["bypass"] else deny(
                "中书不亲自改文件：交给尚书派出的执行体；用户明确让你直接做时，把原话发给门下，由门下记录 bypass（引用用户原话）。")
        if seat in ("menxia", "shangshu"):
            return deny(f"{seat} 不改文件。")
        if seat == "executor" and not task_id and active_dispatched_task(root):
            return None
        if seat == "executor" and not valid_skill_receipt(root, task_id, seat, runtime):
            return deny("执行体尚无有效技能加载回执；先读取本席位 SKILL.md 并运行 aos_skill_receipt.py。")
        if state["dispatched"] or state["bypass"]:
            return None
        return deny("还没有尚书的 dispatch 记录：执行发生在尚书派工之后。")

    return None


def gate_posttool(data: dict, root: Path, runtime: str) -> None:
    tool = str(data.get("tool_name") or "")
    seat = seat_of(data, root, runtime)
    if tool in SHELL_TOOLS and seat == "zhongshu":
        for call in ledger_calls(command_text(data.get("tool_input") or {})):
            if (call.get("role") == "zhongshu" and call.get("kind") == "delivery"
                    and call.get("status") == "completed"):
                task_id = str(call.get("task") or current_task(
                    root, runtime, aos.runtime_session(data)) or "")
                if task_id:
                    unbind_relays_for_task(root, runtime, task_id)
    if runtime != "codex":
        return None
    if seat is None:
        return None
    if tool.endswith("set_thread_title"):
        title = str((data.get("tool_input") or {}).get("title") or "")
        target, task_id = seat_from_title(title)
        if target == "agentos-zhongshu" and task_id and seat in ("relay", "zhongshu"):
            thread_id = str((data.get("tool_input") or {}).get("threadId")
                            or aos.runtime_session(data))
            if thread_id:
                record_seat_thread(root, thread_id, target, task_id, title)
        return None
    if not tool.endswith("create_thread"):
        return None
    title = str((data.get("tool_input") or {}).get("title") or "")
    target, task_id = seat_from_title(title)
    if target is None or not task_id:
        return None
    required = {"agentos-zhongshu": "relay", "agentos-executor": "shangshu"}.get(target, "zhongshu")
    if seat != required:
        return None
    thread_id = response_thread_id(data.get("tool_response"))
    if not thread_id:
        return None
    record_seat_thread(root, thread_id, target, task_id, title)
    return None


def zhongshu_stop(root: Path, runtime: str, task_id: str | None) -> dict | None:
    """中书 may end a turn only after leaving a record for the latest user increment
    the relay brought; delivery or a terminal failure ends the task."""
    if not task_id:
        return None
    events = ledger_events(root, task_id)
    state = phase(events)
    if state["delivered"] or state["terminal_failure"]:
        return None
    if not valid_skill_receipt(root, task_id, "zhongshu", runtime):
        return block("中书尚无有效技能加载回执：完整读取 seat-skills.json 列出的 SKILL.md，"
                     "再运行 aos_skill_receipt.py。")
    latest_relay = max((str(e.get("ts") or "") for e in events
                        if e.get("role") == "relay" and e.get("kind") == "user_message"), default="")
    if any(e.get("role") == "zhongshu" and e.get("kind") != "skill_load"
           and str(e.get("ts") or "") > latest_relay for e in events):
        return None
    return block(f"任务 {task_id} 这一轮用户增量还没有中书记录：先把本轮结论或阶段写进账本"
                 "（append --role zhongshu …），交付时记 delivery，再结束。")


def gate_stop(data: dict, root: Path, runtime: str) -> dict | None:
    if aos_truthy(data.get("stop_hook_active")):
        return None
    seat = seat_of(data, root, runtime)
    if seat is None or seat == "relay":
        return None
    if runtime == "codex" and seat in ("menxia", "shangshu", "executor", "yushi"):
        return gate_subagent_stop(data, root, runtime)
    if seat != "zhongshu":
        return None
    session = aos.runtime_session(data)
    return zhongshu_stop(root, runtime, current_task(root, runtime, session))


def gate_subagent_stop(data: dict, root: Path, runtime: str) -> dict | None:
    if aos_truthy(data.get("stop_hook_active")):
        return None
    seat = seat_of(data, root, runtime)
    session = aos.runtime_session(data)
    if seat == "zhongshu":
        return zhongshu_stop(root, runtime, current_task(root, runtime, session))
    if seat not in ("menxia", "shangshu", "executor", "yushi"):
        return None
    task_id = current_task(root, runtime, session)
    if not task_id:
        return None
    events = ledger_events(root, task_id)
    terminal_kind = TERMINAL_FAILURE_KINDS.get(seat)
    if terminal_kind and any(
        e.get("role") == seat and e.get("kind") == terminal_kind
        and e.get("status") in ("failed", "blocked") for e in events
    ):
        return None
    if not valid_skill_receipt(root, task_id, seat, runtime):
        return block(f"{seat} 结束前必须完整读取本席位 SKILL.md，并运行 aos_skill_receipt.py 生成有效回执。")
    if seat == "executor":
        if any(e.get("role") == "executor" and e.get("kind") == "execution_result" for e in events):
            return None
        return block("执行体结束前必须写终态记录：append --role executor --kind execution_result "
                     "--status completed|failed|blocked。")
    required_kind = {"menxia": "independent_review", "yushi": "error_record"}.get(seat)
    if seat == "shangshu":
        state = phase(events)
        if not state["menxia_pass"]:
            return None
        if not state["dispatched"]:
            return block("尚书结束前必须写 dispatch 并派出执行体。")
        if not state["executed"]:
            return block("尚书已 dispatch，但执行体还没有自己的 execution_result；等待执行体完成。")
        if not state["integrated"]:
            return block("执行体已有 execution_result；尚书结束前必须核对 done_when 并写 integration。")
        return None
    if required_kind and any(e.get("role") == seat and e.get("kind") == required_kind for e in events):
        return None
    return block(f"{seat} 结束前必须把本阶段的 {required_kind or 'record'} 写进任务账本。")


def aos_truthy(value) -> bool:
    return value is True or str(value).lower() in {"1", "true", "yes"}


def decide(data: dict, root: Path, runtime: str) -> dict | None:
    event = str(data.get("hook_event_name") or "")
    if event == "PreToolUse":
        return gate_pretool(data, root, runtime)
    if event == "PostToolUse":
        return gate_posttool(data, root, runtime)
    if event == "Stop":
        return gate_stop(data, root, runtime)
    if event == "SubagentStop":
        return gate_subagent_stop(data, root, runtime)
    return None


def main() -> int:
    data = aos.hook_input()
    if aos.disabled():
        return 0
    root = aos.project_root(data)
    if not (root / "agent-os").is_dir():
        return 0
    runtime = "codex" if Path(__file__).resolve().parent.parent.name == ".codex" else "claude"
    result = decide(data, root, runtime)
    if result:
        print(json.dumps(result, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    aos.run_guarded(main)
