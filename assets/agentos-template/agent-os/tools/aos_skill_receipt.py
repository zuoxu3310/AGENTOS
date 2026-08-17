#!/usr/bin/env python3
"""Record one mechanically verifiable AgentOS seat-skill load receipt."""
from __future__ import annotations

import argparse
import hashlib
import json
import re
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
MANIFEST = ROOT / "agent-os" / "skills" / "seat-skills.json"


def load_manifest() -> dict[str, list[str]]:
    value = json.loads(MANIFEST.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError("seat-skills.json must contain an object")
    return value


def receipt(role: str, runtime: str) -> tuple[list[str], str]:
    skills = load_manifest().get(role)
    if not isinstance(skills, list) or not skills:
        raise ValueError(f"unknown or empty seat skill set: {role}")
    parts: list[str] = []
    skill_root = ".agents" if runtime == "codex" else ".claude"
    for name in skills:
        path = ROOT / skill_root / "skills" / name / "SKILL.md"
        payload = path.read_bytes()
        parts.append(f"{name}:{hashlib.sha256(payload).hexdigest()}")
    return skills, f"{runtime}|" + ";".join(parts)


def record(task_id: str, role: str, runtime: str) -> int:
    skills, evidence = receipt(role, runtime)
    safe_task = re.sub(r"[^A-Za-z0-9._-]", "_", task_id or "anonymous")[:160]
    path = ROOT / "agent-os" / "state" / "tasks" / f"{safe_task}.jsonl"
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists():
        for raw in path.read_text(encoding="utf-8", errors="replace").splitlines():
            try:
                event = json.loads(raw)
            except ValueError:
                continue
            if (event.get("role") == role and event.get("kind") == "skill_load"
                    and event.get("status") == "ok" and event.get("evidence") == evidence):
                print(f"PASS existing skill receipt: {runtime}/{role} ({len(skills)} skills)")
                return 0
    event = {
        "ts": datetime.now(timezone.utc).isoformat(),
        "role": role,
        "kind": "skill_load",
        "status": "ok",
        "text": ",".join(skills),
        "evidence": evidence,
    }
    payload = (json.dumps(event, ensure_ascii=False) + "\n").encode("utf-8")
    with path.open("ab", buffering=0) as stream:
        stream.write(payload)
    print(f"PASS recorded skill receipt: {runtime}/{role} ({len(skills)} skills)")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--task", required=True)
    parser.add_argument("--role", required=True,
                        choices=("zhongshu", "menxia", "shangshu", "executor", "yushi"))
    parser.add_argument("--runtime", required=True, choices=("codex", "claude"))
    args = parser.parse_args()
    try:
        return record(args.task, args.role, args.runtime)
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        print(f"FAIL skill receipt: {exc}")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
