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

check "ENTRY-ECG" "AGENTS.md" "## Evidence-to-Claim Gate"
check "ENTRY-REPORT-GATE" "AGENTS.md" "Report Gate is the reporting-facing application of Evidence-to-Claim Gate"
check "ENTRY-USER-FACING" "AGENTS.md" "user-facing claim"
check "ENTRY-KEY-CLAIMS" "AGENTS.md" "completion, causal, root-cause, recommendation, handoff, and memory"
check "ENTRY-QUESTION-1" "AGENTS.md" "What type of claim is this"
check "ENTRY-QUESTION-2" "AGENTS.md" "What evidence allows it"
check "ENTRY-QUESTION-3" "AGENTS.md" "How strong may the wording be"
check "ENTRY-LADDER" "AGENTS.md" "observed, supported, strongly_supported, best_current_explanation, proven, causal, root_cause, complete"
check "ENTRY-ECG-TEMPLATE-REF" "AGENTS.md" "outputs/evidence-to-claim-gate-v1-templates-2026-07-01.md"
check "ENTRY-ECG-REGRESSION-REF" "AGENTS.md" "outputs/evidence-to-claim-gate-v1-regression-report-2026-07-01.md"

check "TPL-CLAIM-GATE" "outputs/evidence-to-claim-gate-v1-templates-2026-07-01.md" "evidence_to_claim_gate:"
check "TPL-REPORT-GATE-MAPPING" "outputs/evidence-to-claim-gate-v1-templates-2026-07-01.md" "Report Gate is the reporting-facing application of Evidence-to-Claim Gate"
check "TPL-CLAIM" "outputs/evidence-to-claim-gate-v1-templates-2026-07-01.md" "claim:"
check "TPL-CLAIM-TYPE" "outputs/evidence-to-claim-gate-v1-templates-2026-07-01.md" "claim_type:"
check "TPL-EVIDENCE-SOURCE" "outputs/evidence-to-claim-gate-v1-templates-2026-07-01.md" "evidence_source:"
check "TPL-EVIDENCE-STRENGTH" "outputs/evidence-to-claim-gate-v1-templates-2026-07-01.md" "evidence_strength:"
check "TPL-ALLOWED-WORDING" "outputs/evidence-to-claim-gate-v1-templates-2026-07-01.md" "allowed_wording:"
check "TPL-FORBIDDEN-WORDING" "outputs/evidence-to-claim-gate-v1-templates-2026-07-01.md" "forbidden_wording:"
check "TPL-UNCERTAINTY" "outputs/evidence-to-claim-gate-v1-templates-2026-07-01.md" "uncertainty:"
check "TPL-USER-CONSEQUENCE" "outputs/evidence-to-claim-gate-v1-templates-2026-07-01.md" "user_visible_consequence:"
check "TPL-LADDER" "outputs/evidence-to-claim-gate-v1-templates-2026-07-01.md" "observed \\| supported \\| strongly_supported \\| best_current_explanation \\| proven \\| causal \\| root_cause \\| complete"
check "TPL-TEST-PASS" "outputs/evidence-to-claim-gate-v1-templates-2026-07-01.md" "test pass:"
check "TPL-SUBAGENT" "outputs/evidence-to-claim-gate-v1-templates-2026-07-01.md" "subagent report:"
check "TPL-CORRELATION" "outputs/evidence-to-claim-gate-v1-templates-2026-07-01.md" "correlation:"
check "TPL-REPORT-WRITTEN" "outputs/evidence-to-claim-gate-v1-templates-2026-07-01.md" "report written:"
check "TPL-SOURCE-FOUND" "outputs/evidence-to-claim-gate-v1-templates-2026-07-01.md" "source found:"
check "TPL-PARTIAL-EVIDENCE" "outputs/evidence-to-claim-gate-v1-templates-2026-07-01.md" "partial evidence:"

for id in ECG-01 ECG-02 ECG-03 ECG-04 ECG-05 ECG-06 ECG-07; do
  check "$id-heading" "outputs/evidence-to-claim-gate-v1-regression-report-2026-07-01.md" "### $id:"
  check "$id-verdict" "outputs/evidence-to-claim-gate-v1-regression-report-2026-07-01.md" "$id PASS"
done
