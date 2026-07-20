# Contributing to AgentOS

AgentOS values small, verifiable changes and honest claim boundaries.

## Ground rules

- `agent-os/` is the kernel. Runtime files and skills are adapters, not competing rule sources.
- The installer and hooks use the Python 3 standard library. The pressure test uses the Node standard library.
- Installation must preserve user-owned entry content, configuration, Wiki files, and runtime state.
- The main model and skills own semantic judgment. Hooks may restore attention or enforce deterministic facts; do not add command-text intent guessing or answer scoring.
- A test proves only the behavior it observes. Runtime activation claims require a fresh trusted session.

## Required checks

```bash
python3 scripts/test_installer_behavior.py
python3 scripts/validate-agentos-install.py assets/agentos-template
python3 assets/agentos-template/agent-os/tools/aos-lint.py
cd assets/agentos-template
python3 -m unittest discover -s tests/unit -p 'test_*.py'
python3 -m unittest discover -s tests/integration -p 'test_*.py'
python3 -m unittest discover -s tests/scenarios -p 'test_*.py'
```

If you change an installation contract, test fresh install, brownfield merge, reinstall, invalid configuration preservation, and validator rejection. If you change a hook response, test both runtime adapters and the real runtime when available.

## Reporting issues

Describe the expected result, observed result, runtime, operating system, and the smallest reproduction. Use [SECURITY.md](SECURITY.md) for security-sensitive reports.
