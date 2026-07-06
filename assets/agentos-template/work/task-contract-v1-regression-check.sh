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

check "ENTRY-TC" "AGENTS.md" "## Task Contract"
check "ENTRY-NON-SMALL" "AGENTS.md" "non-small tasks"
check "ENTRY-TC-FIELDS" "AGENTS.md" "active user object, user-visible success, requested layer, deliverable, non-substitutable invariants, forbidden substitutions, evidence standard, autonomy, ask-required conditions, and handoff minimum state"
check "ENTRY-SUPPORT-ARTIFACTS" "AGENTS.md" "support artifacts unless the contract explicitly makes them the deliverable"
check "ENTRY-COMPLETION" "AGENTS.md" "Completion requires evidence that the active user object changed"
check "ENTRY-TC-TEMPLATE-REF" "AGENTS.md" "outputs/task-contract-v1-templates-2026-07-01.md"
check "ENTRY-TC-REGRESSION-REF" "AGENTS.md" "outputs/task-contract-v1-regression-report-2026-07-01.md"

check "TPL-TASK-CONTRACT" "outputs/task-contract-v1-templates-2026-07-01.md" "task_contract:"
check "TPL-ACTIVE-OBJECT" "outputs/task-contract-v1-templates-2026-07-01.md" "active_user_object:"
check "TPL-USER-SUCCESS" "outputs/task-contract-v1-templates-2026-07-01.md" "user_visible_success:"
check "TPL-REQUESTED-LAYER" "outputs/task-contract-v1-templates-2026-07-01.md" "requested_layer:"
check "TPL-DELIVERABLE" "outputs/task-contract-v1-templates-2026-07-01.md" "deliverable:"
check "TPL-INVARIANTS" "outputs/task-contract-v1-templates-2026-07-01.md" "non_substitutable_invariants:"
check "TPL-FORBIDDEN" "outputs/task-contract-v1-templates-2026-07-01.md" "forbidden_substitutions:"
check "TPL-EVIDENCE" "outputs/task-contract-v1-templates-2026-07-01.md" "evidence_standard:"
check "TPL-AUTONOMY" "outputs/task-contract-v1-templates-2026-07-01.md" "autonomy:"
check "TPL-ASK" "outputs/task-contract-v1-templates-2026-07-01.md" "ask_required_when:"
check "TPL-HANDOFF" "outputs/task-contract-v1-templates-2026-07-01.md" "handoff_min_state:"
check "TPL-COMPLETION-GATE" "outputs/task-contract-v1-templates-2026-07-01.md" "completion_gate:"
check "TPL-COMPLETION-STATUS" "outputs/task-contract-v1-templates-2026-07-01.md" "complete \\| partial \\| support_only \\| blocked \\| not_started"

for id in TC-01 TC-02 TC-03 TC-04 TC-05 TC-06 TC-07; do
  check "$id-heading" "outputs/task-contract-v1-regression-report-2026-07-01.md" "### $id:"
  check "$id-verdict" "outputs/task-contract-v1-regression-report-2026-07-01.md" "$id PASS"
done

