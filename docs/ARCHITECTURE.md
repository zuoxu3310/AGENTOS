# Architecture

One task = one append-only event log (`board/tasks/<id>/events.jsonl`). Kinds: task (phase), step (role started/completed/failed, with its JSON output), message, gate, action, changes, tool (every Read/Edit/Bash a role performed, paired start/end), error. The panel and `aos.py` are pure readers of this log plus a small actions API; replay is just "apply events up to a cursor".

Chain per turn (mode 3): zhongshu reads (step 1) ∥ each menxia seat reads blind (1) → menxia compare & verdict (2) → zhongshu reply (3, may carry one question and the contract) → [contract gate] → shangshu plan (4) → executors (5, the only writers, serial with per-node snapshots) → shangshu integration (6) → zhongshu delivery (7) → [changes gate] → yushi audit (8). Modes 1/2 stop the chain at the reply.

Roles are subprocesses: `claude -p --json-schema … --tools …` / `codex exec --json --output-schema …`, prompts assembled from `kernel/workflows/<role>.md` plus the materials of that step; a non-zero exit is a failure even if JSON was produced. Executor permission tiers map to `--permission-mode acceptEdits|auto|bypassPermissions` (Codex: workspace-write / danger-full-access).

Changes are tracked against a git shadow repository (works in non-git directories too): tree snapshot before execution, tree after, diff = the changes card; revert restores the pre-turn tree. A changes card can only be settled once (claimed under a lock); if the process dies holding an unsettled card, restart restores it and hands the gate back to the user.

Auto approval mode: the question gate is answered with "use your own recommendation, record the assumption", the contract is auto-approved, and the changes card is held while yushi audits first — clean audit auto-adopts, any filled deviation stops and waits for the human. Every automatic action is an `action` event flagged `auto:true`.
