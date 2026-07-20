#!/usr/bin/env python3
"""PreToolUse hook: mechanical trigger for the Prompt Craft Gate (Codex port).

Why this exists: the gate (agent-os/review/prompt-craft-gate.md) has been law
since 2026-07-06, yet a bare one-line prompt still went out to an external
Codex CLI probe on 2026-07-10 (wiki/errors). Prompt-layer rules do not fire by
themselves; the trigger point moves into the tool boundary (ZX 2026-07-11).
Structure is the only thing checked — XML-sectioned shape, never prose quality.

Scope (deny = rewrite the dispatch; fail-open on error):
- Agent/Task-style spawn tools: `prompt` must carry >= MIN_TAGS distinct tags.
- Workflow scripts: bare short string-literal agent() prompts are flagged.
- shell/Bash: external model dispatches (codex exec / claude -p / gemini -p)
  need tags inline or a prompt file/heredoc. Probes are NOT exempt
  (error rule 2026-07-10: 简单机械探针也不豁免).
"""
from __future__ import annotations

import json
import re

import aos_common as aos

MIN_TAGS = 3
TAG_RE = re.compile(r"<([A-Za-z_][\w-]{1,30})>")
_CMD = r"(?:^|[;&|(]\s*|\$\(\s*)(?:\S*/)?"
BASH_DISPATCH_RES = (
    re.compile(_CMD + r"codex\s+exec\b", re.MULTILINE),
    re.compile(_CMD + r"claude\s[^\n;|&]*(?:-p|--print)\b", re.MULTILINE),
    re.compile(_CMD + r"gemini\s[^\n;|&]*-p\b", re.MULTILINE),
)
FILE_PROMPT_HINTS = re.compile(r"<<|\$\(\s*cat\b|--?(?:input|prompt-file|file)\b|\.(?:md|txt|xml)\b")
WORKFLOW_BARE_AGENT = re.compile(r"""agent\(\s*(['"`])((?:(?!\1).){1,200}?)\1""", re.DOTALL)

GATE_HINT = (
    " Assemble XML sections (role / context / instructions / output_format / question,"
    " materials top, question last) before dispatch — a bare one-liner is a violation"
    " even for probes. Rule: agent-os/review/prompt-craft-gate.md (structure check only;"
    " quality is still on you)."
)


def decide(decision: str, reason: str) -> None:
    print(json.dumps({
        "hookSpecificOutput": {
            "hookEventName": "PreToolUse",
            "permissionDecision": decision,
            "permissionDecisionReason": reason,
        }
    }, ensure_ascii=False))


def _tool_input(data: dict) -> dict:
    value = data.get("tool_input") or data.get("input") or data.get("arguments") or {}
    return value if isinstance(value, dict) else {}


def distinct_tags(text: str) -> set[str]:
    return set(TAG_RE.findall(text or ""))


def main() -> int:
    data = aos.hook_input()
    if aos.disabled():
        return 0
    tool = str(data.get("tool_name") or data.get("tool") or data.get("name") or "")
    tool_input = _tool_input(data)

    if tool in ("Agent", "Task", "spawn_agent", "collab"):
        prompt = str(tool_input.get("prompt") or tool_input.get("message") or "")
        if prompt:
            tags = distinct_tags(prompt)
            if len(tags) < MIN_TAGS:
                decide("deny",
                       f"Prompt Craft Gate: subagent prompt has {len(tags)} XML section tag(s)"
                       f" (need >= {MIN_TAGS} distinct)." + GATE_HINT)
        return 0

    if tool == "Workflow":
        script = str(tool_input.get("script") or "")
        for m in WORKFLOW_BARE_AGENT.finditer(script):
            literal = m.group(2)
            if len(distinct_tags(literal)) < MIN_TAGS:
                decide("deny",
                       "Prompt Craft Gate: workflow script contains a bare string-literal agent()"
                       f" prompt (starts 「{literal[:60]}…」) without XML sections." + GATE_HINT)
                return 0
        return 0

    if tool in ("Bash", "shell", "exec_command"):
        cmd = str(tool_input.get("command") or tool_input.get("cmd") or "")
        if cmd.strip() in {"codex exec --help", "codex exec -h"}:
            return 0
        if any(p.search(cmd) for p in BASH_DISPATCH_RES):
            if len(distinct_tags(cmd)) < MIN_TAGS and not FILE_PROMPT_HINTS.search(cmd):
                decide("deny",
                       "Prompt Craft Gate: external model dispatch (codex/claude/gemini CLI) carries"
                       " a bare inline prompt — no XML sections and no prompt file/heredoc."
                       + GATE_HINT)
        return 0

    return 0


if __name__ == "__main__":
    aos.run_guarded(main)
