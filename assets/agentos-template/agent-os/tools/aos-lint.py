#!/usr/bin/env python3
"""Structural lint for a repo-local AgentOS scaffold.

This check proves structure only. It does not prove AgentOS behavioral success,
runtime auto-triggering, hooks, worker visibility, or production durable replay.
"""

from __future__ import annotations

import argparse
import re
import sys
import tomllib
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]

REQUIRED_DIRS = [
    "agent-os",
    "agent-os/adapters",
    "agent-os/memory",
    "agent-os/review",
    "agent-os/workflows",
    "agent-os/skills",
    "agent-os/handoffs",
    "agent-os/tools",
    ".agents/skills",
    ".claude/skills",
    "wiki",
    "wiki/TASKS",
    "wiki/CHATS",
    "wiki/errors",
    "wiki/knowledge",
    "wiki/raw",
    "wiki/docs",
    "wiki/ledgers",
    "outputs",
    "work/e2e-pressure-tests",
]

REQUIRED_FILES = [
    "AGENTS.md",
    "CLAUDE.md",
    "PLANS.md",
    "PROGRESS.md",
    "DECISIONS.md",
    "HANDOFF.md",
    "agent-os/boot.md",
    "agent-os/router.md",
    "agent-os/rules-card.md",
    "agent-os/artifact-contracts.toml",
    "agent-os/adapters/runtime-visibility.md",
    "agent-os/adapters/skill-parity.md",
    "agent-os/adapters/codex-workflow.md",
    "agent-os/memory/bootstrap.md",
    "agent-os/memory/routing.md",
    "agent-os/memory/sync-audit.md",
    "agent-os/memory/error-learning.md",
    "agent-os/memory/wiki-v2.md",
    "agent-os/review/reasoning-base.md",
    "agent-os/review/intent-causal-gate.md",
    "agent-os/review/task-contract.md",
    "agent-os/review/route-keeper-promotion-gate.md",
    "agent-os/review/evidence-to-claim-gate.md",
    "agent-os/review/completion-gate.md",
    "agent-os/review/anti-sycophancy-gate.md",
    "agent-os/review/minimal-code-gate.md",
    "agent-os/workflows/agent-execution-lifecycle.md",
    "agent-os/handoffs/README.md",
    "agent-os/skills/README.md",
    "agent-os/tools/aos-lint.py",
    "agent-os/tools/aos_active_work.py",
    ".claude/settings.json",
    ".codex/config.toml",
    ".codex/hooks.json",
    ".codex/hooks/aos_common.py",
    ".codex/hooks/aos_session_start.py",
    ".codex/hooks/aos_prompt_baseline.py",
    ".codex/hooks/aos_stop_gate.py",
    ".codex/hooks/aos_kernel_lint.py",
    ".codex/hooks/aos_guard_enforcer.py",
    ".claude/hooks/aos_common.py",
    ".claude/hooks/aos_session_start.py",
    ".claude/hooks/aos_prompt_baseline.py",
    ".claude/hooks/aos_stop_gate.py",
    ".claude/hooks/aos_kernel_lint.py",
    ".claude/rules/agentos-local-rules.md",
    ".agents/skills/dynamic-workflow/SKILL.md",
    ".agents/skills/dynamic-workflow/agents/openai.yaml",
    ".agents/skills/evidence-claim-review/SKILL.md",
    ".agents/skills/intent-contract-review/SKILL.md",
    ".agents/skills/lifecycle-execution/SKILL.md",
    ".agents/skills/memory-wiki-routing/SKILL.md",
    ".agents/skills/reasoning-causality-review/SKILL.md",
    ".agents/skills/route-promotion-review/SKILL.md",
    ".claude/skills/evidence-claim-review/SKILL.md",
    ".claude/skills/intent-contract-review/SKILL.md",
    ".claude/skills/lifecycle-execution/SKILL.md",
    ".claude/skills/memory-wiki-routing/SKILL.md",
    ".claude/skills/reasoning-causality-review/SKILL.md",
    ".claude/skills/route-promotion-review/SKILL.md",
    ".claude/skills/anti-sycophancy-review/SKILL.md",
    ".claude/skills/minimal-code-review/SKILL.md",
    ".agents/skills/anti-sycophancy-review/SKILL.md",
    ".agents/skills/anti-sycophancy-review/agents/openai.yaml",
    ".agents/skills/minimal-code-review/SKILL.md",
    ".agents/skills/minimal-code-review/agents/openai.yaml",
    "wiki/index.md",
    "wiki/log.md",
    "wiki/raw/MANIFEST.md",
    "wiki/CHATS/README.md",
    "wiki/TASKS/README.md",
    "wiki/docs/README.md",
    "wiki/errors/_INDEX.md",
    "wiki/knowledge/README.md",
    "wiki/knowledge/agentos-wiki-v2-method.md",
    "wiki/ledgers/README.md",
    "outputs/reasoning-base-v1-templates-2026-07-01.md",
    "outputs/intent-causal-gate-v1-templates-2026-07-01.md",
    "outputs/task-contract-v1-templates-2026-07-01.md",
    "outputs/route-keeper-promotion-gate-v1-templates-2026-07-01.md",
    "outputs/evidence-to-claim-gate-v1-templates-2026-07-01.md",
    "outputs/agent-execution-lifecycle-v1-templates-2026-07-01.md",
    "outputs/agent-os-kernel-placement-map-v1-2026-07-01.md",
    "work/e2e-pressure-tests/agentos-e2e-pressure-test.mjs",
]

