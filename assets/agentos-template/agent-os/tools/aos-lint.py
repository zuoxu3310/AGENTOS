#!/usr/bin/env python3
"""Structural lint for a repo-local AgentOS scaffold.

This check proves structure only. It does not prove AgentOS behavioral success,
runtime auto-triggering, hooks, worker visibility, or production durable replay.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]

REQUIRED_DIRS = [
    "agent-os",
    "agent-os/adapters",
    "agent-os/memory",
    "agent-os/review",
    "agent-os/workflows",
    "agent-os/skills",
    "agent-os/state",
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
    "agent-os/adapters/runtime-visibility.md",
    "agent-os/adapters/skill-parity.md",
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
    "agent-os/review/per-turn-audit-gate.md",
    "agent-os/review/anti-sycophancy-gate.md",
    "agent-os/review/minimal-code-gate.md",
    "agent-os/workflows/agent-execution-lifecycle.md",
    "agent-os/workflows/dynamic-workflow.md",
    "agent-os/state/current.md",
    "agent-os/state/audit-log.md",
    "agent-os/handoffs/README.md",
    "agent-os/skills/README.md",
    "agent-os/tools/aos-lint.py",
    ".claude/settings.json",
    ".codex/config.toml",
    ".codex/hooks.json",
    ".codex/agentos-local-rules.md",
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
    ".claude/hooks/aos_guard_enforcer.py",
    ".claude/rules/agentos-local-rules.md",
    ".agents/skills/dynamic-workflow/SKILL.md",
    ".agents/skills/dynamic-workflow/agents/openai.yaml",
    ".agents/skills/evidence-claim-review/SKILL.md",
    ".agents/skills/intent-contract-review/SKILL.md",
    ".agents/skills/lifecycle-execution/SKILL.md",
    ".agents/skills/memory-wiki-routing/SKILL.md",
    ".agents/skills/reasoning-causality-review/SKILL.md",
    ".agents/skills/route-promotion-review/SKILL.md",
    ".claude/skills/dynamic-workflow/SKILL.md",
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
        r"Start every user-facing answer with",
        r"agent-os/boot\.md",
        r"agent-os/router\.md",
        r"adapters/projections",
        r"\.codex/agentos-local-rules\.md",
    ],
    "CLAUDE.md": [
        r"Claude Code adapter",
        r"agent-os/boot\.md",
        r"\.claude/skills/",
        r"agentos-local-rules\.md",
    ],
    "agent-os/boot.md": [
        r"Minimum Startup",
        r"agent-os/router\.md",
        r"agent-os/state/current\.md",
        r"Manual until wired",
        r"structure only",
    ],
    "agent-os/router.md": [
        r"active user object",
        r"Skill Routing",
        r"\.agents/skills/",
        r"\.claude/skills/",
        r"kernel:.*adapter:.*extension:.*verification:.*undecided:",
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
        r"Full Task Contract",
        r"forbidden_substitutions",
        r"evidence_standard",
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
        r"intake -> reasoning_base_check -> intent_gate -> task_contract -> execution_plan -> route_checkpoints -> verification -> evidence_to_claim_gate -> per_turn_audit -> final_response -> handoff_or_memory",
        r"Context Compression Resume State",
    ],
    "agent-os/review/per-turn-audit-gate.md": [
        r"Every turn",
        r"agent-os/state/audit-log\.md",
        r"missing report means the audit was not done",
        r"aos_stop_gate\.py",
    ],
    ".claude/settings.json": [
        r"SessionStart",
        r"UserPromptSubmit",
        r"\"Stop\"",
        r"aos_stop_gate\.py",
        r"aos_guard_enforcer\.py",
        r"aos_kernel_lint\.py",
    ],
    ".codex/config.toml": [
        r"developer_instructions",
        r"\.codex/agentos-local-rules\.md",
        r"Do not use \.codex/rules/",
    ],
    ".codex/agentos-local-rules.md": [
        r"AgentOS Local Rules Card for Codex",
        r"Start every user-facing answer with",
        r"agent-os/state/audit-log\.md",
        r"\.codex/rules/.*command execution policy",
    ],
    ".codex/hooks/aos_session_start.py": [
        r"STATIC_RULE_CARD",
        r"Codex Static Rules Card",
        r"agentos-local-rules",
    ],
    ".claude/rules/agentos-local-rules.md": [
        r"agent-os/state/audit-log\.md",
        r"anti-sycophancy-review",
        r"Source order",
        r"zero-context reader",
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
    "agent-os/state/audit-log.md": [
        r"Per-Turn Audit Log",
    ],
    "agent-os/workflows/dynamic-workflow.md": [
        r"Dynamic Workflow",
        r"Three-Agent Squad",
        r"Worker Monitor / Reaper",
        r"worker outputs are support artifacts",
    ],
    "agent-os/state/current.md": [
        r"next_safe_action",
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


def read(path: str) -> str:
    return (ROOT / path).read_text(encoding="utf-8")


def fail(message: str, failures: list[str]) -> None:
    failures.append(message)
    print(f"FAIL {message}")


def main() -> int:
    failures: list[str] = []

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

    if failures:
        print(f"AgentOS structural lint FAIL: {len(failures)} issue(s)")
        return 1

    print("AgentOS structural lint PASS")
    print("Scope: structure only; behavioral success is not proven by this check.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
