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

check "ENTRY-RKP" "AGENTS.md" "## Route Keeper / Promotion Gate"
check "ENTRY-MAIN-THREAD" "AGENTS.md" "main thread is always the Route Keeper"
check "ENTRY-ACTIVE-OBJECT" "AGENTS.md" "active_user_object"
check "ENTRY-CLASSIFICATION" "AGENTS.md" "mainline.*support.*blocker.*side_route.*discard|mainline.*blocker.*support.*side_route.*discard"
check "ENTRY-ROUTE-CHECKPOINT" "AGENTS.md" "Route Checkpoint"
check "ENTRY-DRIFT-TRIGGERS" "AGENTS.md" "runtime, FRUS, source gate, subagent report, test pass, and report done"
check "ENTRY-RKP-TEMPLATE-REF" "AGENTS.md" "outputs/route-keeper-promotion-gate-v1-templates-2026-07-01.md"
check "ENTRY-RKP-REGRESSION-REF" "AGENTS.md" "outputs/route-keeper-promotion-gate-v1-regression-report-2026-07-01.md"

check "TPL-ROUTE-CHECKPOINT" "outputs/route-keeper-promotion-gate-v1-templates-2026-07-01.md" "route_checkpoint:"
check "TPL-PROMOTION-GATE" "outputs/route-keeper-promotion-gate-v1-templates-2026-07-01.md" "promotion_gate:"
check "TPL-ARTIFACT" "outputs/route-keeper-promotion-gate-v1-templates-2026-07-01.md" "artifact_or_branch:"
check "TPL-SOURCE" "outputs/route-keeper-promotion-gate-v1-templates-2026-07-01.md" "source:"
check "TPL-CLAIM-TYPE" "outputs/route-keeper-promotion-gate-v1-templates-2026-07-01.md" "claim_type:"
check "TPL-RELATION" "outputs/route-keeper-promotion-gate-v1-templates-2026-07-01.md" "relation_to_task_contract:"
check "TPL-PROMOTION-CLASS" "outputs/route-keeper-promotion-gate-v1-templates-2026-07-01.md" "promotion_class:"
check "TPL-EVIDENCE" "outputs/route-keeper-promotion-gate-v1-templates-2026-07-01.md" "evidence_checked:"
check "TPL-USER-IMPACT" "outputs/route-keeper-promotion-gate-v1-templates-2026-07-01.md" "user_visible_impact:"
check "TPL-RETURN" "outputs/route-keeper-promotion-gate-v1-templates-2026-07-01.md" "return_to_mainline_rule:"
check "TPL-CLASSES" "outputs/route-keeper-promotion-gate-v1-templates-2026-07-01.md" "mainline \\| support \\| blocker \\| side_route \\| discard"
check "TPL-RUNTIME" "outputs/route-keeper-promotion-gate-v1-templates-2026-07-01.md" "runtime:"
check "TPL-FRUS" "outputs/route-keeper-promotion-gate-v1-templates-2026-07-01.md" "FRUS:"
check "TPL-SOURCE-GATE" "outputs/route-keeper-promotion-gate-v1-templates-2026-07-01.md" "source gate:"
check "TPL-SUBAGENT" "outputs/route-keeper-promotion-gate-v1-templates-2026-07-01.md" "subagent report:"
check "TPL-TEST-PASS" "outputs/route-keeper-promotion-gate-v1-templates-2026-07-01.md" "test pass:"
check "TPL-REPORT-DONE" "outputs/route-keeper-promotion-gate-v1-templates-2026-07-01.md" "report done:"

for id in RKP-01 RKP-02 RKP-03 RKP-04 RKP-05 RKP-06 RKP-07; do
  check "$id-heading" "outputs/route-keeper-promotion-gate-v1-regression-report-2026-07-01.md" "### $id:"
  check "$id-verdict" "outputs/route-keeper-promotion-gate-v1-regression-report-2026-07-01.md" "$id PASS"
done
