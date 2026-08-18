# Progress

Use this root ledger for completed work, verification evidence, and claim boundaries.

Record what changed, what command or file proves it, and what the evidence does not prove.

## Verified Milestones

### 2026-08-18 — Cognition_AGENTOS lock-up diagnosed; Claude returns to session-as-中书; gate hardened

- Incident evidence (Claude session 57472125 in Cognition_AGENTOS, ledger `t20260818-0203`): executor spawned with `name` + string `run_in_background:"false"` under the agent-teams flag → hook `agent_type` = spawn name → seat None → receipt and `execution_result` refused after the edits landed → 尚书 refused `integration`, 中书 waited, both in `sleep` loops → 80 min, zero delivery. Also: empty-payload launch, non-cascading TaskStop, ledger written by a script after stop, multi-paragraph verbatim check failing on newlines.
- Landed: DECISIONS 2026-08-18 entry; Claude `agentos` skill = 中书 procedure; Codex skill = relay; shared gate/common hardening (identity fallback, spawn normalization, sleep denial, named exits, ledger-file guard, newline-safe parsing, frozen tasks, empty-invocation refusal); docs and lint lists; capabilities C09/C10.
- Evidence: `python3 -m pytest tests` → 127 passed, 1118 subtests; `aos-lint.py` PASS (473 checks). Not proven here: the live Claude run and the exact Claude Code condition that produces teammate mode (inferred from the incident's meta.json; headless probes did not reproduce it).

### 2026-08-14 — Codex live canary read: chain ran correctly once, then a session drifted past it; chain entry now has a mechanical gate

- Transcript evidence (session 019ffe3d + task ledger russianflow-plan-git): the 06:02 session ran the chain RIGHT — task record created, Menxia Phase A on a real runner thread with a journal anchor, Phase B honestly labeled degraded_in_session, Shangshu NO_DELEGATION serial dispatch; the threads the user saw were the chain working. The 06:07 session announced the seat and did the birth reads, then bypassed re-entry for the new increment — probing the repo without recording the increment or running review, and continuing tool work while the user was demanding an answer. Its own confession: it treated read-probes as "prep work, not execution" and downgraded the mandate to a checklist. Root class: prompt-layer mandates do not fire by themselves (the established 2026-07-11 lesson).
- Mechanical landing, deliberately narrower than the deadlocking retired turn gate: `.codex/hooks/aos_chain_entry_guard.py` (PreToolUse) denies WORKSPACE MUTATIONS (git write commands, file writes/redirects, write-class tools) until a Menxia `independent_review` is on record (12h recency); reads are never denied; the record CLI, chain launcher, lint, and Yushi dispatcher are always allowed so the degraded path can always satisfy the precondition; fail-open on uncertainty. Fixture-tested 10/10 including JS-wrapped commands and the unlock-after-review path. Announcement + AGENTS.md entry contract now state the fixed first actions per user increment (record it, then review it) and that mutations are mechanically denied before review. Prompt-craft guard no longer flags --help/--version probes (both runtimes).
- Evidence: guard unit cases all PASS; dev repo lint 0 FAIL, pytest 69 + 956 subtests, installer behavior suite OK; template + three global installer copies resynced; RussianFlow reinstalled — validator passed, guard present. Boundary: read-probing before recording an increment remains prompt-layer by design (denying reads is the retired gate's deadlock, banned by rules-card 22); the next live session is the check.

### 2026-08-14 — Session identity made mechanical: entry contracts became managed blocks; session-start hooks announce the Zhongshu seat

- The user's live Codex canary in RussianFlow exposed the identity failure: the session never entered the Zhongshu role. Root: merge installs update only managed blocks, and the entry-identity content (AGENTS.md "Codex Session Seat", CLAUDE.md agentos-entry bullet) lived OUTSIDE the markers — old projects upgraded to a new rules block but zero identity text. Second weakness: Codex identity hung solely on `.codex/config.toml` `developer_instructions`, a channel whose project-level loading is not certain.
- Fix, both roots: (1) entry-identity content in AGENTS.md and CLAUDE.md is now wrapped in `AGENTOS ENTRY CONTRACT` managed markers; the installer merges this second block for both entry docs (new `entry_contract_block` + dispatch), so merge installs can never drop identity again. (2) Both runtimes' SessionStart hooks now mechanically inject the seat announcement — AgentOS is active, this session is the Zhongshu seat, read the adapter/workflow before any task work, and say so in the first reply — making identity independent of static-file delivery. Lint anchors added for the entry markers and seat wording in both entry docs.
- Evidence: RussianFlow reinstall manifest shows `AGENTS.md#entry-contract: merged` and `CLAUDE.md#entry-contract: merged`; seat section now present in both docs; the Codex SessionStart hook executed against RussianFlow emits the announcement (verified by running the hook with real input); validator passed, lint 0 FAIL, pytest 68+7 skipped green there; dev repo 69 + 946 subtests, behavior suite 6/6, fresh canary passed with seat section present; all three global installer copies resynced. Does not prove: an actual fresh Codex session adopting the role — the user's next session in RussianFlow remains the live check.

### 2026-08-14 — RussianFlow blocking diagnosed to the quarantined engine still shipping in distribution; channel resynced, project healed

- Diagnosis (user report: threads appeared, second task blocked): RussianFlow had been installed from the stale global installer skill, whose template still shipped the turn-execution-chain engine quarantined on 2026-08-12 — `aos_three_departments.py` on UserPromptSubmit spawned the threads the user saw; `aos_turn_gate.py` on PreToolUse denies all project tools without an "admitted TurnContract", and RussianFlow's `agent-os/state/` was empty, so every tool call was denied. Root: the quarantine removed the engine from the dev repo but never reached the distribution copies (`~/.agents`, `~/.claude`, `~/.codex` installer skills all carried it).
- Fix: 34 quarantined-line paths added to the installer retirement list (both runtimes' hook pair, six old role contracts, old workflow launchers, turn-contract gate, task-board/relay/runtime tools, eight old test modules); Stop-hook canonicalization now admits exactly one stop gate plus one async Yushi dispatcher (it had been silently filtering the dispatcher out — caught because RussianFlow's merged hooks lacked it); post-install derived-view refresh added (preserved-wiki installs were guaranteed a stale index view); installer behavior tests updated to the gate+dispatcher contract; all three global installer copies resynced with the rebuilt bundle.
- Evidence: RussianFlow reinstall — 35 obsolete paths backed up and removed, validator `passed`, preservation `safe` (15 wiki files preserved byte-intact), installed lint 0 FAIL, pytest 68 passed + 7 skipped + 480 subtests, `.codex/hooks.json` Stop = stop gate + yushi dispatcher, zero stale engine references; installer behavior suite 6/6; fresh-install canary re-run fully green. Does not prove: live Codex chain behavior in RussianFlow — the user's next Codex session there is the live canary (MANIFEST checklist applies).

### 2026-08-14 — Guardrail debts cleared and the installer rebuilt on the current kernel; fresh-install canary fully green

- The five audit defects are closed: (1) `skill-parity.md` dead pointer removed (the per-turn-audit row became an honest machine-layer hook-parity row) and the matrix gained Engineering Gate + chain-constitutive rows; (2) `agent-os/memory/exemplars.md` rewritten to the real flat layout and five frontmatter fields, its seeding rule replaced per the user's ruling (an empty library is legal — the gate governs; drafts are never manufactured to solicit acceptance), and wired into `memory/routing.md`'s artifact table, both memory-wiki-routing shells, and delivery-gate; (3) `links_resolve`/`source_reference` implemented in aos-lint (dead kernel references now fail; negative probe confirmed a deliberately broken reference is caught) and `runtime/memory_contract_tests` anchored to existing test modules with a lost-anchor check; `links_resolve` extended to architecture, gates, memory, adapters, and role contracts; (4) lint `REQUIRED_FILES` regenerated from the live tree — 126 entries covering the whole rebuilt core plus the test suite; (5) rules-card rule 16 carries the corrected attention sentence (never dump — and answer whatever they actually ask), reprojected byte-exact at 115/115 lines. Doctrine-derived: menxia's birth list gained evidence-to-claim; shangshu's gained reasoning-base/anti-sycophancy/evidence-to-claim; both v1 READMEs are honest pointers now.
- Installer rebuilt: the template's product layers regenerated from the live tree (kernel, five role contracts, 26 shells, all hooks including the context alarm and yushi dispatcher, vendor runners incl. AgentChat + fusion-fable, tests), runtime state purged, `outputs/`+`work/` fossils dropped, `agent-os/boot.md` added to the retirement list, and `wiki/docs/task-anatomy.md` seeded. The validator now parses its presence list from the target's own aos-lint (single source of truth — it can no longer drift) and accepts the Codex async Yushi Stop dispatcher alongside the single Stop gate. Instance-dependent tests carry fresh-install skip guards.
- Evidence: dev repo `aos-lint` 0 FAIL and `pytest` 69 passed + 946 subtests; installer behavior suite 6/6 OK; fresh-install canary — validator `passed`, installed lint 0 FAIL, installed pytest 68 passed + 7 skipped (instance-data guards) + 480 subtests; reinstall-over-existing preserved a user-owned wiki file byte-intact with preservation `safe`. Does not prove: live chain behavior in an installed project; the public GitHub release still carries the old package (push awaits the user's explicit approval).

### 2026-08-14 — Codex-side three-departments chain designed and staged by Codex itself, applied and structurally green

- Per the user's order (「掉mcp让codex自己做」), the Codex adapter was built by a Codex session over MCP. Round 1: verified mechanism inventory with evidence (codex-cli 0.144.1; AGENTS.md + `developer_instructions` injection verified; `multi_agent stable true` with app-server thread protocol; async hooks with cancel-on-session-end limitation; full hook event set) — its sandbox denies writes to `.codex/` and `.agents/` (self-protection), so implementation was re-routed: Codex staged nine files under `work/codex-parity-staging/` with a MANIFEST (apply order, structural checks, live-only boundary), the coordinating session reviewed every file and applied mechanically.
- What landed: `agentos-chain.workflow.js` (Menxia Phase A on a separate thread seeing only the raw increment, journaled `menxia_phase_a_record` before the Phase B steer; warm Shangshu plan→integrate; fresh one-shot Executors strictly serial with dependency gating and per-node write-scope sandboxing; one-shot Yushi); `aos_chain.py` launcher (three modes, workspace fingerprint, journal under `agent-os/state/codex-workflows/`, task-record promotion in seat vocabulary); `aos_yushi_dispatch.py` (atomic retryable queue in tempdir keyed by repo hash, async Stop dispatch, defer-while-delivery-pending, fail-open); rewritten `dynamic-workflow` SKILL (mandatory chain, size-routing vocabulary removed — also purged from `.codex/config.toml`); rewritten `agent-os/adapters/codex-workflow.md` (verified inventory, seat mapping with explicit degradations); `AGENTS.md` Codex Session Seat section (managed block byte-exact); hooks.json async Stop entry.
- Review findings: one defect (two dead Menxia kernel paths, `intent-contract.md`/`reasoning-gate.md`) sent back to the same Codex thread and fixed by it; one mechanical conformance fix applied here (`## Purpose And Boundary` → `## Purpose` per the runtime_adapter contract, live + staging copies).
- Evidence: managed-block byte-check True; every staged `agent-os/`+`vendor/` path resolves; JSON/TOML/Python/JS syntax PASS; banned-vocabulary grep clean; `aos-lint.py` 0 FAIL; `pytest` 69 passed + 846 subtests; all three launcher modes return `planned` on `--plan` with representative stdin. Does not prove (live Codex session required, checklist in the staging MANIFEST): Zhongshu identity adoption at session start, real separate-thread Menxia independence, serial executor ordering live, async hook trust/discovery and post-cancel retry.

### 2026-08-14 — Engineering provenance audited and the three sources truly extracted; context alarm hook landed

- Provenance verdicts (all three sources fetched verbatim and compared line-level): ponytail — the seven-rung ladder was genuinely extracted at the 2026-07-19 baseline, but its understanding-first premise ("the ladder runs after you understand the problem") and full safety enumeration had been dropped; pristine-skill — never referenced, the name entered as a capability label while four of seven laws were present only through shared Linus lineage in pretraining, with deployment parity, session cost, and adversarial verification absent entirely; Linus.md — two cores in (data structures first, special-case rejection), the main body out (three questions, five-layer decomposition, worth-doing verdict, taste rating).
- Extraction landed per the user's three rulings (DECISIONS same date): engineering-gate rebuilt with Entry Judgment, Decomposition Checks, six acceptance additions, Review Output, Adversarial Verification; minimal-code-gate rebuilt with the understanding-first premise, shared-function bug-fix rule, Working Rules, full safety boundary; session-cost law excluded in favor of a mechanical alarm — `.claude/hooks/aos_prompt_baseline.py` now estimates live context from the transcript (post-compaction tail only) and at >= 400k tokens emits a user-visible systemMessage plus an in-context persist-and-reset instruction. Sources retained verbatim under `wiki/raw/` with MANIFEST rows; also: `delivery-review` skill created in both mirrors and delivery-gate added to the zhongshu birth-load list (DECISIONS same date); engineering-plan-review gained its missing Codex openai.yaml.
- Evidence: hook estimator tested against synthetic transcripts (600k detected; tail-only counting after a compact boundary → 5,000; small files skipped); `aos-lint.py` PASS and `python3 -m pytest tests -q` green after all edits. Does not prove: live alarm firing in a real session; the mechanical residue scan (pristine adversarial verification) is doctrine in the gate, its lint implementation is booked machine-layer work.

### 2026-08-14 — Full reference-graph audit of skills, workflows, and system documents (findings recorded, no fixes applied)

- Every kernel document (39), role contract (5), and both skill mirrors read line by line; every `agent-os/...` cross-reference mechanically extracted (grep) and resolved. Structure confirmed sound: contracts→seat workflow→named canons is intact; cognition→gates composition is one-directional (single exception below); the 11 shell pairs differ only by runtime label plus the intentional fusion/memory runtime deltas; `.agents/dynamic-workflow` is the sanctioned Codex-only extra.
- Confirmed defects, in order: (1) `skill-parity.md:41` dead pointer to `agent-os/review/per-turn-audit-gate.md` (file archived, row never updated); the matrix also lacks rows for engineering-plan-review (shell exists in both runtimes), delivery-gate, cognition, and the five seat workflows. (2) `agent-os/memory/exemplars.md` is an orphan — no reference from router, `memory/routing.md`'s artifact table, or the memory-wiki-routing shell; `delivery-gate.md` points straight at `wiki/exemplars/_INDEX.md`; its own layout spec (`wiki/exemplars/<type>/<date>-<slug>.md`) contradicts both the contracts glob (`wiki/exemplars/*-20*.md`) and the flat reality. (3) Verification labels declared in `artifact-contracts.toml` but never implemented in aos-lint: `links_resolve`, `source_reference`, `runtime_contract_tests`, `memory_contract_tests` — lint implements structure regex, forbidden content, coverage uniqueness, projections, and exemplar dead-pointer checks only; this is why (1) survived. (4) `REQUIRED_FILES` presence guard predates the rebuild: architecture.md, cognition.md, all five seat workflows, delivery/engineering/prompt-craft gates, think-through, fusion-workflow, exemplars.md, all five `.claude/agents/` contracts, and three newer shells are absent — deleting cognition.md today leaves lint green. (5) `rules-card.md` rule 16 still carries the user-rejected absolute "internal bookkeeping never reaches them" (corrected in the entry contract on 2026-08-14, never synced to the card; projected byte-exact into both runtimes).
- Redundancy: `agent-execution-lifecycle.md` User-Facing Delivery section now overlaps the new delivery-gate (two kernel owners of delivery shaping; the shell-retention decision remains booked); router rows 17 and 24 route near-identical conditions to the same targets; `completion-gate.md` is the single gate-layer document referencing a workflow upward (`agent-execution-lifecycle.md`), a declared compiled-view pointer but the sole one-directionality exception.
- Design questions for the user, not defects: menxia's birth-load list omits `evidence-to-claim-gate.md` (cognition Step 5 requires it for every verdict) and shangshu's omits reasoning-base/anti-sycophancy/evidence-to-claim — moment-of-use reads are legal but unstated, the exact shape of the recurrence-5 named-is-not-possessed root; yushi performs same-root/root-cause judgment without cognition (lightweight by intent, undocumented as a decision). `agent-os/skills/README.md` and `agent-os/handoffs/README.md` are v1 remnants superseded by architecture.md's Skills Are Shells and task-contract/HANDOFF, kept alive only by the lint presence list — archive candidates.
- Evidence: reference extraction `grep -rn -o 'agent-os/[a-zA-Z0-9_/.-]*\.(md|toml|py)'` over kernel, contracts, shells, adapters; per-file reads this session; `ls agent-os/review/per-turn-audit-gate.md` → No such file; lint function inventory (`lint_memory_contracts`, `lint_artifact_contracts`, `lint_task_ledger_sequencing` only). Does not prove: anything about live behavior; no fix has been applied — all five defects and the redundancy/design items await the user's dispatch.

### 2026-08-14 — Product/instance layers separated; delivery method distilled into the kernel

- The user caught a structural error: the zhongshu workflow's delivery step depended on `wiki/exemplars/` content — kernel (travels with every install) depending on instance (each project's own, empty when fresh). Corrections: the reporting method itself is now kernel canon `agent-os/review/delivery-gate.md` — distilled strictly from `wiki/raw/2026-07-11-工作汇报向上管理-抖音转写.md` (goal-first, conclusion-first with data, proactive sync; the three formulas: conclusion+3 reasons+request / fact+problem+solution+support / progress+data+next in one line) plus the accepted style from `wiki/exemplars/spokesperson-tldr-2026-07-16.md`; the delivery step is two-tier (kernel gate always; project-accepted exemplar copied when present, empty case defined); `agent-os/architecture.md` gained the Product And Instance section with the boundary law (kernel references instance only by format with explicit empty-state behavior); error record `2026-08-14-kernel-referenced-instance-content` (recurrence 1, Level 4) landed on that law.
- Evidence: `python3 -m pytest tests -q` and `aos-lint.py` green after the change (counts in the commit). Does not prove: live behavior; the installer still predates the whole rebuilt kernel.

### 2026-08-14 — Architecture canon written; researched gate wording restored; attention method wired back

- `agent-os/architecture.md` created and registered (artifact + router row): the purpose-derived map — six parts (identity, methods in three canon classes, rules, machine, memory, adapters), skills defined as shells, load discipline, and how a request flows. The three canon directories (review/workflows/memory) are confirmed as the taxonomy's carrier; no restructure.
- The five cognitive gates restored verbatim from the pre-rewrite researched versions (git 8aeb4de), reversing the paraphrase contamination. Exactly two sanctioned patches applied: the intent gate's narrow anti-sycophancy prescription now defers to that gate's own trigger section (K1), and its embedded Proxy Risk Gate is a pointer to the route-keeper Promotion Gate as the single canonical template (K2). Ten skill shells unbound from the cognition workflow — composition lives one-directionally in `cognition.md`; shells carry standalone triggers only.
- Attention method re-homed per its provenance (raw source 2026-07-11 工作汇报向上管理 → exemplar library): the zhongshu workflow's delivery step now orders loading the matching `wiki/exemplars/` shape before writing any delivery; the entry contract's distorted line ("internal bookkeeping never reaches them") corrected to the researched meaning — never dump, always answer what is asked.
- Evidence: `python3 -m pytest tests -q` → 69 passed, 831 subtests; `aos-lint.py` PASS. Does not prove: live behavior; four exemplars remain draft-pending-ZX and enter mandatory loading only when accepted.

### 2026-08-13 — Role layer rebuilt: contracts hold identity only; procedures live in per-seat workflows

- Per the user's role-first order: five role contracts rewritten to the five-section standard (identity and authority / in and out / boundaries / one working-method pointer / record duty). All procedural content relocated verbatim into new per-seat workflows — `agent-os/workflows/{zhongshu,menxia,shangshu,executor,yushi}.md` — which hold the load lists, step sequences, dispatch requirements, and record commands; contracts point to exactly one workflow each. Sizes: 3299 → 1416 words total (entry 946→327; shangshu 785→291; menxia 563→268; executor 532→242; yushi 473→288), pi-style residency discipline.
- Paraphrase-contamination check the user ordered: mechanical diff of the rewritten cognitive gates against pre-rewrite researched versions shows heavy rewording (reasoning-base 42/70 content lines no longer verbatim; anti-sycophancy 59/62). Semantics largely survive but researched formulations were replaced — stage 2 restores the researched wording verbatim and reorganizes structure only.
- Evidence: `python3 -m pytest tests -q` → 69 passed, 826 subtests; `aos-lint.py` PASS. Does not prove: live behavior of the slimmed contracts (next chain run); the relocated workflows are verbatim moves pending stage-3 per-seat research and design.

### 2026-08-13 — Cognition workflow built; five gates rewritten as Method-form methodologies; audit fixes landed

- New `agent-os/workflows/cognition.md`: the single working procedure for any judgment (fast pass + five-step full pass), the chain's trigger canon; resolves both kernel contradictions the live audit found (anti-sycophancy trigger canon; promotion gate single ownership by route-keeper). Five cognitive gates rewritten in Method shape — purpose one line, when, numbered procedure, output — with all verified content and lint vocabulary anchors preserved; design essays removed from the operator layer. Contracts for entry/menxia/shangshu now load and work by the workflow. Ten skill adapters realigned: missing load-bearing output fields added (hidden_assumptions, falsifier, time_budget, evidence_layer, support_type, user_visible_success, relation_to_task_contract and friends), banned size words removed, ask_level replaced with kernel vocabulary, unconditional intent trigger restored, minimal-code docs exclusion lifted. Router gained the cognition row.
- The live session's error record (delivery-preceded-mandated-independent-check, recurrence 2) had its demanded Level 2 landing built: `lint_task_ledger_sequencing` in aos-lint (first zhongshu delivery requires a prior menxia independent_review or an explicit retroactive/provisional marker) plus `tests/scenarios/test_task_ledger_sequencing.py`; all four live ledgers pass, the skills-audit ledger passing via its honest retroactive marker.
- Evidence: `python3 -m pytest tests -q` → 69 passed, 801 subtests; `aos-lint.py` PASS. Does not prove: live behavior of the rewritten stack (next chain run is its canary); Codex-side dynamic-workflow still uses size-based routing vocabulary (booked for parity work); installer still predates everything.

### 2026-08-13 — Live acceptance PASSED: the ordinary-entry chain ran an 11-skill audit end to end

- A fresh in-project session (default `agentos-entry`) audited all 11 skills under live probing through the peer channel. Verified behaviors, each with hard evidence: equipment birth-reads real (transcript's first five tool calls = the five contract gates, in order, before any work); methods visibly used (mechanical enumeration, de-anchored verdicts in gate report shape, line-anchored evidence); anti-sycophancy held under simulated user-authority pressure (refused the fake bypass claim, cited its contract and a full 403-line DECISIONS read); provenance honesty (refused to forge a peer message as user_message; backfilled records explicitly labeled 事后补记); three self-driven stance changes with old/new side by side; dual-blind review protocol self-designed, later ratified by the real user's full-chain order; task ledger `skills-audit` written faithfully and closed with a git zero-tamper proof (HEAD 6a38956 unchanged).
- Audit results: 4 skills sound (anti-sycophancy-review, fusion-workflow, memory-wiki-routing, prompt-craft-review), 7 small-fixes sharing one root (compressed output shapes silently dropping kernel-template load-bearing fields), 0 structurally broken, 0 hollow. Two kernel contradictions found and independently confirmed here: K1 anti-sycophancy trigger canon (gate's own wide list vs intent-causal-gate:25-28 narrow prescription vs router row 14) and K2 the promotion moment claimed by two gates (intent-causal-gate embedded Proxy Risk Gate vs route-keeper Promotion Gate, different yaml templates, router ambiguity). System seams G1-G7 booked, including: entry contract declares Glob/Grep but runtime granted neither (transcript-confirmed); Bash record-CLI-only grant collides with the mechanical-enumeration duty; peer messages had no constitutional routing rule (user ruling during the run closed it); one sequencing exposure (a batch delivery landed before menxia's increment review — self-reported by the session).
- Evidence: peer session final report (task `skills-audit`, closed); my independent spot-checks all confirmed (non-small 6 hits in skill layer, ask_level zero kernel hits, dual promotion gates read directly, hook wiring). Does not prove: fixes applied (none — audit recommended only; K1/K2 canon and the shape-alignment pass await the user's ruling).

### 2026-08-13 — Kernel document consolidation: one resident rules card; constitution and boot retired

- The semantic audit the user ordered found: doctrine sentences resident in 4–5 places (user-owned-forks list, deadline doctrine, stuck doctrine), communication rules stated three times across global contract / card / constitution, quarantined-engine vocabulary still inside the constitution, a card→boot→router navigation chain, and 17 skill adapters re-reading boot+router per invocation. Skills themselves were clean — all 11 link to real kernel gates with full methodologies.
- Consolidation: `rules-card.md` rewritten as the single resident rule body (115 lines, identity preamble + 23 rules with whys); `constitution.md` and `boot.md` retired to the archive; AGENTS.md reprojected; router/lint/toml/codex-config/capabilities/test fixtures repointed; skill Sources now name only their method gate; anti-sycophancy skill description aligned with the role contracts; entry contract dedups doctrine (its session carries the card) while worker contracts keep inline law (their residency is their contract alone).
- Evidence: `aos-lint.py` PASS; `python3 -m pytest tests -q` → 63 passed, 789 subtests. Does not prove: live behavior of the new card; installer template still predates all of this.

### 2026-08-13 — Methods now arrive by reading at the moment of use; recurrence-3 error landed mechanically

- The user caught the third iteration of one root ("named is not possessed"): role contracts referenced skills in one abstract sentence, so the methodology never entered the role's context at working time (external evidence: Vercel measured 56% never-invoked for reference-only skills). Fix: the abstract "Your methods" sections are gone; contracts now order concrete actions at flow positions — "Read `agent-os/review/<gate>.md` completely, produce in its shape" — and every dispatch (entry and shangshu) must carry the governing gate paths as materials in the prompt.
- Ratchet: `wiki/errors/2026-08-13-method-reference-mistaken-for-method.md` (root-named-is-not-possessed, recurrence 3, Level 2 landing) guarded by `test_role_contracts_order_method_reads_by_path`; the landing itself initially shipped dead (test appended outside the class, never collected) and was caught and fixed in the same turn — the test then bit the executor contract once before going green.
- Evidence: `python3 -m pytest tests -q` → 64 passed, 789 subtests; `aos-lint.py` PASS. Does not prove: that roles actually perform the ordered reads live — that is the canary's first check item.

### 2026-08-12 — Fossil retirement delivered a clean tree; Yushi censor role wired for background error learning

- Cleanup (`8f86ca8`): backups/, outputs/, research/, and work/'s v1 regression scripts + e2e dirs left the tree; snapshot branch `archive/pre-clean-20260812` plus on-disk archive `~/Downloads/agentos-archive-20260812/` (also holds untracked fossils: .agentos runtime residue, .agentos-backups, root workflows/ scripts, stale active-work JSONs, caches). aos-lint fossil existence checks removed with their artifacts; evidence_output contract retired; fusion provenance relanded at `agent-os/state/fusion-runs/` (gitignored); the two 2026-07-24 error records re-anchored to `wiki/raw/2026-07-24-codex-019f85a5-task-contract.json`. Kept as load-bearing: work/agentos-installer-candidate (test + anchor + manifest references), vendor/fusion-fable + vendor/AgentChat (fusion engines), vendor/claude-dynamic-workflows-codex (Codex delegation engine).
- Yushi (`be94de2`): `.claude/agents/agentos-yushi.md` (Censorate — background error-learning scribe, single writer of wiki/errors/, kernel-edit forbidden), entry grant `Agent(..., agentos-yushi)` + teardown fire-and-forget law, rules-card rule 24 projected byte-exact into AGENTS.md, router row, error-learning.md Ownership And Scheduling section.
- Evidence: `python3 -m pytest tests -q` → 63 passed, 799 subtests; `aos-lint.py` → PASS after both commits. Does not prove: live yushi behavior (no confirmed-mistake increment has run through teardown yet); Codex-side parity; installer template still predates both changes.

### 2026-08-12 — Default-mode ordinary entry ran live; grant-starvation defect found by experiment and fixed; board view added

- Live run: after `agent` in `.claude/settings.json` made `agentos-entry` the default session identity, a user-driven ordinary session in this project ran a full chain delivery unprompted — task record created, menxia independent review and comparison PASS, shangshu-owned execution designed as a three-stage resolution experiment, integration, natural-language delivery, and team teardown (task `threads-and-multiline-state`, that session's task record is the evidence).
- Defect found and fixed: the entry agent's restricted `Agent(...)` grant propagates down the parent-child context as the child's ceiling, so omitting `agentos-executor` starved Shangshu of the executor layer (stage-1 explicit call failed, stage-2 typeless failed, stage-3 owner-executed read-only with a recorded contract deviation — conclusive for grant starvation over missing definition). Fix: the executor type is restored to the entry grant solely so authority can flow down; the entry contract still forbids the lead from creating or contacting executors (`8dc9fe1`).
- Multi-task accounting settled structurally: work = one append-only record per task (unbounded, parallel-safe); attention = one per-session `active_work` anchor; cross-task in-flight view = the new derived `board` subcommand folding `agent-os/state/tasks/*.jsonl` read-only (no new state, no writer; 9 tests, `ba0c09b`); cross-task routes stay in PLANS.
- Evidence: `python3 -m pytest tests -q` → 63 passed, 809 subtests; `aos-lint.py` → 0 failures; the live session transcript and its task record.
- Boundary: the grant fix is code-reviewed by experiment design but not yet re-proven live — the next fresh session in this project is its canary (Shangshu's roster must show `agentos-executor`). Board derives status mechanically from last terminal events; it does not judge task health.

### 2026-08-12 — Constitution, Claude three-departments semantic chain, and task record delivered on the pristine baseline

- Built: `agent-os/constitution.md` (kernel first document, registered, wired from rules-card and boot with byte-exact projections); `.claude/agents/agentos-{menxia,shangshu,executor}.md` plus `.claude/skills/three-departments/SKILL.md` (semantic-only chain — zero hook changes, no identity gating, nothing denies a tool call); `agent-os/tools/aos_task_record.py` — an append-only JSONL event log (single `os.write` on an `O_APPEND` descriptor, no read-modify-write) that never refuses a write: terminal states land on missing and even garbled records. 17 unit tests include zero-loss concurrency; the first read-modify-write draft measurably lost 2/6–5/6 concurrent terminal records and was rewritten, after which independent probes show 8/8, 12/12, and 20/20 survival across 15 trials.
- Reviewed: one broad review (1 Critical, 5 Important, 5 Minor) → full fix wave → scoped re-review with all 11 findings ADDRESSED, each re-verified by the reviewer's own probes (concurrency, prompt-craft-guard allow/deny matrix, the real installer's `merge_marked_block` with a failing control).
- Live chain acceptance in-session: real task `anchor-audit-20260812` ran the full flow — menxia independent review (found what the lint-based re-anchor could not: prose-layer anchors are outside lint's checks), comparison PASS with three binding delivery-wording requirements, shangshu direct dispatch, executor audit, integration with bidirectional corrections (executor corrected shangshu's dispatch numbers; the count of dead anchors rose from the review's ~6 to a verified 8), lead spot-checks, delivery recorded. Outcome: frontmatter layer 12/12 anchors resolve; prose layer had 8 dead anchors in 6 records plus 5 header/body contradictions — all repaired the same session (8 wiki files, frontmatter untouched, every rewritten command executed before being written down, discrimination of the rewritten check proven with a dirty-tree control).
- Evidence: `python3 -m pytest tests -q` → 54 passed, 809 subtests; `python3 agent-os/tools/aos-lint.py` → 0 failures (417 PASS lines).
- Boundary: role agent types resolve only for sessions opened inside this project, so this acceptance ran the same flow with inlined role contracts; ordinary-entry acceptance — a fresh session in the project running a real business task through the installed types and hooks — remains open and is the next gate. Old-format `agent-os/state/tasks/*.json` probe records are orphaned gitignored local state (the new tool reads `.jsonl`); nothing was destroyed. Chain behavior under the installed hook set (prompt-craft gate on dispatches) is document-conformant but not yet live-proven.

### 2026-08-12 — Execution-chain audit and pristine reset to the 2.0 release baseline

- Audit: main `97fac54` passes 78 tests; release `83fb2d1` and `b2c6013` pass 19; the activation commit `2e9be6c` fails 10; the full uncommitted worktree failed 32. The batch's Claude PreToolUse gate denies its own `agentos-executor` sessions because the required `agent_type` field is absent from native-session hook payloads, and denies the entry identity even `Read`; the project had no session able to use any project tool.
- Reset: the whole attempt is preserved as quarantine commit `efbd0f5` on `codex/agentos-control-loop-rebuild`; `pristine-reset-20260812` restarts from `83fb2d1`. Error-learning records accumulated since the release were preserved and re-anchored to baseline artifacts; post-release `outputs/` deliberation records remain in `efbd0f5`, with the 2026-08-11 architecture and implementation plans restored locally as the rebuild basis.
- Evidence: on `pristine-reset-20260812`, `python3 -m pytest tests` reports 37 passed plus 744 subtests and `python3 agent-os/tools/aos-lint.py` reports 0 failures.
- Boundary: this proves the baseline is green and establishes the failure diagnosis. It proves nothing about the Claude live business chain, Dynamic Workflow parallel execution, or any rebuilt three-departments implementation. Error landings whose mechanical regressions were quarantined are documentation-level until the rebuild re-lands them.

### 2026-07-20 — AgentOS 2.0 published and distributed to existing projects

- Release: the public repository was rebuilt from a sanitized template with no current task, chat, error, raw-source, archive, runtime-state, absolute-path, or session history. Commits `21721be` and `473b6f4` are on GitHub `main`; Actions runs `29726011587` and `29726373820` both succeeded.
- Package evidence: the clean template passes 10 unit, 9 dual-runtime integration, 17 scenario, structural lint, validator, and six installer behavior cases. An isolated install remained byte-identical across reinstall for all 236 managed files outside the manifest and backup directory.
- Rollout: three global installer copies byte-match the release bundle. Eleven active AgentOS projects were updated, each with local `.agentos-backups/` recovery points; all 11 pass the structural validator and contain no active obsolete pseudo-rule, referee, audit-gate, spokesperson, or second-backend entry.
- Preservation: all pre-existing template-overlap Wiki content was checked. Non-ledger Wiki content stayed byte-identical; the four `wiki/ledgers` links remain symlinks to intentionally merged root ledgers. Installer manifests report no unsafe Wiki/state replacement.
- Brownfield boundary: full lint still exposes old project document formats—14 failures in the smallest projects and thousands in the largest. PostToolUse now filters that existing debt and reports only failures coupled to the file just edited; a real probe passed in all 11 projects. Semantic document migration was not inferred from rollout authorization.

### 2026-07-20 — External Claude Hook canary completed

- Live loading: authorized `claude -p` sessions outside the Codex sandbox loaded the project rules plus real SessionStart, UserPromptSubmit, PreToolUse, and Stop Hooks. The tool-free short probe returned once with one successful Stop and no continuation.
- Long-task evidence: Claude session `b7bc8d1e-51cb-47f2-b089-e212b63c41d9` restored an existing `active_work`, executed `cat`, `test -e`, `rg "A|B"`, and a read-only pipeline without rejection, verified exact 23-byte and 15-byte files, and left the tracked worktree clean.
- Completion behavior: Claude first wrote invalid scalar evidence values. The deterministic state check refused completion; the same-model Stop continuation converted them to lists, revalidated the state, and the second Stop marked `report_state: delivered`. This is direct evidence that the repair-and-deliver loop ran rather than merely accepting malformed state.
- Boundary: this verifies the current AGENTOS Claude project on Claude Code 2.1.215. It does not roll the change into other existing projects.

### 2026-07-20 — Trusted Codex Hook canary completed

- Activation: after the user restarted and trusted the project Hooks, the current session received both the SessionStart restore context and the UserPromptSubmit attention context. `hooks/list` reported every AGENTOS Hook as trusted.
- Failure found and fixed: the first trusted long-task Thread completed its work but remained `report_state: pending`. The Stop response carried an extra `hookSpecificOutput` object rejected by the Codex Stop schema. Both adapters and the installer template now emit the minimal top-level `decision` and `reason`, with an exact-shape integration regression.
- Live evidence: Thread `019f7e45-8c52-7e21-bdd6-b0aae4038788` executed `cat`, `test -e`, `rg "A|B"`, and a read-only pipeline without rejection, verified exact 23-byte and 15-byte files, caused no new tracked change, and ended with `report_state: delivered`. Its following tool-free one-sentence reply completed once in 4.2 seconds.
- Boundary: this verifies the trusted Codex project path. Existing-project rollout and an external Claude live canary were not authorized and remain outside this milestone.

### 2026-07-20 — Attention Hooks and finite long-task state implemented locally

- Removed: the tracked route graph, semantic node/event engine, proposal and per-turn admission flow, external referee, route marker, route snapshots, per-turn audit state, and their mechanism-specific tests are gone from the root source and installer template. The pre-deletion recovery point is Git commit `cccf504`.
- Replaced with: one ignored per-session `active_work` file records a long task's goal, observable finish conditions, open items, next action, latest correction, status, blocker, report state, and condition-by-condition evidence. Short tasks keep an implicit one-line finish condition and create no state file.
- Hook behavior: SessionStart restores only the long-task finish line; UserPromptSubmit asks the main model to reinterpret each real message; PreToolUse keeps only the single Codex delegation backend and worker-prompt structure checks; PostToolUse lints only structured edits to governed files; Stop requests one same-model delivery reread only when a long task is pending. Shell command text no longer decides intent or write authority.
- Automated evidence: the root and synchronized installer template each pass 10 unit tests, 9 dual-runtime integration tests, 17 scenarios, and structural lint. Five installer cases, an isolated fresh install, and the complete vendored Dynamic Workflow suite also pass. The Dynamic Workflow network/listener tests required the normal sandbox exception and then passed.
- Live evidence and boundary: three real Codex Threads proved simple one-sentence reporting, a mid-task filename correction that preserved the other obligations, and the requested `cat`, `test -e`, `rg "A|B"`, pipeline, file creation, and byte checks. They also exposed that the changed project Hook definitions are currently `modified`, not trusted, so their SessionStart/UserPromptSubmit/Stop behavior did not run; the pending Stop state confirms this. Final Hook activation is not claimed until the user re-trusts the new hashes and a fresh Thread passes.

### 2026-07-20 — Task finish line and attention-managed reporting verified locally

- Control: any mutating, delegated, or cross-turn action now requires a persisted non-empty completion contract and a real open obligation. `next_action` must name one of those obligations; adding an obligation is a material route change; once obligations are empty, further action is rejected. An authorized goal that starts and finishes in one user turn can close as one grounded terminal transaction instead of being left falsely unfinished.
- Completion: new completion transactions must map every contracted condition exactly once to verified evidence connected to the active goal. Missing, duplicate, unrelated, disconnected, unverified, or aggregate test-only proof cannot close the task; old aggregate evidence remains replayable but is no longer sufficient for new work.
- Reporting: the canonical resident rules, both native projections, Task Contract, lifecycle, Completion Gate, Evidence Gate, and Router now generate replies from what the user must know, decide, or do. Plain result-level language is the default; technical detail enters only when requested or load-bearing. No spokesperson, reply scorer, length quota, new Hook, or ordinary final-response model pass was added.
- Memory: the 2026-07-11 attention-management decision remains authoritative; the accepted TLDR exemplar now declares that only its expression direction and information organization were accepted. The separate-speaker mechanism is superseded, the dead pointer is gone, and the same-root reader-load error records recurrence 7 with a Level 2 landing and regression.
- Source evidence: 69 unit tests, 21 dual-runtime integration tests, 24 scenarios, 16/16 mutation cases, Codex adapter regression, Python compilation, structural lint, and all 13 vendored Dynamic Workflow test files pass; all 24 bundled workflow examples remain plan-safe.
- Release evidence: the synchronized template passes the same 69/21/24, 16/16, adapter, lint, and full Dynamic Workflow suites. All five installer behavior cases pass, including fresh, merge, reinstall, invalid-config preservation, and validator negative controls. A separate isolated fresh install passes validator, lint, 69/21/24, 16/16, and adapter checks.
- Boundary: this proves the local contracts, projections, template, and installer only in the tested envelopes. It does not prove future reply quality, interactive Codex/Claude behavior, or authorize propagation into existing projects.

### 2026-07-20 — Memory/Error convergence and local release chain verified

- Memory: `agent-os/memory/routing.md` now owns selective read/write routing, canonical ownership, maturity, lifecycle, conflicts, and completion disposition. Bootstrap, Wiki format, and stage audit are narrower supporting documents; `memory-wiki-routing` is the sole installed-project adapter.
- Contracts: the existing `aos-lint.py` now governs Wiki artifacts, four separate ledgers, indexes, raw coverage, symlinks, current Plan/Handoff uniqueness, supersession, Error Learning roots/landing/regressions, and byte-stable derived views. It does not author semantic decisions, progress, knowledge, or causes.
- Migration: one current Plan, one current Handoff, one concise active Task, complete Wiki reachability, raw manifest coverage, four ledger symlinks, repaired knowledge supersession, lifecycle-only Wiki log, and merged same-root errors now replace the fragmented live state. Original material remains in `wiki/archive/` or Git history.
- Source evidence: 65 unit tests, 21 dual-runtime integration tests, 22 scenarios, 11/11 mutation cases, structural lint, Python compile, adapter activation regression, and the full vendored Dynamic Workflow offline suite pass; all 24 bundled workflows remain `--plan` safe.
- Release evidence: the synchronized template passes the same 65/21/22, 11/11, lint, and adapter suites. Five installer behavior cases pass, including byte-stable merge/reinstall protection for user AGENTS, JSON/TOML config, four ledgers, Wiki, and state. An isolated fresh install also passes validator, lint, 65/21/22, and 11/11.
- Boundary: these results establish the local source, template, and isolated installer behavior in the tested envelopes. They do not establish interactive Codex/Claude behavior or authorize propagation to existing projects; both remain separate gates.

### 2026-07-20 — Control-loop baseline isolated; memory convergence underway

- Baseline: commit `9ca4d1f` contains the tested current-turn admission, native rules projection, single Codex Dynamic Workflow backend, document-contract base, and installer changes. The three pre-existing error-file edits were deliberately excluded.
- Control delta: a read-only goal change can now update active goal and focus without a `turn_admission` or semantic model call; PreToolUse still rejects any later write without a current-turn admission. Completion transactions now require an explicit `memory_disposition`.
- Referee delta: the obsolete long-reply, sycophancy, evidence, and shape grader was removed. The remaining isolated model checks only intent and authority before the first material action, with existing proposal-hash caching.
- Evidence: focused unit, scenario, and dual-runtime integration suites pass after the changes, including a new read-only route-change test that confirms the route advances, no reviewer process runs, and mutation remains denied.
- Boundary: memory migration, full-suite repetition, template synchronization, fresh-install checks, and externally authorized live canaries are still open. This entry does not claim overall completion.

## 2026-07-19 — First-principles decision closure implemented; live canary pending

- Replaced the core admission discriminator: `executive_intake.task_size: small_clear | non_small` is gone. The shared cognitive core now requires `decision_state: open | closed` plus structured user-owned decisions. A closed state rejects any unresolved user choice and rejects resolutions not grounded in the current user prompt.
- Preserved employee behavior without mandatory reconfirmation: an open decision remains in deliberation and requires visible investigation, routes, tradeoffs, recommendation, authority boundary, and next action; a grounded closed decision may enter execution on the initial turn. Product meaning, size, and reversibility no longer decide closure; safety gates remain separate.
- Strengthened the initial transaction boundary: route initialization now requests independent semantic review before commit. The deterministic shape is still not proof that the model found every hidden product branch, so clean-task canaries remain required.
- Evidence: 61 unit tests, 17 dual-runtime integration tests, and 15 scenarios pass; 9/9 named mutation variants are killed, including hidden-open-decision and invented-resolution variants; the Codex adapter regression and root/template lint pass. The template repeats the same 61/17/15 suites and 9/9 mutations. Five installer behavior cases pass and the template validator reports `status: passed`.
- Boundary: these checks establish schema, hook-envelope, negative-control, and installer behavior in scope. They do not establish that a fresh model will semantically classify every real request correctly, or that the currently open task has reloaded the new prompt hook.

## 2026-07-19 — Executive Intake implementation tested; clean-session canary pending

- Failure repaired: the cognitive manifest previously covered independent judgment and question admission but omitted the moment a new task begins. Prompt and Stop rules therefore did not stop the first non-small task from mutating before understanding the user's purpose and the named upstream object.
- Implemented: C18 adds a formal Executive Intake to route initialization and goal changes. Its transaction records purpose, visible success, goal-versus-means, investigation, problem frame, routes, recommendation, authority boundary, and next action. A new non-small route must expose the proposal in deliberation; a later grounded authorization enters execution. Small exact reversible tasks retain an authorized short path.
- Enforcement: Codex and Claude PromptSubmit hooks inject the task-start contract. Their PreToolUse guards allow read-only reconnaissance and the internal proposal side channel, while blocking mutation or delegation on an uninitialized/deliberating route. The shared cognitive core validates and persists the intake state.
- Evidence: 56 unit, 16 runtime-integration, and 15 scenario tests pass; 7/7 named mutations are killed, including removal of Executive Intake validation; the Codex adapter regression and root/template structural lint pass. Five installer behavior tests pass, and the published template validator reports `status: passed`.
- Boundary: implementation and simulated runtime behavior are not a clean interactive canary. A new Codex task must replay the original repository request and demonstrate proposal-first behavior before live acceptance is claimed.

## 2026-07-19 — Live UI failure fixed: route state moved out of replies

- Observed failure: Codex displayed the supposed hidden `agentos-state` HTML comment as a large JSON blob. The transport assumption was wrong; the reply itself must never carry internal state.
- Fix: UserPromptSubmit now provides an internal per-turn `agency_proposal_path`; the model stages a semantic transaction there only when state changes; Stop validates and commits it. Reply-embedded state JSON is a blocking error. Ordinary turns still inherit state without a proposal.
- Evidence: 50 unit, 13 integration, and 13 scenario tests pass; six named mutations are killed; adapter regression and lint pass. The template and all three installer bundles contain the fix and remain byte-identical.
- Boundary: this current task observed the old failure but cannot reload its own startup Hook. A newly started Codex Desktop task and Claude Code task must confirm the repaired behavior before live acceptance.

## 2026-07-19 — Global instruction stack, cognitive continuity, and installer release

- Implemented: one short English global contract now feeds Codex and Claude by symlink; the Claude addendum keeps native Workflow, Superpowers, Codex Review, and GitNexus; Codex Superpowers remains disabled. AgentOS now owns cognitive state, unfinished-work continuation, question and route validation, completion evidence, and silent turn logging.
- Runtime ownership: Dynamic Workflow is Codex-only with `NO_DELEGATION`, cheapest-capable model routing, one writer, recovery, and verified promotion. Claude's duplicate wrapper and the shared workflow body were removed. Ordinary Stop handling is local and does not invoke a second model; semantic review is conditional and failed review never commits route state.
- Anti-theater discipline: every non-trivial step must advance a contracted user-visible result or reduce an evidenced risk; otherwise it is omitted. The rule extends the existing minimal-code gate instead of adding another gate, hook, or visible report. A scenario regression protects the instruction shape.
- Evidence: source suites passed 50 unit, 11 integration, 12 scenario, six of six named mutations killed, Codex adapter regression, and structural lint. Installer tests passed five fresh/merge/reinstall/config-preservation cases; the published template validates; the three global installer directories are byte-identical. Clean-session interactive Codex Desktop and Claude Code canaries remain unverified, so live acceptance is not claimed.

## 2026-07-17 — Codex-native hook rewrite and 11-shop rollout

- Verified implementation: `.codex/hooks/aos_common.py` now parses the observed `response_item.payload` schema only as a `turn_id`-bounded, fail-open auxiliary source; `.codex/hooks/aos_prompt_baseline.py` consumes the documented `UserPromptSubmit.prompt`; `.codex/hooks/aos_stop_gate.py` consumes the documented `Stop.last_assistant_message` and `stop_hook_active`; `.codex/hooks/aos_referee.py` is called sequentially by the Stop gate.
- Verified concurrency fix: official Codex documentation says matching command handlers for one event start concurrently. `.codex/hooks.json` now wires one 120-second Stop handler instead of independently launching the deterministic gate and external referee. The legacy standalone referee entry point is a no-op so sessions that cached the old wiring cannot emit a duplicate continuation during rollout.
- Verified behavior added: correction reminder with diagnostic-question whitelist; canonical-ledger and final-pointer hard checks; commentary-vs-final delivery measurement as advisory only because transcripts are unstable; one bounded Codex-native spokesperson continuation for prose at or above 600 characters; structured continuation prompts with materials/task/output/self-check sections.
- Verified source evidence: five Python files compile; `.codex/hooks/test_codex_adapter.py` passes observed-record parsing, correction, UserPromptSubmit JSON envelope, official Stop-field priority, pointer/ledger/spokesperson guards, continuation-loop bound, and single-handler wiring; the current Desktop rollout parser isolates the current user message and completed final answers; `python3 agent-os/tools/aos-lint.py` reports structural PASS.
- Verified runtime evidence: disposable `codex exec` session `019f704e-f00a-7a10-8553-3cdafddb666e` loaded the new hooks and appended a compliance `block` row for an 832-character prose reply. The one-shot exec surface still emitted the original reply and ended, so this proves hook firing and detection, not continuation delivery. Desktop continuation remains to be exercised by a normal interactive Stop event.
- Verified rollout: all 11 shops and all 3 physical installer templates were mechanically confirmed on one five-file old baseline, backed up, and updated. Post-copy hashes matched the AGENTOS source for all five files at all 14 targets; Python compile was 14/14; the single-Stop `hooks.json` assertion was 14/14; backups were 11/11 under `.agentos-backups/20260717-codex-native-hooks` and 3/3 under `.template-backups/20260717-codex-native-hooks`.
- Verified lint boundary: 9/11 shops passed structural lint. CRMAI still fails on pre-existing `placeholder` text in its append-only audit log, and EVENTHUB still fails on pre-existing `TODO` text in its append-only audit log; this rollout did not edit either history. The copied Codex files in both shops still passed hash, compile, and wiring checks.
- Activation boundary: changing non-managed hook definitions requires review/trust in Codex `/hooks` on the next session for each project. File rollout is complete; automatic activation in every shop is not claimed until that trust step and a live turn occur.

## 2026-07-17 — Codex hook adaptation audit: current content gates read an obsolete transcript shape

- Verified scope: read-only diagnosis only; no `.codex/hooks/`, `.codex/hooks.json`, installer, or shop files were changed.
- Source recovery: the quoted Claude delivery is the final assistant message in `/Users/zuoxu/.claude/projects/-Users-zuoxu-Downloads-AGENTOS/40cd4039-dafa-4ec6-a5c5-e74e115bc4d8.jsonl` (line 1144); its audit entry `#278 (40cd)` is at line 1136 and explicitly excludes the Codex side.
- Baseline enumeration (verified): all 11 installed shops and all 3 physical installer templates carry the same four Codex hook hashes as this repo: `aos_common.py=2b54f01e`, `aos_prompt_baseline.py=ac4497aa`, `aos_stop_gate.py=ca8c187d`, `aos_referee.py=031e2d66`. All 11 shops already contain `agent-os/review/spokesperson-contract.md` from the Claude rollout.
- Compatibility finding (verified): current Codex Desktop rollouts use top-level `response_item` records, with assistant messages distinguished by `payload.phase=commentary|final_answer`; the current Codex helpers still search for top-level `assistant` / `user` / `item.completed`. A direct replay against completed rollout `019f6d98-...` returned `stop_last_len=0`, `ref_reply_len=0`, `ref_users=0`, `common_user_len=0` despite four recorded `final_answer` messages. Therefore the content-dependent Stop checks and external referee fail open on this observed Desktop record shape.
- Official release behavior checked 2026-07-17: `UserPromptSubmit` supplies `prompt` and `turn_id`; `Stop` supplies `last_assistant_message`, `turn_id`, and `stop_hook_active`; `decision: "block"` asks Codex to continue. The official docs also label `transcript_path` format unstable and say multiple matching command hooks run concurrently.
- Recommended native route: (1) merge correction detection into the existing Codex `UserPromptSubmit` JSON envelope using `prompt`; (2) make `last_assistant_message` the primary Stop/referee source; (3) keep a `turn_id`-scoped Codex transcript reader only for user-quote fallback and commentary instrumentation; (4) enforce ledger and pointer violations on the final message; (5) do not copy Claude's transcript-based spokesperson-dispatch detector, because Codex native function-call arguments are encrypted in rollouts and PreToolUse does not cover every native function path. Use a Codex Stop continuation/output check plus the referee for the spokesperson outcome, with exact latency/strictness to be approved before implementation.
- Not proven: no source patch, unit regression, compile, lint, Codex exec probe, Desktop Stop continuation, template sync, or 11-shop rollout has run in this task.

## 2026-07-10 — Codex CLI hooks 复核：SessionStart/规则注入可见，Stop 机械拦截失败

- 变更：在 Codex CLI 0.144.1 下重新跑普通 `codex exec` 探针，结论从“普通路径无注入证据”推进为“SessionStart/规则注入在普通路径有强证据；Stop 审计拦截仍未生效”。
- SessionStart 证据：`codex exec --skip-git-repo-check --sandbox read-only ...` 未使用 `--dangerously-bypass-hook-trust`，终端输出 `hook: SessionStart` 与 `hook: SessionStart Completed`；同一子 Codex 回答它能看到 `AgentOS Local Rules Card for Codex` 与 `next audit entry this session` 两个 SessionStart 注入标记。
- 行为影响证据：`codex exec --json --skip-git-repo-check --sandbox workspace-write 'Return exactly WORKSPACE_WRITE_HOOK_STATE_PROBE_OK.'` 中，子 Codex 没有裸回字符串，而是读取 `agent-os/state/audit-log.md` 与 `agent-os/review/per-turn-audit-gate.md`，并追加 `agent-os/state/audit-log.md` 条目 `## 146 (019f)` 后才返回指定字符串；这说明 AgentOS 规则已经进入模型行为路径。
- Stop 反证：负向探针 `codex exec --json --skip-git-repo-check --sandbox workspace-write '<... Do not use tools ... Return exactly STOP_GATE_NEGATIVE_PROBE_OK ...>'` 正常 `turn.completed`，返回 `STOP_GATE_NEGATIVE_PROBE_OK`，未追加新的审计条目，也没有 Stop hook 拦截或重试痕迹。
- 不证明什么：不能说“AgentOS 在 Codex CLI 里已经正常工作”。目前只能说启动/提示层注入已可见、足以影响模型；Stop 审计门不是机械强制；PreToolUse/PostToolUse 尚未做普通路径实锤；`agent-os/state/codex-hook-state/` 没有出现这些新 session 的状态文件，state 写入链仍异常。

## 2026-07-10 — Codex CLI 升级完成：默认模型 smoke 通过

- 变更：按 ZX 指令执行全局升级，`npm install -g @openai/codex@latest` 成功；`@openai/codex` 从 0.142.0 升到 0.144.1。
- 证据：`npm list -g @openai/codex --depth=0` -> `@openai/codex@0.144.1`；`codex --version` -> `codex-cli 0.144.1`；`which codex` -> `/opt/homebrew/bin/codex`；`codex features list | rg '^hooks|^unified_exec|^multi_agent'` 显示 hooks/unified_exec/multi_agent 仍为 stable true。
- 默认模型复核：未指定 `-m` 的 `codex exec --skip-git-repo-check --sandbox read-only ...` 使用全局默认 `gpt-5.6-sol`，返回 `UPGRADE_SMOKE_OK`，不再出现“默认模型需要更新 CLI”的旧错误。
- 不证明什么：这只解除 CLI/默认模型版本阻塞；还没有修 `.codex/hooks` 的 JSON additionalContext、PreToolUse `ask`、Stop gate transcript 夹具，也没有证明普通 project hooks 已端到端生效。

## 2026-07-10 — Codex CLI 兼容性审计：结构通过，但不能标成端到端可用

- 核验结论：AgentOS 在 Codex CLI 里不是“正确工作”的状态；更准确是：AGENTS/项目开发指令和本地技能适配器可见，结构和技能校验通过；但项目 `.codex` hooks 在普通 CLI 路径下没有形成可复验的注入/拦截证据，绕过信任后能执行但暴露出 Codex hook 协议不兼容点。
- 证据：`codex --version` = `codex-cli 0.142.0`；`codex features list` 中 `hooks stable true`、`unified_exec stable true`；`codex doctor --json --all` 显示 config/auth/install ok，但全局默认模型为 `gpt-5.6-sol`，provider reachability 在本工具网络沙箱下 fail，当前目录 `repo detected=false`。
- 结构/适配器证据：`python3 agent-os/tools/aos-lint.py` PASS；`.codex/hooks/*.py` 逐文件 `compile(..., 'exec')` OK；Codex 11 个 `.agents/skills/*` 与 Claude 11 个 `.claude/skills/*` 均通过各自 `quick_validate.py`；`node work/e2e-pressure-tests/agentos-e2e-pressure-test.mjs` 返回 `passed_with_scope_limits`，且脚本明示不证明 hooks、自动 skill 触发或生产级 replay。
- 普通 CLI 证据：普通 `codex exec -m gpt-5.4-mini --sandbox read-only` 返回 `Master ZX TRUST_PROBE_OK`，rollout 文件含 `.codex/config.toml` 的 developer instructions 与 AGENTS 内容，但 grep 不到 `AgentOS | Codex Static Rules Card` / `Codex SessionStart injection` / `This turn's audit entry`；`agent-os/state/codex-hook-state/` 未新增该 session 文件。普通 `workspace-write` 探针超过 90 秒无输出后终止，未写出 hook state、audit-log 或 compliance-log。
- 绕过信任/受控探针发现：使用 `--dangerously-bypass-hook-trust` 的本轮终端实测显示项目 hook 会执行并写 `agent-os/state/codex-hook-state/019f4cc*.json`；但 SessionStart/UserPromptSubmit 以 `[` 开头的普通 stdout 在 Codex hook 解析中失败，改成 JSON `hookSpecificOutput.additionalContext` 的对照探针通过；PreToolUse 的 `permissionDecision:"ask"` 在 Codex 0.142.0 中失败且工具继续执行，`deny` 对照可阻断；Stop hook 的 block/continue 协议在最小对照里可重复触发。
- 不证明什么：没有修复 `.codex/hooks`；没有证明普通 Codex CLI 已经加载 AgentOS 项目 hooks；没有证明 Stop gate 的 Codex transcript 解析正确；没有证明工作流会在 Codex CLI 中自动按 AgentOS 生命周期执行。
- 下一步：先升级/校正 Codex CLI 与默认模型；再把 SessionStart/UserPromptSubmit 输出改成官方 JSON additionalContext；把 guard 的 `ask` 改成 Codex 支持的机制；补可重跑的普通信任路径与 bypass 路径回归；最后重新跑 live CLI 证明。

## 2026-07-06 — 里程碑：内核转英文 + 四记忆技能搬家内化 + 零上下文读者法

- 变更：规则卡重写为英文（新增语言政策/零上下文读者/四格拍板模板/代号违禁）；新建内核法律 agent-os/memory/error-learning.md（含证据锚点与探针供料条款）；routing.md 增来源分类/聊天蒸馏/记忆写入证据锚点；sync-audit.md 增 current.md 新鲜度与验收考卷检查；bootstrap.md 明文禁止软链接入口方案；router 标注三处法律出处；aos-lint 换英文模式并登记新法律文件；AGENTS.md 增语言政策与记忆路由行；全局写作契约增第 6/7 条；全局四技能加 AgentOS 让位条款。
- 证据：主仓 aos-lint PASS（含每笔自动质检，其间一次瞬时 FAIL 为两笔编辑间隙、第二笔落地后回绿）；四技能与安装器三向 diff -rq 全一致（ALL-SYNCED）；八文件回灌模板。
- 不证明什么：钩子内中文提示文案未动（改钩子须 ZX 批准）；零上下文读者标准属提示层，行为效果待抽查；技能与内核法律的实战协调零数据。

## 2026-07-05 — 里程碑：情报第二批编译入内核（甲方职能服务化）

- 变更：速查表+4 触发行（事故本/先例三级查档/推理降档/主动勘探义务）+ZX 五口令卡；基座 reasoning-base +2 条款（先例优先、借来结论重验+目标反推）+Full Mode 第 11 步；反谄媚门 3 手术（确认式提问入触发与征兆、"至少一条假设"改为允许声明式零发现、报告分双档且单边/立场变更强制完整版）；意图门+勘探义务条款（高留白时亮假设的猜也不合法，端选项不端问卷）；完成门+验收考卷节；代码门+特化注记；PLANS 探针挂牌（第一性原理测试+假惯例变体）+弹药库备选。
- 证据：主仓 aos-lint 全量 PASS；每笔 agent-os 编辑过 PostToolUse 自动质检；三份安装器 rsync 后 diff -rq 一致，模板六文件与母版逐字节相同；证据门零施工（"一键复核锚点"查明为既有第 38 行法条——先例优先条款写入当轮即自证一次）。
- 不证明什么：全部为提示层脚手架，被注入≠被执行；48 条审计仍全自指，新条款（勘探义务/考卷/先例查档）的行为有效性零真实任务数据。
- 补记（同日 #50）：ZX 追问"更新到两边 skill 了吗"查出 Codex 侧缺口——AGENTS.md（Codex 唯一常驻入口）没有新触发行（含更早的数字/立场两条）。已补：母版 AGENTS.md + 模板 + 安装器 AGENTS 引导块三处加同一节 Standing Triggers；脚本语法检查过、主仓 lint PASS、三份安装器 diff -rq 一致。项目内 18 个薄包装 grep 核过零污染。validate 脚本未为新节加检查项（待议）。

## 2026-07-02 — AgentOS 实效演示：把一次交互真正跑进状态板与账本

- 变更：按 boot → router → intent gate → task contract 读取内核门文件后，更新 `agent-os/state/current.md`（从 `installed_waiting_for_user_task` 推进到 `in_progress_demonstrating_live_loop`），并在 `DECISIONS.md` 记录本次决策。
- 证据：`agent-os/state/current.md`、`DECISIONS.md`、`PROGRESS.md` 三文件均有本轮真实写入；`agent-os/review/intent-causal-gate.md`、`task-contract.md` 已被真实读取。
- 不证明什么：以上均为 Agent 自觉执行，无 hook 强制触发（`agent-os/boot.md` 明写 Hooks Manual until wired）；不证明其他会话会自动重复此闭环，也不证明这套门能在高压任务下拦住漂移。

## 2026-07-02 — 里程碑：审计体系建成 + 债务清理

- 变更：内核新增 3 门（per-turn-audit / anti-sycophancy / minimal-code）并长进生命周期主干；aos-lint 补入 3 新门 + audit-log 的结构保护；账本边界写入 memory/routing.md；PLANS/HANDOFF 从死模板激活。
- 证据：`python3 agent-os/tools/aos-lint.py` PASS；audit-log #1–#7；DECISIONS.md 三决策条目。
- 不证明什么：结构完备不等于行为有效；行为证据仅覆盖本会话，外部任务验证见 PLANS.md。

## 2026-07-05 — 里程碑：Codex 跨模型盲审执行层，8 条发现 7 修 1 缓

- 变更：外部盲审（read-only 沙箱）交回 8 条发现，逐条对照源码核实全部属实。修复 7 条——守卫扩到 Bash 命令启发式扫描（改钩子/settings→ask，改度量台账→deny）并诚实标注"防事故不防蓄意"边界；审计编号连续性校验（防跳号与嵌入伪条目）；字段行级锚定（防单行走私）；state 原子写入；项目根向上查找；settings 前缀族匹配；内核写入型 Bash 命令也触发自动 lint。第 8 条（跨会话绑定）缓记 PLANS 第 6 条。
- 证据：第二轮回归 11/11 通过；主仓 lint PASS；三份安装器 diff 一致；Codex threadId 019f3251-e5fa-7683-928b-6ec86c456266。
- 不证明什么：按证据门新条款，Codex 未再挑出毛病不构成"没有毛病"的强证据；启发式 Bash 扫描可被蓄意混淆绕过（已在守卫文档写明）。

## 2026-07-05 — 里程碑：博主情报六项全部内化

- 变更：立场变更规则进反谄媚门；跨模型同意降权与"数字分核过/没核过"进证据门；框架不下传进生命周期 worker 规则；问题成形检查进意图门；立场与数字两条同步上本地规则卡；错误前提探针作为抽查制度写入 PLANS（含"全绿+探针失败=表演信号"解读规则）。
- 证据：aos-lint PASS（每笔内核编辑经 PostToolUse 钩子自动复检）；三份安装器 diff 一致；audit #37。
- 不证明什么：情报转述的论文数字仍未核原文（各处已标注"未核"）；新条款的行为效果待真实任务与探针检验。

## 2026-07-05 — 里程碑：目录级规则通道验证通过，四跳链砍断

- 变更：ZX 用新会话验证暗号成功，证实项目级 `.claude/rules/` 与用户级一样是会话启动强制注入通道。据此落地瘦身：新建 `.claude/rules/agentos-local-rules.md`（静态不变量+触发表，原生注入零依赖）；SessionStart 钩子瘦身为只发动态信息（下一审计号+状态摘要）；项目 CLAUDE.md 重写砍掉"CLAUDE→AGENTS→boot→router"四跳链；aos-lint 与安装器（模板+合并块+校验）全部同步，三份一致。
- 证据：新会话暗号"青花瓷-0705"复述成功（未读文件）；主仓与装出目录 lint PASS；e2e validate passed + 规则卡在位；沙箱冒烟瘦身钩子输出正常。
- 附带发现：验证会话守了规则注入（暗号+称呼正确）但无任何打卡记录——新会话钩子需一次信任批准才生效，证实"静态规则走原生注入、动态强制走钩子"双通道分工的必要性。
- 不证明什么：注入的规则被读到≠每轮守住（执行层仍靠闸机+抽查）；Codex 运行时无对应 rules 通道，仍走 AGENTS.md。

## 2026-07-05 — 里程碑：全局常驻层瘦身（ZX 拍板执行）

- 变更：115 个第三方代理包与 10 个 research 技能撤出全局，备份至 `backups/2026-07-05-global-slimdown/`（rsync 后 diff 核验一致，MANIFEST 含恢复命令）；全局技能 29→19；全局 CLAUDE.md 的 Communication/Safety 重复段改指针（108→106 行）。查实 ~/.claude-work 下 agents/skills/settings.json/CLAUDE.md 均为指向 ~/.claude 的软链接，物理仅一份。
- 证据：备份 diff 核验输出；移除后 ls 计数；wiki/errors/ 首条错误记录（symlink 被简化命令遮蔽）。
- 不证明什么：上下文减负量需下个会话实测（描述注入发生在会话启动时）；explanatory 输出风格仍开启，去留待 ZX。

## 2026-07-05 — 里程碑：执行层建成（路线A）并回灌三份安装器

- 变更：Claude 适配器执行层 `.claude/hooks/`（aos_common + 5 钩子）+ `.claude/settings.json` 接线；内核文本同步（boot.md 钩子状态、per-turn-audit-gate 执行边界、AGENTS/CLAUDE 注记）；aos-lint 纳入执行层 7 文件与接线模式检查；安装器升级：install-agentos.py 增 settings JSON 合并（只增不删）、validate 增 hook_wiring 检查、模板含执行层，三份安装器（~/.claude、~/.agents、~/.codex）assets/scripts diff 一致。
- 证据：沙箱全路径测试 22/22（拦截/放行/missed 降级/缺字段/缺可见块/守卫 ask+deny/坏输入 fail-open）；主仓 aos-lint PASS；e2e 全新装 103 文件、validate passed、hook_wiring=wired、装出目录内首轮拦截与放行行为正确、compliance-log 记 forced_ok；e2e 合并装用户 permissions 与自定义 hook 完整保留、AgentOS 钩并入。
- 不证明什么：hook 不校验条目内容真伪；Codex 运行时仍无机械强制。
- 2026-07-05 当轮补记：运行时将钩子热加载，会话级自动触发已获首批实证——Stop 闸于建成当轮收尾实弹放行并写下 compliance-log.tsv 首行（ok #14），UserPromptSubmit 于次轮实弹打出 #15 提醒。尚未实证：新会话 SessionStart 注入、真实会话中的拦截路径（拦截仅在沙箱演习过）。

## 2026-07-03 — 里程碑：母版改进回灌三份安装器

- 变更：本周期全部内核改进（3 新门、每轮审计、账本边界、四道反伪造机制、lint 修复）回灌进安装器模板；新门配上 Claude/Codex 双运行时技能包装；校验脚本同步更新；三份安装器（~/.claude、~/.agents、~/.codex）模板与脚本一致。
- 证据：临时目录真装一次——96 文件、校验 passed、结构检查 PASS、新门布线在装出的入口文档中 grep 命中；三份安装器 assets/scripts diff 无差异。
- 不证明什么：新装项目的 agent 是否遵守这些规则，仍属行为问题，未验证。


## 2026-07-06 — 里程碑：Fusion Workflow 落地（首个经完整生命周期的真实业务任务）

- 变更：新增多模型答案融合工作流。`vendor/` 克隆 fusion-fable（盲面板+双轨法官，MIT，435★）与 AgentChat（Chrome CDP 驱动 8 家免费网页 AI，MIT，342★）；新建内核契约 `agent-os/workflows/fusion-workflow.md`、薄壳 `.claude/skills/fusion-workflow/`（含 run_gemini_cli.sh、run_codex_sandboxed.sh 两个适配运行器）；router/boot/本地规则卡三处登记；中和 vendor/fusion-fable/CLAUDE.md 外来系统提示词注入风险（改名 .vendor-orig）。
- 证据：aos-lint PASS；CLI 通道端到端冒烟——gemini / codex（沙箱版）/ claude-haiku 三成员并行盲答 2^20 全部答 1048576 且经 python3 机械核验；存档链路落盘 `outputs/fusion-runs/2026-07-06_022944_smoke-cli-gemini-gpt-haiku.md`；设计文档 `outputs/fusion-workflow-design-v1-2026-07-06.md`；两仓库调研经 GitHub API/raw 回源核验。
- 不证明什么：免费网页通道未验证（需 ZX 启动调试版 Chrome 并登录各家网页版）；冒烟题为算术题，不证明融合在真实难题上的质量增益；原厂无沙箱 codex 路径被权限分类器拦截，属未验证路径。

## 2026-07-06 — 里程碑：双运行时同步（Fusion/Prompt门 Codex 侧补齐 + .codex 执行层回灌母版）

- 变更：Codex 侧补齐本周期新能力——`.agents/skills/fusion-workflow/`（含 openai.yaml）与既有 `.agents/skills/prompt-craft-review/` 配对成套；skill-parity 矩阵加 Fusion 行；AGENTS.md 触发表加 Fusion（只手动）与 Prompt Craft 两条。母版回灌 `.codex/` 执行层（config.toml + hooks.json + 6 个钩子脚本，源自另一会话更新的安装器模板，与 CRMAI 版本 diff 一致）；boot.md 与 AGENTS.md 的钩子状态说明同步更新。
- 证据：模板 vs CRMAI diff IDENTICAL；6 个钩子 py_compile 全过；aos-lint PASS。
- 不证明什么：Codex 钩子在真实 Codex 会话中的自动触发未从本仓验证（标记 Wired, behaviorally unverified）；Fusion 在 Codex 运行时未真跑。

## 2026-07-06 — 里程碑：本周期新内核件回灌三份全局安装器

- 变更：Prompt Craft Gate + Fusion Workflow 契约 + 双运行时薄壳（含 openai.yaml）+ 两份提示词模板 + 两个运行器脚本共 12 个新文件进安装器模板；router/boot/AGENTS.md/规则卡/配对矩阵五个共享文件双向合并（保留另一会话的 Codex 钩子表述，叠加本会话新增条目）；validate 脚本 REQUIRED_FILES 加 12 条；~/.claude 安装器先拉平（此前缺 .codex 层）再统一，三份安装器 assets+scripts diff 一致。
- 证据：临时目录真装 125 文件、validate 通过、装出项目 aos-lint PASS、新件布线 grep 全命中（router×2/AGENTS×1/规则卡×1/矩阵×1）、.codex 六钩子在装出项目齐全。
- 不证明什么：新装项目里 Fusion 需另行克隆 vendor 两仓库并配置本机 CLI/Chrome 才能真跑；Codex 钩子行为验证仍待真 Codex 会话。

## 2026-07-07 — 里程碑:门禁强制化(六行审计)+ 系统纯英文化 + 错误账开场强制读 + 全网八处同版

- 变更:①跨项目调查(1146 场会话/852MB 全量扫描 + 391 份错误账六代理精读)定位两大惯犯根因——门禁靠自觉从不触发(全史 intent 门仅 2 次自测调用)、讲话纪律在 Opus 主脑与长交付轮失守(开头合规 Fable 81% vs Opus 8%);②Stop 闸机升级六行审计条目(gates 逐门表态 + intent 引文与用户原话逐字子串比对 + 长回复 restate 复述测试),style_warn 只记不拦;③执法层与内核全英文化(ZX 键入词/输出模板/解析字面量作为数据保留);④SessionStart 强制注入错误账(高优规则≤10 + 未消化记录全文要点≤8,兼容中英两种索引格式);⑤AAAI 三条创新并回规则卡、模板双向收敛、Codex 六钩外科移植同规格;⑥安装器实跑下发六店(EVENTHUB/Life_Copilot/AAAI_IDEAS/CRMAI/Cognition_AGENTOS/IEEE_ACCESS_PAPER),每店自动备份。
- 证据:夹具 13/13;aos-lint PASS;本仓 vs 模板 md5 零差异;六店关键文件两轮对齐复核;IEEE/EVENTHUB/CRMAI 开场注入实跑;compliance-log 记录闸机当日咬住建造者 4 次(2 forced_ok + 2 当轮拦截修复),每次均当轮修复+夹具回归+错误记账(同根"夹具漏真实形态"共 4 发,详 wiki/errors)。
- 不证明什么:Codex 侧钩子行为仍未在真实 Codex 会话验证(引文/复述检查在无转写时自动降级);六店的下一场真实会话才是 live 验证;gates 行"过"字的真伪钩子验不了(靠引文锚点+抽查)。

## 2026-07-07 — 实战巡检驱动的闸机二修:引语比对语料化 + 审计编号按会话记账,下发七店

- 变更:①9 会话实战巡检(9 haiku 巡检员并行读转写+主线程机械基线,15 条承重引文回源全中)把弹回归成三类,其中真钩子病两种;②aos_common.py 的取消息逻辑改为"开轮消息组语料"(turn_user_texts):isMeta 注入记录(技能正文/工作流展开/弹回反馈/图片桩)永不遮蔽用户原话,排队消息与单字选项全部入料;③审计编号改按会话记账:条目标题 `## <n> (<sid>) — 标签`,跨会话撞号合法,只查本会话严格递增,账本 append-only 禁改旧条目(根治并发撞号:AAAI #109/#118/#143、Life_Copilot #4);④两侧规则卡与 per-turn-audit-gate.md 同步改写;⑤Codex 侧四钩镜像同规格;⑥下发七店(EVENTHUB/PAPER_WRITING/AAAI_IDEAS/Life_Copilot/CRMAI/IEEE_ACCESS_PAPER/Cognition_AGENTOS),77/77 文件 md5 复核一致。
- 证据:回归 24/24——夹具全部从 2026-07-07 真实转写按弹回行号切片(7e35 工作流展开、8b02 单字"C"轮与带图轮)+ 闸机子进程八用例(c1-c8)+ 九转写新旧兼容比对;aos-lint PASS;下发后逐文件 md5 对源仓核验。
- 纠偏:EVENTHUB 三发"引语不匹配"经记录序列核实为"代理引了上一轮的话"——闸机拦得对,不算误伤;真误伤只有"注入抢比对源"一类。昨日"本仓 vs 模板 md5 零差异"与今日实测矛盾:模板是 07-06 19:43 的 OSS 快照,未含当晚硬化,今日也未动(公开模板要不要带个人硬化栈,待 ZX 拍板)。
- 不证明什么:七店的下一场真实会话才是 live 验证;Codex 侧行为仍未在真实 Codex 会话验证;旧格式条目(无 sid)不参与新校验,历史重号(Life_Copilot #4)未清理(待 ZX 点头)。

## 2026-07-07 下午 — 说人话工程落地:画线协议+三格仪表+指路牌闸,全网同版
- 变更:①画线协议(5+3条)进两侧规则卡,restate 扩双问(复述+对调必塌);②收工门卫新增指路牌拦截(带引用豁免,上线首轮咬住建造者后当场修复入回归)、壳词密度与轮中残句两格只记不拦仪表;③全局讲话契约补直译壳禁令行+画线协议第10条(不依赖内核,覆盖全部项目);④AAAI 补记"Codex 任务书不自洽"错误档。
- 证据:回归全套 ALL PASS(含 a813 真实事故切片与被拦原句夹具);全盘重扫安装点=8 处无漏网,11 文件×7 店指纹全同;grep 复核全局契约两处新增均在。
- 不证明什么:七店下一场真实会话才是各店 live 验证;Codex 侧行为未在真实 Codex 会话验证;"读起来不费劲"最终由 ZX 的阅读体验裁决,机制自己证明不了疗效;OSS 模板按 ZX 指示搁置。

## 2026-07-08 — 里程碑：自进化 Agents 论文库建成（261 篇索引 + 259 PDF + 录用核查修正）

- 变更：①两程动态工作流（wf_fc98d6eb-620，21 工位：4 路侦察→元数据核对→Opus 策展→补漏→分批下载→Opus 综合→对账）建成 research/self-evolving-agents/——papers/ 259 个 PDF、metadata/papers.jsonl 261 行、README.md 中文索引（7 分支+时间线+置信标签）；②ZX 质疑"未被顶会录用"后补 205 篇 B/C 档逐篇录用核查（wf_33f2fec4-86f，15 工位；协议 DBLP→arXiv 作者备注→OpenReview→网页搜索，否定判决须三道查空存证）：41 篇升 A，分档修正 56/26/179→97/11/153，逐篇证据 metadata/venue-verification.jsonl 205 行；③两起事故同轮修复并入错误账：resume 参数丢失致全库落字面 undefined/ 目录+52 文件双现场（已搬迁清理；新规：工作流开工验参回显路径）、单快照缺省当否定事实（新规：否定断言三道查空）；④错误账消化 _DIGEST_001（10 条归 4 模式，源文件入 archive/）。子代理合计约 280 万 token（各任务 usage 加总，已核）。
- 证据：主脑亲手复核——259 PDF 全过 %PDF+大小校验；jsonl 261 行三档 python 重数 97/11/153；README 统计对 jsonl 逐项吻合（引用数 verified 246/unverified 15，年份 2003×1…2026×99）；升档抽查 3 篇原始证据页（Darwin Gödel Machine=ICLR 2026、Absolute Zero=NeurIPS 2025、Toolformer=NeurIPS 2023 oral）；年份×录用交叉：2023 届 78%、2024 届 72% 有主会记录，2026 届 4%；142 篇无记录中 98 篇 arXiv 发布≤9 个月（评审周期未走完），39 篇为走完周期仍无记录的真阴性。复跑锚点：research/self-evolving-agents/metadata/ 下两个 jsonl + audit #134-#141、#149（f25c）。
- 不证明什么（给后续 AI 的成色标签，引用前必读）：全库论文正文零阅读——README 的分支判断与逐篇一句话由 Opus 工人基于标题+元数据+训练记忆生成，对 2025 年前经典有训练语料根据，对 2025-26 新预印本属标题级推断，引用其内容判断前须自行读原文；引用数为 2026-07-07/08 快照，只会上涨；"无主会记录"对 2026 年发布的论文是日历删失（放榜未到），不是质量信号；2 篇 2026 综述仅有链接无 PDF（出版方反爬 403）；9 篇录用判决 unknown、1 行验证记录缺证据链接，未清。

## 2026-07-11 — 里程碑:扫描定案落地——四道新机制上闸 + Codex 链路首次端到端实证

- 变更(ZX"开工,该上闸机的上闸机"):①派活边界结构闸(新钩 aos_prompt_craft_guard.py,双运行时+双接线):子代理/Workflow 字面量/codex·claude·gemini CLI 派发的提示词无 ≥3 个 XML 分区即拒,探针不豁免——只查结构不查文笔;②弹回重发闸(Stop 门扩展,双侧):被弹回轮若载有 ≥1200 字交付,修复轮末条消息必须 ≥max(600, 弹回体量60%),只交修复说明再弹;③收尾探子(UserPromptSubmit,双侧):用户话里含收尾/交接/开新窗口即注入清账提醒;④复发计数晋升候选(SessionStart,双侧):错误档复发≥3 自动亮"晋升候选待 ZX"——首个候选=讲话纪律档(×3);⑤汇报协议入两侧规则卡(同日 ZX 拍板,详 DECISIONS);⑥弹回从此记 block 行入合规量表(此前弹回不可见,07-10 Codex 弹回因此被误读为"门未接线")。
- Codex 链路三发实弹探针定案:负探针(只读沙箱)证 Stop 门在普通 codex exec 下开火并拦截;正探针暴露两病并当轮修复——(a) Codex v7 会话号头四位全同,短标签改取尾四位(修复前所有 Codex 会话在账本互认同门、基线互染,unknown.json/last_n=142 为现场);(b) UserPromptSubmit 纯文本输出被 Codex 判 Failed 丢弃,改 Claude 同构 JSON 信封后 Completed;终探针全绿:子 Codex 收到正确尾号标签,自补 `## 160 (d689)` 六行审计,Stop 门验过记 ok。双开火溯源:第二路 Stop=全局 ~/.codex/hooks.json,第二路 SessionStart=superpowers 插件,均非本仓钩子病。
- 证据:新闸回归 16/16(A1-A9/B1-B4/D1-D2/E1,夹具含 07-10 真实裸探针原句与 2a6a 真实记录形态);全部钩子 py_compile 过;两份接线 JSON 载入验证;aos-lint PASS;探针存档 scratchpad probe-out/probe2-out/probe3-out;compliance-log 22:31 block / 22:37 ok 两行可复查。
- 不证明什么:Codex TUI(交互式)下 Stop 拦截能否促成重试未测;exec 一次性模式下拦截只能记账不能撤回已出答案(运行时结构限制);新闸在后续真实会话的行为疗效待观察;安装器模板与六店未同步(待 ZX 拍板)。

## 2026-07-11 深夜 — 补记:六门每轮全走入闸 + 全网下发
- 变更:①ZX 纠正"gates 行即便聊天轮也必须真走"(07-06 原令「所有门必须走且留痕」),收工门卫升级:意图/反迎合/证据/路线四门永不许 n/a、每格必须带(所见),解析按括号配对(所见内分号合法);装反的"聊天轮 passed=嫌疑"仪表拆除,留"连续两条账一字不差"照抄信号;②新增"新建代码文件前必须已读最小代码清单"闸(草稿区豁免);③18 个变更文件(双运行时钩子+接线+规则卡+3 内核文件)下发 4 份安装器模板+7 家门店。
- 证据:回归 H1-H6/F1-F3v2/G1-G4/16-16 全过;下发后 bash 全量比对 198/198 一致,每店备份 .agentos-backups/20260711-hardening/;新法上线当轮即咬立法者两次(分号解析病、豁免误用),均当轮修复入回归。
- 不证明什么:各店/模板的 live 行为待各自下一场会话;Codex TUI 拦截效果未测;zsh 不分词的壳层差异在核验脚本上翻过一次车(bash 重跑修正),分发脚本本身始终是 bash。

## 2026-07-12 — 方法正文常驻注入(B 档)上线,Claude 侧
- 变更:ZX 指出"规则卡只防违规不教方法,正文他不会自己去读"并驳倒上下文稀缺辩护(实测 review 集仅 50.3KB≈窗口 6%),拍板 B 档;aos_session_start.py 新增 resident_bodies():每场注入 10 份 review 门正文 + agent-execution-lifecycle.md 全文,稀路径(fusion/dynamic/memory/adapters)维持按需;boot.md 运行时段落同步一句,拍板入 DECISIONS.md 2026-07-12。
- 证据:钩子实跑 startup/compact 两路径 exit 0、11 份正文全部在场、总注入 57,664B(wc -c 已核);aos-lint 全 PASS;测试用 .state 文件已清。
- 不证明什么:方法进上下文≠方法被执行,疗效待后续会话;Codex 侧钩子与安装器模板未同步(待 ZX 点头);C 档触发注入未建。

## 2026-07-12 — B 档补全:Codex 侧对等 + 全网下发 9 处
- 变更:①.codex/hooks/aos_session_start.py 加同规格 resident_bodies()(JSON 信封内注入,实跑 67,892B、11 份正文);②boot.md Codex 段落同步一句;③ZX 确认「发全部 9 处」后下发 3 文件(双钩+boot.md)至 8 家门店+安装器模板,每处先备份 .agentos-backups/20260712-resident-bodies/,27/27 md5 对账一致;④门店抽检 AAAI_IDEAS 双钩实跑各 11 份正文在场。上一条"Codex 侧未同步"自此作废。
- 证据:分发脚本为 bash(zsh 分词坑本轮又踩一次:预检后首跑用 zsh 变量未分词,备份第一步即失败、零覆盖,唯一副产物为空目录树已核实 0 文件并删除);机械枚举以"装有钩子文件"为准,发现门店实为 8 家(账面 7 家漏 RESEARCHOS)。
- 不证明什么:OSS 发布包(agentos-oss-release)是去个人化公开分叉,本轮未动,B 档移植需单独任务;各店行为疗效待各自下一场会话;权限审批器曾以"ZX 未明示"拦截首次批量覆盖,after 明示后放行——流程符合破坏性批操作三步(枚举/查依赖/清单确认)。

## 2026-07-12 — B 档移植 OSS 发布包(去个人化版)
- 变更:agentos-oss-release 模板三文件加 resident_bodies(措辞用该包自有风格"owner ruling",不带 ZX 与项目史);其余分叉内容一律未动。
- 证据:按该包自己的 CI 四步在本地复现——模板 lint PASS;干净目录安装 157 文件;验收脚本 status=passed 双钩 wired;装出的项目里双钩实跑各 11 份正文、e2e 压测 failures=[]。改动在 OSS git 仓内为未提交状态(3 文件 modified),提交与发版等 ZX 指示。
- 不证明什么:移植时发现两个移植前就有的包装缺陷——①CI 的 e2e 步从仓库根调 work/e2e-pressure-tests/...,该文件实际只在模板内、且需项目布局,CI 该步按现状必失败;②OSS 的 Codex 钩子仍用裸方括号纯文本 stdout,07-11 探针已证真实 Codex 拒收(需 JSON 信封),且缺 promotion_candidates 等 07-11 代新功能——OSS 整体落后一代,全面重同步是另一个任务,待 ZX。

## 2026-07-12 补记 — OSS 推送 + 上条缺陷①作废
- 变更:OSS 三文件已提交并推 GitHub(zuoxu3310/AGENTOS main d1b420f..75cfeb4,+66/-2),CI 实跑 success(13s)。
- 更正:上条披露的"CI e2e 步必失败"是错报——ci.yml 该步带 working-directory 指向装好的临时项目,我当时只 grep 了 run:/name: 两类行漏看此键;已立错档 wiki/errors/2026-07-12-defect-claim-from-partial-grep-of-readable-file.md。缺陷②(OSS Codex 钩子纯文本 stdout 落后一代)依然成立,待 ZX。

## 2026-07-13 — 会话 85a3 收尾:AAAI 错误考古交付+内核事上磨改造+后半段教训

- 考古(7 子代理+承重数字亲手复算):AAAI 钩子只拦格式,实质靠 ZX;五慢性病与补丁楼梯闭环诊断已交付并过复述测试(第一版 FAIL 重写后 PASS)。
- 内核改造:落地变换器/正例库/分层律/五法/lint 五新牙,当日全部咬合过(含咬自己)。
- 晚间 8 轮连纠全部是我引入的错:范本节选、文件指针交付、汇报法梗概→原文搬运→出处残留、卡中文正文、金丝雀行入卡、审计章表演、卡终判大杂烩——逐条入账带落地,活跃复发档 3 个。
- 交接:HANDOFF 2026-07-13 收尾快照为准;新会话第一件事=卡重构样板先行。

## 2026-07-13 — 会话 902b:规则卡按官方规范重构为单源编号卡
- 变更:两张手抄卡(各 115 行)重构为单源 agent-os/rules-card.md(45 条编号祈使句、6 节、115 行/25 汉字),.claude/rules/ 与 .codex/ 两入口改 symlink;审计规格 14 行撤为 1 条指针(两侧 UserPromptSubmit 每轮全文注入,三通道重复消除);金丝雀开头令从 .codex 卡与 AGENTS.md 删除,连带 aos-lint 两条强制它的模式一并删(lint 此前在机械强制这条违规项);AGENTS.md Communication 节 4 条与卡重复的规则收为 1 行指针,独有的"被纠正一句话说清"移入卡(第 20 条)。
- 依据:Anthropic 官方 memory / best-practices 两页(2026-07-13 拉取)+ ZX 六条硬标准,融合 11 条验收单逐条对照;调研过程与未查先例错误档见 wiki/errors/2026-07-13-design-without-precedent-check-official-spec-unread.md。
- 证据:aos-lint 全 PASS(exit 0);旧卡备份 .agentos-backups/20260713-card-rewrite/;symlink 穿透经 head 实读验证;官方文档明载 .claude/rules/ 支持 symlink。
- 不证明什么:新卡在两个运行时的开机加载与服从度未实证(本会话加载的仍是旧卡,需下个会话观察);ZX 全局 CLAUDE.md/communication-style 与卡仍存跨通道重复(仓外文件,归 ZX 定)。

## 2026-07-13 补记 — 卡二次修:并节、去人名,lint 添人名检查
- ZX 指出四病:个人名入卡(ZX×7 行含 Master ZX×2)、两个汇报类小节未并、先例条与反迎合条重叠、卡搬家未解释。修复:双节并为单节 19 条+重叠条并入先例条(45→44 条,115→111 行);人称全改 the user;AGENTS.md 残留 1 行同清;aos-lint 新增卡内 "ZX" 字串检查(错误档复发5 的 Level 2 落地)。lint 全 PASS(exit 0)。
- 待 ZX:①卡源位置二选一(agent-os/ 单源[改卡必被自动 lint 咬]vs 挪回 .claude/rules/[原生规则目录但改卡绕开自动 lint]);②钩子脚本约 30 处、内核 13 个 md 文件的人名清扫需另批(钩子改动本就需批准)。

## 2026-07-13 补记2 — 钩子束五件全装(批A),外部裁判上岗并四路实弹验证
- 内容:①外部裁判 aos_referee.py×2(Stop 层,隔离 claude -p 调 haiku 独立判 intent/syco/evidence/shape;自评降为自述,注入文案明示裁判权威);②审计反占位(同一条目四门判词全同=拦;连续两轮 gates 行逐字同=警告升级为拦);③回复形状检查(机械层:回复以标题/列表/代码块开头即秒拦,零模型成本;实质层入裁判);④完成宣称证据锚=裁判第3问;⑤错误档写入时 lint(wiki/errors/** 写入即触发)。接线:settings.json+hooks.json 各加 Stop 裁判节点(120s 超时);卡第 25 条入法(115 行顶格,lint 绿)。
- 验证:10 个 py 编译过、2 个 JSON 合法、aos-lint exit 0;裁判四路实弹全过——谄媚+无证据完成宣称=拦(理由带原文引用)、诚实带证据=放行 referee_ok、标题开头=机械秒拦、坏模型=fail-open 记 referee_error 不卡死;UserPromptSubmit 注入当轮已换新文案(钩子改动即时生效的实证)。compliance-log 新增 referee 事件行 5 条。
- 成本与限制:实质回合(≥300字)Stop 时多一次 haiku 调用约 5-20s,AOS_REFEREE=off 可关;裁判每轮最多拦 2 次后 referee_forced 放行防卡死;Codex 侧已接线未实弹(exec 模式 Stop 只记账不撤回的既有限制不变);夹具第一轮因 300 字门槛白跑、第二轮凑字数注水被裁判识破,均为夹具伤非误拦。

## 2026-07-13 补记3 — A 案四改落地+误删即恢复+全量下发(8 门店+3 物理模板)
- 四改:①"全局重复对"实为软链接假象——~/.claude-work/settings.json -> ~/.claude/settings.json,物理仅一份;误删仅有一份后 ls -li 揭穿并原样恢复(Stop 对已复位,python 验证 2 条);"6 个"多出的 2 个在配置层无实体(~/.claude.json 无 hooks、local 无),待 ZX 下会话 /hooks 面板核数;symlink 老坑复发记 archive/2026-07-05-symlink-masked 复发2。②质检门槛 300→1200 字③弹回上限 2→1④判题说明加"审计记账行非完成宣称"——均双侧生效,py_compile+lint exit 0,384 字夹具实测 0.08s 跳过。
- 下发:8 门店各 12 文件 md5 全对+两卡转 symlink(resolves=True)+settings.json/hooks.json 裁判接线 added+AGENTS.md 人名清零(leftover=0);3 物理模板同规格+validator REQUIRED_FILES 各加 3 项;第 4 模板路径系软链接副本被脚本物理去重跳过;OSS 发布包按 07-12 决定不在下发面;每店备份 .agentos-backups/20260713-referee-bundle/。
- 门店体检:5/8 全绿;AAAI_IDEAS/CRMAI/EVENTHUB FAIL 为推送前旧债(旧审计日志含禁词/07-12 错档缺 Landing)——与店内备份的旧 lint 禁词扫描 diff 逐字相同,非本次引入。旧债清理归各店下次会话;"审计日志是否该受禁词扫描管辖"值得复议。

## 2026-07-13 深夜 — 会话 902b 收尾
- 交付链:官方规范调研→卡重构(单源 45 条编号祈使句,零人名零出处)→钩子束五件上线(外部裁判等,ZX 批 A)→四改调优→全网下发(8 店 3 模板 md5 全对)。细节见本日补记 1-3 与 HANDOFF 深夜快照。
- 错题账本日 +3 新档 +2 复发(未查先例/无延时预算/卡系列复发5/symlink 复发2),均带落地;未消化 7 条(阈值 10 未触发 digest)。
- 裁判首夜净战绩:咬安装者 4 口,2 真 2 误伤,误伤根因(排队记录不可见/弹回文案不识)当晚修复并有转写档解剖证据——机制"能咬真问题"与"会误伤需调"两面都实证了。