PATTERNS = {
    "AGENTS.md": [
        r"agent-os/boot\.md",
        r"agent-os/router\.md",
        r"Every real user message",
        r"active_work",
    ],
    "CLAUDE.md": [
        r"Claude Code Adapter",
        r"\.claude/skills/",
        r"agentos-local-rules\.md",
        r"native Workflow",
    ],
    "agent-os/boot.md": [
        r"Startup Sequence",
        r"agent-os/router\.md",
        r"structure only",
    ],
    "agent-os/router.md": [
        r"active user object",
        r"Route Table",
        r"\.agents/skills/",
        r"\.claude/skills/",
        r"one delegated execution engine",
    ],
    "agent-os/adapters/runtime-visibility.md": [
        r"Runtime Visibility Adapter",
        r"Codex Visible Thread Standard",
        r"Claude Visibility Standard",
        r"user_visible",
    ],
    "agent-os/adapters/skill-parity.md": [
        r"Skill Parity Matrix",
        r"same capability",
        r"same copied skill format",
    ],
    "agent-os/adapters/codex-workflow.md": [
        r"Codex Workflow Adapter",
        r"NO_DELEGATION",
        r"cheapest capable",
        r"single writer",
        r"Worker And Model Routing",
        r"Harness Compiler",
        r"fan-out and synthesize.*staged pipeline.*race and cancel.*sessionful steering.*human checkpoint",
        r"one delegated execution engine",
        r"vendor/claude-dynamic-workflows-codex/runner/bin/run-workflow\.js",
        r"agent\.start.*agent\.waitAny.*session\.steer.*session\.cancel",
        r"workspace fingerprint",
    ],
    "agent-os/memory/bootstrap.md": [
        r"Memory Bootstrap",
        r"Required Memory Scaffold",
        r"PLANS\.md.*PROGRESS\.md.*DECISIONS\.md.*HANDOFF\.md",
    ],
    "agent-os/memory/wiki-v2.md": [
        r"AgentOS Wiki v2",
        r"Open Knowledge Format",
        r"YAML frontmatter",
        r"confidence",
        r"supersession",
    ],
    "agent-os/review/reasoning-base.md": [
        r"first principles",
        r"Causal Roles",
        r"Full Reasoning Mode",
    ],
    "agent-os/review/intent-causal-gate.md": [
        r"active_user_object",
        r"Ask Gate",
        r"Proxy Risk Gate",
    ],
    "agent-os/review/task-contract.md": [
        r"Long-Task State",
        r"done_when",
        r"report_state",
    ],
    "agent-os/review/route-keeper-promotion-gate.md": [
        r"Route Checkpoint",
        r"Promotion Gate",
        r"mainline.*support.*blocker.*side_route.*discard",
    ],
    "agent-os/review/evidence-to-claim-gate.md": [
        r"Claim Strength Ladder",
        r"observed.*supported.*strongly_supported.*best_current_explanation.*proven.*causal.*root_cause.*complete",
    ],
    "agent-os/review/completion-gate.md": [
        r"active_user_object",
        r"completion_status",
        r"aos-lint proves structure only",
    ],
    "agent-os/workflows/agent-execution-lifecycle.md": [
        r"read the real user message.*reconstruct the result and finish conditions",
        r"Several tools may serve one segment",
        r"report_state: pending",
        r"simple natural language",
    ],
    "agent-os/tools/aos_active_work.py": [
        r"def validate",
        r"def mark_delivered",
        r"done work needs evidence for every done_when condition exactly once",
    ],
    ".codex/hooks/aos_prompt_baseline.py": [
        r"agentos_attention",
        r"Several tools may serve that one segment",
    ],
    ".claude/hooks/aos_prompt_baseline.py": [
        r"agentos_attention",
        r"Several tools may serve that one segment",
    ],
    ".codex/hooks/aos_guard_enforcer.py": [
        r"vendored Dynamic Workflow runner",
        r"permissionDecision.*deny",
    ],
    ".claude/settings.json": [
        r"SessionStart",
        r"UserPromptSubmit",
        r"\"Stop\"",
        r"aos_stop_gate\.py",
        r"aos_kernel_lint\.py",
    ],
    ".codex/config.toml": [
        r"developer_instructions",
        r"AGENTS\.md",
        r"Do not use \.codex/rules/",
    ],
    ".codex/hooks/aos_session_start.py": [
        r"restore only the current long-task finish line",
        r"active_work_state",
        r"agentos_attention",
    ],
    ".claude/hooks/aos_session_start.py": [
        r"restore only the current long-task finish line",
        r"active_work_state",
        r"agentos_attention",
    ],
    ".claude/rules/agentos-local-rules.md": [
        r"Every real user message",
        r"native Workflow",
        r"Superpowers",
        r"Source order",
        r"simple, natural, direct language",
    ],
    "agent-os/memory/error-learning.md": [
        r"same-root",
        r"evidence anchor",
        r"wiki/errors",
    ],
    "agent-os/review/anti-sycophancy-gate.md": [
        r"Toolbox",
        r"sycophan",
        r"Trigger",
    ],
    "agent-os/review/minimal-code-gate.md": [
        r"Decision Ladder",
        r"YAGNI",
    ],
    "wiki/knowledge/agentos-wiki-v2-method.md": [
        r"type: AgentOS Method",
        r"confidence:",
        r"supersedes:",
        r"sources:",
    ],
    "work/e2e-pressure-tests/agentos-e2e-pressure-test.mjs": [
        r"promotion-gate:downgrade-unsupported-worker-claim",
        r"skill-parity",
        r"runtime-visibility",
    ],
}

