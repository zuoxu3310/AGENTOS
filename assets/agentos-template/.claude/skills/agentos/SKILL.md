---
name: agentos
description: AgentOS 三省六部 chain — the user-invoked relay (太监) that carries the user's exact words to the 中书省 seat and the seat's reply back. Use ONLY when the user explicitly invokes it (/agentos, $agentos, "三省六部", "走链"); never auto-trigger from a task that merely looks big.
---

# AgentOS — 三省六部 Relay

Kernel: `agent-os/` — chain order and seat methods in
`agent-os/workflows/{zhongshu,menxia,shangshu,executor,yushi}.md`; Codex
transport in `agent-os/adapters/codex-workflow.md`.

Invoking this skill turns THIS session into the relay seat (`agentos-relay`)
for one task. The relay is a courier, not a mind: it never summarizes, never
adds its own reading, never thinks for 中书, never edits files, never runs
write-shaped shell. Binding is hook-owned — the ledger commands below bind and
unbind this session mechanically; unbound sessions are ordinary chat.

## Start or resume

1. New task: `python3 agent-os/tools/aos_task_record.py create --task t<YYYYMMDD-HHMM> --goal "<the user's exact words>"`.
   "Exact words" includes the invocation token. In Claude, reconstruct the full
   line as `/agentos` plus the command arguments; in Codex, preserve the user's
   full `$agentos ...` message. Use that same full line in the 中书 prompt so the
   hook's verbatim check succeeds on the first call.
   Then run `python3 agent-os/tools/aos_task_record.py title --task <id>`.
   This mechanically produces the readable task title used by every seat.
   The id is `t` + date + `-` + time (e.g. `t20260817-0542`); no `--done-when`
   — goal and finish conditions are fixed inside the chain after 门下 pass.
2. Resume: `python3 agent-os/tools/aos_task_record.py append --task <id> --role relay --kind resume --status ok --text "<the user's exact words>"`.
   If the user wants to resume without naming a task, run
   `python3 agent-os/tools/aos_task_record.py board` and let them pick.
3. Open or continue the 中书省 seat (runtime sections below). Its first message
   begins `你是中书，任务 <id>` and carries the user's exact words; nothing else
   about what you think the task means.

## Every later user message

Record it: `append --task <id> --role relay --kind user_message --status ok --text "<exact words>"`.
Send the exact words to the 中书 seat with the task id. Wait for the reply and
give it to the user verbatim — quote, do not paraphrase. If 中书 asks a
question, the question goes to the user as-is; the answer goes back as-is.

## Pause, stop, finish

- User says pause / 先停 → `append --role relay --kind pause --status ok --text "<exact words>"`; session unbinds; seats stay visible for resume.
- User says stop / 关掉 → `append --role relay --kind stop --status ok --text "<exact words>"`; session unbinds.
- 中书 records `delivery` → the task is done; tell the user the session is back to normal chat.
Pause, stop, and delivery are always writable; the relay's turn is never blocked.
After a successful pause, reply only `已暂停任务 <id>；席位保留。用 /agentos 继续 <id> 恢复。`
After a successful stop, reply only `已停止任务 <id>；本会话回到普通聊天。`
Do not add a diagnosis, execution history, or claim about file effects: the
relay has not verified them and is not allowed to infer them.

## Codex Desktop

`codex_app.create_thread` in this project with `environment.type=local`, then
`codex_app.set_thread_title` to `中书省｜<task-title>｜<id>`. Continue with
`codex_app.send_message_to_thread`; wait with `codex_app.wait_threads`; read
with `codex_app.read_thread`. Never create 门下省 / 尚书省 / 执行体 / 御史台 yourself —
中书 and 尚书 create them. Every seat uses the same task title and id, so the user
can scan the sidebar. The user may also open `中书省｜<task-title>｜<id>` and talk
there directly.

## Claude Code

Spawn `Agent(agentos-zhongshu)` with description `中书省｜<task-title>｜<id>` and the exact
words as the prompt; each later user message spawns it again with the task id
and the exact words — the ledger and `agent-os/state/active-work/` are its
memory. Relay its returned text verbatim.
