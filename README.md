# AgentOS

AgentOS is a self-hosted panel that runs a fixed multi-agent chain — 三省六部, the Three Departments — on top of the Claude Code and Codex CLIs.

You say one thing. The program then runs the whole chain: 中书 (Secretariat) reads your words → 门下 (Chancellery) seats review it blind and compare → a **contract waits for your approval** → 尚书 (State Affairs) plans → executors edit files → integration → delivery → the **change set waits for your adopt / revert** → 御史 (Censorate) audits the delivery item by item. Every role is a fresh `claude -p` / `codex exec` subprocess given a role workflow from `kernel/` and forced to answer in a per-step JSON schema. The panel shows the chain live — desktop and phone are the same page — with a replayable timeline of everything that happened.

The design stance: the human owns meaning and irreversible decisions (the contract, the changes); the program owns order and evidence; understanding, review, and execution are separated across model contexts so no single context can fake all three.

## Run

```bash
python3 board/server.py 8765 ~/your-projects-root
# open http://127.0.0.1:8765/
```

Requires Python 3.10+ and a logged-in `claude` and/or `codex` CLI. To see the whole chain without spending tokens:

```bash
python3 board/tests/test_board.py   # 13 scenarios against bundled fake CLIs
```

## Install on a machine

```bash
python3 scripts/install-agentos.py ~/AgentOS --source .
```

This copies `board/` + `kernel/` and registers a global `agentos` skill, so `/agentos <task>` in Claude Code (or `$agentos` in Codex) from **any** directory operates the panel — the chat session is a panel operator, never a seat.

## Layout

| Path | What |
|---|---|
| `board/run.py` | The chain state machine: turns, gates, snapshots, auto mode, permission tiers |
| `board/server.py` | HTTP API (stdlib only) |
| `board/panel.html` | One-file UI, responsive (three-pane desktop, two-level mobile, live process graph with replay) |
| `board/aos.py` | CLI client — what the `agentos` skill calls |
| `board/snapshot.py` | Git-shadow change tracking; adopt/revert is real |
| `kernel/workflows/` | The five role workflows |
| `kernel/schemas/` | The JSON each step must hand over |
| `kernel/*/SKILL.md` | Eleven role-agnostic method skills (written in Chinese — they are the product's methodology) |

Per-task modes: chain depth 1/2/3 · approval **manual / auto** (auto still stops when the censor finds a deviation) · executor permission **edits / auto / bypass**.

## History

v2 (2026-08) was a hook-enforced in-session chain installed into each project; it lives in this repository's git history. v3 is this panel: one resident program, one URL, and your projects stay clean.
