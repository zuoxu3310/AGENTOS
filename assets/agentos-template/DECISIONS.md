# Decisions

Use this root ledger for durable project decisions.

Each entry should include the decision, reason, scope, and claim boundary.

## Durable Decisions

### 2026-08-18 — Same kernel, one skill per runtime: Claude's invoking session IS 中书; Codex keeps the relay thread (ZX directive after the Cognition_AGENTOS incident)

- Decision: (1) On Claude the `agentos` skill binds the invoking session as 中书 (the ledger `create` writes the session mapping as `agentos-zhongshu`); 中书 talks with the user directly, records each user message verbatim, spawns 门下 (raw words verbatim, gate-checked), 尚书 after pass, and delivers once. There is no Claude 中书 subagent and no courier session; `.claude/agents/agentos-zhongshu.md` is retired. (2) On Codex the invoking thread stays the relay (太监) and 中书 is the `中书省｜<task>` Desktop thread. (3) The two skill files therefore differ by transport on purpose; the kernel, workflows, gate, ledger, and receipts are shared. (4) An invocation without task content opens nothing (skill rule + gate backstop). (5) Pause/stop freeze the ledger and stop-gates for every seat until resume; on Claude 中书 `TaskStop`s running seats first.
- Reason: the 2026-08-18 Cognition_AGENTOS run (`t20260818-0203`, 80 min, 10 agents, ~354k output tokens, zero chain delivery): 尚书 spawned the executor as a named/teamed agent (`name`, string `run_in_background:"false"`, agent-teams flag on), Claude reported the NAME as hook `agent_type`, the gate found no seat, the executor's receipt and `execution_result` were refused after it had already edited the files, 尚书 was refused `integration`, 中书 waited on 尚书, and the user saw nothing for an hour because a subagent 中书 can only speak at the end and both seats waited with `sleep` loops. The relay shape hid the chain on Claude; the user's pre-08-17 shape (session = 中书) is the right one there. Codex threads are readable at any time, so the relay stays.
- Mechanical guards landed with it (shared gate + `aos_common.py`): seat identity falls back to the runtime's spawn metadata (`agent-<id>.meta.json` customAgentType) when `agent_type` is a spawn name; seat spawns are normalized (name/team_name dropped, boolean run_in_background, isolation refused); `sleep` polling denied for 中书/门下/尚书; every waiting gate names its exit (`integration --status blocked`); the ledger file is written only through `aos_task_record.py`; multi-paragraph `user_message` is verbatim with its newlines (newline-safe CLI parsing); a paused/stopped task freezes seat writes and stop-gates.
- Scope: `.claude/skills/agentos/SKILL.md` (中书 identity + procedure), `.agents/skills/agentos/SKILL.md` (relay), `.claude/hooks/{aos_chain_gate,aos_common,aos_session_start,aos_prompt_baseline}.py`, `.codex/hooks/{aos_chain_gate,aos_common}.py`, `.claude/agents/agentos-shangshu.md`, `agent-os/workflows/zhongshu.md`, rules card 18/22, `AGENTS.md`/`CLAUDE.md` entry blocks, router, skill-parity, codex-workflow adapter, lint lists, installer (retire `.claude/agents/agentos-zhongshu.md`), capabilities C09/C10, tests.
- Evidence boundary: gate/hook unit tests, scenario tests, lint, and installer suite prove the mechanics; the teammate-mode trigger inside Claude Code is inferred from the incident's agent metadata (headless probes did not reproduce it), so the fix covers both the spawn shape and the identity fallback; live acceptance on Claude (`/agentos <task>` from a plain session through delivery) remains the user's run.

### 2026-08-17 — The chain is opt-in through one relay skill; 中书 is a seat, not the default session (ZX directive)

- Decision: (1) AgentOS stays installed but silent by default: ordinary chat runs with no seat, no ledger, and hooks that do nothing for an unbound session. (2) The user starts the chain by invoking the `agentos` skill (`$agentos` on Codex, `/agentos` on Claude; "三省六部" / "走链" are the human names); the invoking session becomes the relay (`agentos-relay`, the 太监) — a courier that records the user's exact words (`create --task t<YYYYMMDD-HHMM> --goal "<exact words>"`, no `--done-when`; later `append --role relay --kind user_message|pause|resume|stop`), opens `中书省｜<task>` (Codex thread / Claude `agentos-zhongshu` agent), and carries messages verbatim both ways; it never thinks or edits in the user's place and its Stop is never blocked. Binding is hook-owned and ends at delivery, pause, or stop; a new session is unbound. (3) 中书 becomes a seat with a clean, identity-first prompt (`.codex/agents/agentos-zhongshu.toml`, `.claude/agents/agentos-zhongshu.md`): sharpest reader of intent, source-checked claims only, "my call failed" until the interface is checked, strongest rival before any root cause; it no longer creates the task record and Phase B never hints at a verdict; goal/done_when are recorded only after 门下 pass. `agentos-entry` and the `agent` key in `.claude/settings.json` are retired. (4) The AI never starts the chain on its own judgment; the trigger is the skill invocation, a mechanical fact — hooks still never read intent from text.
- Reason: the RussianFlow live run (`agentos-runtime-audit`, 2026-08-17) proved the mechanism but showed the lead seat weak: it carried orchestration, ~1,800 lines of preloaded rules, and long developer instructions, and under tool friction asserted two root causes without checking the source (one was its own parameter guess). 门下 and the executor, given clean single-purpose prompts, reasoned visibly well. Splitting courier from mind gives 中书 the same conditions, closes the pre-review prior leaks (the relay cannot write goal/done_when; the task id is neutral), and lets the user decide when the ceremony is worth its cost — ZX: "如果我没说要走三省六部，它就不要走".
- Scope: `.agents/skills/agentos/`, `.claude/skills/agentos/`, `.codex/agents/agentos-zhongshu.toml`, `.claude/agents/agentos-zhongshu.md` (replaces `agentos-entry.md`), `.codex/config.toml`, `.claude/settings.json`, `AGENTS.md`, `CLAUDE.md`, rules card 18–19, `agent-os/workflows/zhongshu.md`, `codex-workflow.md`, `router.md`, `skill-parity.md`, lint lists, capabilities C09, scenario tests; hooks/gate tests and the installer template are separate deliveries of the same day.
- Evidence boundary: structural lint and scenario tests only at this entry; the gate's silent-when-unbound behaviour and relay rules are proven by hook tests; live acceptance on both runtimes remains the user's run.

### 2026-08-17 — Codex seats use Desktop-native local threads with role-skill receipts (ZX directive)

- Decision: (1) The user bypass is never the actor's call: only 门下 (`--role menxia --kind bypass`) may record it, still quoting the user's exact words which the hook verifies. (2) 中书 titles the current Desktop task `中书省｜<task>` and creates 门下/尚书 with `codex_app.create_thread` in the same project's local environment; 尚书 creates the local 执行体. (3) The hook registers every seat/thread and rejects duplicate seats, out-of-order messages, worktree seats, and current-task early archive. (4) `agent-os/skills/seat-skills.json` binds native skills to all five roles; phase work requires a runtime-specific receipt containing exact SKILL.md hashes. (5) The executor writes its own `execution_result`; 尚书 cannot integrate or stop before it and seats stay visible through final delivery.
- Reason: RussianFlow run `check-project-health-20260817` showed 中书 recording an ordinary user request as its own bypass and skipping 门下 comparison/尚书/executor; 门下 first believed it was 中书 (inherited wording), could not write the ledger under a read-only sandbox, and was spawned twice. Root cause of the bypass hole: the actor judged its own exemption; the hook can only verify a quote, not intent — so the judgment moves to the independent seat that already reads the raw increment.
- Evidence boundary: `pytest tests` 106 passed + 1053 subtests; lint PASS; `thread/name/set` verified from a fresh app-server process on an existing thread. Live Desktop behavior is for the user to test.

### 2026-08-16 — The chain order is enforced by hooks on mechanical facts; seats are runtime-native agents on both runtimes (ZX directive)

- Decision: One shared chain gate (`.claude/hooks/aos_chain_gate.py` ≡ `.codex/hooks/aos_chain_gate.py`) enforces the three-departments ORDER on exactly two mechanical facts — the hook-provided caller identity (`agent_type`) and the task ledger — never on semantics: 尚书 is spawned only after a menxia `comparison/pass`; executors only by 尚书 after its `dispatch`; workspace writes only by executors after a dispatch (御史 under `wiki/`, `agent-os/state/` always); each seat appends to the ledger only as itself; 中书 may not end a turn before shangshu `integration` (or a bypass / terminal failure). The user's bypass stays semantic — 中书 judges it and records `--kind bypass` quoting the user's exact words; the hook only verifies the quote exists in a real user message. On Codex, seats become native subagents in `.codex/agents/*.toml` (Desktop-visible), `AGENTS.md` is seat-neutral (children inherit it), the 中书 seat lives in `.codex/config.toml` `developer_instructions`; the vendored runner, `dynamic-workflow`, `NO_DELEGATION`, the guard enforcer, entry guard and yushi dispatcher are retired.
- Reason: three real Claude chain runs since 8/12 showed the prompt-owned order breaking (shangshu executing itself, delivery before menxia, self-reported executor lines) — the same shape as the Codex `NO_DELEGATION` failures. This refines, not reverses, 2026-07-20 ("hooks do not own meaning"): the gate owns order on facts the runtime provides, still never denies reads and keeps terminal records writable. The 2026-08-12 blocker is gone: a 2026-08-16 probe showed Claude hook input carries `agent_type` on the main thread and `agent_id`+`agent_type` inside subagents.
- Scope: both hook dirs, `.claude/settings.json`, `.codex/hooks.json`, `.codex/config.toml`, `.codex/agents/`, `AGENTS.md`, `CLAUDE.md`, rules card 18, router, `codex-workflow.md`, `skill-parity.md`, lint, tests (`tests/unit/test_chain_gate.py`), capabilities C05, and the installer template/scripts.
- Evidence boundary: `pytest tests` 87 passed + 1028 subtests; `aos-lint.py` PASS; installer tests 6 passed. Claude live acceptance in a scratch copy: task `probe-note-file` ran user_message → menxia review+comparison/pass → shangshu dispatch → executor result → integration → delivery with the gate denying 6 premature calls (2 shangshu spawns before pass, 4 foreign-role ledger writes) and the file created by the executor. Codex: a `codex exec` probe showed PreToolUse deny and `updatedInput` honored on the main thread but no hook events inside child threads and role `sandbox_mode` ignored both ways; the first REAL Codex Desktop run (RussianFlow, thread `01a00c1c…`, 2026-08-16 22:46) then showed native children menxia/shangshu (depth 1) and executor (depth 2, spawned by shangshu) with `agent_role` recorded, the gate denying 3 main-thread calls AND one inside the shangshu child ("shangshu 不改动工作区") — so in the Desktop app hooks DO fire in children with `agent_type`; the exec-mode gap is exec-only. Follow-up landing the same day: every seat spawn is retitled `席位｜任务号` (role + task, nothing longer, ZX ruling) via `updatedInput` (Codex `task_name`, Claude `description`) and 中书's first reply must declare AgentOS + 中书 (Stop blocks once) — the RussianFlow recurring desktop-visibility error's Level 2 landing.

