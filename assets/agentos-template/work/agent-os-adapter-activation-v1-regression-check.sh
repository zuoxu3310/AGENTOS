#!/usr/bin/env bash
set -euo pipefail

check() {
  local id="$1"
  local file="$2"
  local pattern="$3"
  if rg -q -- "$pattern" "$file"; then
    printf '%s PASS\n' "$id"
  else
    printf '%s FAIL: missing pattern %s in %s\n' "$id" "$pattern" "$file"
    return 1
  fi
}

check_file() {
  local id="$1"
  local file="$2"
  if test -f "$file"; then
    printf '%s PASS\n' "$id"
  else
    printf '%s FAIL: missing file %s\n' "$id" "$file"
    return 1
  fi
}

check_lines_under() {
  local id="$1"
  local file="$2"
  local max_lines="$3"
  local lines
  lines="$(wc -l < "$file" | tr -d ' ')"
  if [ "$lines" -le "$max_lines" ]; then
    printf '%s PASS (%s lines)\n' "$id" "$lines"
  else
    printf '%s FAIL: %s has %s lines, max %s\n' "$id" "$file" "$lines" "$max_lines"
    return 1
  fi
}

check_absent() {
  local id="$1"
  local file="$2"
  local pattern="$3"
  if rg -q -- "$pattern" "$file"; then
    printf '%s FAIL: unexpected pattern %s in %s\n' "$id" "$pattern" "$file"
    return 1
  else
    printf '%s PASS\n' "$id"
  fi
}

check_frontmatter_only_name_description() {
  local id="$1"
  local file="$2"
  local unexpected
  unexpected="$(sed -n '/^---$/,/^---$/p' "$file" | sed '1d;$d' | awk -F: '/^[A-Za-z0-9_-]+:/ { if ($1 != "name" && $1 != "description") print $1 }')"
  if [ -z "$unexpected" ]; then
    printf '%s PASS\n' "$id"
  else
    printf '%s FAIL: unexpected frontmatter keys in %s: %s\n' "$id" "$file" "$unexpected"
    return 1
  fi
}

# Optional: point SKILL_CREATOR_VALIDATOR at a skill-creator quick_validate.py to
# enable these checks. When it is unset or missing, the checks SKIP (they are not
# part of the AgentOS kernel and are environment-specific).
check_codex_quick_validate() {
  local id="$1"
  local skill_dir="$2"
  local validator="${SKILL_CREATOR_VALIDATOR:-}"
  if [ -z "$validator" ] || [ ! -f "$validator" ]; then
    printf '%s SKIP (set SKILL_CREATOR_VALIDATOR to enable)\n' "$id"
    return 0
  fi
  python3 "$validator" "$skill_dir" >/dev/null
  printf '%s PASS\n' "$id"
}

check_claude_quick_validate() {
  local id="$1"
  local skill_dir="$2"
  local validator="${SKILL_CREATOR_VALIDATOR:-}"
  if [ -z "$validator" ] || [ ! -f "$validator" ]; then
    printf '%s SKIP (set SKILL_CREATOR_VALIDATOR to enable)\n' "$id"
    return 0
  fi
  python3 "$validator" "$skill_dir" >/dev/null
  printf '%s PASS\n' "$id"
}

check_file "AAA-AGENTS" "AGENTS.md"
check_file "AAA-CLAUDE" "CLAUDE.md"
check "AAA-AGENTS-BOOT" "AGENTS.md" "agent-os/boot.md"
check "AAA-AGENTS-ROUTER" "AGENTS.md" "agent-os/router.md"
check "AAA-AGENTS-THIN" "AGENTS.md" "thin adapter"
check "AAA-AGENTS-CODEX-SHAPE" "AGENTS.md" "Codex .*agents/openai.yaml"
check "AAA-AGENTS-CLAUDE-SHAPE" "AGENTS.md" "Claude .*what.*trigger"
check "AAA-CLAUDE-BOOT" "CLAUDE.md" "agent-os/boot.md"
check "AAA-CLAUDE-ROUTER" "CLAUDE.md" "agent-os/router.md"
check "AAA-CLAUDE-THIN" "CLAUDE.md" "adapter/projection"
check "AAA-CLAUDE-NO-OPENAI-YAML" "CLAUDE.md" "do not include Codex .*agents/openai.yaml"
check_lines_under "AAA-AGENTS-LINES" "AGENTS.md" 160
check_lines_under "AAA-CLAUDE-LINES" "CLAUDE.md" 40

skills=(
  reasoning-causality-review
  intent-contract-review
  route-promotion-review
  evidence-claim-review
  lifecycle-execution
)

