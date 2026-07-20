#!/usr/bin/env python3
"""Install the bundled AgentOS template into a project directory."""

from __future__ import annotations

import argparse
import copy
import hashlib
import json
import os
import re
import shutil
import sys
import tempfile
import tomllib
from datetime import datetime, timezone
from pathlib import Path


SKILL_DIR = Path(__file__).resolve().parents[1]
DEFAULT_TEMPLATE = SKILL_DIR / "assets" / "agentos-template"
BACKUP_ROOT = ".agentos-backups"
MERGE_FILES = {
    ".gitignore", "AGENTS.md", "CLAUDE.md", "PLANS.md", "PROGRESS.md",
    "DECISIONS.md", "HANDOFF.md",
}
JSON_HOOK_MERGE_FILES = {".claude/settings.json", ".codex/hooks.json"}
TOML_MERGE_FILES = {".codex/config.toml"}
MERGE_FAILURE_PREFIX = "merge-failed-"

# Exact paths owned by older AgentOS releases and intentionally retired from
# the current package. They are backed up before removal. Runtime state and
# project Wiki paths never belong in this list.
OBSOLETE_AGENTOS_PATHS = (
    ".codex/agentos-local-rules.md",
    ".codex/hooks/aos_referee.py",
    ".claude/hooks/aos_guard_enforcer.py",
    ".claude/hooks/aos_referee.py",
    ".claude/skills/dynamic-workflow",
    ".agents/skills/error-learning",
    ".agents/skills/error-neat",
    ".agents/skills/neat-freak",
    ".agents/skills/project-memory-bootstrap",
    ".agents/skills/wiki-maintenance",
    ".agents/skills/writing-agent-md",
    ".claude/skills/error-learning",
    ".claude/skills/error-neat",
    ".claude/skills/neat-freak",
    ".claude/skills/project-memory-bootstrap",
    ".claude/skills/wiki-maintenance",
    ".claude/skills/writing-agent-md",
    "agent-os/review/per-turn-audit-gate.md",
    "agent-os/review/spokesperson-contract.md",
    "agent-os/workflows/dynamic-workflow.md",
    "work/agent-execution-lifecycle-v1-regression-check.sh",
    "work/agent-os-adapter-activation-v1-regression-check.sh",
    "work/agent-os-kernel-definition-v1-regression-check.sh",
    "work/agent-os-kernel-migration-v1-regression-check.sh",
    "work/evidence-to-claim-gate-v1-regression-check.sh",
    "work/intent-causal-gate-v1-regression-check.sh",
    "work/reasoning-base-v1-regression-check.sh",
    "work/route-keeper-promotion-gate-v1-regression-check.sh",
    "work/task-contract-v1-regression-check.sh",
)

AGENTOS_DEV_BEGIN = "<!-- BEGIN AGENTOS CODEX DEVELOPER INSTRUCTIONS -->"
AGENTOS_DEV_END = "<!-- END AGENTOS CODEX DEVELOPER INSTRUCTIONS -->"
AGENTOS_RULES_BEGIN = "<!-- BEGIN AGENTOS RESIDENT RULES -->"
AGENTOS_RULES_END = "<!-- END AGENTOS RESIDENT RULES -->"
LEGACY_AGENTS_BEGIN = "<!-- BEGIN AGENTOS KERNEL BOOTSTRAP -->"
LEGACY_AGENTS_END = "<!-- END AGENTOS KERNEL BOOTSTRAP -->"
AGENTOS_IGNORE_BEGIN = "# BEGIN AGENTOS LOCAL STATE"
AGENTOS_IGNORE_END = "# END AGENTOS LOCAL STATE"
AGENTOS_HOOK_RE = re.compile(r"\baos_[A-Za-z0-9_-]+\.py\b")

