#!/usr/bin/env bash
# run_gemini_cli.sh — run one Gemini panelist via the official `gemini` CLI (one-shot mode).
#
# AgentOS adaptation. The vendor runner (vendor/fusion-fable/skills/fusion/scripts/run_gemini.sh)
# targets the `agy` / Antigravity CLI, which is not installed on this machine; this machine has
# the official Gemini CLI (`gemini`, one-shot positional prompt). All agy-specific PTY/transcript
# workarounds are irrelevant here, so this runner stays minimal: timeout + ANSI strip + anti-empty.
#
# Usage:
#   run_gemini_cli.sh <prompt_file> <output_file>
#
# Exit codes (kept compatible with the vendor contract so the orchestrator logic is unchanged):
#   0 = ok, 127 = gemini CLI not installed, 124 = timed out, 1 = empty answer.
#
# Env: FUSION_TIMEOUT (seconds, default 300 via vendor _fusion_lib.sh).

set -uo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../../../.." && pwd)"
. "$PROJECT_ROOT/vendor/fusion-fable/skills/fusion/scripts/_fusion_lib.sh"

prompt_file="${1:?usage: run_gemini_cli.sh <prompt_file> <output_file>}"
output_file="${2:?usage: run_gemini_cli.sh <prompt_file> <output_file>}"

if ! have gemini; then
  echo "[run_gemini_cli.sh] gemini CLI not installed — skip this panelist." >&2
  exit 127
fi
if [ ! -s "$prompt_file" ]; then
  echo "[run_gemini_cli.sh] prompt file is missing or empty: $prompt_file" >&2
  exit 2
fi

scratch="$(mktemp -d "${TMPDIR:-/tmp}/fusion-gemini-cli.XXXXXX")"
trap 'rm -rf "$scratch"' EXIT

_run_with_timeout "$FUSION_TIMEOUT" gemini "$(cat "$prompt_file")" < /dev/null \
  2> "$scratch/stderr.log" \
  | sed -e 's/\x1b\[[0-9;]*m//g' \
  | LC_ALL=C tr -d '\000-\010\013-\037\177' > "$output_file"
status=${PIPESTATUS[0]:-$?}

if [ "$status" -eq 124 ]; then
  echo "[run_gemini_cli.sh] gemini timed out after ${FUSION_TIMEOUT}s." >&2
  exit 124
fi
if [ ! -s "$output_file" ]; then
  echo "[run_gemini_cli.sh] gemini produced no answer (exit $status). Dropping Gemini." >&2
  [ -s "$scratch/stderr.log" ] && { echo "[run_gemini_cli.sh] stderr tail:" >&2; tail -10 "$scratch/stderr.log" >&2; }
  exit 1
fi
echo "[run_gemini_cli.sh] ok -> $output_file"
