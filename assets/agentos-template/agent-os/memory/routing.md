# Memory Operating Contract

## Purpose

This is the single operating contract for AgentOS project memory. It decides
what must be read, what may be written, which file owns each fact, how memory
matures, and when old state stops being current.

Memory exists to reduce future reconstruction and improve future action. A
write that will not change a later decision, verification, recovery, or
handoff is unnecessary.

## Boundaries

```text
agent-os/        stable behavior kernel
root ledgers     canonical cross-session work state
wiki/            durable episodic and semantic project memory
source + output  primary evidence
Git              history and recovery, not current-state routing
```

Wiki summaries never replace source files, command output, or root ledgers.
Only one artifact owns each current fact.

## Artifact Responsibilities

| Artifact | One question it answers | Read when | Write when | Canonical owner |
|---|---|---|---|---|
| `PLANS.md` | What multi-stage route is current? | Start/resume a planned task | A real multi-stage route changes | Root ledger |
| `PROGRESS.md` | What verified milestone is complete? | Resume, report, or verify history | Evidence proves a durable milestone | Root ledger |
| `DECISIONS.md` | What did the user durably decide, and why? | A decision constrains the current task | The user makes or changes a durable decision | Root ledger |
| `HANDOFF.md` | What must the next session know and do now? | Every start or resume | The resumable state changes or a stage ends | Root ledger; one current snapshot |
| `wiki/TASKS/` | What is this cross-session task contract? | Start/resume the named task | A non-trivial cross-session task starts or its contract changes | One active task file |
| `wiki/CHATS/` | Which exact user intent will need later verification? | A task depends on prior wording or scope history | Exact intent or scope must survive beyond ledgers | Distilled note, not transcript |
| `wiki/knowledge/` | What verified reusable concept is true enough to reuse? | The present task triggers that concept | Reusable evidence passes promotion | Concept path identity |
| `wiki/errors/` | Which confirmed failure must change a future action? | A high-risk action matches its triggers | A confirmed correction has reuse value | Same-root error record |
| `wiki/raw/` | What original material entered the project? | A task needs that source | Source material is retained | Source file plus manifest row |
| `wiki/docs/` | What should a human reader use? | Explicit documentation work | Human-facing documentation changes | Named document |
| `wiki/index.md` | How can a reader reach durable Wiki memory? | Navigating Wiki memory | A durable Wiki artifact changes lifecycle | Derived link view |
| `wiki/log.md` | Which Wiki lifecycle events occurred? | Auditing lifecycle changes | Create, promote, supersede, archive, or migrate | Lifecycle log only |

Do not create a `PLAN` for a one-step task. Do not write `PROGRESS` for effort,
intent, or a passing check that does not prove a milestone. Do not create a
`CHAT` merely because a conversation happened.

## Selective Read Route

On start or resume, read in this order:

```text
1. current HANDOFF
2. active TASK, if one exists
3. current PLAN, if one exists
4. only the Decisions that constrain the task
5. only the Knowledge and Errors whose topics or triggers match the next action
6. source files and runtime evidence needed for the action
```

Do not preload the whole Wiki or error library. For a related high-risk action,
retrieve at most three active error rules by explicit trigger terms; verify the
landing target before relying on them.

## Event Route

```text
start or resume:
  read HANDOFF -> active TASK -> current PLAN -> selected Decisions/Knowledge/Errors

new cross-session task:
  create TASK; create PLAN only for a real multi-stage route

durable user decision:
  update DECISIONS; create CHAT only if exact original intent will need checking

source ingest:
  retain under wiki/raw and register MANIFEST; promote only after verification

verified milestone:
  update PROGRESS; refresh PLAN/HANDOFF only if their current state changed

user correction:
  fix the task first; then merge into an error root only if future reuse is likely

stage end:
  refresh one HANDOFF; run the stage audit; write wiki/log only for Wiki lifecycle changes

task close:
  close or archive TASK/PLAN; remove stale current HANDOFF content; record only needed memory
```

## Memory Maturity

```text
working:
  current conversation, session-local active_work, and scratch state; not
  durable by default

episodic:
  TASK, CHAT, PLAN, PROGRESS, DECISION, HANDOFF, and error observations

semantic:
  verified reusable knowledge with sources and lifecycle metadata

procedural:
  kernel rule, native skill, hook, or regression protection that changes behavior
```

Promotion requires verified reuse value. Working observations do not become
knowledge, and a correction does not become a kernel rule, merely because it
was written down.

## Lifecycle

Use these states consistently:

```text
current      the one authoritative live object of its class
completed    contracted result has matching evidence
superseded   a named replacement owns the meaning now
stale        no longer trustworthy; replacement not yet established
archived     retained only for history
```

Every superseded artifact names its replacement, and the replacement names
what it supersedes. A missing target is invalid. There may be only one current
HANDOFF and one clearly identified current PLAN.

## Semantic Judgment And Mechanical Views

Human or AI semantic judgment is required for:

```text
decisions, progress claims, task goals, knowledge conclusions, error roots,
causes, trigger meaning, promotion, supersession meaning, and landing choice
```

Automation may only:

```text
validate structure and links; detect duplicates or stale pointers; generate
Wiki link views, error record lists, counts, and health metrics; verify manifest
coverage and ledger links
```

`--fix-memory-views` must be byte-stable on a second run and must never change
semantic prose.

## Source And Conflict Order

When claims conflict, use:

```text
1. latest user message
2. accepted current-conversation decision
3. verified source files and runtime evidence
4. current root ledger or active task contract
5. current indexed knowledge with stronger direct sources
6. verified worker report
7. older, stale, superseded, or archived memory
```

Do not silently reconcile a conflict. Mark the weaker source stale or
superseded, preserve the evidence anchor, and state what would resolve it.

## Write Gate

Before a durable memory write, establish:

```yaml
memory_write_gate:
  content:
  destination:
  future_use:
  evidence_source:
  lifecycle_change:
  semantic_or_derived: semantic | derived
```

If the destination already owns the fact, update it instead of copying the
fact elsewhere. If future use is not concrete, do not write.

## Completion Disposition

At explicit closeout, decide whether durable memory needs reconciliation:

```yaml
memory_disposition:
  status: reconciled | not_needed
  destinations: []
  reason:
```

`reconciled` lists only artifacts actually changed. `not_needed` requires a
reason and no destinations. This is a semantic closeout decision by the main
model; Stop never invents decisions, progress, knowledge, or error causes.

## Forbidden Substitutions

- Do not put all state into `HANDOFF.md`.
- Do not mirror every turn into ledgers or `wiki/log.md`.
- Do not store full transcripts unless the user explicitly requests them.
- Do not make global maintenance skills an installed project's hidden dependency.
- Do not treat a memory write as task completion unless memory is the active user object.