AGENTOS_BLOCKS = {
    "CLAUDE.md": """<!-- BEGIN AGENTOS KERNEL BOOTSTRAP -->

## AgentOS Claude Adapter

- Shared resident rules load through `.claude/rules/agentos-local-rules.md`.
- Claude uses native Workflow and keeps Superpowers enabled.
- The Codex-only Dynamic Workflow adapter is not installed under `.claude/skills/`.
- Hooks restore long-task attention and run deterministic checks; `agent-os/`
  remains the kernel.

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

Use this file for the current task, verified evidence, blockers, and next safe action.

<!-- END AGENTOS LEDGER BOOTSTRAP -->
""",
    ".gitignore": f"""{AGENTOS_IGNORE_BEGIN}
/agent-os/state/active-work/
{AGENTOS_IGNORE_END}
""",
}


def agents_rules_block(template: Path) -> str:
    """Generate the Codex projection from the one canonical resident card."""
    card = read_text(template / "agent-os/rules-card.md").strip()
    return f"{AGENTOS_RULES_BEGIN}\n{card}\n{AGENTOS_RULES_END}\n"


def managed_block(template: Path, relative_path: str) -> str:
    if relative_path == "AGENTS.md":
        return agents_rules_block(template)
    return AGENTOS_BLOCKS[relative_path]


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


def atomic_write_text(dst: Path, content: str) -> None:
    """Replace a text file only after the complete candidate is available."""
    dst.parent.mkdir(parents=True, exist_ok=True)
    mode = (dst.stat().st_mode & 0o777) if dst.exists() else 0o644
    fd, temporary_name = tempfile.mkstemp(prefix=f".{dst.name}.", dir=str(dst.parent))
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as stream:
            stream.write(content)
            stream.flush()
            os.fsync(stream.fileno())
        os.chmod(temporary_name, mode)
        os.replace(temporary_name, dst)
    except Exception:
        try:
            os.unlink(temporary_name)
        except FileNotFoundError:
            pass
        raise


def merge_marked_block(dst: Path, block: str, dry_run: bool) -> str:
    """Insert or update only the AgentOS-owned block in an entry document."""
    existing = read_text(dst)
    lines = block.splitlines()
    begin_marker = lines[0]
    end_marker = lines[-1]
    begin = existing.find(begin_marker)
    end = existing.find(end_marker, begin + len(begin_marker)) if begin >= 0 else -1
    if begin < 0 and begin_marker == AGENTOS_RULES_BEGIN:
        legacy_begin = existing.find(LEGACY_AGENTS_BEGIN)
        legacy_end = existing.find(
            LEGACY_AGENTS_END, legacy_begin + len(LEGACY_AGENTS_BEGIN)
        ) if legacy_begin >= 0 else -1
        if legacy_begin >= 0 and legacy_end >= 0:
            legacy_end += len(LEGACY_AGENTS_END)
            candidate = existing[:legacy_begin] + block.rstrip("\n") + existing[legacy_end:]
            if not dry_run:
                atomic_write_text(dst, candidate)
            return "agentos-block-migrated"
    if begin >= 0 and end >= 0:
        end += len(end_marker)
        candidate = existing[:begin] + block.rstrip("\n") + existing[end:]
        if candidate == existing:
            return "already-merged"
        if not dry_run:
            atomic_write_text(dst, candidate)
        return "agentos-block-updated"
    if begin >= 0 or end >= 0:
        return "merge-failed-malformed-agentos-markers"
    if not dry_run:
        separator = "" if existing.endswith("\n") else "\n"
        atomic_write_text(dst, existing + separator + "\n" + block)
    return "merged"


def is_agentos_hook_command(command: object) -> bool:
    return isinstance(command, str) and AGENTOS_HOOK_RE.search(command) is not None


def _merge_missing_keys(current: dict, incoming: dict, *, skip: set[str] | None = None) -> bool:
    """Recursively add template defaults without overwriting user-owned values."""
    changed = False
    ignored = skip or set()
    for key, value in incoming.items():
        if key in ignored:
            continue
        if key not in current:
            current[key] = copy.deepcopy(value)
            changed = True
        elif isinstance(current[key], dict) and isinstance(value, dict):
            changed = _merge_missing_keys(current[key], value) or changed
    return changed


