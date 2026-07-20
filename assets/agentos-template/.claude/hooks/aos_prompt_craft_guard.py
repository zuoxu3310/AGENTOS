#!/usr/bin/env python3
"""PreToolUse hook: mechanical trigger for the Prompt Craft Gate.

Why this exists: the gate (agent-os/review/prompt-craft-gate.md) has been law
since 2026-07-06, yet a bare one-line prompt still went out to an external
Codex CLI probe on 2026-07-10 (wiki/errors). Prompt-layer rules do not fire by
themselves; the trigger point moves into the tool boundary (ZX 2026-07-11
"该上闸机的上闸机"). Structure is the only thing checked here — XML-sectioned
shape, never prose quality. Quality stays a judgment call at the prompt layer.

Scope (deny = rewrite the dispatch, never a session brick; fail-open on error):
- Agent/Task tool: `prompt` must carry >= MIN_TAGS distinct XML section tags.
- Workflow tool: agent("...") calls whose FIRST argument is a short bare string
  literal without tags are flagged (computed prompts pass — checkable limit).
- Bash tool: external model dispatches (codex exec / claude -p / gemini -p)
  must carry tags inline or read the prompt from a file/heredoc. Probes are
  NOT exempt (error rule 2026-07-10: 简单机械探针也不豁免).
"""
from __future__ import annotations

import json
import re

import aos_common as aos

MIN_TAGS = 3
TAG_RE = re.compile(r"<([A-Za-z_][\w-]{1,30})>")
# External model dispatch shapes seen in real transcripts (07-06 fusion smoke,
# 07-10 codex probes). Anchored to a COMMAND position (line start / after ; & |
# or $( ) so `grep "codex exec" log` and other quoted mentions never match —
# precision over recall; `env X=1 codex …` slips through and that is accepted.
_CMD = r"(?:^|[;&|(]\s*|\$\(\s*)(?:\S*/)?"
BASH_DISPATCH_RES = (
    re.compile(_CMD + r"codex\s+exec\b", re.MULTILINE),
    re.compile(_CMD + r"claude\s[^\n;|&]*(?:-p|--print)\b", re.MULTILINE),
    re.compile(_CMD + r"gemini\s[^\n;|&]*-p\b", re.MULTILINE),
)
# Inline command may legitimately carry the prompt out-of-band.
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


def distinct_tags(text: str) -> set[str]:
    return set(TAG_RE.findall(text or ""))


def main() -> int:
    data = aos.hook_input()
    if aos.disabled():
        return 0
    tool = data.get("tool_name") or ""
    tool_input = data.get("tool_input") or {}

    if tool in ("Agent", "Task"):
        prompt = tool_input.get("prompt") or ""
        tags = distinct_tags(prompt)
        if len(tags) < MIN_TAGS:
            decide("deny",
                   f"Prompt Craft Gate: subagent prompt has {len(tags)} XML section tag(s)"
                   f" (need >= {MIN_TAGS} distinct)." + GATE_HINT)
        return 0

    if tool == "Workflow":
        script = tool_input.get("script") or ""
        for m in WORKFLOW_BARE_AGENT.finditer(script):
            literal = m.group(2)
            if len(distinct_tags(literal)) < MIN_TAGS:
                decide("deny",
                       "Prompt Craft Gate: workflow script contains a bare string-literal agent()"
                       f" prompt (starts 「{literal[:60]}…」) without XML sections." + GATE_HINT)
                return 0
        return 0

    if tool == "Bash":
        cmd = tool_input.get("command") or ""
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