### 2026-08-14 — Codex seat visibility is mandatory, never opt-in (ZX directive)

- Decision: On Codex the chain seats are ALWAYS user-visible: main thread titled 中书省, 门下 and 尚书 as desktop tasks titled by seat name, verified list/read/open per runtime-visibility. Separate sub-agent threads open only when real executor work is dispatched. This replaces the old "create visible tasks only when the user explicitly requests" boundary, which the AI had first silently narrowed further — both moves reversed.
- Reason: the user audits the chain by watching the seats work; an invisible chain is unauditable regardless of journals.
- Evidence boundary: user verbatim — 「我他妈强制他必须给我开可视化的事…除非说让子代理干活的时候才可以单独的开子代理，明确三省六部这几个角色必须要可视化」. Live adoption unproven until the next Codex session.

### 2026-08-14 — Engineering sources extracted for real; three rulings on what enters (ZX directive)

- Decision: The three engineering sources are extracted into the kernel by their original meaning — extraction means moving the core over, not copying and not condensing, with no improvisation. Rulings: (1) pristine law 6 (session cost, ~15-turn reset) does NOT enter — its purpose is already carried by ledgers/HANDOFF/task records; instead a mechanical context alarm lands in the Claude UserPromptSubmit hook: estimated live context >= 400k tokens raises a user-visible alarm and an in-context instruction to persist conclusions and recommend a fresh session. (2) pristine law 4 (deployment parity) enters the engineering gate by its original meaning. (3) The Linus review output (taste rating three tiers + fatal flaw + improvement direction) enters as the gate's Review Output alongside the five-layer method.
- Reason: the provenance audit found pristine-skill had never been referenced (name only), Linus.md contributed two cores out of its main body, and ponytail's ladder was real but had lost its understanding-first premise and safety enumeration. The user's standard: 「提取两个字不是照抄也不是精简，是真的把核心搬过去，不允许自作主张」.
- Scope: verbatim sources retained under `wiki/raw/2026-08-14-{pristine-skill-SKILL,ponytail-AGENTS,linus-role-method}.md` with MANIFEST rows; `engineering-gate.md` gained Entry Judgment (Linus three questions + worth-doing verdict), Decomposition Checks (complexity halving, destruction analysis, practicality validation), acceptance additions (deployment parity, rewrite-guard, pristine: markers, error-reach rule, no deferred-work markers, no naked constants), Review Output, and Adversarial Verification (scan output is evidence; mechanical residue scan booked for the machine layer); `minimal-code-gate.md` gained the understanding-first premise, the shared-function bug-fix rule, Working Rules, and the full safety enumeration with the one-runnable-check rule.
- Evidence boundary: direct user words — 「不进，但是出处你打算记在那儿？还有Claude，400k左右上下文必须警报，可能需要hook」「原义进工程门」「进，作审查输出形」. Hook estimator verified against synthetic transcripts (600k detected, post-compaction tail-only counting, small files skipped); live-session firing unproven.

### 2026-08-14 — The delivery method gets a skill AND enters the zhongshu birth-load list (ZX directive)

- Decision: `delivery-review` exists as a standalone skill shell in both runtime mirrors (Source: `agent-os/review/delivery-gate.md`), like every other method gate — and the gate joins the zhongshu workflow's Load list as birth equipment, not a delivery-step-only reference. The pattern is the anti-sycophancy precedent made explicit: a method skill is independently callable anywhere, and every seat that constitutively needs it reads the canon completely at birth. Being seat-constitutive and being a skill are not alternatives.
- Reason: the AI first proposed a shell without must-load, then proposed seat-binding without a shell; the user corrected both — the established doctrine already covers this case (skills stay separate and callable; constitutive methods are must-load equipment).
- Scope: shells `.claude/skills/delivery-review/` and `.agents/skills/delivery-review/` (with openai.yaml); `agent-os/workflows/zhongshu.md` Load list now includes `agent-os/review/delivery-gate.md`; router row's runtime column repointed from "zhongshu delivery step" to `delivery-review`; skill-parity matrix gained the Delivery Gate row.
- Evidence boundary: direct user words — 「不，skill要做，但是是中书省必须加载的，属于是中书省的workflow必须的不是吗？」. Structure only; live birth-read of the seventh document is unproven until the next chain run.

### 2026-08-13 — Skills stay separate; the cognitive process composes as one workflow; a method is a paper-grade Method (ZX directive)

- Decision: The cognitive gates remain separate documents, but each is rewritten as a real methodology — a one-line purpose, a trigger, a numbered step-by-step procedure with criteria, and an output contribution, like a paper's Method section; design essays leave the operator layer. Their combination is fixed by one new workflow, `agent-os/workflows/cognition.md`: reconstruct the object → de-anchor → explain and test → check the route → speak to the evidence, with a fast pass for ordinary rounds and a mandatory full pass for judgment moments. Chain seats invoke the workflow, not scattered gates; while working the chain the workflow is the trigger canon (resolving the anti-sycophancy trigger dispute), and the Promotion Gate in route-keeper-promotion-gate.md is the single canonical promotion template (the intent gate's embedded duplicate became a pointer). The output is one integrated judgment, never five parallel reports.
- Reason: anti-sycophancy, first principles, causality, logic, and drift-checking are facets of one act of thinking; splitting them into five independently triggered rituals manufactured the two kernel contradictions the live audit found, hid how the capabilities combine, and invited ceremony over cognition — the exact drift AgentOS exists to counter.
- Scope: cognition.md created; five gates rewritten in Method form (content preserved, structure and canon fixed); role contracts load the workflow plus its gates at birth and work by it; ten skill adapters re-aligned (audit's missing output fields added, banned size vocabulary removed from the operating layer, invented vocabulary replaced with kernel terms, the docs exclusion in minimal-code lifted). The sequencing ratchet demanded by the live session's error record landed: aos-lint task-ledger check plus its regression test.
- Evidence boundary: direct user directives — 「这几个分散的 Skill 就保持分散状态。核心是要把"认知过程"合成一个 Workflow…Workflow 里要包含这几个 Skill 具体怎么组合使用」「什么是方法论？就像论文里的 Method 一样」「反对谄媚…是不是要结合第一性原理？是不是要结合因果？…结合这几个功能来一起使用」. Structure verified (69 tests + 801 subtests, lint PASS); live behavior of the rewritten stack is unproven until the next chain run.

### 2026-08-13 — A role's constitutive methods are must-load equipment, never on-demand references (ZX directive)

- Decision: Every capability listed in a role contract's capability section is paired inline with its method document, and the role's first action at the start of its life — session start for the lead, spawn for teammates — is to Read every paired document completely. Progressive disclosure applies only to long-tail methods outside a role's constitutive capabilities; a constitutive method is equipment the role uses every round and is therefore loaded before any work. Method use must be visible in output shape (verdicts carry the framing assumption and de-anchored conclusion; reconstructions carry the gates' shape).
- Reason: deferring constitutive methods to trigger-time re-created the named-is-not-possessed gap for the very capabilities each seat exists for — the fifth recurrence of that root. What a role reads at birth it can use immediately; what it is told to fetch later fires probabilistically.
- Scope: all four chain contracts now pair capabilities with method paths and carry a "Load your equipment first" first-action section (entry: five gates; menxia: four; shangshu: four; executor: minimal-code-gate plus dispatch-named gates). The skill wrappers and router remain for long-tail, trigger-based use.
- Evidence boundary: direct user directive — 「第一段写的能力里面就直接配套 Skill…这些东西本来就是必须加载的，你搞渐进加载干什么？那就是他读了马上就要用的东西」. Contract-level only; whether roles actually perform the birth reads is the canary's first check item.

### 2026-08-13 — One resident rule body; documents are prompts, machine rules, or memory (ZX directive)

- Decision: A document in this system acts through exactly three channels — it enters context (a prompt: probabilistic, paying rent in behavior-change per token), it drives a mechanism (deterministic), or it is recalled as memory. A "constitution" has no independent status in this physics: the model has no court, and a precedence line is just more prompt text competing for attention — the constitution/rules split manufactured the very conflict-resolution problem it claimed to solve. Therefore one resident rule body: `agent-os/rules-card.md` absorbs the constitution's identity and value judgments (each rule carrying its why), `boot.md`'s load boundaries, and the de-fossilized hard constraints; `DECISIONS.md` is the constitutional record (user rulings with evidence); anything mechanically enforceable lives in lint/hooks/contracts, not prose. `constitution.md` and `boot.md` are retired. This supersedes 2026-08-12 "The constitution is the kernel's first document".
- Reason: the user diagnosed false document expansion — documents multiplying in structurally valid form while nobody audited necessity, overlap, or best phrasing. The audit found the same doctrine sentences resident in up to five places, stale vocabulary from the quarantined engine inside the constitution, a three-hop navigation chain (card→boot→router) before any content, and 17 skill adapters re-reading boot+router on every invocation.
- Scope: card rewritten at 115 lines (within budget) with communication rules deduplicated to the global operating contract except the two reader-load regression anchors kept verbatim; AGENTS.md reprojected byte-exact; router, lint, artifact contracts, codex config, capabilities, and test fixtures repointed; worker role contracts keep their inline escalation law because a spawned teammate's residency is its contract alone, while the entry contract dedups fully (its session carries the card).
- Evidence boundary: direct user words — 「宪法不就是规则的高级版吗？…是不是应该只需要一份就够了？」「文档的虚假扩张，反而忽略了文档精简的必要性」「开始做」. Structure verified (lint PASS; 63 tests + 789 subtests); the new card's live behavioral quality is unproven until real chain runs.

### 2026-08-12 — Error learning is a separate background censor; the system grinds sharper through real work (ZX directive)

