# AgentOS Architecture

## Purpose

The map of what AgentOS is, derived from its purpose: turn an ordinary user
message into a real, correct, user-acceptable result, against a model's
native drift toward the appearance of work. Every part below exists as one
counter-drift mechanism; a part that cannot answer "what failure does this
prevent" does not belong.

## The Six Parts

1. Identity — who works. Separated seats so no single thread can fake
   understanding, independent review, and execution at once. Lives in
   `.claude/agents/*.md` (each seat's birth identity: authority, in/out,
   boundaries, one working-method pointer). The `agent` key in
   `.claude/settings.json` makes every session start as the Zhongshu.
2. Methods — how work is done so it does not drift. Three canon classes,
   one directory each:
   - Gates (`agent-os/review/`): the method of one judgment or one act —
     causal reasoning, de-anchoring, claim wording, plan translation.
     Research-derived; their wording is the researched artifact.
   - Workflows (`agent-os/workflows/`): multi-step procedures — how the
     cognitive methods compose into one act of thinking (`cognition.md`),
     how each seat does its job (`zhongshu/menxia/shangshu/executor/
     yushi.md`), and special operations (`think-through.md`,
     `fusion-workflow.md`).
   - Memory methods (`agent-os/memory/`): how to record, recall, and learn
     from errors across sessions.
3. Rules — what must never happen, regardless of step. One resident card,
   `agent-os/rules-card.md`, projected byte-exact into both runtimes; the
   user's rulings behind it live in `DECISIONS.md`.
4. Machine — what is guaranteed without relying on model diligence. Hooks
   (attention restore, prompt-structure denial, post-edit lint, delivery
   recheck), `agent-os/tools/aos-lint.py` (structure, projections, anchors,
   error-learning ratchet, ledger sequencing), the append-only task record
   CLI, and `agent-os/artifact-contracts.toml` (every governed document's
   contract).
5. Memory — what survives the session. Root ledgers (`PLANS`, `PROGRESS`,
   `DECISIONS`, `HANDOFF`) and `wiki/`: the error library with its
   mechanical-landing ratchet, the exemplar library (user-accepted delivery
   shapes — load the matching exemplar before writing that class of
   delivery), raw sources, knowledge. Runtime state (`agent-os/state/`) is
   local and gitignored.
6. Adapters — how two runtimes reach one kernel. Entry documents point and
   carry projections, nothing else: `CLAUDE.md` points Claude at the rules
   channel (`.claude/rules/` symlink) and the kernel; `AGENTS.md` carries
   the projected card for Codex. `.claude/` and `.codex/`+`.agents/` wire
   hooks, skills, and config to their runtime's mechanics. The kernel stays
   pure text and portable; every runtime difference lives in an adapter.

## Product And Instance

AgentOS is installable, and it is two layers. The product — the kernel
(`agent-os/`), the runtime adapters, and the tests — travels with every
installation and is identical everywhere. The instance — `wiki/`, the root
ledgers, `agent-os/state/` — belongs to one project: its formats are
defined by the product's memory methods, it is seeded empty at install,
and it grows only through that project's own work. The boundary law:
kernel documents reference kernel paths freely, and reference instance
locations only by their defined format with explicit empty-state behavior
— "copy the accepted exemplar if the index has one, else this gate alone
governs" is legal; depending on any particular project's content is not.
This repository is special: it is the product's source and carries its own
instance, so the two layers coexist here and nowhere else.

## Skills Are Shells

`.claude/skills/` and `.agents/skills/` contain no methods: each skill is a
thin invocation shell — trigger description resident, Source pointing at
exactly one canon document, output shape — for contexts that decide
invocation at runtime (the main session, Codex, explicit user calls). Chain
seats do not go through shells: their contracts point at their seat
workflow, which names the canon documents to read at the moment of use. A
shell may share its canon's name (`fusion-workflow` the skill invokes
`fusion-workflow.md` the canon); the shell is the entrance, the canon is
the method.

## Load Discipline

Resident always: the rules card and the seat's contract. Loaded at birth:
the seat's workflow and the canon documents it names. Loaded at the moment
of use: everything else, through the router (`agent-os/router.md`) — one
condition, one canon document, one shell. Never loaded: ledgers, wiki, and
history, except through explicit routing. Verification status, design
rationale, and provenance live in ledgers and wiki, never in operator
documents.

## How A Request Flows

The session is born as Zhongshu with its contract and workflow. Per
increment: record → raw text to Menxia, own reconstruction in parallel
(cognition workflow) → goal fixed by comparison → approved package to
Shangshu → plan by the engineering gate, one-shot executors per node, real
verification → one integrated result back → verified against `done_when` →
one delivery in the exemplar shape → teardown, with the Censor spawned in
the background when a confirmed mistake surfaced. Every step lands in the
task record; lint and hooks guard the mechanical facts; the error ratchet
turns any recurring mistake into a permanent guard.