FORBIDDEN_PATTERNS = [
    r"\b" + "".join(["T", "B", "D"]) + r"\b",
    r"\b" + "".join(["T", "O", "D", "O"]) + r"\b",
    r"implement\s+later",
    r"fill\s+in\s+details",
    r"place" + r"holder",
]

CONTRACT_FIELDS = {
    "id", "paths", "canonical_owner", "consumer", "load_mode",
    "required_structure", "forbidden_content", "projections", "verification",
}
AGENTOS_RULES_BEGIN = "<!-- BEGIN AGENTOS RESIDENT RULES -->"
AGENTOS_RULES_END = "<!-- END AGENTOS RESIDENT RULES -->"
WIKI_LINKS_BEGIN = "<!-- BEGIN AGENTOS WIKI LINKS -->"
WIKI_LINKS_END = "<!-- END AGENTOS WIKI LINKS -->"
ERROR_RECORDS_BEGIN = "<!-- BEGIN AGENTOS ERROR RECORDS -->"
ERROR_RECORDS_END = "<!-- END AGENTOS ERROR RECORDS -->"


def read(path: str) -> str:
    return (ROOT / path).read_text(encoding="utf-8")


def fail(message: str, failures: list[str]) -> None:
    failures.append(message)
    print(f"FAIL {message}")


def _glob_files(pattern: str) -> set[str]:
    return {
        path.relative_to(ROOT).as_posix()
        for path in ROOT.glob(pattern)
        if path.is_file()
    }


def _frontmatter(path: Path) -> dict[str, object]:
    """Parse the deliberately small YAML subset used by AgentOS memory."""
    lines = path.read_text(encoding="utf-8").splitlines()
    if not lines or lines[0].strip() != "---":
        return {}
    try:
        end = lines.index("---", 1)
    except ValueError:
        return {}
    result: dict[str, object] = {}
    current_list: str | None = None
    for line in lines[1:end]:
        if current_list and re.match(r"^\s+-\s+", line):
            value = re.sub(r"^\s+-\s+", "", line).strip()
            cast = result.setdefault(current_list, [])
            if isinstance(cast, list):
                cast.append(value)
            continue
        current_list = None
        if ":" not in line:
            continue
        key, raw = line.split(":", 1)
        key, raw = key.strip(), raw.strip()
        if not raw:
            result[key] = []
            current_list = key
        elif raw.startswith("[") and raw.endswith("]"):
            result[key] = [item.strip() for item in raw[1:-1].split(",") if item.strip()]
        elif raw.isdigit():
            result[key] = int(raw)
        else:
            result[key] = raw.strip("\"'")
    return result


def _replace_view(path: Path, begin: str, end: str, body: str, heading: str) -> bool:
    text = path.read_text(encoding="utf-8")
    block = f"{begin}\n{body.rstrip()}\n{end}"
    if begin in text and end in text:
        updated = text.split(begin, 1)[0] + block + text.split(end, 1)[1]
    else:
        updated = text.rstrip() + f"\n\n## {heading}\n\n{block}\n"
    if updated == text:
        return False
    path.write_text(updated, encoding="utf-8")
    return True


