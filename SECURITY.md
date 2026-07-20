# Security Policy

## Scope

AgentOS is not a security sandbox. It runs inside the permissions granted to Codex or Claude Code and relies on each runtime's native sandbox, permission system, and command policy for operating-system protection.

AgentOS hooks enforce only narrow deterministic boundaries. They do not infer intent from shell text, decide whether an action is important, or protect against a hostile agent that already has permission to change the repository. Treat hook output as workflow control, not a security boundary.

The installer is designed to stay inside its target directory, preserve existing Wiki and runtime state, merge supported entry/configuration files, and back up replacements under `.agentos-backups/`. A path escape, data loss, secret exposure, or silent weakening of runtime security is a vulnerability.

## Reporting a vulnerability

Use a GitHub [security advisory](https://github.com/zuoxu3310/AGENTOS/security/advisories/new), or open a minimal issue requesting a private channel without publishing exploit details. Include the runtime, operating system, affected version, and a minimal reproduction.

## Supported versions

AgentOS is distributed as a rolling template on `main`. Reinstall to receive fixes; existing project Wiki and runtime state are preserved.
