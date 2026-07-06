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

test -d agent-os
printf 'AOM-DIR PASS\n'

python3 agent-os/tools/aos-lint.py

check "AOM-ENTRY-BOOT" "AGENTS.md" "agent-os/boot.md"
check "AOM-ENTRY-ROUTER" "AGENTS.md" "agent-os/router.md"
check "AOM-ENTRY-LINT" "AGENTS.md" "python3 agent-os/tools/aos-lint.py"
check "AOM-ENTRY-ADAPTER" "AGENTS.md" "adapter excerpts"
check "AOM-BOOT-MINIMUM" "agent-os/boot.md" "Minimum Startup"
check "AOM-BOOT-STATE" "agent-os/boot.md" "agent-os/state/current.md"
check "AOM-ROUTER-SKILLS" "agent-os/router.md" "Skill Routing"
check "AOM-ROUTER-CLASS" "agent-os/router.md" "kernel:|adapter:|extension:|verification:|undecided:"
check "AOM-REASONING" "agent-os/review/reasoning-base.md" "Full Reasoning Mode"
check "AOM-INTENT" "agent-os/review/intent-causal-gate.md" "Proxy Risk Gate"
check "AOM-CONTRACT" "agent-os/review/task-contract.md" "Full Task Contract"
check "AOM-ROUTE" "agent-os/review/route-keeper-promotion-gate.md" "Promotion Gate"
check "AOM-EVIDENCE" "agent-os/review/evidence-to-claim-gate.md" "Report Gate is the reporting-facing application"
check "AOM-COMPLETION" "agent-os/review/completion-gate.md" "Completion Template"
check "AOM-LIFECYCLE" "agent-os/workflows/agent-execution-lifecycle.md" "intake.*reasoning_base_check.*intent_gate.*task_contract.*execution_plan.*route_checkpoints.*verification.*evidence_to_claim_gate.*final_response.*handoff_or_memory"
check "AOM-STATE" "agent-os/state/current.md" "Agent OS Kernel Migration v1"
check "AOM-HANDOFF" "agent-os/handoffs/README.md" "handoff:"
check "AOM-SKILLS" "agent-os/skills/README.md" "Native wrappers"

