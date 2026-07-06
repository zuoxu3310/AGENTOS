#!/usr/bin/env python3
"""PostToolUse hook: auto-run aos-lint after any edit under agent-os/ (state/ excluded).

Converts the prose rule "run aos-lint after editing the AgentOS kernel" into a
mechanical step: lint failures are fed straight back to the agent (exit 2).
state/ files churn every turn and are structure-checked elsewhere, so they do
not trigger a lint run.
"""
from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import aos_common as aos


def main() -> int:
    data = aos.hook_input()
    if aos.disabled():
        return 0
    tool = data.get("tool_name") or ""
    tool_input = data.get("tool_input") or {}
    root = aos.project_root(data)

    if tool == "Bash":
        # Heuristic: shell commands that look like writes into the kernel (state/ excluded) also trigger lint
        cmd = tool_input.get("command") or ""
        write_hints = ("rm ", "mv ", "cp ", "sed -i", "tee ", "truncate")
        import re as _re
        redirected = _re.search(r">>?\s*\S*agent-os/(?!state/)", cmd)
        if not ("agent-os/" in cmd and (redirected or any(h in cmd for h in write_hints))):
            return 0
        rel_posix = "agent-os/(via Bash)"
    else:
        file_path = tool_input.get("file_path") or ""
        if not file_path:
            return 0
        try:
            rel = Path(file_path).resolve().relative_to(root.resolve())
        except ValueError:
            return 0
        rel_posix = rel.as_posix()
        if not rel_posix.startswith("agent-os/") or rel_posix.startswith("agent-os/state/"):
            return 0
    lint = root / "agent-os" / "tools" / "aos-lint.py"
    if not lint.is_file():
        return 0
    proc = subprocess.run(
        [sys.executable, str(lint)], capture_output=True, text=True, cwd=root, timeout=60
    )
    if proc.returncode != 0:
        fails = [l for l in proc.stdout.splitlines() if l.startswith("FAIL")]
        print(
            f"aos-lint FAIL after edit to {rel_posix} (the kernel is structurally consistent only after this is fixed):\n"
            + "\n".join(fails[:20]),
            file=sys.stderr,
        )
        return 2
    return 0


if __name__ == "__main__":
    aos.run_guarded(main)
