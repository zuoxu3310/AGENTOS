# Prompt Craft Gate

## Purpose

Every prompt written for another model or agent — subagent tasks, panel and
judge prompts, worker prompts, DAG node prompts, external CLI calls (codex,
gemini, claude -p), web-AI dispatches — must pass this gate before dispatch.
A bare one-line role assignment ("you are the judge") is a violation.

Sources (fetched and distilled 2026-07-06): Anthropic prompting best practices
(claude-prompting-best-practices) and the OpenAI GPT-5 prompting guide. The
Fusion adapter templates (.claude/skills/fusion-workflow/references/) are the
worked examples of this gate.

## Checklist

Apply before dispatching the prompt:

```xml
<role>Who the receiving model is and what boundary it must preserve.</role>
<context>Grounded materials, source paths, and task contract.</context>
<instructions>What to do, why it matters, and what is forbidden.</instructions>
<output_format>Required artifact, language, evidence, and completeness.</output_format>
<question>The concrete assignment, placed after its materials.</question>
```

```text
structure:
  - XML-tagged sections: role / context / instructions / output_format / question
  - long materials at the TOP, the actual question or task LAST
    (Anthropic-measured gain up to +30% on long-context tasks)
  - long documents: instruct quote-grounding — extract the relevant quotes
    into <quotes> before answering

content:
  - explicit role with boundaries (system position when the runtime has one)
  - instructions carry their WHY — models generalize from motivation
  - positive instructions: say what to do, not what to avoid
  - state goal and constraints; do NOT hand frontier models a prescriptive
    step-by-step reasoning plan (it lowers output quality)
  - 3-5 <example> blocks when the output format or tone matters and is hard
    to describe in words
  - evidence discipline: require support for load-bearing claims, each
    labeled verified or unverified; uncertainty stated, never fabricated
  - end with a self-check instruction against the success criteria/contract

output:
  - explicit output format, language, and verbosity

review/judge prompts specifically:
  - coverage-first: report every finding with a confidence label; filtering
    happens downstream
  - never instruct "only report important/high-severity issues" — frontier
    models obey the filter and measured recall drops

final scan:
  - reread the assembled prompt once; remove contradictory directives
    (contradictions burn reasoning tokens and break adherence)
  - zero-context test: would a colleague with no context on the task know
    exactly what to produce from this prompt alone?
```

## Enforcement Boundary

2026-07-11 (ZX "该上闸机的上闸机"): the gate's TRIGGER is now mechanical. The gate
was law since 2026-07-06 yet a bare one-line probe still went out to codex exec
on 2026-07-10 (wiki/errors) — prompt-layer rules do not fire by themselves. A
PreToolUse hook (aos_prompt_craft_guard.py, both runtimes) is a structure-only
guard. It denies dispatches
whose prompt lacks XML-sectioned STRUCTURE (>=3 distinct tags): Agent/Task
prompts, bare string-literal agent() prompts in Workflow scripts, and inline
codex exec / claude -p / gemini -p commands without a prompt file or heredoc.
Probes are not exempt. Passing three labels does not prove prompt quality. The
hook checks structure only; semantic prompt quality still comes from the gate's
content review — section quality, quote
grounding, motivation, and self-checks remain this gate's prompt-layer
checklist and are NOT mechanically verified.

## Claim Boundary

Passing this gate improves format compliance, evidence quality, and
instruction adherence. It does not guarantee content correctness — content
still goes through the evidence and promotion gates.
