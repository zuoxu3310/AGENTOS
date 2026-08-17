# Codex Workflow Adapter

## Purpose

This is the Codex-only transport adapter for the AgentOS three-departments
chain. Seat methods remain in `agent-os/workflows/*.md`; review methods remain
in `agent-os/review/*.md`. Claude keeps its native Agent, Workflow, and
Superpowers route unchanged.

The chain is opt-in. Ordinary Codex chat is the default; nothing here applies
until the user explicitly invokes the `agentos` skill (`$agentos`, "三省六部",
"走链"). The invoking thread then becomes the relay (`agentos-relay`,
`.agents/skills/agentos/SKILL.md`): it records the user's exact words
(`aos_task_record.py create --task t<YYYYMMDD-HHMM> --goal "<exact words>"`,
later `append --role relay --kind user_message|pause|resume|stop`), creates
`中书省｜<task-title>｜<task-id>`, and carries messages verbatim in both directions. The relay never
thinks or edits in the user's place. Only an explicit user instruction, recorded
by 门下 (never by the actor) as a verbatim `bypass` ledger entry, may bypass the
chain inside a task.

## Desktop Thread Mechanism

Codex uses the Desktop's built-in `codex_app` thread tools. The relay creates
`中书省｜<task-title>｜<task-id>` in the current project with `codex_app.create_thread`
(`environment.type=local`); Zhongshu creates `门下省｜<task-title>｜<task-id>` and
`尚书省｜<task-title>｜<task-id>`; Shangshu creates
`执行体｜<task-title>｜<task-id>`; Zhongshu creates
`御史台｜<task-title>｜<task-id>` only for
confirmed error learning. The title passed to `codex_app.set_thread_title` is
exactly the same. Every initial message begins with
`你是中书/门下/尚书/执行体/御史，任务 <task>` and directs the thread to its matching
`.codex/agents/agentos-*.toml` and kernel workflow; every seat reads the SKILL.md
files listed for its role in `agent-os/skills/seat-skills.json` and records the
hash skill receipt (`aos_skill_receipt.py`) before phase work. Follow-ups use
`codex_app.send_message_to_thread`; callers wait with `codex_app.wait_threads`,
read results with `codex_app.read_thread`, and archive completed seat threads
with `codex_app.set_thread_archived` at the next task start.
The task title is not an AI summary: task creation stores a deterministic
first-clause label, printed by `aos_task_record.py title --task <task-id>`.
Every seat for that task reuses the exact same label.

The chain hook binds the relay thread on its first ledger command, records
successful seat creation in `agent-os/state/seats.json`, and writes the
corresponding session identity; unbound threads see silent hooks. Native Codex
`spawn_agent` seats remain denied. The seat roster and seat methods are unchanged.

## Chain Mapping

| Seat | Codex Desktop route | Kernel method |
| --- | --- | --- |
| relay | the invoking Desktop thread after `$agentos`; `.agents/skills/agentos/SKILL.md` | courier only — no method |
| 中书 | relay creates `中书省｜<title>｜<id>`; `.codex/agents/agentos-zhongshu.toml` | `agent-os/workflows/zhongshu.md` |
| 门下 | Zhongshu creates `门下省｜<title>｜<id>`; Phase B uses `send_message_to_thread` | `agent-os/workflows/menxia.md` |
| 尚书 | Zhongshu creates `尚书省｜<title>｜<id>`; approved work uses `send_message_to_thread` | `agent-os/workflows/shangshu.md` |
| executor | Shangshu creates `执行体｜<title>｜<id>` and sends task work to it | `agent-os/workflows/executor.md` |
| 御史 | Zhongshu creates `御史台｜<title>｜<id>` only for confirmed error learning | `agent-os/workflows/yushi.md` |

The relay alone starts 中书; Zhongshu alone starts menxia, shangshu, and yushi;
Shangshu alone starts executors. No thread simulates another seat. A transport
failure is reported raw and nonzero; the caller never substitutes itself for the
missing seat.

## Chain Gate

`.codex/hooks/aos_chain_gate.py` uses the mapped session identity and task
ledger to enforce only mechanical order:

```text
unbound thread            : all hooks silent (no inject, no deny, no block)
relay bind                : first `create` (id t<YYYYMMDD-HHMM>, goal = verbatim user
                            words, no --done-when) or `append --role relay --kind resume`
create zhongshu           : relay only; duplicate seat+task denied
create menxia/shangshu/yushi : Zhongshu only; duplicate seat+task denied
create executor           : Shangshu only; duplicate seat+task denied
send zhongshu             : relay only, prompt must quote the latest user message
send shangshu             : Zhongshu only, after comparison/pass or bypass
send executor             : Shangshu only, after dispatch
send menxia/yushi         : Zhongshu only
native spawn_agent        : denied for agentos-* on Codex
workspace writes          : executors after dispatch; 御史 under wiki/;
                            中书 only under a bypass recorded by 门下; relay never
relay Stop                : never blocked; pause/stop/delivery unbind
zhongshu Stop             : blocked once until this turn left a zhongshu record
```

Reads and terminal records remain writable; unknown hook input fails open.
Claude Agent/Task spawning and retitling are not changed by this adapter.

## Prompt, Ownership, And Authority

Before each seat creation or task message, apply `agent-os/review/prompt-craft-gate.md`:
materials first, at least three distinct XML sections, assignment last, and the
exact kernel paths the seat must read. Each writable artifact has a single
writer at a time. Use the cheapest capable model for bounded, verifiable work
and escalate for ambiguity, synthesis, security, or a costly miss. The user
retains changed outcomes, spend, destructive actions, production risk, and
values.

## Seat Visibility And Evidence Boundary

Gate tests establish create registration, duplicate prevention, ordered sends,
mapped identity, and native-route denial while preserving Claude. Installer and
structural tests establish publication only. Live Desktop behavior remains a
separate user-run acceptance check.
