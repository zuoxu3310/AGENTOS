#!/usr/bin/env bash
# run_codex_sandboxed.sh — run one GPT panelist via `codex exec`, SANDBOXED.
#
# AgentOS adaptation. The vendor runner (vendor/fusion-fable/skills/fusion/scripts/run_codex.sh)
# launches codex with --dangerously-bypass-approvals-and-sandbox and copies the whole workdir so
# the panelist gets full local tool access. For fusion Q&A panelists that power is unnecessary,
# and running an unsandboxed agent needs explicit user approval. This runner keeps codex in
# its default sandbox, works in an empty scratch dir, and only enables web search.
#
# Usage:
#   run_codex_sandboxed.sh <prompt_file> <output_file> [reasoning_effort]   # effort default: low
#
# Exit codes (vendor-compatible): 0 ok, 124 timeout, 1 failed/empty, 2 bad prompt file.

set -uo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../../../.." && pwd)"
. "$PROJECT_ROOT/vendor/fusion-fable/skills/fusion/scripts/_fusion_lib.sh"

prompt_file="${1:?usage: run_codex_sandboxed.sh <prompt_file> <output_file> [effort]}"
output_file="${2:?usage: run_codex_sandboxed.sh <prompt_file> <output_file> [effort]}"
effort="${3:-low}"

if ! have codex; then
  echo "[run_codex_sandboxed.sh] codex CLI not installed — skip this panelist." >&2
  exit 127
fi
if [ ! -s "$prompt_file" ]; then
  echo "[run_codex_sandboxed.sh] prompt file is missing or empty: $prompt_file" >&2
  exit 2
fi
mkdir -p "$(dirname "$output_file")"
rm -f "$output_file"

scratch="$(mktemp -d "${TMPDIR:-/tmp}/fusion-codex-sbx.XXXXXX")"
trap 'rm -rf "$scratch"' EXIT

_run_with_timeout "$FUSION_TIMEOUT" codex exec \
  --skip-git-repo-check \
  --ephemeral \
  --cd "$scratch" \
  -c tools.web_search=true \
  -c "model_reasoning_effort=$effort" \
  -o "$output_file" \
  - < "$prompt_file" \
  > "$scratch/stream.log" 2>&1
status=$?

if [ "$status" -eq 124 ]; then
  echo "[run_codex_sandboxed.sh] codex timed out after ${FUSION_TIMEOUT}s; tail of log:" >&2
  tail -20 "$scratch/stream.log" >&2
  exit 124
fi
if [ "$status" -ne 0 ] || [ ! -s "$output_file" ]; then
  echo "[run_codex_sandboxed.sh] codex exited $status; tail of log:" >&2
  tail -20 "$scratch/stream.log" >&2
  exit 1
fi
echo "[run_codex_sandboxed.sh] ok -> $output_file"
