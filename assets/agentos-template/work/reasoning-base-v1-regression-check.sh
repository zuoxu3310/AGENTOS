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

check "RB-01" "AGENTS.md" "temporal order.*counterfactual|counterfactual.*temporal order"
check "RB-02" "AGENTS.md" "root mechanism, trigger, amplifier, mediator, confounder, symptom, protective factor, irrelevant, unknown"
check "RB-03" "AGENTS.md" "Support artifacts cannot count as user-goal completion"
check "RB-04" "AGENTS.md" "active object, purpose, invariants"
check "RB-05" "AGENTS.md" "Treat user-proposed methods, tools, workflows, and subagents as candidate interventions"
check "RB-06" "AGENTS.md" "best current explanation.*rival explanations|rival explanations.*best current explanation"
check "RB-07" "AGENTS.md" "supports.*weakens.*neutral.*proves|proves.*supports.*weakens.*neutral"

check "TPL-CLAIM" "outputs/reasoning-base-v1-templates-2026-07-01.md" "type: observation \\| deductive \\| evidential \\| abductive \\| causal \\| root_cause \\| recommendation"
check "TPL-ROLE" "outputs/reasoning-base-v1-templates-2026-07-01.md" "causal_roles:"
check "TPL-CHECKLIST" "outputs/reasoning-base-v1-templates-2026-07-01.md" "Fast Mode"
check "TPL-FULL" "outputs/reasoning-base-v1-templates-2026-07-01.md" "Full Reasoning Mode"

