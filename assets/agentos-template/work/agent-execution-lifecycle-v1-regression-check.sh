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

check "ENTRY-AEL" "AGENTS.md" "## Agent Execution Lifecycle"
check "ENTRY-NON-SMALL" "AGENTS.md" "Non-small tasks must follow Agent Execution Lifecycle"
check "ENTRY-SEQUENCE" "AGENTS.md" "intake.*reasoning_base_check.*intent_gate.*task_contract.*execution_plan.*route_checkpoints.*verification.*evidence_to_claim_gate.*final_response.*handoff_or_memory"
check "ENTRY-INTENT-FALLBACK" "AGENTS.md" "Intent unclear.*Intent-Causal Gate"
check "ENTRY-CONTRACT-FALLBACK" "AGENTS.md" "Contract invalid.*Task Contract"
check "ENTRY-ROUTE-FALLBACK" "AGENTS.md" "Branch hijack.*Route Keeper"
check "ENTRY-EVIDENCE-FALLBACK" "AGENTS.md" "Evidence insufficient.*Verification.*downgrade"
check "ENTRY-COMPLETION-FALLBACK" "AGENTS.md" "Completion evidence insufficient.*Do not final"
check "ENTRY-CONTEXT-STATE" "AGENTS.md" "active_user_object, contract, route, and evidence_state"
check "ENTRY-AEL-TEMPLATE-REF" "AGENTS.md" "outputs/agent-execution-lifecycle-v1-templates-2026-07-01.md"
check "ENTRY-AEL-REGRESSION-REF" "AGENTS.md" "outputs/agent-execution-lifecycle-v1-regression-report-2026-07-01.md"

check "TPL-LIFECYCLE" "outputs/agent-execution-lifecycle-v1-templates-2026-07-01.md" "agent_execution_lifecycle:"
check "TPL-INTAKE" "outputs/agent-execution-lifecycle-v1-templates-2026-07-01.md" "intake:"
check "TPL-RB" "outputs/agent-execution-lifecycle-v1-templates-2026-07-01.md" "reasoning_base_check:"
check "TPL-INTENT" "outputs/agent-execution-lifecycle-v1-templates-2026-07-01.md" "intent_gate:"
check "TPL-CONTRACT" "outputs/agent-execution-lifecycle-v1-templates-2026-07-01.md" "task_contract:"
check "TPL-PLAN" "outputs/agent-execution-lifecycle-v1-templates-2026-07-01.md" "execution_plan:"
check "TPL-ROUTE" "outputs/agent-execution-lifecycle-v1-templates-2026-07-01.md" "route_checkpoints:"
check "TPL-VERIFICATION" "outputs/agent-execution-lifecycle-v1-templates-2026-07-01.md" "verification:"
check "TPL-ECG" "outputs/agent-execution-lifecycle-v1-templates-2026-07-01.md" "evidence_to_claim_gate:"
check "TPL-FINAL" "outputs/agent-execution-lifecycle-v1-templates-2026-07-01.md" "final_response:"
check "TPL-HANDOFF" "outputs/agent-execution-lifecycle-v1-templates-2026-07-01.md" "handoff_or_memory:"
check "TPL-FALLBACKS" "outputs/agent-execution-lifecycle-v1-templates-2026-07-01.md" "Failure Fallbacks"
check "TPL-FORBIDDEN" "outputs/agent-execution-lifecycle-v1-templates-2026-07-01.md" "Forbidden Shortcuts"
check "TPL-CONTEXT" "outputs/agent-execution-lifecycle-v1-templates-2026-07-01.md" "context_compression_resume_state:"
check "TPL-CONTEXT-FIELDS" "outputs/agent-execution-lifecycle-v1-templates-2026-07-01.md" "active_user_object:|evidence_state:"

for id in AEL-01 AEL-02 AEL-03 AEL-04 AEL-05 AEL-06; do
  check "$id-heading" "outputs/agent-execution-lifecycle-v1-regression-report-2026-07-01.md" "### $id:"
  check "$id-verdict" "outputs/agent-execution-lifecycle-v1-regression-report-2026-07-01.md" "$id PASS"
done