def _validated_hook_groups(value: object, source: str) -> list[dict]:
    if not isinstance(value, list):
        raise ValueError(f"{source}-hook-groups-must-be-a-list")
    groups: list[dict] = []
    for group in value:
        if not isinstance(group, dict) or not isinstance(group.get("hooks", []), list):
            raise ValueError(f"{source}-hook-group-shape-invalid")
        if any(not isinstance(hook, dict) for hook in group.get("hooks", [])):
            raise ValueError(f"{source}-hook-shape-invalid")
        groups.append(copy.deepcopy(group))
    return groups


def _remove_agentos_hooks(hooks: dict) -> bool:
    """Remove only hook commands owned by AgentOS, including obsolete handlers."""
    changed = False
    for event, raw_groups in list(hooks.items()):
        groups = _validated_hook_groups(raw_groups, "target")
        kept_groups = []
        for group in groups:
            original_hooks = group.get("hooks", [])
            kept_hooks = [
                hook for hook in original_hooks
                if not is_agentos_hook_command(hook.get("command"))
            ]
            changed = changed or len(kept_hooks) != len(original_hooks)
            if kept_hooks:
                group["hooks"] = kept_hooks
                kept_groups.append(group)
            elif not original_hooks:
                kept_groups.append(group)
        if kept_groups:
            hooks[event] = kept_groups
        else:
            hooks.pop(event, None)
    return changed


def _canonical_incoming_hooks(incoming_hooks: dict) -> dict[str, list[dict]]:
    """Keep one AgentOS Stop gate and one copy of each incoming Hook."""
    canonical: dict[str, list[dict]] = {}
    stop_gate_seen = False
    for event, raw_groups in incoming_hooks.items():
        groups = _validated_hook_groups(raw_groups, "template")
        canonical_groups = []
        for group in groups:
            kept_hooks = []
            for hook in group.get("hooks", []):
                command = hook.get("command")
                if event == "Stop" and is_agentos_hook_command(command):
                    if "aos_stop_gate.py" not in command or stop_gate_seen:
                        continue
                    stop_gate_seen = True
                kept_hooks.append(hook)
            if kept_hooks:
                group["hooks"] = kept_hooks
                canonical_groups.append(group)
        if canonical_groups:
            canonical[event] = canonical_groups
    if not stop_gate_seen:
        raise ValueError("template-missing-agentos-stop-gate")
    return canonical


def _add_hook_groups(current_hooks: dict, incoming_hooks: dict[str, list[dict]]) -> bool:
    changed = False
    for event, groups in incoming_hooks.items():
        current_groups = current_hooks.setdefault(event, [])
        _validated_hook_groups(current_groups, "target")
        existing_commands = {
            hook.get("command")
            for group in current_groups
            for hook in group.get("hooks", [])
        }
        for group in groups:
            new_hooks = [
                copy.deepcopy(hook)
                for hook in group.get("hooks", [])
                if hook.get("command") not in existing_commands
            ]
            if not new_hooks:
                continue
            matcher = group.get("matcher")
            target_group = next(
                (item for item in current_groups if item.get("matcher") == matcher),
                None,
            )
            if target_group is None:
                target_group = {key: copy.deepcopy(value) for key, value in group.items() if key != "hooks"}
                target_group["hooks"] = []
                current_groups.append(target_group)
            target_group.setdefault("hooks", []).extend(new_hooks)
            existing_commands.update(hook.get("command") for hook in new_hooks)
            changed = True
    return changed