def _wiki_link_view() -> str:
    paths = sorted(
        path.relative_to(ROOT / "wiki").as_posix()
        for path in (ROOT / "wiki").rglob("*.md")
        if path.name not in {"index.md", "log.md"}
    )
    groups: dict[str, list[str]] = {}
    for relative in paths:
        group = relative.split("/", 1)[0] if "/" in relative else "root"
        groups.setdefault(group, []).append(relative)
    lines = ["Generated from governed Wiki files; edit source files, not this list."]
    for group, items in sorted(groups.items()):
        lines.extend(("", f"### {group}"))
        lines.extend(f"- [{item}]({item})" for item in items)
    return "\n".join(lines)


def _error_records() -> tuple[str, dict[str, int]]:
    records: list[tuple[str, dict[str, object]]] = []
    for path in sorted((ROOT / "wiki/errors").glob("20*.md")):
        records.append((path.relative_to(ROOT).as_posix(), _frontmatter(path)))
    recurring = sum(item.get("status") == "recurring" for _, item in records)
    missing_regression = sum(
        not str(item.get("regression") or "").strip()
        for _, item in records
        if item.get("status") != "superseded"
    )
    roots = [str(item.get("root_id") or "") for _, item in records]
    conflicts = len(roots) - len(set(roots)) + sum(
        item.get("status") == "stale" for _, item in records
    )
    metrics = {
        "active": sum(item.get("status") != "superseded" for _, item in records),
        "recurring": recurring,
        "missing_regression": missing_regression,
        "conflicts": conflicts,
    }
    lines = [
        f"- Active records: {metrics['active']}",
        f"- Recurrences after landing: {metrics['recurring']}",
        f"- Active records without regression: {metrics['missing_regression']}",
        f"- Stale or conflicting rules: {metrics['conflicts']}",
        "",
    ]
    for relative, item in records:
        triggers = ", ".join(str(value) for value in item.get("triggers") or [])
        lines.append(
            f"- [{item.get('error_id')}]({Path(relative).name}) — "
            f"status={item.get('status')}; recurrence={item.get('recurrence')}; "
            f"triggers={triggers}"
        )
    return "\n".join(lines), metrics


def fix_memory_views() -> bool:
    """Update only the two mechanically derived memory views."""
    changed = _replace_view(
        ROOT / "wiki/index.md",
        WIKI_LINKS_BEGIN,
        WIKI_LINKS_END,
        _wiki_link_view(),
        "Managed Memory Map",
    )
    error_view, _ = _error_records()
    changed = _replace_view(
        ROOT / "wiki/errors/_INDEX.md",
        ERROR_RECORDS_BEGIN,
        ERROR_RECORDS_END,
        error_view,
        "Error Records",
    ) or changed
    return changed


def _anchor_path(value: object) -> tuple[Path | None, str]:
    raw = str(value or "").strip()
    if not raw:
        return None, ""
    relative, _, anchor = raw.partition("::")
    return ROOT / relative, anchor


def _check_anchor(label: str, value: object, failures: list[str]) -> bool:
    path, anchor = _anchor_path(value)
    if path is None or not path.is_file():
        fail(f"{label} does not resolve: {value}", failures)
        return False
    if anchor and f"def {anchor}(" not in path.read_text(encoding="utf-8"):
        fail(f"{label} test anchor does not resolve: {value}", failures)
        return False
    return True


