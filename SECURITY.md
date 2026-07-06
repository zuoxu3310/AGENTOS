# Security Policy

## Threat model — read this first

AgentOS's enforcement hooks are an **anti-accident bar, not an anti-adversary one.**

The `PreToolUse` guard screens edit paths and does a heuristic scan of shell commands to
stop an agent from *accidentally* modifying its own enforcement layer or the script-owned
metrics log. An intentionally obfuscated command can evade it. True adversarial
protection would require OS-level permissions outside the agent's own user, which is
outside AgentOS's scope.

In short:

- AgentOS raises the cost of accidental self-tampering and drift.
- AgentOS does **not** sandbox a hostile agent or a hostile prompt.
- Hooks are **fail-open**: a broken hook degrades to a no-op so it can never brick a
  session. This is a deliberate availability choice, not a security gap to report.

Run agents under the OS-level isolation appropriate to how much you trust the code and
prompts they handle.

## Reporting a vulnerability

If you find a way that AgentOS actively *weakens* a project's security (for example, an
installer path that writes outside the target directory, or a hook that exfiltrates
data), please report it privately:

- Open a GitHub [security advisory](https://github.com/zuoxu3310/AGENTOS/security/advisories/new), or
- Open a minimal issue asking for a private channel (do not include exploit details in
  the public issue).

Please include the runtime, OS, and a minimal reproduction. We aim to acknowledge
reports promptly.

## Supported versions

AgentOS is distributed as a rolling template; fixes land on `main`. Reinstall to pick up
security fixes — your live state and `wiki/` are preserved across reinstalls.