- Decision: Error learning runs as its own role — the Censorate, `agentos-yushi` on Claude — spawned by the lead in the background at teardown when an increment surfaced a confirmed mistake, fire-and-forget: delivery never waits for it and it gates nothing. Fixing the user-visible problem stays main-chain work, and for `recurrence >= 2` the mechanical landing ships inside that fix; yushi owns `wiki/errors/` as single writer, verifies landings by reading them, detects recurrence, regenerates derived views, and never edits kernel or code — a missing mandatory landing goes back to the lead as the next chain task. The evolution model is 事上磨: every real task grinds the system; confirmed mistakes become trigger-recallable records, recurrence forces a mechanical guard plus regression (the existing ratchet), and the guard holds forever.
- Reason: inline error learning repeatedly blocked the main chain — the user's stated problem ("你经常在那就是阻塞到主链路了"). Recording and fixing are different work with different owners: fixing needs the chain's authority, recording needs only evidence and the memory layer, so recording can and must leave the critical path.
- Scope: `.claude/agents/agentos-yushi.md`, entry grant + teardown law, rules-card rule 24 (projected byte-exact), router row, error-learning.md Ownership And Scheduling section. Codex-side parity is open work.
- Evidence boundary: direct user directives — 「错误学习这个东西就应该单独的出一个角色去干这件事情，不要阻塞我们的主链路」「你让他去干就行了，你为什么一定要等他的回复呢？他干完就干完呗」「根据王阳明的"事上磨"…不停的完善我们的这个 Agent OS」. Contract-level only; no live yushi run has happened yet.

### 2026-08-12 — The working tree keeps only load-bearing content; fossils are archived, never hoarded (ZX directive)

- Decision: The repository working tree holds only what the product currently stands on. Superseded artifacts — backups, era-specific reports and templates, dead experiment dirs, stale runtime state — leave the tree: tracked fossils are removed on top of an archive snapshot branch (`archive/pre-clean-20260812`), untracked ones move to an on-disk archive (`~/Downloads/agentos-archive-20260812/`). The deterministic layer must never depend on fossils: existence checks retire with their artifacts, and runtime products land in gitignored state (`agent-os/state/`), never in tracked product space.
- Reason: the user's cleanliness ruling — a system whose tree mixes product with residue cannot be read, and lint checks pinned to dead artifacts are the checks defending the residue.
- Scope: removed backups/, outputs/ (evidence_output contract retired, fusion provenance relanded at `agent-os/state/fusion-runs/`), research/ corpus, work/ v1 regression scripts and e2e dirs; kept the installer candidate, vendor engines, and all memory-layer content. Two 2026-07-24 error records re-anchored from gitignored runtime state to a durable tracked copy under `wiki/raw/`.
- Evidence boundary: direct user directive — 「我需要一个干净的 Agent OS 的一个版本…该封存的就封存，该 Archive 的就 Archive，不要全部都放在一起」「有些东西早就没用了，你还放在那干什么呢」. Everything is recoverable from the archive branch and the on-disk archive; nothing was destroyed.

### 2026-08-12 — Capability profiles per seat; task-size judgment banned; Shangshu is the chain's center (ZX directive)

- Decision: The three departments are three genuinely capable minds in seats evolved by history, not three role labels — the seat count is incidental; the capabilities operating every round are the product. Zhongshu and Menxia each carry the full cognitive core in their own right — first principles, anti-sycophancy, causal and logical reasoning, anti-drift — and Zhongshu never outsources its cognition to Menxia. The task goal is fixed by Zhongshu with Menxia after understanding the user. Shangshu is the most important seat: engineering judgment and plan-making — the three translations (priority, classification, parallel/serial), Linus thinking and the pristine principle as its acceptance standard, time-budget stewardship — with executors as its least important, one-shot implementation hands. A round whose output does not come from the seat's capabilities is non-work. The phrase "non-small task" and every AI-side task-size judgment are banned from the operating layer: every request runs the chain; the only bypass is the user's explicit instruction to skip process.
- Reason: an architecture whose only guarantee is cross-checking degenerates into "open a second chat window to check the first" — the user's own failure criterion. Runaway long-running work traces to the missing translations at plan level, not to executor behavior. AI-judged smallness silently mutates user intent, the gravest violation.
- Scope: all four role contracts rewritten to differentiated capability profiles; rules-card, boot, and router de-sized. Ledger and audit machinery are support, never the center of the product.
- Evidence boundary: direct user directives this session — 「我们需要的不是三个角色，而是三个真正像三省一样有能力的人」「执行者其实是最不重要的一环，尚书才是最重要的」「"非小任务"这是我严令禁止的说法……除非用户明说」「任务的优先级翻译、分类翻译、并行串行翻译没有做好」. Behavioral effect is unproven until live chain runs under the rewritten contracts.

### 2026-08-12 — The constitution is the kernel's first document (ZX directive)

- Decision: `agent-os/constitution.md` owns the product's essence: the highest principle (only a real, correct, user-acceptable delivery counts as done; process completeness earns nothing, an incorrect result is punished a hundredfold), the first principle (derive backward from the real-world result; the user's attention and judgment are the only scarce, irreplaceable resources), the cognitive-system law (every intervention carries a constructive increment; capabilities count only when demonstrated inside real judgments), the stuck doctrine (root cause, then a different perspective, repeated; "this cannot be done" is not a deliverable; escalate only user-owned forks), the separation of powers, and nine hard constraints. Every rule, role, hook, skill, and test derives from it; on conflict the constitution wins. The constitution is pure operative text; the user's verbatim source statements it translates are preserved in this entry's evidence boundary, not in the kernel.
- Reason: three failed rebuild waves optimized legible proxies — gates, hashes, test matrices — because the binding goal was structurally absent; the project's own 2026-07-19 route decision to define the human problem, core promise, authority boundary, v1 boundary, and acceptance evidence first was never executed. When work necessity is undecidable, models select work by short feedback, easy verification, and easy reporting.
- Scope: one kernel page, registered as artifact `constitution`, referenced from `rules-card.md` and `boot.md`. It adds no mechanism itself and does not change runtime behavior.
- Evidence boundary: existence, registration, one-type-per-document, and byte-exact projections are verified; behavioral effect on future sessions is not yet proven. Source statements, in the user's words: 「只有真实、正确、用户可接受的业务交付才算完成；流程完整不会得到任何奖励，但结果不正确将得到百倍惩罚」「先确定要改变的现实结果，再倒推必要的判断和动作；流程、测试、审核、记录都只能作证，不能替代交付」「把普通用户消息稳定转化为高质量业务结果——系统负责理解、独立纠偏、执行和交付，用户不需要管理内部流程」「每一轮必须要有建设性的意见才行，不能光有产出就完事儿」「卡住的时候该干什么？找根因去解决；找半天找不到就从别的视角重新去找去解决。反正就是把问题解决掉」「你要知道用户的认知是有上限的，把所有的东西全部压到用户的身上也是一种非常不负责任的表现」.

### 2026-08-12 — Judgment stays in thin documents; judgment-free actions sink into deterministic structure (ZX directive)

