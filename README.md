# AgentOS

AgentOS is a repository-local operating layer for Codex and Claude Code. It helps an AI keep the user's real goal in view, work against explicit finish conditions, verify what it claims, preserve useful project memory, and stop when the job is done.

The design has one important boundary: AI performs semantic judgment; hooks only restore attention or check facts that software can determine reliably.

## What it changes

- Every real user message asks the main model to reconsider whether the request continues, corrects, replaces, or starts work.
- Long tasks keep a small session-local `active_work` record: goal, finish conditions, open items, next action, status, and evidence.
- Session start and context recovery restore only that long-task state. Restored state is context, not permission to continue old actions.
- Tool hooks stay quiet during normal work. They guard the single Codex delegation backend, validate worker-prompt structure, and lint governed documents after structured edits.
- A completed or blocked long task gets one same-model delivery reread before the answer reaches the user. Short answers are not forced through another generation.
- The canonical resident rules live in `agent-os/rules-card.md`; Codex and Claude receive native projections of that one source.

## Install

Python 3 is the only installer dependency.

```bash
git clone https://github.com/zuoxu3310/AGENTOS.git
python3 AGENTOS/scripts/install-agentos.py /path/to/project
python3 AGENTOS/scripts/validate-agentos-install.py /path/to/project
python3 /path/to/project/agent-os/tools/aos-lint.py
```

The installer merges user entry documents and runtime configuration. Existing `agent-os/state/**` and `wiki/**` files are preserved. Replaced files are backed up under the target project's `.agentos-backups/` directory.

After installation or an update, start a new Codex or Claude session in the project. Changed project hooks may require approval before they run.

## Architecture

```text
user message
    ↓
main model understands the goal and finish line
    ↓
task contract guides work and evidence
    ↓
hooks restore attention or run mechanical checks
    ↓
verified result and plain-language delivery
    ↓
selective project memory for future sessions
```

The repository installs these layers:

- `agent-os/`: canonical rules, review gates, workflows, memory contract, and tools.
- `AGENTS.md` and `.agents/skills/`: Codex and portable agent adapters.
- `CLAUDE.md`, `.claude/rules/`, `.claude/skills/`, and `.claude/hooks/`: Claude Code adapters.
- `.codex/config.toml` and `.codex/hooks/`: Codex project configuration and hooks.
- `PLANS.md`, `PROGRESS.md`, `DECISIONS.md`, `HANDOFF.md`, and `wiki/`: project-owned memory.
- `vendor/claude-dynamic-workflows-codex/`: the sole delegated workflow engine used by Codex.

Codex may work directly in the main conversation or delegate through the vendored Dynamic Workflow runner. Claude keeps its native Workflow. AgentOS does not add a second orchestration backend.

## What hooks do not do

Hooks do not decide user intent, whether an action is important, whether a route is correct, or whether an answer is good. Those are semantic judgments for the main model and reusable skills. The linter proves document and installation structure only; it does not prove behavioral quality.

## Verify the release bundle

```bash
python3 scripts/test_installer_behavior.py
python3 assets/agentos-template/agent-os/tools/aos-lint.py
cd assets/agentos-template
python3 -m unittest discover -s tests/unit -p 'test_*.py'
python3 -m unittest discover -s tests/integration -p 'test_*.py'
python3 -m unittest discover -s tests/scenarios -p 'test_*.py'
```

See [Quickstart](docs/QUICKSTART.md) for installation details and [Architecture](docs/ARCHITECTURE.md) for the runtime flow.

## License

Apache-2.0. The vendored Dynamic Workflow keeps its upstream license and attribution.