def merge_hook_json(src: Path, dst: Path, dry_run: bool) -> str:
    """Merge hook JSON while replacing only AgentOS-owned hook commands."""
    original = read_text(dst) if dst.exists() else ""
    try:
        current = json.loads(original) if original.strip() else {}
        if not isinstance(current, dict):
            raise ValueError("target-root-must-be-an-object")
    except Exception:
        return "merge-failed-invalid-target-json"
    try:
        incoming = json.loads(read_text(src))
        if not isinstance(incoming, dict):
            raise ValueError("template-root-must-be-an-object")
    except Exception:
        return "merge-failed-invalid-template-json"

    try:
        target_hooks = current.setdefault("hooks", {})
        template_hooks = incoming.get("hooks") or {}
        if not isinstance(target_hooks, dict) or not isinstance(template_hooks, dict):
            raise ValueError("hooks-must-be-an-object")
        canonical_hooks = _canonical_incoming_hooks(template_hooks)
        changed = _remove_agentos_hooks(target_hooks)
        changed = _add_hook_groups(target_hooks, canonical_hooks) or changed
        changed = _merge_missing_keys(current, incoming, skip={"hooks"}) or changed
    except (TypeError, ValueError):
        return "merge-failed-invalid-hook-shape"

    candidate = json.dumps(current, indent=2, ensure_ascii=False) + "\n"
    if not changed and original == candidate:
        return "already-merged"
    if not dry_run:
        atomic_write_text(dst, candidate)
    return "json-hooks-merged"


def _strip_managed_developer_block(value: str) -> str:
    pattern = re.compile(
        re.escape(AGENTOS_DEV_BEGIN) + r".*?" + re.escape(AGENTOS_DEV_END),
        re.DOTALL,
    )
    return pattern.sub("", value).strip()


def _looks_like_legacy_agentos_developer_instructions(value: str) -> bool:
    return (
        value.strip().startswith("This trusted project uses the repo-local AgentOS kernel.")
        and "Codex-specific AgentOS startup is native to Codex:" in value
        and ".codex/hooks" in value
    )


def _replace_top_level_string_assignment(text: str, key: str, value: str) -> str:
    """Replace a conventional top-level TOML string without rewriting other keys."""
    assignment = re.search(rf"(?m)^[ \t]*{re.escape(key)}[ \t]*=[ \t]*", text)
    if assignment is None:
        prefix = f"{key} = {json.dumps(value, ensure_ascii=False)}\n"
        return prefix + ("\n" if text and not text.startswith("\n") else "") + text
    if re.search(r"(?m)^[ \t]*\[", text[: assignment.start()]):
        raise ValueError(f"{key}-is-not-top-level")

    value_start = assignment.end()
    if text.startswith('"""', value_start) or text.startswith("'''", value_start):
        quote = text[value_start : value_start + 3]
        close = text.find(quote, value_start + 3)
        if close < 0:
            raise ValueError(f"{key}-multiline-string-not-closed")
        replace_end = close + 3
    elif text.startswith("'", value_start):
        close = text.find("'", value_start + 1)
        if close < 0:
            raise ValueError(f"{key}-literal-string-not-closed")
        replace_end = close + 1
    elif text.startswith('"', value_start):
        cursor = value_start + 1
        escaped = False
        close = -1
        while cursor < len(text):
            character = text[cursor]
            if character == '"' and not escaped:
                close = cursor
                break
            if character == "\\" and not escaped:
                escaped = True
            else:
                escaped = False
            cursor += 1
        if close < 0:
            raise ValueError(f"{key}-basic-string-not-closed")
        replace_end = close + 1
    else:
        raise ValueError(f"{key}-must-be-a-string-assignment")
    replacement = f"{key} = {json.dumps(value, ensure_ascii=False)}"
    return text[: assignment.start()] + replacement + text[replace_end:]


