#!/usr/bin/env python3
"""PostToolUse hook: run aos-lint after AgentOS kernel edits in Codex."""
from __future__ import annotations

import json
import re
import subprocess
import sys
from pathlib import Path

import aos_common as aos


def _tool_input(data: dict) -> dict:
    value = data.get("tool_input") or data.get("input") or data.get("arguments") or {}
    return value if isinstance(value, dict) else {}


def _payload_text(data: dict) -> str:
    try:
        return json.dumps(data, ensure_ascii=False)
    except Exception:
        return str(data)


def edited_kernel_path(data: dict, root: Path) -> str | None:
    tool = str(data.get("tool_name") or data.get("tool") or data.get("name") or "")
    tool_input = _tool_input(data)

    if tool in ("Bash", "shell", "exec_command"):
        cmd = str(tool_input.get("command") or tool_input.get("cmd") or "")
        write_hints = ("rm ", "mv ", "cp ", "sed -i", "tee ", "truncate", "apply_patch")
        redirected = re.search(r">>?\s*\S*agent-os/(?!state/)", cmd)
        if "agent-os/" in cmd and (redirected or any(h in cmd for h in write_hints)):
            return "agent-os/(via Bash)"
        return None

    for key in ("file_path", "path", "target_file", "file"):
        file_path = tool_input.get(key)
        if not isinstance(file_path, str) or not file_path:
            continue
        try:
            rel = Path(file_path).resolve().relative_to(root.resolve()).as_posix()
        except ValueError:
            continue
        if rel.startswith("agent-os/") and not rel.startswith("agent-os/state/"):
            return rel

    payload = _payload_text(data)
    if "agent-os/" in payload and "agent-os/state/" not in payload:
        return "agent-os/(via tool payload)"
    return None


def main() -> int:
    data = aos.hook_input()
    if aos.disabled():
        return 0
    root = aos.project_root(data)
    rel_posix = edited_kernel_path(data, root)
    if not rel_posix:
        return 0

    lint = root / "agent-os" / "tools" / "aos-lint.py"
    if not lint.is_file():
        return 0
    proc = subprocess.run(
        [sys.executable, str(lint)], capture_output=True, text=True, cwd=root, timeout=60
    )
    if proc.returncode != 0:
        fails = [line for line in proc.stdout.splitlines() if line.startswith("FAIL")]
        print(
            f"aos-lint FAIL after edit to {rel_posix} (the kernel is structurally consistent only after this is fixed):\n"
            + "\n".join(fails[:20]),
            file=sys.stderr,
        )
        return 2
    return 0


if __name__ == "__main__":
    aos.run_guarded(main)