for skill in "${skills[@]}"; do
  file=".agents/skills/$skill/SKILL.md"
  yaml_file=".agents/skills/$skill/agents/openai.yaml"
  prefix="AAA-agents-$skill"
  check_file "$prefix-file" "$file"
  check "$prefix-frontmatter-name" "$file" "name: $skill"
  check "$prefix-description-codex" "$file" "description: .*\\. Use when"
  check_frontmatter_only_name_description "$prefix-frontmatter-only-name-description" "$file"
  check "$prefix-thin" "$file" "Thin Codex adapter"
  check "$prefix-boot" "$file" "agent-os/boot.md"
  check "$prefix-router" "$file" "agent-os/router.md"
  check "$prefix-output" "$file" "Output Shape"
  check "$prefix-no-copy" "$file" "Do not copy kernel text"
  check_lines_under "$prefix-lines" "$file" 50
  check_file "$prefix-openai-yaml" "$yaml_file"
  check "$prefix-openai-interface" "$yaml_file" "^interface:"
  check "$prefix-openai-display" "$yaml_file" "display_name: \""
  check "$prefix-openai-short" "$yaml_file" "short_description: \""
  check "$prefix-openai-prompt" "$yaml_file" "default_prompt: \"Use [$]$skill"
  check_codex_quick_validate "$prefix-quick-validate" ".agents/skills/$skill"
done

for skill in "${skills[@]}"; do
  file=".claude/skills/$skill/SKILL.md"
  yaml_file=".claude/skills/$skill/agents/openai.yaml"
  prefix="AAA-claude-$skill"
  check_file "$prefix-file" "$file"
  check "$prefix-frontmatter-name" "$file" "name: $skill"
  check "$prefix-description-claude-what-trigger" "$file" "description: .*\\. Use when"
  check_absent "$prefix-description-no-workflow-summary" "$file" "^description: .*agent-os/"
  check_frontmatter_only_name_description "$prefix-frontmatter-only-name-description" "$file"
  check "$prefix-thin" "$file" "Thin Claude adapter"
  check "$prefix-boot" "$file" "agent-os/boot.md"
  check "$prefix-router" "$file" "agent-os/router.md"
  check "$prefix-output" "$file" "Output Shape"
  check "$prefix-no-copy" "$file" "Do not copy kernel text"
  check_lines_under "$prefix-lines" "$file" 50
  if test -f "$yaml_file"; then
    printf '%s-no-openai-yaml FAIL: Claude skill must not include %s\n' "$prefix" "$yaml_file"
    exit 1
  else
    printf '%s-no-openai-yaml PASS\n' "$prefix"
  fi
  check_claude_quick_validate "$prefix-quick-validate" ".claude/skills/$skill"
done

check "AAA-RCR-SOURCE" ".agents/skills/reasoning-causality-review/SKILL.md" "agent-os/review/reasoning-base.md"
check "AAA-ICR-INTENT" ".agents/skills/intent-contract-review/SKILL.md" "agent-os/review/intent-causal-gate.md"
check "AAA-ICR-CONTRACT" ".agents/skills/intent-contract-review/SKILL.md" "agent-os/review/task-contract.md"
check "AAA-RPR-SOURCE" ".agents/skills/route-promotion-review/SKILL.md" "agent-os/review/route-keeper-promotion-gate.md"
check "AAA-ECR-EVIDENCE" ".agents/skills/evidence-claim-review/SKILL.md" "agent-os/review/evidence-to-claim-gate.md"
check "AAA-ECR-COMPLETION" ".agents/skills/evidence-claim-review/SKILL.md" "agent-os/review/completion-gate.md"
check "AAA-LC-SOURCE" ".agents/skills/lifecycle-execution/SKILL.md" "agent-os/workflows/agent-execution-lifecycle.md"
check "AAA-CLAUDE-RCR-SOURCE" ".claude/skills/reasoning-causality-review/SKILL.md" "agent-os/review/reasoning-base.md"
check "AAA-CLAUDE-ICR-INTENT" ".claude/skills/intent-contract-review/SKILL.md" "agent-os/review/intent-causal-gate.md"
check "AAA-CLAUDE-ICR-CONTRACT" ".claude/skills/intent-contract-review/SKILL.md" "agent-os/review/task-contract.md"
check "AAA-CLAUDE-RPR-SOURCE" ".claude/skills/route-promotion-review/SKILL.md" "agent-os/review/route-keeper-promotion-gate.md"
check "AAA-CLAUDE-ECR-EVIDENCE" ".claude/skills/evidence-claim-review/SKILL.md" "agent-os/review/evidence-to-claim-gate.md"
check "AAA-CLAUDE-ECR-COMPLETION" ".claude/skills/evidence-claim-review/SKILL.md" "agent-os/review/completion-gate.md"
check "AAA-CLAUDE-LC-SOURCE" ".claude/skills/lifecycle-execution/SKILL.md" "agent-os/workflows/agent-execution-lifecycle.md"

for target in \
  agent-os/review/reasoning-base.md \
  agent-os/review/intent-causal-gate.md \
  agent-os/review/task-contract.md \
  agent-os/review/route-keeper-promotion-gate.md \
  agent-os/review/evidence-to-claim-gate.md \
  agent-os/review/completion-gate.md \
  agent-os/workflows/agent-execution-lifecycle.md
do
  check_file "AAA-TARGET-$target" "$target"
done

if rg -q -- "Claim Type Template|Full Task Contract|Claim Strength Ladder|Full Lifecycle|Causal Roles" .agents/skills .claude/skills; then
  printf 'AAA-WRAPPER-NOT-THIN FAIL: wrapper appears to copy kernel body\n'
  exit 1
else
  printf 'AAA-WRAPPER-NOT-THIN PASS\n'
fi
