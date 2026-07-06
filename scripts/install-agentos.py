#!/usr/bin/env python3
"""Install the bundled AgentOS template into a project directory."""

from __future__ import annotations

import argparse
import hashlib
import json
import shutil
import sys
from datetime import datetime, timezone
from pathlib import Path


SKILL_DIR = Path(__file__).resolve().parents[1]
DEFAULT_TEMPLATE = SKILL_DIR / "assets" / "agentos-template"
BACKUP_ROOT = ".agentos-backups"
MERGE_FILES = {"CLAUDE.md", "PLANS.md", "PROGRESS.md", "DECISIONS.md", "HANDOFF.md"}
SETTINGS_MERGE_FILES = {".claude/settings.json"}
# Files the template only seeds on first install. Once the project owns them they
# accumulate live runtime state / knowledge, so a reinstall must never overwrite
# them (that would wipe the audit log, wiki index, and wiki log). Matched by prefix.
PRESERVE_IF_EXISTS_PREFIXES = ("agent-os/state/", "wiki/")

AGENTOS_BLOCKS = {
    "CLAUDE.md": """<!-- BEGIN AGENTOS KERNEL BOOTSTRAP -->

## AgentOS Kernel Bootstrap

This project uses the repo-local AgentOS kernel.

Resident law: `.claude/rules/agentos-local-rules.md` (auto-injected every session).
For non-small tasks read `agent-os/boot.md` and route via `agent-os/router.md`.

Claude native skill wrappers live in `.claude/skills/` and remain adapters/projections.

<!-- END AGENTOS KERNEL BOOTSTRAP -->
""",
    "PLANS.md": """<!-- BEGIN AGENTOS LEDGER BOOTSTRAP -->

## AgentOS Ledger

Use this file for durable plans that future agents must preserve. Keep task-local scratch outside this ledger.

<!-- END AGENTOS LEDGER BOOTSTRAP -->
""",
    "PROGRESS.md": """<!-- BEGIN AGENTOS LEDGER BOOTSTRAP -->

## AgentOS Ledger

Use this file for completed work, verification evidence, and claim boundaries.

<!-- END AGENTOS LEDGER BOOTSTRAP -->
""",
    "DECISIONS.md": """<!-- BEGIN AGENTOS LEDGER BOOTSTRAP -->

## AgentOS Ledger

Use this file for durable decisions, reasons, scope, and claim boundaries.

<!-- END AGENTOS LEDGER BOOTSTRAP -->
""",
    "HANDOFF.md": """<!-- BEGIN AGENTOS LEDGER BOOTSTRAP -->

## AgentOS Ledger

Use this file for current active object, route, evidence state, blocker state, and next safe action.

<!-- END AGENTOS LEDGER BOOTSTRAP -->
""",
}


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def same_file(src: Path, dst: Path) -> bool:
    return dst.is_file() and src.stat().st_size == dst.stat().st_size and sha256(src) == sha256(dst)


def iter_template_files(template: Path):
    for src in sorted(template.rglob("*")):
        if src.is_dir():
            continue
        if src.name == ".DS_Store":
            continue
        yield src, src.relative_to(template)


def backup_existing(dst: Path, rel: Path, backup_dir: Path, dry_run: bool) -> str | None:
    if not dst.exists():
        return None
    backup_path = backup_dir / rel
    if not dry_run:
        backup_path.parent.mkdir(parents=True, exist_ok=True)
        if dst.is_dir():
            shutil.copytree(dst, backup_path, dirs_exist_ok=True)
        else:
            shutil.copy2(dst, backup_path)
    return str(backup_path)


def read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        return path.read_text()


def append_block(dst: Path, block: str, dry_run: bool) -> str:
    existing = read_text(dst)
    begin_marker = block.splitlines()[0]
    if begin_marker in existing:
        return "already-merged"
    if not dry_run:
        separator = "" if existing.endswith("\n") else "\n"
        dst.write_text(existing + separator + "\n" + block, encoding="utf-8")
    return "merged"


