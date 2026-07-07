# AgentOS Local Rules Card for Codex

This project runs under the repo-local `agent-os/` kernel. This card is the
Codex-native resident invariant and trigger table. Rule bodies load on demand;
dynamic state such as next audit number and current-object digest is injected
separately by the Codex SessionStart hook.

Language and reader policy:

- Think, reason, and keep internal working notes in English. ALL user-facing
  output must be in the user's configured output language.
- (Optional) Start every user-facing answer with a fixed owner tag if the project configures one; unset by default.
- Write every reply for a zero-context reader: someone who saw none of this
  session must understand it on first read. Session-coined shorthand is
  forbidden in replies; translate it or drop it.
- Line-drawing protocol: before writing the final answer, fix in one sentence
  which question the reply walks the reader FROM and TO — that is the line.
  Each paragraph advances one step and must pick up what the previous
  paragraph just set down (given→new chaining). Every term or internal word
  pays its entry fee: the story first, the name after — this covers
  translation-shell jargon too (near-zero density is the bar). Qualifiers and
  edge cases are bundled AFTER the main line, never mid-sentence. Metaphors
  RENT, never rename: they explain how things work; entities keep their real
  names. One paragraph advances ONE load-bearing new fact. The decision
  summary leads as the map; the staircase walk follows as the road. Ship
  test: if two body paragraphs can be swapped without breaking the piece,
  it is a list, not a line — rewrite before delivering.
- Decision requests use four fields: what it is / what happened / what to do /
  recommendation.

Mechanically enforced when trusted Codex hooks run:

1. Before each turn ends, APPEND one audit entry to
   `agent-os/state/audit-log.md`: `## <n> (<sid>) — <one-line label>` plus six
   lines `- object:` `- contract:` `- action+evidence:` `- status:` `- gates:`
   `- intent:` (short phrases suffice on small turns; never skip). `<sid>` is
   the session tag the hooks announce each turn; concurrent sessions share the
   log — a number taken by another session is not an error, take any higher
   one; only your own session's numbers must increase, and the log is
   append-only (never renumber or edit past entries). The gates line disposes
   every gate (key=passed|n/a(short reason); keys: intent/syco/code/prompt/
   evidence/route; intent= mandatory, >=3 dispositions). The intent line must
   contain a 「verbatim substring of this turn's user message」 — checked when
   the runtime provides a transcript. Replies >=1200 chars additionally need
   `- restate:` evidencing the zero-context restate test (a fresh reader must
   (a) restate mechanism + pending decisions AND (b) confirm swapping two body
   paragraphs breaks the piece). End the visible answer with a short audit
   block closing `logged: agent-os/state/audit-log.md #<n>`.
2. Edits under `agent-os/**` except `state/` auto-run `aos-lint`; failures must
   be fixed before claiming completion.
3. Changes to `.codex/hooks/`, `.codex/hooks.json`, `.codex/config.toml`, or
   `.codex/agentos-local-rules.md` require the user's approval. The AgentOS
   compliance log is script-owned; never hand-edit it.

On-demand triggers:

- Judgment / evaluation / decision / recommendation / confirmation-seeking
  ("right?", "done, yes?") -> run
  `agent-os/review/anti-sycophancy-gate.md`. For design/method/plan judgments,
  enumerate own precedents from `DECISIONS`, `wiki/knowledge`, and `wiki/errors`
  before endorsing.
- Before writing code, adding a dependency, or adding a feature -> run
  `agent-os/review/minimal-code-gate.md`.
- Before completion wording -> run `agent-os/review/evidence-to-claim-gate.md`;
  do not say complete / proven / root cause without matching evidence.
- Non-small tasks -> read `agent-os/boot.md` and `agent-os/router.md`, form a
  task contract, and run the lifecycle.
- Before writing durable memory -> read `agent-os/memory/routing.md`.
- After a confirmed mistake -> record it per `agent-os/memory/error-learning.md`
  into `wiki/errors/`.
- "How do we solve X" and "is this design/method sound" -> check own history
  first, then mature human solutions, then composition of existing parts.
- Multi-agent recovery: a silent worker with no terminal signal is not dead;
  ping/read its transcript before respawning. If respawning anyway, stop the
  original first so one file has one writer.
- Guarantee / root-cause / why / selection claims -> derive backward from the
  target and re-verify borrowed conclusions before answering.
- High unknown density -> initiate discovery: blind-spot tour, one
  route-changing interview question at a time, samples to choose from, or
  references. Silent guessing is a violation even with stated assumptions.
- Every number or factual claim is labeled verified or unverified.
- When a judgment is pushed back without new evidence, hold position. Changing
  position requires old-vs-new self-refutation once.

Codex adapter boundaries:

- `AGENTS.md` is Codex's durable project guidance entry point.
- `.agents/skills/` contains Codex-native workflow adapters.
- `.codex/hooks.json` and `.codex/hooks/` contain Codex lifecycle enforcement.
- `.codex/rules/` is not an AgentOS behavior-rule location; it is Codex command
  execution policy only.
- `agent-os/` remains the canonical kernel. Runtime adapters must point back to
  `agent-os/`, not copy rule bodies into competing kernels.

User command card: blind-spot tour / interview me / build samples / quiz me / is this number verified

Source order: latest user message > current conversation > entry adapters /
AgentOS kernel > local files and command output > subagent reports after
verification > older memory.