- Decision: a three-way split governs where rules live. (1) Judgment — intent, verdicts, completion, dispatch choices — lives only in the role/prompt layer, and that layer stays deliberately thin (the constitution is one page; the rules card is lint-capped). (2) Judgment-free actions — checks, reconciliation, projection sync, install parity — are deterministic structure: lint, layout, hooks. (3) The middle class — judgment that leaves an observable trace — is executed by roles and verified by hooks non-blockingly: automatic recording of transport events, and a single Stop reminder when an active task lacks a terminal record. Any prompt rule restatable as a deterministic check migrates to the check; the prompt keeps only the why. Hooks may verify observable traces and mechanical facts; they never judge meaning or quality, never outrank the user, and never loop.
- Reason: prompt-only rules are probabilistic — attention dilution makes execution "玄学" (user's words this session) — while the quarantined implementation proved the opposite pole, hooks judging semantics, deadlocks the system. Both failure modes are now on the record; the boundary between them is the trace.
- Scope: next milestone implements the observer hook, the Stop single reminder, and the two-layer anchor resolution in `aos-lint.py`, each behind its own fresh-session canary. Deliberately not implemented in this session: changing hooks at the tail of a long session without a canary is how the quarantined failure began.
- Evidence boundary: direct user directive in this session fixes the product rule; behavioral effectiveness is unverified until implemented and canaried.

### 2026-08-12 — Execution-chain activation quarantined; work restarts from the green 2.0 release (ZX directive)

- Decision: The turn-execution-chain activation line — commit `2e9be6c` plus its uncommitted continuation — is quarantined whole as commit `efbd0f5` on `codex/agentos-control-loop-rebuild`. Active work restarts from release commit `83fb2d1` on `pristine-reset-20260812`. Stuck mechanisms are discarded and rebuilt clean, never patched in place; no compatibility layer may keep a dead mechanism half-alive.
- Reason: Three independent hard facts. The test suite is red at `2e9be6c` (10 failures) and redder with the uncommitted continuation (32 failures). The Claude identity gate requires an `agent_type` hook field that Claude Code does not deliver for native sessions — the implementation's own comment records the omission — so the chain's own `agentos-executor` sessions cannot pass their own PreToolUse gate, and the entry identity is denied even read-only tools; no session in the project could use any project tool. The approved implementation plan's own stop rule ("若需要靠 PreTool semantic Gate 才能维持链路，停止并重做责任分配") had already triggered in live use.
- Scope: Quarantine, not deletion; everything is recoverable from `efbd0f5`. The three-departments product semantics and the 2026-08-11 architecture and implementation plans remain the design basis. Rebuilt enforcement may deny a tool only on facts the runtime mechanically provides, must never deny read-only tools, and must keep `failed`/`blocked` always writable. This does not reopen the 2.0 release or distribution decisions.
- Evidence boundary: pytest runs at `97fac54` (78 passed), `b2c6013` and `83fb2d1` (19 passed), `2e9be6c` (10 failed), and the pre-reset worktree (32 failed); the blocked entry session's live report of executor denial. These prove the quarantined state was unreleasable; they prove nothing about a future rebuild's behavior.

### 2026-07-20 — The Git release is a clean distribution source, not a project-memory mirror

- Decision: `https://github.com/zuoxu3310/AGENTOS` owns the distributable AgentOS bundle. Its template contains the kernel, adapters, skills, tests, installer, vendor runtime, and empty project memory scaffolding; it does not copy the AGENTOS source project's live task, Wiki history, errors, raw sources, archives, or runtime state. All global installers and project rollouts derive from that clean bundle.
- Reason: the internal installer candidate had become a mirror of the live repository. Installing it into another project would silently seed unrelated private history and make the package impossible to audit as a reusable product.
- Scope: public release, internal installer candidate, three global installer copies, isolated installs, and the 11 active project updates. The installer backs up and removes only an explicit list of retired AgentOS-owned paths; Wiki and runtime state are never cleanup targets.
- Claim boundary: this proves package cleanliness against the scanned private identifiers and included history classes. Existing projects retain their own memory and may still need separate contract migration.

### 2026-07-20 — Brownfield lint reports the edited artifact, not unrelated historical debt

- Decision: PostToolUse still runs the full deterministic linter after a structured governed edit, but returns only failures that name or are structurally coupled to the edited path. Full `aos-lint.py` remains the explicit repository-wide migration audit.
- Reason: every existing project predates the current document contracts. Returning thousands of unrelated legacy failures after one valid kernel edit would make the Hook noisy and train users to ignore it; automatically rewriting semantic Wiki content would be worse.
- Scope: Codex and Claude PostToolUse adapters, integration regression, release package, global installers, and the 11 updated projects.
- Claim boundary: path filtering prevents unrelated feedback, not legacy debt. An edited legacy document can still fail its own current contract and must be migrated deliberately.

### 2026-07-20 — Hook output follows each runtime's real schema

- Decision: a Hook may emit only fields accepted by the target runtime event. Codex Stop blocking uses top-level `decision` and `reason`; Claude keeps the same minimal shape. Shared semantic intent does not justify copying a richer envelope between runtimes.
- Reason: after the Hooks were trusted, a real Codex Thread still left `report_state: pending`. The Stop helper included an extra `hookSpecificOutput` object that the current Codex Stop output schema rejects, so the runtime ignored the block even though fixture tests passed.
- Scope: both runtime helpers, the dual-runtime integration regression, installer template, and live Stop canary.
- Claim boundary: Thread `019f7e45-...` proves the trusted Codex path moved a finished long task from `pending` to `delivered` and a following short reply stayed single-pass. External Claude live behavior remains outside the authorized scope.

### 2026-07-20 — Hooks restore attention; they do not own meaning

- Decision: the old route graph, semantic event stream, proposal transaction, per-turn admission, external referee, and route marker are replaced by one session-local `active_work` record for long tasks. The main model decides intent, corrections, task boundaries, and completion meaning. Hooks only restore that record at session boundaries, remind the model to reread a real user message, enforce deterministic prompt/delegation/document checks, and request one final delivery reread for a completed or blocked long task.
- Reason: a mechanical Hook cannot reliably decide semantic importance or user intent. Making it try produced false blocks, inherited authority, repeated reminders, opaque state, and work whose machinery exceeded its user value. The useful invariant is smaller: preserve the finish line across attention loss, then let the model reason again.
- Scope: Codex and Claude adapters, Task Contract, lifecycle, resident rules, tests, installer template, and long-task local state. Codex delegation remains single-backend; Claude keeps native Workflow.
- Claim boundary: tracked implementation and isolated tests are verified. Codex treats any changed Hook definition as modified until the user trusts it again; therefore a source update is not an activated runtime. Final interactive acceptance remains open until the new Hook hashes are trusted and a fresh Thread passes.

### 2026-07-20 — Finish lines and attention management replace reply machinery

- Decision: every mutating, delegated, or cross-turn task must persist user-observable completion conditions before its first action, keep `next_action` inside the real open obligations, and close only when every condition has connected verified evidence. User-facing replies are generated by the main runtime from what the user must know, decide, or do; plain result-level language is the default.
- Reason: the repeated failure was not missing prose templates. Work lacked an enforceable stopping line, while the accepted 2026-07-11 attention-management principle had fallen out of resident instructions. That combination produced both endless extra work and reports that alternated between technical dumping and destructive over-compression.
- Scope: shared cognitive validation, existing PreToolUse and Stop gates, Task Contract, Completion Gate, lifecycle, resident rule projections, Router, exemplars, Error Learning, tests, and installer templates. The accepted scope of the 2026-07-16 TLDR exemplar is its expression direction and information organization only.
- Claim boundary: the former fixed-length and separate spokesperson implementation is superseded. No second model, reply scorer, length quota, new hook, or automatic semantic authoring is introduced. Mechanical tests can prove the contract and loading path, but only real conversations and user acceptance can prove that future reports reduce attention cost.

### 2026-07-20 — One Memory Operating Contract owns project-memory behavior

- Decision: `agent-os/memory/routing.md` is the single contract for selective reading, write destinations, canonical ownership, maturity, lifecycle, conflicts, and completion reconciliation. Bootstrap only initializes structure, Wiki v2 only defines knowledge format and supersession, and sync-audit only checks stage-end state.
- Reason: overlapping maintenance documents and optional global skills made file purpose and load timing unclear. A memory system creates value only when later work can find the right current fact without reconstructing or loading everything.
- Scope: root ledgers, Wiki task/chat/knowledge/error/raw/docs collections, the project `memory-wiki-routing` adapters, completion transactions, lint, derived views, and installer preservation. Global maintenance skills remain optional tools, not policy or hidden dependencies.
- Claim boundary: the contract defines and mechanically checks routing; it cannot decide semantic truth, progress, user decisions, error causes, or knowledge promotion automatically.

### 2026-07-20 — Read-only understanding updates route state but grants no action authority

- Decision: analysis, audit, reporting, or planning that changes the active goal or focus commits a normal agency route transaction without `turn_admission`. Only a current-turn admission can authorize write, shell mutation, or delegation; semantic review runs only when such a material admission exists.
- Reason: route state must reflect what the conversation is actually doing, but understanding a new object is not permission to act on it. Conflating route phase with authority caused stale focus and encouraged old execution rights to leak into new goals.
- Scope: shared cognitive validation, pre-action guard, Stop commit behavior, both runtime adapters, and their tests.
- Claim boundary: deterministic and subprocess tests prove the enforced boundary in their observed envelopes. Fresh interactive classification remains a separate canary.

## 2026-07-19 — Route transactions use an internal side channel, never the reply

- Decision: semantic route transactions are staged at the per-turn `agency_proposal_path` and consumed by Stop. User-facing replies may show a compact route marker when useful, but never machine state JSON; any embedded state transaction is blocked.
- Reason: HTML comments are presentation syntax, not a guaranteed private runtime channel. Machine state and human communication have different consumers and must not share the same payload.
- Scope: Codex and Claude prompt-submit, Stop, common helpers, question guards, the shared cognitive core, resident rules, and installer templates. No new model call, dependency, daemon, or visible report was added.
- Claim boundary: subprocess tests prove staged commit, retry idempotency, and leak rejection in both adapters. Fresh interactive runtime behavior remains pending.

## 2026-07-19 — Minimal mechanism is a step-admission rule, not a smaller product

- Decision: Before any non-trivial step, the agent must identify the contracted user-visible result it advances or the evidenced risk it reduces; if neither exists, it skips the step. This applies to code, tests, documents, abstractions, tools, workers, reports, and process artifacts. Use the least mechanism that delivers every accepted capability.
- Reason: activity volume is not progress. Over-engineering and performative work share one root: optimizing visible machinery instead of the user's result. A separate gate or report would reproduce the failure it is meant to prevent.
- Scope: the resident AgentOS rules card, existing minimal-work/code gate, lifecycle step admission, Codex delegation economics, and the cross-project global contract. It creates no new hook, runtime dependency, mandatory report, or license to reduce functionality.
- Claim boundary: a RED/GREEN scenario and the full source/template suites prove the rule is present and mechanically protected. They cannot prove that every future model step will be substantively justified; real-task recurrence remains the behavioral test.

## 2026-07-17 — Codex uses official event fields and one sequential Stop entry

- Decision: Codex hook logic must use `UserPromptSubmit.prompt` and `Stop.last_assistant_message` as primary content inputs. `transcript_path` is limited to `turn_id`-bounded, fail-open quote verification and commentary measurement. The deterministic Stop gate calls the external referee sequentially through one configured Stop command.
- Reason: the observed Desktop transcript is `response_item.payload`, while the previous helpers read obsolete top-level `assistant/user/item.completed` records and returned empty. Official Codex documentation also states that multiple command handlers for the same event start concurrently, so separate blocking Stop handlers can race and emit duplicate continuations.
- Scope: the Codex adapter, its project wiring, the three installer templates, and the 11 installed shops. Claude hook behavior is unchanged. No new dependency or separate spokesperson model was added; the spokesperson pass is a bounded Codex Stop continuation with an outcome check.
- Claim boundary: source behavior, real-record replay, hook firing in `codex exec`, and file rollout are verified. One-shot `codex exec` records the block but does not perform the continuation; interactive Desktop continuation and per-shop activation require a live trusted session.

## 2026-07-06 — 语言政策：内核全英文，输出强制中文，读者按零上下文设定

- 决策：AgentOS 内核、规则卡、适配器全部使用英文（思考/推理/内部笔记英文）；用户可见输出强制普通话中文，且每轮按"零上下文读者"标准写——没跟过会话的人一读就懂，会话自造代号列为交稿违禁词；拍板类汇报固定四格（是什么/出了什么事/要做什么/建议）。规则同步写入规则卡、AGENTS.md 与全局写作契约。
- 理由：ZX 直接指令；英文内部语言与其全局 CLAUDE.md 一致，降低规则被模型误读的概率；零上下文标准是"说人话"问题的结构性解法（把交稿标准从修辞要求改为可检验的读者定义）。
- 范围：规则卡重写为英文（质检模式同步改）；钩子内的中文提示文案未动——改钩子须 ZX 单独批准，为唯一剩余中文件。
- 主张边界：读者标准仍属提示层，买概率不买保证；真伪靠 ZX 抽查（拿回复给第三人试读即是探针）。

## 2026-07-06 — 四个记忆技能搬家内化（推翻 07-05"法律内化、班组外聘"）

- 决策：错题本工序写成内核法律 agent-os/memory/error-learning.md（新建）；wiki 维护工序并入 routing.md（新增来源分类、聊天蒸馏、证据锚点条款）；收尾审计并入 sync-audit.md（新增 current.md 新鲜度、验收考卷检查）；bootstrap.md 明文禁止软链接入口方案进 AgentOS 项目。router 路由行标注法律出处。全局四技能各加"遇 AgentOS 让位于内核法律"条款并三向同步；安装器模板随箱发行全部法律。
- 理由：ZX 质疑"凭什么不内化"触发重推——旧三条理由（内核要薄/跨项目通用/指针会断）两条不成立：薄是偏好非约束；内化不删全局副本；指针断恰是内化能根治（新机器装 AgentOS 时全局技能缺位为查实缺口）。搬家按"提取规则、不复印技能文本"原则执行（bootstrap.md 第 29 行既有条款）。
- 范围：内核 5 文件 + lint + 规则卡 + AGENTS.md + 全局 4 技能 + 安装器；error-neat 为 error-learning 内部阶段随法律并入，不单列。
- 主张边界：法律随箱发行=新装项目零缺件；技能与法律是否在真实使用中协调顺畅，零实战数据。

- 决策：对 AI 的约束不再加厚（机械层已封顶、提示层接线即封笔）；博主情报与未知数文章的融合方式定为——甲方职能尽数编译进 Agent 侧的主动服务：留白密度高时 Agent 必须主动勘探（讲盲区/一次一问/做样板/要参照物，闷头猜判违规）、承重断言带一键复核锚点（既有法条）、大交付默认附认出型验收考卷、"手册"退化为五口令遥控卡（盲区巡场/采访我/先做样板/出考卷/这数核了吗）。人只保留答题、挑样、不定期按不信任按钮。
- 理由：ZX 驳回"给人一份要学会的手册"——能执行那份手册的人不需要该手册（循环），且它把认知负担扣回用户，违反系统第一目标。心理学依据：认出成本≈0、想起/学会成本高，故一切甲方职能改造成"认出型"。保留项：最终不信任按钮必须在人手，因被约束方不能自证。
- 范围：内核五文件+速查表+PLANS 挂牌，三份安装器已回灌；证据门零改动（复核锚点为既有第38行法条，先例优先条款首次实战即命中"已在库房"）。
- 主张边界：全部为提示层脚手架，买概率不买保证；行为有效性零真实任务数据，待真任务与探针检验。

## 2026-07-05 — 采纳路线A：机械不变量下沉 Claude 适配器 hooks（推翻 07-02 报告制决策）

- 决策：每轮审计等机械不变量从报告制升级为 hook 强制（Claude 运行时）。五个钩子：SessionStart 注入内核卡（不变量+状态摘要+下一条审计号，压缩/清屏后重注入）；UserPromptSubmit 记基线+一行提醒；Stop 校验审计条目存在/格式/编号唯一/回答含可见审计块，最多拦 2 次后放行并记 missed 进 compliance-log.tsv；PostToolUse 对 agent-os/**（state/ 除外）编辑自动跑 aos-lint；PreToolUse 守卫执行层（改 .claude/hooks|settings 须用户批准，compliance-log.tsv 拒改）。
- 理由：PLANS 07-02 第 3 条预留的决定点被触发——冷启动实验被日常使用跑完，结果=常态失守（用户直接观察 + 主仓自身 current.md 07-02 过期实证）。提示层内"用更多规则解决不守规则"没有不动点；仅有的两条纯机械规则应搬进机械层。
- 范围：Claude Code 运行时。Codex 及其他运行时仍报告制（Manual until wired）。内核保持纯文本可移植；enforcement 属 adapter 层职责，与既有 kernel/adapter 分类学一致。质量类门（反谄媚、证据分级）不下沉——不可脚本判定，仍走提示层脚手架+事后抽查。
- 主张边界：hook 强制的是存在/格式/编号，不是内容真实性；伪造但格式合规的条目仍会通过，真伪靠用户抽查+定期外部复核。脚本级测试 22/22、装机级 e2e 两路径已过；会话级自动触发要等下个会话才有第一手证据（hook 于会话启动时注册）。

## 2026-07-02 — 面对"这套东西是不是真在跑"的质疑，选择当场演示而非再讲解

- 决策：不再输出架构讲解，改为当场按生命周期跑一个最小闭环，并把过程落盘为可查证据（`agent-os/state/current.md`、本文件、`PROGRESS.md`）。
- 理由：用户重启后指出上一轮"没理解对"。按 intent-causal-gate 复盘，上一轮把"验证实效"的诉求错当成"科普讲解"。纠偏动作是"做"，不是再"说"。
- 范围：仅本次交互的演示性落盘；未触碰任何用户已有数据（三文件此前均为模板初始态）。
- 主张边界：此举证明"执行可以进入 AgentOS 审计/账本"，不证明它会自动发生——本轮全部步骤靠 Agent 自觉，无 hook 强制。

## 2026-07-02 — 债务清理三决策

- 决策①：新门长进主干——生命周期主序列纳入 per_turn_audit；anti-sycophancy/minimal-code 作为条件门挂在 intent_gate/execution_plan 内，不进恒跑主干。理由：每轮必跑的进脊柱，条件触发的不进，防止脊柱膨胀。
- 决策②：账本边界——audit-log=每轮流水，PROGRESS=里程碑晋升，PLANS=活跃跨轮计划，HANDOFF=阶段末刷新。理由：三层记账开始分裂，必须定分工，否则 audit-log 会事实取代根账本。
- 决策③：停止加新门——下一份有效性证据必须来自真实业务任务，不是继续建设系统自身。
- 主张边界：以上为结构决策；行为有效性仍待 PLANS.md 验证计划兑现。


## 2026-07-06 — Fusion Workflow 三决策

- 决策①：只手动触发——Master ZX 明确说（/fusion、"跑 Fusion"）才跑；禁止自动触发，也禁止建议式触发。理由：面板成本约为单答 N 倍，触发权属钱路，归 ZX。
- 决策②：双通道+档位开关——默认 AgentChat 免费网页通道（零 token）；CLI 档需 ZX 点名；会话内面板成员默认 haiku，Fable/Opus 档先报量报价获批（规则源自 wiki/errors/2026-07-06-expensive-subagents-without-approval.md）。
- 决策③：装原厂不重写——两个 MIT 仓库原码进 vendor/，自己只写内核契约+薄壳+两个运行器适配（agy→官方 gemini CLI；无沙箱 codex→默认沙箱版，原厂无沙箱版需 ZX 显式批准）。理由：先复用成熟现成方案；ZX 当场纠正过"工程量大"的错误框架。
- 主张边界：结构（lint）与 CLI 通道冒烟已验证；免费通道与真实难题上的融合增益未验证。

## 2026-07-06 — Fusion 机制优化三决策（第一性原理复查后）

- 决策①：模式与通道解耦——同题盲答（fusion）/分工发散（divergence）按任务类型选，免费/CLI 通道按钱选，两开关正交；免费通道用"调用方自建同题计划"绕过原厂拆题器，把免费网页前沿模型变成同题盲面板。理由：融合增益来自同题冗余互纠错，原厂免费通道默认只有分工，与购买目的错配。
- 决策②：匿名评审 + 家族回避——评审阶段答案只标 A/B/C（映射只进存档）；法官为 Claude 时面板优先非 Claude 家。理由：堵法官偏自家（llm-council 已验证的零成本手法）。
- 决策③：交叉质证轮受限开放——仅当法官发现承重矛盾时触发，免费通道默认可用、CLI 通道需 ZX 点头、最多一轮。理由：辩论提升事实性但成本乘轮数，按矛盾触发把成本压到零起步。
- 主张边界：三项均为提示层机制修正，未增加代码依赖；免费通道整体仍未在本机真跑验证。

## 2026-07-06 — Fusion 上下文卷宗决策（ZX 指出同题模式进料缺口）

- 决策：新增"进料双轨"——依赖项目/会话上下文的题，由主脑先打一份对全员完全相同的自足卷宗（事实/摘录/约束/原题原文/期望输出），卷宗内禁止出现主脑的任何候选答案或倾向（防锚定污染），全文进存档供审；公共知识题则原题直发，让带工具的成员自行查证（来源差异本身是多样性）。
- 理由：面板成员全是冷启动，不等料时答案差异=信息不对称噪声，法官会把缺料误判为分歧；而打包者兼任法官，夹带倾向会让全场被锚住、独立性归零。
- 主张边界：规则已进契约与技能壳（lint PASS）；卷宗机制的实际效果待免费通道首次真跑检验。

## 2026-07-06 — Fusion 卷宗骨架＝任务契约投影（ZX 提议）

- 决策：Fusion 上下文卷宗不另起格式，骨架直接用当前任务契约的对外投影；进卷宗字段走白名单——目标对象/交付物/边界约束/证据标准/禁止替换项；路线与候选方案一律排除（防主脑定调锚定全场）。同一份契约贯穿出题→答题→评卷→完成门，全链一个标准。
- 理由：契约本就是"只装目的与约束、不装答案"的中立格式，复用免造轮子；证据标准随卷宗下发，面板答案自带可核验支撑，法官评卷质量直接提升。
- 主张边界：规则层落盘（lint PASS）；实际效果待免费通道首次真跑检验。

## 2026-07-06 — Fusion 法官独立决策（ZX 纠正）

- 决策：法官从"主会话兼任"改为"每次运行冷启动的独立子代理"——只见契约投影+卷宗+匿名答案，不见会话、不见身份映射、不见主脑倾向；裁决须可从存档独立复现。主会话退回本职：打卷宗、派面板、盯场、对法官融合稿过晋升门与证据门验收。法官模型档默认继承主会话档（每次 /fusion 手动触发即自带这一名法官的开销授权，可在触发时点名换档）。
- 理由：主脑编卷宗且有会话内倾向，兼任法官可挑"最像自己想法"的答案，匿名规则堵不住这个口子；原厂那样做是其运行时限制，不是我们的。此改动同时使 Fusion 对齐 AgentOS 角色分离律。
- 主张边界：规则层落盘（lint PASS）；独立法官的实际增益待真跑对照。

## 2026-07-06 — Fusion 提示词工程化决策（ZX 追问"有没有遵循官方最佳实践"）

- 决策：面板成员与法官的提示词不再现场临拼，改为从两份工程化模板组装（.claude/skills/fusion-workflow/references/）。模板依据当日抓取的 Anthropic claude-prompting-best-practices 与 OpenAI GPT-5 prompting guide 编制：XML 分区、长材料在上/原题在下（官方实测最高 +30%）、引文定位、明确角色与边界、指令附理由、正向指令、证据标注（已验证/推测）、收尾自查、组装后查矛盾指令；法官模板另采纳官方评审类硬教训——覆盖优先带置信度、下游过滤，以及"实测压过纸面合理性、独立一致为最高置信信号"。
- 理由：ZX 指出"一句话说你是法官"的裸提示词会让整套架构落空；此前契约只定材料与规矩、未定提示词工艺，属实缺口。
- 主张边界：模板已落盘并写入契约不变量（裸角色提示词=违约）；模板实际效果待真跑对照检验。全 Agent OS 范围的提示词审计是更大的独立任务，未在本轮展开。

## 2026-07-06 — 提示词工艺升格为通用门（ZX 拍板）

- 决策：新建 Prompt Craft Gate（agent-os/review/prompt-craft-gate.md）——凡给另一个模型/代理写提示词（子代理、面板、法官、worker、外部 CLI、网页 AI）必须过此门；裸一句话角色提示词=违规。双运行时薄壳 prompt-craft-review（.claude/.agents 两侧）+ 配对矩阵登记 + router/规则卡触发登记；Fusion 契约的提示词纪律改为引用此门。
- 理由：ZX 指出这不是 Fusion 一家的事，是"写 prompt 的规矩"；规则内容源自当日抓取的 Anthropic/OpenAI 官方最佳实践，Fusion 两模板作为该门的样板工程。
- 主张边界：门属提示层规矩（不是 hook 机械强制）；对既存技能/门内提示词的存量审计未展开，属独立任务。

## 2026-07-06/07 — 门禁强制化四项裁定(ZX 拍板)

- 决策:①所有门每轮必须处置留痕——审计条目扩为六行,gates 行逐门表态(intent= 必有,处置≥3),静默跳门变成白纸黑字可追责;②意图门带内容锚点——intent 行必须含用户原话逐字引用,Stop 钩子做子串机械验真(通知/命令轮豁免);③长交付轮(≥1200字)必须先过零上下文复述测试,复述不出重写;④"Master ZX"开头是 ZX 的上下文丢失金丝雀,永不机械检查/补全——约束进钩子,诊断信号永不机械化(Fable 主脑报警项 ZX 裁定不装)。
- 理由:全量调查证明机械执行的规则(每轮审计)100% 守住,自觉规则(意图门/讲话纪律)在长会话/换模型下反复失守;但强制"全套仪式"会复制表演性,故强制对象是"留痕处置+可验内容锚点"。
- 主张边界:引文锚点是少数程序能验真伪的点;gates 表态本身的真伪仍靠抽查。

## 2026-07-07 — 系统纯英文 + 错误账三级台阶(ZX 拍板)

- 决策:①AgentOS 系统层(内核/钩子/规则卡)纯英文,ZX 键入的命令词、面向 ZX 的输出模板、解析既存中文索引的字面量作为数据保留;②错误账三级台阶:未消化记录开场强制读全文要点→digest 提炼进 _INDEX 高优规则区(开场强制读)→反复复发者人工晋升进 Rules;提炼物不自动进 Rules——防 AI 给自己立法,晋升须 ZX 过目;③文档默认是 AI 读物,能在会话讲清必须会话讲清;④汇报须含探索/尝试/未走通,死格子四格仅是拍板摘要。
- 理由:中文指令层含黑话歧义(ZX);错误账"纯看着好看"没有价值,必须每场进脑(ZX);Life_Copilot 07-03 已有"文档不是我拿来读的"前科。
- 主张边界:错误注入体积有界(10 规则+8 记录×320字);跨项目"复发满 N 次自动生成晋升候选"未实现,待需求。

## 2026-07-11 — 论文库深读挂起 + 本任务角色分工（ZX 拍板）

- 决策：①全库深读（259 篇逐篇结构化笔记流水线）ZX 明示"先不急，放在这儿吧"——三档选项（维持现状/按需精读/全库深读）暂取维持现状；②本任务角色分工按 ZX 2026-07-07 原话：Fable 只 plan/compose/synthesize 不碰实现，Sonnet 5=Fast Worker，Opus 4.8=Deep Reasoner（本任务实际只占策展+综合两席），Codex=peer engineer 非 reviewer（本任务未派活——无需要对拍的工程实现）；③收录口径：宁收勿漏（"全部拉下来"），分档 A=核实主会正刊/B=里程碑预印本/C=其余，录用核查只升不降。
- 理由：深读量级估算为大几百万 token（未核），按贵模型报量规矩须单独批；宁收勿漏因错漏不可见、多收成本仅一个 PDF。
- 主张边界：深读挂起≠否决，随时可启动（入口见 HANDOFF 2026-07-11）；落账遵 ZX 本日指示"只记录真实的你干了什么，不要影响其他 AI 的判断"——判断类内容一律带成色标签。

## 2026-07-11 — 汇报协议入规则卡（ZX 拍板"内化成 Agent OS 的规则"）

- 决策：ZX 指定的汇报法（源：cognition-wiki 抖音转写 2026-07-11-工作汇报向上管理）写入两侧规则卡 Language and reader policy——每条消息=管理 ZX 的注意力和预期，不是干活日志；开口前先定目标（拍板/批准/知会），要拍板给选择题；首句=结论+数字，禁"挺好的/差不多"；长任务主动一行同步，等 ZX 来问即失职；三公式（要东西=结论+三理由+明确请求；出问题=事实+原因+已做方案+需要的支持；例行=进度+数字+下一步一行）；机器轮（钩子反馈/子代理通知）只回一行且不算交付；被 Stop 闸弹回的轮次修复时必须整段重发交付正文。
- 理由：私人自动记忆只覆盖单个脑子，规则卡每场注入、双运行时同管；当日两起复发（正文未达 ZX、机器腔短复）即触发证据，同根错误档见 wiki/errors/2026-07-11-machinery-turn-mistaken-for-delivery.md。
- 主张边界：规则层落盘（aos-lint PASS，双卡同文 diff 一致）；安装器模板与各门店未同步，待 ZX 点头；行为疗效由后续会话检验，规则本身证明不了。

## 2026-07-12 — 方法正文常驻注入（B 档，ZX 拍板）

- 决策：SessionStart 钩子在动态状态与错题簿之后，追加注入全部 review 门正文（10 份）+ agent-execution-lifecycle.md 全文（"Resident method bodies"段）。稀路径正文（fusion/dynamic-workflow、memory/、adapters/）维持 router 按需。三档选项（A 全量常驻 110KB / B 方法常驻 50KB / C 触发注入需造分类器）ZX 取 B；C 可作后续。
- 理由：ZX 指出规则卡只防违规、不教方法——"他怎么办事，必须要让他根据 rules 去读"；实测（wc -c 已核）review 集 50.3KB≈1.2 万 token≈20 万窗口 6%，"上下文稀缺"辩护被数字打掉；07-11 裁决（DECISIONS.md:95）禁的是强制仪式、不禁注入文本，两者同根：不指望自觉。
- 主张边界：实跑验证 startup/compact 两路径 exit 0、11 份正文全部在场、总注入 57.7KB（已核）；只改了 Claude 侧钩子，Codex 侧与安装器模板未同步，待 ZX 点头；方法进了上下文≠方法被执行，疗效由后续会话检验。

## 2026-07-19 — Independent judgment must remain visibly attributable (ZX chose A)

- Decision: Whenever the AI makes a substantive judgment—trying to influence what the user believes, chooses, or abandons—it must naturally state three things: its conclusion, the key basis, and what would change that conclusion. A separate full review block is not required.
- Reason: A fully hidden check is not auditable by the user, while a full report on every turn creates ritual and additional anchoring. The chosen shape exposes the load-bearing judgment without transferring final authority away from the user.
- Scope: Product meaning only. No implementation, trigger classifier, hook, subagent, or test was approved by this choice.
- Evidence boundary: Direct user selection 「A」 in the current conversation after the three options recorded in audit #295. Behavioral effectiveness remains unverified.

## 2026-07-19 — Clear action authorization is the decision signal (ZX chose A)

- Decision: When context is clear, a direct authorization to act—such as “do it this way” or “start execution”—counts as the user's final decision and switches the AI from deliberation to execution. The AI asks one clarification only when the language is genuinely ambiguous; no fixed confirmation phrase is required.
- Reason: Treating every clear instruction as provisional lets the AI retain de facto control, while requiring a magic phrase turns user authority into paperwork. A single ambiguity check protects against accidental execution without making the AI the decision gatekeeper.
- Scope: Product meaning only. Safety, legal, capability, and permission limits remain separate execution boundaries. No implementation or phrase classifier was approved.
- Evidence boundary: Direct user selection 「A」 in the current conversation after the options recorded in audit #296. Behavioral effectiveness remains unverified.

## 2026-07-19 — Judgment basis must preserve evidence type (ZX chose A)

- Decision: The AI must keep factual claims, uncertain predictions, and value principles distinct inside the visible basis for a substantive judgment. It shows only the categories that actually carry the conclusion: facts state verification status, predictions state uncertainty and conditions, and value judgments name the governing principle plus a reasonable opposing principle.
- Reason: Blending the three lets an AI preference masquerade as objective evidence and lets uncertain forecasts inherit the certainty of facts. Separating evidence type makes the real source of disagreement inspectable without forcing an empty three-part form on every reply.
- Scope: Product meaning only. This choice does not require a fixed report block or authorize implementation.
- Evidence boundary: Direct user selection 「A」 in the current conversation after the options recorded in audit #297. Behavioral effectiveness remains unverified.

## 2026-07-19 — Questioning may retrieve information and support judgment formation

- Decision: AgentOS questioning may serve two distinct purposes: obtain information, preferences, or authorization that only the user can supply; and help the user discover a not-yet-formed goal, value conflict, or judgment. The AI must not present the second activity as if it were merely uncovering a pre-existing user intent.
- Reason: Restricting questions to information retrieval leaves hidden conflicts and unformed choices untouched. Allowing judgment-forming questions without distinguishing them gives the AI cover to plant its own framing and call it the user's intent.
- Scope: Product meaning only. This decision does not yet define who may initiate judgment exploration, when that mode must be visible, how questions are batched, or any implementation mechanism.
- Evidence boundary: Direct user confirmation 「对，继续」 in response to the recommendation that both purposes belong in AgentOS but must remain distinguishable. Behavioral effectiveness remains unverified.

## 2026-07-19 — Observable unresolved conditions permit AI-initiated judgment exploration (ZX chose A)

- Decision: The AI may initiate judgment exploration when an observable unresolved condition exists: the user requests exploration, expresses uncertainty, states conflicting goals, or a user-owned tradeoff materially blocks the next step. Before asking, the AI states why exploration is needed; a clear user decision ends it. AI-user disagreement alone is never sufficient grounds to initiate or continue exploration.
- Reason: Requiring an explicit request in every case misses blind spots the user cannot yet name, while unrestricted AI discretion lets disagreement become a pretext for retaining control. Observable unresolved conditions preserve initiative without transferring final authority.
- Scope: Product meaning only. This decision does not yet determine whether the user or AI should express a view first, how questions are batched, or how the policy is implemented.
- Evidence boundary: Direct user selection 「A」 in response to the three initiation-authority options presented after audit #300. Behavioral effectiveness remains unverified.

## 2026-07-19 — Exploration ordering adapts to whether the user already has a view (ZX chose C)

- Decision: When the user already has a view, lived experience, or value preference that has not yet been expressed, preserve that independent expression before exposing the AI's recommendation. When the user has no view, is unfamiliar with the domain, or directly asks for the AI's judgment, the AI answers first with materially different alternatives, its recommendation and basis, and an explicit ability to reject all options. If the user has already stated a view, the AI does not ask for it again and responds independently.
- Reason: A fixed AI-first order risks anchoring the user, while a fixed user-first order can become an empty exam or an evasion of a direct request for advice. Adaptive ordering assigns the first move according to which party actually has an unexpressed contribution worth preserving.
- Scope: Product meaning only. The policy mitigates but does not eliminate anchoring; question batching, exact wording, implementation, and behavioral effectiveness remain unresolved.
- Evidence boundary: Direct user selection 「C」 in response to the three ordering options presented after audit #301. Behavioral effectiveness remains unverified.

## 2026-07-19 — Question groups follow dependency, not a fixed count (ZX chose B)

- Decision: Ask the smallest set of mutually independent questions whose answers are jointly required before the next useful step. If one answer can change, remove, or regenerate another question, ask them sequentially. If questions are independent, share the same context, and jointly block the next step, ask them together. The user may answer only part of a group; the AI then re-evaluates the remainder rather than demanding form completion.
- Reason: Always asking one question creates avoidable round trips, while always batching a fixed number asks downstream questions before their premises are known. Dependency-based grouping makes question count an output of the unresolved decision structure rather than a product ritual.
- Scope: Product meaning only. A numeric cap may later be tested as an interface convenience, but it is not the governing principle. Exact wording, stopping conditions, implementation, and behavioral effectiveness remain unresolved.
- Evidence boundary: Direct user selection 「b」 in response to the three batching options presented after audit #302. Behavioral effectiveness remains unverified.

## 2026-07-19 — Substantive question admission and stopping support are both visible (ZX chose B)

- Decision: Before asking a load-bearing question, the AI must visibly name the current decision or next action, the user-owned unknown, the plausible answer branches, and what each branch would change. When it concludes that questioning can stop, it must visibly name what has been resolved, what remains unknown, why the plausible remaining branches do not change the current step, the assumptions and residual risk, and what would reopen questioning. Ordinary factual clarifications may remain conversational; this decision does not claim access to or disclosure of hidden chain-of-thought.
- Reason: A stop explanation alone cannot let the user detect questions that never had decision value, while exhaustive reasoning disclosure is unverifiable and would turn ordinary conversation into a ritual. Visible support on both entry and exit makes the AI's decision to ask, continue, or stop inspectable without transferring final authority away from the user.
- Scope: Product meaning only. This decision does not yet define the proposed cross-turn question-lineage representation, its display cadence, persistence, implementation, or behavioral effectiveness.
- Evidence boundary: Direct user selection 「B」 in response to the three visibility options presented after audit #304. Behavioral effectiveness remains unverified.

## 2026-07-19 — Inquiry lineage is a node network, not a tree (ZX chose C and clarified)

- Decision: The user-visible inquiry lineage is organized as a network of persistent nodes and explicit relationships, not as a single-parent tree. The root goal is an anchor node rather than a requirement that every node have one fixed parent. A node may affect several decisions, several paths may converge on one node, and a resolved or deferred node may be reopened. Chronology is retained as metadata or a secondary view; the mainline is the currently relevant route through the network rather than a permanent trunk.
- Reason: A tree distorts inquiry when one unknown supports several decisions, when separate branches converge, or when later evidence reactivates an earlier issue. A node network preserves these relations and allows the user's current position and level of detail to be shown without pretending that thought develops in one hierarchy.
- Scope: Product meaning only. This decision does not yet define what qualifies as a node, the minimum node types, the relationship vocabulary, display cadence, persistence, implementation, or behavioral effectiveness.
- Evidence boundary: Direct user statement 「C，我更想要的不是一个 tree 结构，而是一个节点结构」. The structural preference is verified; its behavioral benefit remains an unverified design judgment.

## 2026-07-19 — The inquiry network uses typed semantic nodes and exists for route recovery (ZX chose C)

- Decision: The inquiry network uses a small set of typed semantic nodes: goals, decisions, load-bearing questions, evidence, and assumptions. Chat messages and trivial clarifications do not become nodes by default. A node must have an independently revisitable identity, an independently meaningful status, or an explicit effect on another node. The network's primary product purpose is to let the user and AI reconstruct the route from the initial idea to the current result, identify the current position and any unacknowledged divergence, and return to the last still-valid route without deleting the explored branch.
- Reason: A question-only network hides the goals and decisions against which relevance must be judged, while converting every utterance into a node reproduces the transcript in a more complicated form. Typed semantic nodes preserve the objects needed to evaluate route, provenance, and recovery rather than merely visualizing conversation order.
- Scope: Product meaning only. This decision does not yet settle whether the original goal is immutable, how a legitimate goal revision differs from drift, the minimum relationship vocabulary, display cadence, persistence, implementation, or behavioral effectiveness.
- Evidence boundary: Direct user selection 「C」 followed by the stated problem that neither user nor AI can reliably tell whether iterative questioning has left the mainline or how the final result relates to the initial idea. The selected node model and intended purpose are verified; the proposed admission rule and expected benefit remain unverified design judgments.

## 2026-07-19 — Route judgment keeps immutable origin and explicit current-goal versions (ZX chose C)

- Decision: Route judgment uses dual goal anchors. The initial goal remains an immutable origin node. A current goal may be refined, narrowed, expanded, or replaced only by creating a new goal node linked to the previous one with the change type, reason, and visible user confirmation when product meaning materially changes. Mainline relevance is judged against the latest accepted current-goal node, while the complete goal lineage remains visible against the origin. Returning moves the active focus to the last still-valid accepted node and parks later exploration without erasing it.
- Reason: Treating the initial goal as permanently binding misclassifies legitimate learning as drift, while retaining only the latest goal lets unnoticed substitutions erase the evidence that direction changed. Dual anchors preserve both adaptation and accountability.
- Scope: Product meaning only. This decision does not yet define the minimum relationship vocabulary, who proposes and confirms ordinary non-goal relations, display cadence, persistence, implementation, or behavioral effectiveness.
- Evidence boundary: Direct user selection 「c」 in response to the three route-anchor options presented after audit #307. Behavioral effectiveness remains unverified.

## 2026-07-19 — Inquiry routes use a small typed relationship set (ZX chose C)

- Decision: Semantic nodes use a small, extensible relationship set with five families: goal change (`refines`, `narrows`, `expands`, `replaces`); necessity (`requires`, `unblocks`); evidential influence (`supports`, `weakens`); bounded exploration (`explores`, `returns_to`); and conflict (`contradicts`, `blocks`). A natural-language reason may explain a relation but cannot replace its type. A new semantic node must have a typed relation to the active route or be visibly marked unclassified/off-route; it cannot become mainline merely because it is topically related. New relation types are added only after a real uncovered case appears.
- Reason: A generic “related” edge cannot explain direction, while unrestricted prose produces incomparable labels and lets the AI rationalize any transition after the fact. A small typed set makes route claims inspectable without requiring a comprehensive ontology in advance.
- Scope: Product meaning only. This decision does not yet define who proposes or confirms relations, which relation changes require user approval, display cadence, persistence, implementation, or behavioral effectiveness.
- Evidence boundary: Direct user selection 「C」 in response to the three relationship-model options presented after audit #308. Behavioral effectiveness remains unverified.

## 2026-07-19 — AI keeps the route by default; the user may redirect or reintegrate at any time (ZX chose A and clarified)

- Decision: The AI normally maintains and explains the current route. A material change to the actual goal remains the user's decision. The user may at any time declare that the conversation has drifted and direct a return to the last mutually accepted goal or decision node; the AI may state a material disagreement briefly, but may not use that disagreement to keep the detour active. The user may instead ask how discoveries from the detour feed back into the mainline; the AI then identifies which discoveries affect the accepted goal, explains that effect, parks the remainder, and returns. User correction is an additional route-control channel, not a substitute for the AI's duty to detect and disclose possible drift.
- Reason: AI-only route control repeats the self-certification problem, while requiring user approval for every ordinary relation makes the user perform the bookkeeping. Default AI maintenance plus an immediate user override preserves low interaction burden and final user authority. A useful discovery can be salvaged without retroactively making the detour justified.
- Scope: Product meaning only. The default treatment of detour discoveries when the user says only “return to the mainline,” the exact drift criteria, display, persistence, implementation, and behavioral effectiveness remain unresolved.
- Evidence boundary: Direct user selection 「A」 followed by 「我自己可能也会意识到我们走偏了，我会说要求回到原来的路上，或者说我们这一路的发现怎么反哺到我们原来那个主干上。」 Behavioral effectiveness remains unverified.

## 2026-07-19 — A bare return command performs one bounded salvage pass (ZX chose B)

- Decision: When the user says only “return to the mainline,” the AI performs one short salvage pass before restoring the prior active focus. It carries back only findings whose effect on the accepted goal, decision, assumption, evidence, or next action can be stated explicitly; it explains that effect briefly and parks everything else. The AI may not continue investigating the detour or open new detour questions under the label of salvage.
- Reason: Dropping the whole detour can lose information that changes the mainline, while asking for permission every time transfers routine bookkeeping back to the user. A bounded salvage pass preserves relevant learning without letting the return command become another detour.
- Scope: Product meaning only. The route display cadence, exact drift criteria, interface, persistence, implementation, and behavioral effectiveness remain unresolved.
- Evidence boundary: Direct user selection 「B」 in response to the three default treatments presented after audit #311. Behavioral effectiveness remains unverified.

## 2026-07-19 — The route marker appears at meaningful route changes and on demand (ZX chose B)

- Decision: The AI proactively shows a compact “where we are now” route marker when the accepted goal changes, a key judgment changes the direction, the conversation enters a bounded detour, or it returns to the mainline. The user may request the marker at any time. The marker is not repeated on every ordinary turn, and the AI may not wait for the user to notice drift before showing it at one of these events.
- Reason: Showing the marker every turn turns visibility into reading burden, while showing it only on request cannot help with drift the user has not yet noticed. Event-based display makes material route changes inspectable without making route bookkeeping dominate the conversation.
- Scope: Product meaning only. The marker's minimum contents, default level of detail, exact drift criteria, interface, persistence, implementation, and behavioral effectiveness remain unresolved.
- Evidence boundary: Direct user selection 「B」 in response to the three display-timing options presented after audit #312. Behavioral effectiveness remains unverified.

## 2026-07-19 — The compact route marker preserves origin, current position, and route justification (ZX chose B)

- Decision: Each compact route marker shows the initial goal, the latest user-accepted current goal, the current activity or step, and the explicit reason that activity belongs to the current route. When the activity is a bounded detour, the marker additionally shows the detour's purpose and the point to which the conversation will return. It does not unfold the complete node history by default.
- Reason: Showing only the current goal hides whether that goal was silently substituted, while unfolding the full network every time recreates the cognitive burden the marker is meant to reduce. The selected compact comparison exposes origin, adaptation, current position, and route justification together.
- Scope: Product meaning only. The exact drift test, how detail is expanded on demand, interface, persistence, implementation, and behavioral effectiveness remain unresolved.
- Evidence boundary: Direct user selection 「B」 in response to the three marker-content options presented after audit #313. Behavioral effectiveness remains unverified.

## 2026-07-19 — Drift means a missing route relation or a silent goal substitution (ZX chose B)

- Decision: An activity remains on the route only when the AI can state which user-accepted goal, judgment, or next action it affects and how. Necessary exploration that does not yet directly advance the goal remains legitimate only when it is declared as a bounded detour with a purpose and return point. If neither condition is met, or if the accepted goal changes without visible user confirmation, the activity is marked as drift. Topical similarity and a retrospective story are not sufficient route justification.
- Reason: Treating every indirect step as drift blocks necessary discovery, while waiting for the user alone to declare drift removes the AI's monitoring duty. A checkable relation or a declared detour makes exploration possible without allowing silent direction changes.
- Scope: Product meaning only. What the AI must do immediately after detecting possible drift, how disagreement is resolved, detail expansion, interface, implementation, and behavioral effectiveness remain unresolved.
- Evidence boundary: Direct user selection 「B」 in response to the three drift-test options presented after audit #314. Behavioral effectiveness remains unverified.

## 2026-07-19 — Detected drift pauses the branch; present-stage necessity precedes route mechanics (ZX chose B and corrected the route)

- Decision: When the AI detects possible drift, it pauses the branch, shows where the route appears to have broken and what it recommends, and leaves the user to choose return, a bounded detour, or a goal change. ZX exercised that authority in the live deliberation. A question or design detail belongs on the active mainline only when it is not merely related to the goal but necessary for the current top-level decision: the AI must be able to name which next top-level action cannot be taken without the answer. Otherwise the detail is parked. The active mainline now returns to defining the human problem AgentOS solves, its core promise, the AI/user authority boundary, the v1 boundary, and acceptance evidence.
- Reason: Audits #309-#315 form a live counterexample to the prior relation-only criterion. Every micro-question could be connected to route visibility, yet their accumulation displaced the still-unsettled product purpose. “Related eventually” is therefore weaker than “necessary now.”
- Scope: This qualifies the decision immediately above rather than erasing the useful route-recovery findings. The detailed node relations, route marker, salvage behavior, and display choices from #309-#315 are retained as a parked design branch, not as prerequisites or an implementation specification. No implementation or behavioral-effectiveness claim is authorized.
- Evidence boundary: Direct user selection and correction 「B，我们现在就好像走偏了，你有没有这种感觉？我感觉你在问我一些细枝末节的东西，甚至说你没有从第一性原理思考这些东西。」 plus the audit sequence #309-#315. The causal diagnosis is the current best explanation, not a proven universal rule.

## 2026-07-19 — User authority does not transfer decision labor to the user

- Decision: The user retains final authority over goals, values, private facts, material irreversible or high-stakes commitments, spending, external actions, and explicit changes of destination. The AI owns the remaining cognitive and operational labor: research, precedent checks, problem decomposition, synthesis, alternatives, an independent recommendation, safe defaults, reversible choices, and execution inside the accepted boundary. A user question is an exception and is admitted only when all four conditions hold: the answer is genuinely user-owned; it cannot be recovered from context, research, or a stated assumption; plausible answers materially change the current route or risk; and no safe, reversible default exists. Otherwise the AI decides or proposes first and makes any material assumption visible.
- Reason: Final authority and decision labor are different things. Questions consume the user's limited attention and can anchor or exhaust judgment. Making the user answer every unresolved design choice lets the AI avoid the very thinking and synthesis it exists to provide. The opposite extreme—silently deciding user values or irreversible commitments—would take authority away. Proposal-first interaction with a narrow question exception preserves both responsibility and user control.
- Scope: Product meaning only. This constrains the earlier exploration and question-grouping decisions; it does not prohibit a bounded question when all four conditions hold, establish a fixed question count, authorize implementation, or prove behavioral effectiveness. Recognition of a coherent proposal is preferred over asking the user to construct the product from blank questions.
- Evidence boundary: Direct user correction 「还要做什么？你真正的思考了吗？真正的思考清楚了吗？不能无限的问我，这也是一个很重要的点。你要知道用户的认知是有上限的，而且虽然我们讲决策是最重要的部分，但是你如果把所有的东西就逃避全部压到用户的身上也是一种非常不负责任的表现。」 The role boundary is accepted product meaning; its effectiveness remains unverified until real-task trials.

## 2026-07-19 — Complete accepted capability scope with minimum new code

- Decision: Every product capability and constraint retained through the current AgentOS deliberation is part of the implementation target, including independent visible judgment, bounded questioning and decision-labor allocation, user authority, inquiry lineage, typed semantic nodes and relations, original/current goal anchors, route markers, drift detection, pause and bounded salvage, evidence-aware completion, and recovery. “Minimum” applies only to the amount of new implementation: reuse existing kernel rules, state, storage, runtime primitives, skills, and composition wherever they can deliver the required behavior. It does not reduce the capability scope, behavioral semantics, safety, visibility, or verification burden.
- Reason: Code volume and product capability are different variables. Reuse can deliver a large behavior with a small delta, while a small feature set can still require much code. Optimizing the former by deleting the latter substitutes an engineering proxy for the product object.
- Scope: The required scope covers accepted capabilities and corrections, not mutually exclusive options that were rejected during deliberation or a particular candidate mechanism. Grill Me installation, a specific UI technology, or always-on subagents are means and are required only if they are the best minimal-delta way to realize a capability. Delivery may be staged, but final acceptance remains full-scope and behavior-based.
- Evidence boundary: Direct user clarification 「最小部分不代表实现的最小，只代表我们代码改动的最小。但我们现在说的、到目前为止聊的这些所有的东西，都应该被实现。能理解这意思吗？」 This fixes the product scope; no implementation or behavioral completion is claimed.

## 2026-07-19 — New non-small goals start with a formal Executive Intake (ZX chose route 2)

- Decision: Every new non-small goal starts proposal-first. Before mutation, delegation, spending, or external commitment, the AI reconstructs the user's purpose and user-visible success, separates the goal from named means, performs the read-only investigation needed to understand the object, frames the real problem, exposes meaningful routes and tradeoffs, gives an independent recommendation and change condition, divides AI-owned decision labor from the remaining user-owned choice, and names the next action. The first non-small transaction remains in deliberation; execution begins only after the user-owned route is selected or otherwise clearly authorized. A small, exact, reversible task with no product-meaning choice retains a short path.
- Reason: The first live test showed that intent, task-contract, and anti-sycophancy rules did not stop an AI from treating a named repository as the task itself, choosing a partial dual-backend integration, and writing before it had inspected the upstream object or clarified the product route. A Stop-only check is too late once mutation has already happened. The missing capability is a formal employee-style task-start stage plus an action-point gate, not another general prompt reminder.
- Scope: This applies to new sessions and new non-small goals. Read-only reconnaissance is allowed before the visible proposal. It does not require ritual menus for tiny tasks, does not reopen a route the user has already selected, and does not create a second orchestration backend. The current implementation reuses the cognitive transaction, PromptSubmit, PreToolUse, and Stop layers.
- Evidence boundary: Direct user selection 「第二条路线」 after choosing between a prompt-only patch, a formal task-start stage, and a mandatory two-turn protocol. Deterministic and subprocess runtime evidence may establish the implemented contract; behavioral effectiveness still requires a clean-session replay of the original dynamic-workflow request.

## 2026-07-19 — First-principles decision closure supersedes task-size admission

- Decision: First-principles reasoning is AgentOS's highest cognitive-method constraint, subordinate only to verified facts, user authority, and safety boundaries. Every new goal reconstructs the real purpose, visible success, facts, constraints, goal-versus-means, and decision ownership before execution. Admission is determined by `decision_state`: `open` while any present-stage user-owned outcome choice is unresolved, and `closed` only when every such choice has a grounded user resolution. Open decisions require visible investigation, routes, tradeoffs, an independent recommendation, and an authority boundary before mutation or delegation. Closed decisions execute without a redundant confirmation. Task size, reversibility, and product meaning no longer define closure; destructive action, spending, production risk, and external commitment remain independent safety gates.
- Reason: The prior `small_clear | non_small` split used implementation proxies to answer an authority question. A one-line public API rename can leave compatibility policy open, while a major product change can be fully specified and authorized. Adding more evidence fields around the proxy would preserve the wrong frame. Decision closure directly asks whether any user-owned outcome branch remains.
- Scope: This supersedes the task-size short-path clause and the unconditional claim that every new non-small goal must consume a second authorization turn. It preserves the formal Executive Intake, read-only reconnaissance, action-point guard, independent recommendation, user authority, and single Dynamic Workflow backend. Remaining AI-owned investigation and implementation choices do not become user questions merely because they are difficult.
- Evidence boundary: Direct corrections 「最重要的是第一性原理思考」 and acceptance 「对，这种回复就是很好的，需要真正的为老板分忧」 establish the product rule. Unit, runtime-envelope, scenario, mutation, lint, and installer checks establish only the implemented contract; clean Codex and Claude tasks must still test semantic classification on real prompts.
