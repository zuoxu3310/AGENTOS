#!/usr/bin/env python3
"""PostToolUse hook: lint only after structured edits to governed documents."""
from __future__ import annotations

import re
import subprocess
import sys
from pathlib import Path

import aos_common as aos


STRUCTURED_EDIT_TOOLS = {"apply_patch", "Edit", "Write", "MultiEdit"}
ROOT_LEDGERS = {"PLANS.md", "PROGRESS.md", "DECISIONS.md", "HANDOFF.md"}


def _tool_input(data: dict) -> dict:
    value = data.get("tool_input") or data.get("input") or data.get("arguments") or {}
    return value if isinstance(value, dict) else {}


def _relative(root: Path, value: str) -> str | None:
    try:
        path = Path(value).expanduser()
        if not path.is_absolute():
            path = root / path
        return path.resolve().relative_to(root.resolve()).as_posix()
    except Exception:
        return None


def _governed(relative: str) -> bool:
    return (
        (relative.startswith("agent-os/") and not relative.startswith("agent-os/state/"))
        or relative.startswith("wiki/")
        or relative in ROOT_LEDGERS
    )


def edited_governed_paths(data: dict, root: Path) -> list[str]:
    tool = str(data.get("tool_name") or data.get("tool") or data.get("name") or "")
    if tool not in STRUCTURED_EDIT_TOOLS:
        return []
    tool_input = _tool_input(data)
    candidates: list[str] = []
    if tool == "apply_patch":
        patch = str(tool_input.get("patch") or tool_input.get("input") or "")
        candidates.extend(re.findall(
            r"^\*\*\* (?:Update|Add|Delete) File:\s*(.+)$", patch, re.MULTILINE
        ))
    else:
        for key in ("file_path", "path", "target_file", "file"):
            value = tool_input.get(key)
            if isinstance(value, str) and value:
                candidates.append(value)
    relative = [_relative(root, item.strip()) for item in candidates]
    return sorted({item for item in relative if item and _governed(item)})


def main() -> int:
    data = aos.hook_input()
    if aos.disabled():
        return 0
    root = aos.project_root(data)
    paths = edited_governed_paths(data, root)
    if not paths:
        return 0
    lint = root / "agent-os" / "tools" / "aos-lint.py"
    if not lint.is_file():
        return 0
    proc = subprocess.run(
        [sys.executable, str(lint)], capture_output=True, text=True, cwd=root, timeout=60
    )
    if proc.returncode == 0:
        return 0
    failures = [line for line in proc.stdout.splitlines() if line.startswith("FAIL")]
    print(
        "AgentOS 文档结构检查未通过（刚修改："
        + ", ".join(paths)
        + "）：\n"
        + "\n".join(failures[:20]),
        file=sys.stderr,
    )
    return 2


if __name__ == "__main__":
    aos.run_guarded(main)
