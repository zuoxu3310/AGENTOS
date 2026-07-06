# Prompt Craft Gate

Date: 2026-07-06

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

## Claim Boundary

Passing this gate improves format compliance, evidence quality, and
instruction adherence. It does not guarantee content correctness — content
still goes through the evidence and promotion gates.
