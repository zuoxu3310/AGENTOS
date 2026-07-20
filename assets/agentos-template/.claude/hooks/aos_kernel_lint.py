#!/usr/bin/env python3
"""PostToolUse hook: lint only after structured edits to governed documents."""
from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import aos_common as aos


STRUCTURED_EDIT_TOOLS = {"Edit", "Write", "MultiEdit"}
ROOT_LEDGERS = {"PLANS.md", "PROGRESS.md", "DECISIONS.md", "HANDOFF.md"}


def _relative(root: Path, value: str) -> str | None:
    try:
        path = Path(value).expanduser()
        if not path.is_absolute():
            path = root / path
        return path.resolve().relative_to(root.resolve()).as_posix()
    except Exception:
        return None


def edited_governed_paths(data: dict, root: Path) -> list[str]:
    tool = str(data.get("tool_name") or "")
    if tool not in STRUCTURED_EDIT_TOOLS:
        return []
    tool_input = data.get("tool_input") or {}
    candidates = [
        value for key in ("file_path", "path", "target_file", "file")
        if isinstance((value := tool_input.get(key)), str) and value
    ]
    relative = [_relative(root, item) for item in candidates]
    return sorted({
        item for item in relative if item and (
            (item.startswith("agent-os/") and not item.startswith("agent-os/state/"))
            or item.startswith("wiki/")
            or item in ROOT_LEDGERS
        )
    })


def relevant_failures(paths: list[str], failures: list[str]) -> list[str]:
    """Keep failures caused by or structurally coupled to the edited paths."""
    selected: list[str] = []
    for failure in failures:
        if any(path in failure for path in paths):
            selected.append(failure)
            continue
        for path in paths:
            coupled = ()
            if path.startswith("agent-os/"):
                if path == "agent-os/rules-card.md":
                    coupled = ("AGENTS.md", "CLAUDE.md", "projection", "rules card")
                elif path == "agent-os/review/prompt-craft-gate.md":
                    coupled = ("prompt source",)
                elif path == "agent-os/artifact-contracts.toml":
                    coupled = ("artifact contract",)
            elif path.startswith("wiki/errors/"):
                coupled = (
                    "error index", "Error Learning", "error_id", "root_id",
                    "same root", "error landing", "error regression",
                )
            elif path.startswith("wiki/raw/"):
                coupled = ("raw manifest", "wiki index managed view")
            elif path.startswith("wiki/knowledge/"):
                coupled = ("knowledge ", "wiki index managed view")
            elif path.startswith("wiki/"):
                coupled = ("wiki index managed view",)
            elif path == "PLANS.md":
                coupled = ("single current plan", "ledger projection invalid")
            elif path == "HANDOFF.md":
                coupled = ("single current handoff", "ledger projection invalid")
            elif path in ROOT_LEDGERS:
                coupled = ("ledger projection invalid",)
            if coupled and any(token in failure for token in coupled):
                selected.append(failure)
                break
    return selected


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
    failures = relevant_failures(
        paths,
        [line for line in proc.stdout.splitlines() if line.startswith("FAIL")],
    )
    if not failures and paths == ["agent-os/tools/aos-lint.py"] and proc.stderr.strip():
        failures = [proc.stderr.strip()]
    if not failures:
        return 0
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