def _set_features_hooks(text: str, parsed: dict) -> str:
    headers = list(re.finditer(r"(?m)^[ \t]*\[features\][ \t]*(?:#.*)?$", text))
    if len(headers) > 1:
        raise ValueError("duplicate-features-table")
    if not headers:
        if "features" in parsed:
            raise ValueError("unsupported-features-shape")
        separator = "" if not text or text.endswith("\n") else "\n"
        return text + separator + ("\n" if text.strip() else "") + "[features]\nhooks = true\n"

    header = headers[0]
    next_table = re.search(r"(?m)^[ \t]*\[", text[header.end() :])
    section_end = header.end() + next_table.start() if next_table else len(text)
    section = text[header.end() : section_end]
    hook_lines = list(
        re.finditer(
            r"(?m)^(?P<prefix>[ \t]*hooks[ \t]*=[ \t]*)(?P<value>true|false)(?P<suffix>[ \t]*(?:#.*)?)$",
            section,
        )
    )
    if len(hook_lines) > 1:
        raise ValueError("duplicate-features-hooks")
    if hook_lines:
        hook_line = hook_lines[0]
        absolute_start = header.end() + hook_line.start("value")
        absolute_end = header.end() + hook_line.end("value")
        return text[:absolute_start] + "true" + text[absolute_end:]
    if isinstance(parsed.get("features"), dict) and "hooks" in parsed["features"]:
        raise ValueError("unsupported-features-hooks-assignment")
    insertion = header.end()
    return text[:insertion] + "\nhooks = true" + text[insertion:]


def merge_codex_toml(src: Path, dst: Path, dry_run: bool) -> str:
    """Merge AgentOS developer instructions and features.hooks only."""
    original = read_text(dst) if dst.exists() else ""
    try:
        current = tomllib.loads(original) if original.strip() else {}
        if not isinstance(current, dict):
            raise ValueError("target-root-invalid")
    except Exception:
        return "merge-failed-invalid-target-toml"
    try:
        incoming = tomllib.loads(read_text(src))
        incoming_dev = incoming.get("developer_instructions")
        incoming_features = incoming.get("features")
        if not isinstance(incoming_dev, str):
            raise ValueError("template-developer-instructions-missing")
        if not isinstance(incoming_features, dict) or incoming_features.get("hooks") is not True:
            raise ValueError("template-features-hooks-missing")
    except Exception:
        return "merge-failed-invalid-template-toml"

    existing_dev = current.get("developer_instructions", "")
    if not isinstance(existing_dev, str):
        return "merge-failed-unsupported-target-developer-instructions"
    if existing_dev.strip() == incoming_dev.strip() or _looks_like_legacy_agentos_developer_instructions(existing_dev):
        user_dev = ""
    else:
        user_dev = _strip_managed_developer_block(existing_dev)
    managed_dev = f"{AGENTOS_DEV_BEGIN}\n{incoming_dev.strip()}\n{AGENTOS_DEV_END}"
    merged_dev = f"{user_dev}\n\n{managed_dev}".strip() if user_dev else managed_dev

    try:
        candidate = _replace_top_level_string_assignment(original, "developer_instructions", merged_dev)
        candidate = _set_features_hooks(candidate, current)
        parsed_candidate = tomllib.loads(candidate)
        if parsed_candidate.get("features", {}).get("hooks") is not True:
            raise ValueError("features-hooks-not-enabled")
        if AGENTOS_DEV_BEGIN not in parsed_candidate.get("developer_instructions", ""):
            raise ValueError("managed-developer-instructions-missing")
    except Exception:
        return "merge-failed-unsupported-target-toml-shape"

    if candidate == original:
        return "already-merged"
    if not dry_run:
        atomic_write_text(dst, candidate)
    return "codex-toml-merged"


def protected_action(rel: Path) -> str | None:
    path = rel.as_posix()
    if path.startswith("agent-os/state/"):
        return "preserved-existing-state"
    if path.startswith("wiki/"):
        return "preserved-existing-wiki"
    return None