def merge_settings(src: Path, dst: Path, dry_run: bool) -> str:
    """JSON-merge AgentOS hook config into an existing .claude/settings.json.

    Existing user keys are preserved; AgentOS hook commands are appended only
    when absent (matched by command string). An unparsable target aborts the
    merge and leaves the user file untouched.
    """
    try:
        raw = read_text(dst)
        current = json.loads(raw) if raw.strip() else {}
    except Exception:
        return "settings-merge-skipped-invalid-target-json"
    try:
        incoming = json.loads(read_text(src))
    except Exception:
        return "settings-merge-skipped-invalid-template-json"

    hooks_current = current.setdefault("hooks", {})
    changed = False
    for event, groups in (incoming.get("hooks") or {}).items():
        current_groups = hooks_current.setdefault(event, [])
        existing_commands = {
            hook.get("command")
            for group in current_groups
            for hook in group.get("hooks", [])
        }
        for group in groups:
            new_hooks = [
                hook for hook in group.get("hooks", [])
                if hook.get("command") not in existing_commands
            ]
            if not new_hooks:
                continue
            target_group = next(
                (g for g in current_groups if g.get("matcher") == group.get("matcher")),
                None,
            )
            if target_group is None:
                added = dict(group)
                added["hooks"] = new_hooks
                current_groups.append(added)
            else:
                target_group.setdefault("hooks", []).extend(new_hooks)
            changed = True

    if changed and not dry_run:
        dst.write_text(
            json.dumps(current, indent=2, ensure_ascii=False) + "\n",
            encoding="utf-8",
        )
    return "settings-merged" if changed else "already-merged"


def install(template: Path, target: Path, dry_run: bool) -> dict:
    if not template.is_dir():
        raise FileNotFoundError(f"Template directory not found: {template}")

    timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    backup_dir = target / BACKUP_ROOT / timestamp
    actions = []

    if not dry_run:
        target.mkdir(parents=True, exist_ok=True)

    for src, rel in iter_template_files(template):
        dst = target / rel
        action = {"path": str(rel), "action": None, "backup": None}

        if dst.exists() and dst.is_dir():
            action["backup"] = backup_existing(dst, rel, backup_dir, dry_run)
            action["action"] = "blocked-existing-directory"
            actions.append(action)
            continue

        if dst.exists() and any(rel.as_posix().startswith(p) for p in PRESERVE_IF_EXISTS_PREFIXES):
            action["action"] = "preserved-existing"
            actions.append(action)
            continue

        if dst.exists() and same_file(src, dst):
            action["action"] = "unchanged"
            actions.append(action)
            continue

        if rel.as_posix() in MERGE_FILES and dst.exists():
            action["backup"] = backup_existing(dst, rel, backup_dir, dry_run)
            action["action"] = append_block(dst, AGENTOS_BLOCKS[rel.as_posix()], dry_run)
            actions.append(action)
            continue

        if rel.as_posix() in SETTINGS_MERGE_FILES and dst.exists():
            action["backup"] = backup_existing(dst, rel, backup_dir, dry_run)
            action["action"] = merge_settings(src, dst, dry_run)
            actions.append(action)
            continue

        if dst.exists():
            action["backup"] = backup_existing(dst, rel, backup_dir, dry_run)
            action["action"] = "backed-up-and-replaced"
        else:
            action["action"] = "created"

        if not dry_run:
            dst.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(src, dst)
        actions.append(action)

    manifest = {
        "installer": "agentos-kernel-installer",
        "template": str(template),
        "target": str(target),
        "timestamp_utc": timestamp,
        "dry_run": dry_run,
        "backup_dir": str(backup_dir),
        "actions": actions,
    }

    if not dry_run:
        (target / ".agentos-install-manifest.json").write_text(
            json.dumps(manifest, indent=2, ensure_ascii=False) + "\n",
            encoding="utf-8",
        )

    return manifest


def main() -> int:
    parser = argparse.ArgumentParser(description="Install AgentOS Kernel scaffold into a project.")
    parser.add_argument("target", nargs="?", default=".", help="Target project directory. Defaults to current directory.")
    parser.add_argument("--template", default=str(DEFAULT_TEMPLATE), help="Template directory override.")
    parser.add_argument("--dry-run", action="store_true", help="Show actions without writing files.")
    args = parser.parse_args()

    target = Path(args.target).expanduser().resolve()
    template = Path(args.template).expanduser().resolve()

    try:
        manifest = install(template, target, args.dry_run)
    except Exception as exc:
        print(f"agentos_install_failed: {exc}", file=sys.stderr)
        return 1

    summary = {}
    for item in manifest["actions"]:
        summary[item["action"]] = summary.get(item["action"], 0) + 1

    print(json.dumps({
        "status": "ok",
        "target": manifest["target"],
        "backup_dir": manifest["backup_dir"],
        "dry_run": manifest["dry_run"],
        "summary": summary,
    }, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