def lint_memory_contracts(failures: list[str]) -> None:
    """Check memory ownership, reachability, lifecycle, and Error Learning."""
    expected_wiki_view = _wiki_link_view()
    index_text = read("wiki/index.md")
    if WIKI_LINKS_BEGIN not in index_text or WIKI_LINKS_END not in index_text:
        fail("wiki index managed view missing; run --fix-memory-views", failures)
    else:
        actual = index_text.split(WIKI_LINKS_BEGIN, 1)[1].split(WIKI_LINKS_END, 1)[0].strip()
        if actual != expected_wiki_view.strip():
            fail("wiki index managed view stale; run --fix-memory-views", failures)
        else:
            print("PASS wiki index reachability view")

    raw_files = {
        path.relative_to(ROOT).as_posix()
        for path in (ROOT / "wiki/raw").glob("*.md")
        if path.name not in {"README.md", "MANIFEST.md"}
    }
    manifest_text = read("wiki/raw/MANIFEST.md")
    registered = {
        value for value in re.findall(r"`(wiki/raw/[^`]+\.md)`", manifest_text)
        if value not in {"wiki/raw/README.md", "wiki/raw/MANIFEST.md"}
    }
    if raw_files != registered:
        fail(
            "raw manifest coverage mismatch: missing="
            + repr(sorted(raw_files - registered))
            + " extra=" + repr(sorted(registered - raw_files)),
            failures,
        )
    else:
        print("PASS raw manifest coverage")

    for name in ("PLANS.md", "PROGRESS.md", "DECISIONS.md", "HANDOFF.md"):
        link = ROOT / "wiki/ledgers" / name
        target = ROOT / name
        if not link.is_symlink() or link.resolve() != target.resolve():
            fail(f"ledger projection invalid: wiki/ledgers/{name}", failures)
        else:
            print(f"PASS ledger projection: {name}")

    plans = read("PLANS.md")
    if plans.count("## Current Plan") != 1 or plans.count("- Status: current") != 1:
        fail("PLANS.md must identify exactly one current plan", failures)
    else:
        print("PASS single current plan")
    handoff = read("HANDOFF.md")
    if handoff.count("## Current Snapshot") != 1 or handoff.count("- Status: current") != 1:
        fail("HANDOFF.md must contain exactly one current snapshot", failures)
    else:
        print("PASS single current handoff")

    knowledge: dict[str, dict[str, object]] = {}
    for path in sorted((ROOT / "wiki/knowledge").glob("*.md")):
        if path.name == "README.md":
            continue
        meta = _frontmatter(path)
        relative = path.relative_to(ROOT).as_posix()
        knowledge[relative] = meta
        for field in (
            "type", "title", "description", "timestamp", "confidence", "status",
            "last_confirmed", "supersedes", "superseded_by", "sources",
        ):
            if field not in meta:
                fail(f"knowledge field missing: {relative}: {field}", failures)
        if meta.get("status") not in {"current", "superseded", "stale", "archived"}:
            fail(f"knowledge status invalid: {relative}: {meta.get('status')}", failures)
    for relative, meta in knowledge.items():
        for target in meta.get("supersedes") or []:
            target_path = str(target)
            if target_path not in knowledge:
                fail(f"knowledge supersedes target missing: {relative} -> {target_path}", failures)
                continue
            reverse = str(knowledge[target_path].get("superseded_by") or "")
            if reverse != relative:
                fail(f"knowledge supersession not bidirectional: {relative} -> {target_path}", failures)
        successor = str(meta.get("superseded_by") or "")
        if successor:
            if successor not in knowledge:
                fail(f"knowledge superseded_by target missing: {relative} -> {successor}", failures)
            elif relative not in (knowledge[successor].get("supersedes") or []):
                fail(f"knowledge supersession reverse missing: {relative} -> {successor}", failures)
    if knowledge and not any("knowledge" in item for item in failures):
        print("PASS knowledge lifecycle and supersession")

    error_ids: dict[str, str] = {}
    root_ids: dict[str, str] = {}
    error_problems_before = len(failures)
    for path in sorted((ROOT / "wiki/errors").glob("20*.md")):
        relative = path.relative_to(ROOT).as_posix()
        meta = _frontmatter(path)
        error_id = str(meta.get("error_id") or "")
        root_id = str(meta.get("root_id") or "")
        for field in (
            "error_id", "root_id", "status", "recurrence", "triggers",
            "landing_level", "landing_target", "regression",
        ):
            if field not in meta:
                fail(f"error field missing: {relative}: {field}", failures)
        if error_id in error_ids:
            fail(f"duplicate error_id: {error_id}: {error_ids[error_id]}, {relative}", failures)
        error_ids[error_id] = relative
        if root_id in root_ids:
            fail(f"same root split across files: {root_id}: {root_ids[root_id]}, {relative}", failures)
        root_ids[root_id] = relative
        status = meta.get("status")
        recurrence = meta.get("recurrence")
        level = meta.get("landing_level")
        triggers = meta.get("triggers")
        if status not in {"observed", "landed", "verified", "recurring", "superseded"}:
            fail(f"error status invalid: {relative}: {status}", failures)
        if not isinstance(recurrence, int) or recurrence < 1:
            fail(f"error recurrence invalid: {relative}: {recurrence}", failures)
        if not isinstance(triggers, list) or not triggers:
            fail(f"error triggers missing: {relative}", failures)
        if not isinstance(level, int) or level not in range(0, 6):
            fail(f"error landing level invalid: {relative}: {level}", failures)
        target_ok = _check_anchor(f"error landing target {relative}", meta.get("landing_target"), failures)
        regression_ok = _check_anchor(f"error regression {relative}", meta.get("regression"), failures)
        if isinstance(recurrence, int) and recurrence >= 2:
            if level not in {1, 2}:
                fail(f"recurring error lacks Level 1/2 landing: {relative}", failures)
            if not target_ok or not regression_ok:
                fail(f"recurring error lacks mechanical landing or regression: {relative}", failures)
        if status == "recurring" and recurrence == 1:
            fail(f"recurring error must have recurrence >= 2: {relative}", failures)
        line_count = len(path.read_text(encoding="utf-8").splitlines())
        if line_count > 45:
            fail(f"active error over 45 lines: {relative}: {line_count}", failures)

    active_names = {path.name for path in (ROOT / "wiki/errors").glob("20*.md")}
    archived_names = {path.name for path in (ROOT / "wiki/errors/archive").glob("20*.md")}
    for duplicate in sorted(active_names & archived_names):
        fail(f"same error filename split across active and archive: {duplicate}", failures)
    for digest in sorted((ROOT / "wiki/errors").glob("_DIGEST_*.md")):
        if len(digest.read_text(encoding="utf-8").splitlines()) > 50:
            fail(f"error digest over 50 lines: {digest.name}", failures)

    index = read("wiki/errors/_INDEX.md")
    used = re.findall(
        r"\[([A-Z]\d{2})\]",
        "\n".join(
            line for line in index.split("## Error Records", 1)[0].splitlines()
            if line.startswith("- ")
        ),
    )
    definitions = re.findall(r"^\[([A-Z]\d{2})\]:", index, re.MULTILINE)
    if len(used) != len(set(used)) or len(definitions) != len(set(definitions)):
        fail("error index high-priority rule ids must be unique", failures)
    if set(used) != set(definitions):
        fail("error index rule references and definitions differ", failures)
    expected_error_view, _ = _error_records()
    if ERROR_RECORDS_BEGIN not in index or ERROR_RECORDS_END not in index:
        fail("error index generated view missing; run --fix-memory-views", failures)
    else:
        actual = index.split(ERROR_RECORDS_BEGIN, 1)[1].split(ERROR_RECORDS_END, 1)[0].strip()
        if actual != expected_error_view.strip():
            fail("error index generated view stale; run --fix-memory-views", failures)
    if len(failures) == error_problems_before:
        print("PASS Error Learning structure, landing, and derived view")

    allowed_log_operations = {"created", "promoted", "superseded", "archived", "migrated"}
    log_text = read("wiki/log.md")
    rows = [line for line in log_text.splitlines() if line.startswith("|")][2:]
    for row in rows:
        cells = [cell.strip() for cell in row.strip("|").split("|")]
        if len(cells) >= 2 and cells[1] not in allowed_log_operations:
            fail(f"wiki/log contains non-lifecycle operation: {cells[1]}", failures)

    link_files = [
        *sorted((ROOT / "agent-os").rglob("*.md")),
        *sorted((ROOT / "wiki").rglob("*.md")),
        *(ROOT / name for name in ("PLANS.md", "PROGRESS.md", "DECISIONS.md", "HANDOFF.md")),
    ]
    for path in link_files:
        for raw_target in re.findall(r"(?<!!)\[[^\]]+\]\(([^)]+)\)", path.read_text(encoding="utf-8")):
            target = raw_target.strip().strip("<>").split("#", 1)[0]
            if not target or re.match(r"^[a-z]+://", target):
                continue
            resolved = (path.parent / target).resolve()
            if not resolved.exists():
                fail(
                    f"broken local link: {path.relative_to(ROOT).as_posix()} -> {raw_target}",
                    failures,
                )


