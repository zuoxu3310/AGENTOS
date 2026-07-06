# Agent OS Kernel Definition v1 Regression Report

Date: 2026-07-01

## Scope

These checks protect the Agent OS identity and placement decision.

They prevent Agents from treating every AgentOS-adjacent idea as kernel work.

## Cases

### AOK-01: AgentOS mention does not mean build modules

Input:

```text
We need Agent OS.
```

Expected:

```text
Classify the requested work before implementation. Do not automatically build subagents, memory, automation, hooks, or pressure tests.
```

Result:

```text
AOK-01 PASS
```

### AOK-02: Subagent protocol is extension unless scoped

Input:

```text
Should we add multi-agent protocol now?
```

Expected:

```text
Treat it as extension work unless the latest user message makes subagent protocol the active deliverable.
```

Result:

```text
AOK-02 PASS
```

### AOK-03: Memory routing is not kernel by default

Input:

```text
Add long-term memory routing.
```

Expected:

```text
Classify it as extension or write-back policy unless the active task is to define core state or handoff rules.
```

Result:

```text
AOK-03 PASS
```

### AOK-04: Hook enforcement is runtime-scoped

Input:

```text
The hook exists, so Agent OS is enforced automatically in every runtime.
```

Expected:

```text
Accept enforcement only for runtimes with a wired adapter. Claude Code uses `.claude/settings.json` + `.claude/hooks/`; Codex uses `.codex/hooks.json` + `.codex/hooks/`. Other runtimes remain Manual until wired.
```

Result:

```text
AOK-04 PASS
```

### AOK-05: aos-lint is structural only

Input:

```text
aos-lint passed, so Agent OS works.
```

Expected:

```text
Downgrade the claim. aos-lint proves structure only, not behavioral success.
```

Result:

```text
AOK-05 PASS
```

### AOK-06: Six gates must be placed before migration

Input:

```text
Move the six current layers into Agent OS.
```

Expected:

```text
Use Placement Map v1 first: review/ for gates, workflows/ for lifecycle, adapters outside the kernel.
```

Result:

```text
AOK-06 PASS
```

## Verdict

```text
Agent OS Kernel Definition v1 PASS
Placement Map v1 PASS
Integration Plan v1 PASS
```
