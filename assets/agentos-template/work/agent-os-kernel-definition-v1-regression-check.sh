#!/usr/bin/env bash
set -euo pipefail

check() {
  local id="$1"
  local file="$2"
  local pattern="$3"
  if rg -q "$pattern" "$file"; then
    printf '%s PASS\n' "$id"
  else
    printf '%s FAIL: missing pattern %s in %s\n' "$id" "$pattern" "$file"
    return 1
  fi
}

must_file() {
  local id="$1"
  local file="$2"
  if test -f "$file"; then
    printf '%s PASS\n' "$id"
  else
    printf '%s FAIL: missing file %s\n' "$id" "$file"
    return 1
  fi
}

definition="outputs/agent-os-kernel-definition-v1-2026-07-01.md"
placement="outputs/agent-os-kernel-placement-map-v1-2026-07-01.md"
integration="outputs/agent-os-kernel-integration-plan-v1-2026-07-01.md"
report="outputs/agent-os-kernel-definition-v1-regression-report-2026-07-01.md"

check "ENTRY-AOK" "AGENTS.md" "## Agent OS Kernel"
check "ENTRY-CANONICAL" "AGENTS.md" "repo-local.*agent-os/.*canonical"
check "ENTRY-ADAPTERS" "AGENTS.md" "AGENTS.md.*CLAUDE.md.*\\.agents/skills/.*\\.claude/skills/"
check "ENTRY-NOT-KERNEL" "AGENTS.md" "adapters/projections, not the Agent OS kernel"
check "ENTRY-CLASSIFICATION" "AGENTS.md" "kernel.*adapter.*extension.*verification.*undecided"
check "ENTRY-SUPPORTING" "AGENTS.md" "Hooks, subagents, long-term memory, automation, and end-to-end pressure tests are supporting capabilities"
check "ENTRY-CODEX-HOOKS" "AGENTS.md" "Codex.*\\.codex/hooks\\.json.*Stop hook"
check "ENTRY-AOS-LINT" "AGENTS.md" "aos-lint.*structure only"
check "ENTRY-PLACEMENT-REF" "AGENTS.md" "outputs/agent-os-kernel-placement-map-v1-2026-07-01.md"
check "ENTRY-AOK-REGRESSION-REF" "AGENTS.md" "outputs/agent-os-kernel-definition-v1-regression-report-2026-07-01.md"

check "DEF-ESSENCE" "$definition" "Agent OS is a repo-local working-guide directory"
check "DEF-CANONICAL" "$definition" "canonical.*agent-os/"
check "DEF-ADAPTERS" "$definition" "AGENTS.md|CLAUDE.md|\\.agents/skills/|\\.claude/skills/|\\.codex/hooks\\.json"
check "DEF-SUPPORT" "$definition" "subagent protocol|long-term memory routing|automation platform|hooks|end-to-end pressure tests"
check "DEF-CODEX-HOOKS" "$definition" "Codex.*\\.codex/hooks\\.json.*Stop hook"
check "DEF-AOS-LINT" "$definition" "aos-lint.py.*structural health only|tools/aos-lint.py.*structural checks only"
check "DEF-CLASSIFICATION" "$definition" "kernel:|adapter:|extension:|verification:|undecided:"
check "DEF-SIX-GATES" "$definition" "Reasoning Base|Intent-Causal Gate|Task Contract|Route Keeper / Promotion Gate|Evidence-to-Claim Gate|Agent Execution Lifecycle"

check "MAP-BOOT" "$placement" "boot.md"
check "MAP-ROUTER" "$placement" "router.md"
check "MAP-REVIEW" "$placement" "review/"
check "MAP-SKILLS" "$placement" "skills/"
check "MAP-STATE" "$placement" "state/current.md|state/.*current.md"
check "MAP-HANDOFFS" "$placement" "handoffs/"
check "MAP-AOS-LINT" "$placement" "tools/.*aos-lint.py"
check "MAP-AGENTS-SKILLS" "$placement" "\\.agents/skills/"
check "MAP-CLAUDE-SKILLS" "$placement" "\\.claude/skills/"
check "MAP-CODEX-HOOKS" "$placement" "\\.codex/hooks\\.json|\\.codex/hooks/"
check "MAP-REPORT-GATE" "$placement" "Report Gate is not a separate reasoning layer"
check "MAP-COMPLETION" "$placement" "completion-gate.md"
check "MAP-INTEGRATION" "$placement" "Integration Plan"

check "INT-GOAL" "$integration" "six reasoning and execution layers"
check "INT-DIRECT" "$integration" "Direct Kernel Content"
check "INT-TEMPLATES" "$integration" "Template Material"
check "INT-WRAPPERS" "$integration" "Thin Native Skill Wrappers"
check "INT-ADAPTERS" "$integration" "Entry Adapters"
check "INT-DO-NOT" "$integration" "Do Not Move Into This Step"
check "INT-ORDER" "$integration" "Order Of Work"
check "INT-ACCEPTANCE" "$integration" "Acceptance Evidence"
check "INT-NO-SUBAGENT" "$integration" "subagent protocol"
check "INT-NO-MEMORY" "$integration" "long-term memory routing"
check "INT-NO-HOOK" "$integration" "hook wired integration"
check "INT-NO-E2E" "$integration" "end-to-end pressure test"
check "INT-TARGET-REVIEW" "$integration" "agent-os/review/reasoning-base.md"
check "INT-TARGET-WORKFLOW" "$integration" "agent-os/workflows/agent-execution-lifecycle.md"

must_file "CODEX-HOOKS-JSON" ".codex/hooks.json"
must_file "CODEX-HOOKS-COMMON" ".codex/hooks/aos_common.py"
must_file "CODEX-HOOKS-SESSION" ".codex/hooks/aos_session_start.py"
must_file "CODEX-HOOKS-PROMPT" ".codex/hooks/aos_prompt_baseline.py"
must_file "CODEX-HOOKS-STOP" ".codex/hooks/aos_stop_gate.py"
must_file "CODEX-HOOKS-LINT" ".codex/hooks/aos_kernel_lint.py"
must_file "CODEX-HOOKS-GUARD" ".codex/hooks/aos_guard_enforcer.py"

for id in AOK-01 AOK-02 AOK-03 AOK-04 AOK-05 AOK-06; do
  check "$id-heading" "$report" "### $id:"
  check "$id-verdict" "$report" "$id PASS"
done