def lint_artifact_contracts(failures: list[str]) -> None:
    """Enforce one publication type and the declared document shape."""
    contract_path = ROOT / "agent-os/artifact-contracts.toml"
    try:
        contract = tomllib.loads(contract_path.read_text(encoding="utf-8"))
    except Exception as exc:
        fail(f"artifact contract unreadable: {type(exc).__name__}: {exc}", failures)
        return
    if contract.get("schema_version") != 1:
        fail("artifact contract schema_version must be 1", failures)

    governed: set[str] = set()
    for pattern in contract.get("governed_roots") or ():
        governed.update(_glob_files(str(pattern)))
    excluded: set[str] = set()
    for pattern in contract.get("excluded_roots") or ():
        excluded.update(_glob_files(str(pattern)))
    governed.difference_update(excluded)

    assignments: dict[str, list[dict]] = {path: [] for path in governed}
    artifacts = contract.get("artifact") or []
    ids: set[str] = set()
    for artifact in artifacts:
        if not isinstance(artifact, dict):
            fail("artifact contract entry must be a table", failures)
            continue
        missing = CONTRACT_FIELDS - set(artifact)
        if missing:
            fail(
                f"artifact {artifact.get('id', '<unknown>')} missing fields: "
                + ", ".join(sorted(missing)),
                failures,
            )
        artifact_id = str(artifact.get("id") or "")
        if not artifact_id or artifact_id in ids:
            fail(f"artifact id invalid or duplicate: {artifact_id!r}", failures)
        ids.add(artifact_id)
        matched: set[str] = set()
        for pattern in artifact.get("paths") or ():
            matched.update(_glob_files(str(pattern)))
        if not matched and not artifact.get("allow_empty"):
            fail(f"artifact type matches no files: {artifact_id}", failures)
        for path in matched:
            if path in assignments:
                assignments[path].append(artifact)

    for path, matches in sorted(assignments.items()):
        if len(matches) != 1:
            fail(
                f"artifact type coverage for {path}: expected 1, got {len(matches)}",
                failures,
            )
            continue
        artifact = matches[0]
        text = read(path)
        for pattern in artifact.get("required_structure") or ():
            try:
                matched = re.search(str(pattern), text) is not None
            except re.error as exc:
                fail(f"invalid contract regex for {artifact['id']}: {exc}", failures)
                continue
            if not matched:
                fail(
                    f"{path} missing {artifact['id']} structure: {pattern}", failures
                )
        for pattern in artifact.get("forbidden_content") or ():
            try:
                matched = re.search(str(pattern), text) is not None
            except re.error as exc:
                fail(f"invalid forbidden regex for {artifact['id']}: {exc}", failures)
                continue
            if matched:
                fail(f"{path} contains forbidden {artifact['id']} content: {pattern}", failures)
        if len(matches) == 1:
            print(f"PASS artifact type: {path} -> {artifact['id']}")

        if len(matches) == 1 and matches[0].get("id") == "exemplar":
            for pointer in re.findall(r"(?<![\w/])(agent-os/[A-Za-z0-9_./-]+\.md)", text):
                if not (ROOT / pointer).is_file():
                    fail(f"dead exemplar contract pointer in {path}: {pointer}", failures)

    card = read("agent-os/rules-card.md").strip()
    agents = read("AGENTS.md")
    if agents.count(AGENTOS_RULES_BEGIN) != 1 or agents.count(AGENTOS_RULES_END) != 1:
        fail("AGENTS.md managed rules markers must occur exactly once", failures)
    else:
        managed = agents.split(AGENTOS_RULES_BEGIN, 1)[1].split(
            AGENTOS_RULES_END, 1
        )[0].strip()
        if managed != card:
            fail("AGENTS.md managed rules body differs from rules-card.md", failures)
        else:
            print("PASS projection: rules-card.md -> AGENTS.md managed block")

    claude_projection = ROOT / ".claude/rules/agentos-local-rules.md"
    try:
        if claude_projection.resolve() != (ROOT / "agent-os/rules-card.md").resolve():
            fail("Claude resident rules projection does not resolve to rules-card.md", failures)
        elif claude_projection.read_text(encoding="utf-8").strip() != card:
            fail("Claude resident rules projection differs from rules-card.md", failures)
        else:
            print("PASS projection: rules-card.md -> Claude project rules")
    except Exception as exc:
        fail(f"Claude resident rules projection unreadable: {exc}", failures)

    if (ROOT / ".codex/agentos-local-rules.md").exists():
        fail("dead Codex rules pseudo-entry still exists: .codex/agentos-local-rules.md", failures)
    for live_path in (
        ".codex/config.toml",
        ".codex/hooks/aos_prompt_baseline.py",
        ".claude/hooks/aos_prompt_baseline.py",
        "CLAUDE.md",
    ):
        text = read(live_path)
        if ".codex/agentos-local-rules.md" in text:
            fail(f"dead Codex rules pseudo-entry referenced by {live_path}", failures)
        if "<executive_intake>Start every new goal" in text:
            fail(f"duplicate resident rule body in dynamic hook: {live_path}", failures)

    prompt_gate = read("agent-os/review/prompt-craft-gate.md")
    prompt_sources = {
        "agent-os/review/prompt-craft-gate.md": prompt_gate,
        ".codex/hooks/aos_stop_gate.py": read(".codex/hooks/aos_stop_gate.py"),
        ".claude/hooks/aos_stop_gate.py": read(".claude/hooks/aos_stop_gate.py"),
        ".claude/skills/fusion-workflow/references/judge-prompt-template.md": read(
            ".claude/skills/fusion-workflow/references/judge-prompt-template.md"
        ),
        ".claude/skills/fusion-workflow/references/panelist-prompt-template.md": read(
            ".claude/skills/fusion-workflow/references/panelist-prompt-template.md"
        ),
    }
    for source, text in prompt_sources.items():
        for tag in ("role", "context", "instructions", "output_format", "question"):
            if f"<{tag}>" not in text or f"</{tag}>" not in text:
                fail(f"prompt source {source} missing canonical XML tag pair: {tag}", failures)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Lint the AgentOS kernel and memory contract")
    parser.add_argument(
        "--fix-memory-views",
        action="store_true",
        help="regenerate only the Wiki link map and Error Learning record view",
    )
    args = parser.parse_args(argv)
    if args.fix_memory_views:
        changed = fix_memory_views()
        print("FIX memory views updated" if changed else "PASS memory views already current")

    failures: list[str] = []

    lint_artifact_contracts(failures)
    lint_memory_contracts(failures)

    for directory in REQUIRED_DIRS:
        if not (ROOT / directory).is_dir():
            fail(f"missing directory: {directory}", failures)
        else:
            print(f"PASS directory: {directory}")

    for file_path in REQUIRED_FILES:
        if not (ROOT / file_path).is_file():
            fail(f"missing file: {file_path}", failures)
        else:
            print(f"PASS file: {file_path}")

    for file_path, patterns in PATTERNS.items():
        if not (ROOT / file_path).is_file():
            continue
        compact = re.sub(r"\s+", " ", read(file_path))
        for pattern in patterns:
            if re.search(pattern, compact, flags=re.IGNORECASE):
                print(f"PASS pattern: {file_path}: {pattern}")
            else:
                fail(f"missing pattern in {file_path}: {pattern}", failures)

    # Root ledgers and wiki memory files are user-owned running history in
    # brownfield installs; the scaffolding-residue scan applies only to
    # kernel-owned files (agent-os/, hooks, and kernel-shipped docs such as
    # wiki/knowledge/agentos-wiki-v2-method.md).
    user_ledgers = {"PLANS.md", "PROGRESS.md", "DECISIONS.md", "HANDOFF.md"}
    kernel_wiki_docs = {"wiki/knowledge/agentos-wiki-v2-method.md"}
    for file_path in REQUIRED_FILES:
        if file_path in user_ledgers:
            continue
        if file_path.startswith("wiki/") and file_path not in kernel_wiki_docs:
            continue
        path = ROOT / file_path
        if not path.is_file():
            continue
        text = path.read_text(encoding="utf-8")
        for pattern in FORBIDDEN_PATTERNS:
            if re.search(pattern, text, flags=re.IGNORECASE):
                fail(f"forbidden pattern in {file_path}: {pattern}", failures)

    # Landing Rule (error-learning v2, 2026-07-12): every error file created on
    # or after the rule date must record which landing level the correction took
    # ("## Landing" section). Older files are exempt (pre-transformer history).
    landing_cutoff = "2026-07-12"
    errors_dir = ROOT / "wiki/errors"
    if errors_dir.is_dir():
        for err in sorted(errors_dir.glob("*.md")):
            name = err.name
            if name.startswith("_"):
                continue
            if not re.match(r"\d{4}-\d{2}-\d{2}", name[:10]):
                continue
            if name[:10] < landing_cutoff:
                continue
            if "## Landing" in err.read_text(encoding="utf-8"):
                print(f"PASS landing section: wiki/errors/{name}")
            else:
                fail(
                    f"missing '## Landing' section (error-learning v2 Landing Rule) in wiki/errors/{name}",
                    failures,
                )

    # Exemplar integrity (exemplars.md): samples must be verbatim — truncation
    # markers mean the library stores a shape the model would wrongly imitate.
    ex_dir = ROOT / "wiki/exemplars"
    if ex_dir.is_dir():
        for ex in sorted(ex_dir.rglob("*.md")):
            text = ex.read_text(encoding="utf-8")
            if "节选" in text or "(……" in text:
                fail(f"truncated sample (verbatim required) in wiki/exemplars/{ex.name}", failures)
            else:
                print(f"PASS exemplar verbatim: wiki/exemplars/{ex.name}")

    # Rules-card budget: the card is injected into EVERY session; additions must
    # displace lines, never accumulate (anti rule-inflation, ZX 2026-07-13).
    for card_path in ("agent-os/rules-card.md", ".claude/rules/agentos-local-rules.md"):
        cp = ROOT / card_path
        if cp.is_file():
            n_lines = len(cp.read_text(encoding="utf-8").splitlines())
            if n_lines > 115:
                fail(f"rules card over line budget ({n_lines} > 115): {card_path}", failures)
            else:
                print(f"PASS rules-card budget: {card_path} ({n_lines} lines)")
            card_text = cp.read_text(encoding="utf-8")
            for marker in ("verbatim source", "(ZX canon", "(ZX 20"):
                if marker in card_text:
                    fail(f"provenance annotation in rules card ({marker!r}): rules are law, origins live in ledgers/raw: {card_path}", failures)
            if "ZX" in card_text:
                fail(f"personal name in rules card (cards are depersonalized; write 'the user'): {card_path}", failures)
            else:
                print(f"PASS rules-card depersonalized: {card_path}")
            n_han = len(re.findall(r"[\u4e00-\u9fff]", card_text))
            if n_han > 150:
                fail(f"rules card Chinese-char budget exceeded ({n_han} > 150; AI-facing body must be English, Chinese only for verbatim quotes/commands): {card_path}", failures)
            else:
                print(f"PASS rules-card language budget: {card_path} ({n_han} han chars)")

    if failures:
        print(f"AgentOS structural lint FAIL: {len(failures)} issue(s)")
        return 1

    print("AgentOS structural lint PASS")
    print("Scope: structure only; behavioral success is not proven by this check.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
