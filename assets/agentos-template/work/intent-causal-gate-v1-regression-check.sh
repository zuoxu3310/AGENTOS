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

check "ENTRY-ICG" "AGENTS.md" "## Intent-Causal Gate"
check "ENTRY-EVIDENCE-NOT-SPEC" "AGENTS.md" "highest-priority evidence, not as a complete specification"
check "ENTRY-CLASSIFY" "AGENTS.md" "goal, means, constraint, evidence, emotion, or ambiguity"
check "ENTRY-ASK" "AGENTS.md" "0 ask, 1 ask, short grill, or full clarification"
check "ENTRY-PROXY" "AGENTS.md" "Proxy Risk Gate"
check "ENTRY-TEMPLATE-REF" "AGENTS.md" "outputs/intent-causal-gate-v1-templates-2026-07-01.md"
check "ENTRY-REGRESSION-REF" "AGENTS.md" "outputs/intent-causal-gate-v1-regression-report-2026-07-01.md"

check "TPL-INTENT" "outputs/intent-causal-gate-v1-templates-2026-07-01.md" "intent_gate:"
check "TPL-GOAL-MEANS" "outputs/intent-causal-gate-v1-templates-2026-07-01.md" "goal:|means:"
check "TPL-ASK-GATE" "outputs/intent-causal-gate-v1-templates-2026-07-01.md" "ask_gate:"
check "TPL-ASK-LEVELS" "outputs/intent-causal-gate-v1-templates-2026-07-01.md" "0_ask \\| 1_ask \\| short_grill \\| full_clarification"
check "TPL-PROXY" "outputs/intent-causal-gate-v1-templates-2026-07-01.md" "proxy_risk_gate:"
check "TPL-PROMOTION" "outputs/intent-causal-gate-v1-templates-2026-07-01.md" "mainline \\| support \\| blocker \\| side_route \\| discard"

for id in ICG-01 ICG-02 ICG-03 ICG-04 ICG-05 ICG-06 ICG-07; do
  check "$id-heading" "outputs/intent-causal-gate-v1-regression-report-2026-07-01.md" "### $id:"
  check "$id-verdict" "outputs/intent-causal-gate-v1-regression-report-2026-07-01.md" "$id PASS"
done