def remove_obsolete_agentos_paths(
    target: Path, backup_dir: Path, dry_run: bool
) -> list[dict]:
    """Back up and remove only exact paths retired by AgentOS itself."""
    actions = []
    for relative in OBSOLETE_AGENTOS_PATHS:
        rel = Path(relative)
        dst = target / rel
        if not dst.exists() and not dst.is_symlink():
            continue
        action = {
            "path": relative,
            "action": "backed-up-and-removed-obsolete",
            "backup": backup_existing(dst, rel, backup_dir, dry_run),
        }
        if not dry_run:
            if dst.is_dir() and not dst.is_symlink():
                shutil.rmtree(dst)
            else:
                dst.unlink()
        actions.append(action)
    return actions


def install(template: Path, target: Path, dry_run: bool) -> dict:
    if not template.is_dir():
        raise FileNotFoundError(f"Template directory not found: {template}")

    timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S%fZ")
    backup_dir = target / BACKUP_ROOT / timestamp
    actions = []

    if not dry_run:
        target.mkdir(parents=True, exist_ok=True)

    actions.extend(remove_obsolete_agentos_paths(target, backup_dir, dry_run))

    for src, rel in iter_template_files(template):
        dst = target / rel
        action = {"path": str(rel), "action": None, "backup": None}

        preservation = protected_action(rel) if dst.exists() else None
        if preservation:
            action["action"] = preservation
            actions.append(action)
            continue

        if rel.as_posix() in JSON_HOOK_MERGE_FILES:
            if dst.exists() and dst.is_dir():
                action["action"] = "merge-failed-target-is-directory"
            else:
                action["backup"] = backup_existing(dst, rel, backup_dir, dry_run)
                action["action"] = merge_hook_json(src, dst, dry_run)
            actions.append(action)
            continue

        if rel.as_posix() in TOML_MERGE_FILES:
            if dst.exists() and dst.is_dir():
                action["action"] = "merge-failed-target-is-directory"
            else:
                action["backup"] = backup_existing(dst, rel, backup_dir, dry_run)
                action["action"] = merge_codex_toml(src, dst, dry_run)
            actions.append(action)
            continue

        if dst.exists() and dst.is_dir():
            action["backup"] = backup_existing(dst, rel, backup_dir, dry_run)
            action["action"] = "blocked-existing-directory"
            actions.append(action)
            continue

        if dst.exists() and same_file(src, dst):
            action["action"] = "unchanged"
            actions.append(action)
            continue

        if rel.as_posix() in MERGE_FILES and dst.exists():
            action["backup"] = backup_existing(dst, rel, backup_dir, dry_run)
            action["action"] = merge_marked_block(
                dst, managed_block(template, rel.as_posix()), dry_run
            )
            actions.append(action)
            continue

        if dst.exists():
            action["backup"] = backup_existing(dst, rel, backup_dir, dry_run)
            action["action"] = "backed-up-and-replaced"
        else:
            action["action"] = "created"

        if not dry_run:
            dst.parent.mkdir(parents=True, exist_ok=True)
            if src.is_symlink():
                if dst.exists() or dst.is_symlink():
                    dst.unlink()
                dst.symlink_to(os.readlink(src))
            else:
                shutil.copy2(src, dst)
        actions.append(action)

    failed_actions = [
        item for item in actions
        if item["action"].startswith(MERGE_FAILURE_PREFIX)
        or item["action"] == "blocked-existing-directory"
    ]
    manifest = {
        "installer": "agentos-kernel-installer",
        "status": "ok" if not failed_actions else "partial",
        "template": str(template),
        "target": str(target),
        "timestamp_utc": timestamp,
        "dry_run": dry_run,
        "backup_dir": str(backup_dir),
        "actions": actions,
        "failures": failed_actions,
    }

    if not dry_run:
        atomic_write_text(
            target / ".agentos-install-manifest.json",
            json.dumps(manifest, indent=2, ensure_ascii=False) + "\n",
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
        "status": manifest["status"],
        "target": manifest["target"],
        "backup_dir": manifest["backup_dir"],
        "dry_run": manifest["dry_run"],
        "summary": summary,
    }, indent=2, ensure_ascii=False))
    return 0 if manifest["status"] == "ok" else 2


if __name__ == "__main__":
    raise SystemExit(main())
