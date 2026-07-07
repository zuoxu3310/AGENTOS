#!/usr/bin/env python3
"""Create a full project memory scaffold without overwriting existing files."""

from __future__ import annotations

import argparse
from datetime import date
from pathlib import Path


DIRS = [
    "wiki",
    "wiki/errors",
    "wiki/docs",
    "wiki/raw",
    "wiki/ledgers",
    "wiki/TASKS",
    "wiki/CHATS",
    "wiki/knowledge",
]


FILES = {
    "wiki/AGENTS.md": """# Project Agent Instructions

## Operating Rules

- Follow the latest user message first.
- Keep project state in durable files instead of relying on chat memory.
- Do not invent content to fill empty memory files.
- Before writing durable project memory, use `wiki-maintenance` as the router.
- Use `HANDOFF.md` for current next-agent state.
- Keep `PLANS.md`, `PROGRESS.md`, `DECISIONS.md`, and `HANDOFF.md` as canonical root ledgers.
- Treat `wiki/ledgers/` ledger paths as wiki-side symlinks back to the root ledgers.
- Use `wiki/TASKS/` for non-trivial task contracts.
- Use `PLANS.md` for active and recent plans.
- Use `PROGRESS.md` for evidence-backed progress.
- Use `DECISIONS.md` for durable decisions and reasons.
- Use `wiki/CHATS/` for distilled key user intent from conversations.
- Use `wiki/errors/` for confirmed repeated agent errors.
- Use `wiki/docs/` for project documentation.
- Use `wiki/knowledge/` for compiled project knowledge and reusable methodology.
- Treat `wiki/raw/` as read-only source material.
- Do not scatter plans, progress, decisions, or handoff into wiki pages. Wiki may summarize, cite, and link to those ledgers, but not replace them.
- Routine routing is autonomous. Ask the user only for sensitive content, destructive file moves, or ambiguous ownership.

## Completion Rule

Completion means the requested work is done, necessary evidence is available, and durable state is updated when the work changed future context.
""",
    "PLANS.md": """# Plans

Canonical ledger for active and recently completed plans. Do not replace this with wiki pages.

## Active

- None yet.

## Recently Completed

- None yet.
""",
    "PROGRESS.md": """# Progress

Canonical append-only ledger for evidence-backed progress. Do not replace this with wiki pages.

## Entries

""",
    "DECISIONS.md": """# Decisions

Canonical append-only ledger for durable project decisions and why they were made.

## Entries

""",
    "HANDOFF.md": """# Handoff

Canonical current-state handoff for the next agent. Keep current; do not turn it into history.

## Current State

Not initialized beyond memory scaffold.

## Next Step

Fill this after the first meaningful task.

## Risks / Open Questions

- None recorded yet.
""",
    "wiki/index.md": """# Project Memory Index

## Entry Files

- [AGENTS.md](AGENTS.md): canonical shared agent instructions.
- [../AGENTS.md](../AGENTS.md): root symlink to `wiki/AGENTS.md`.
- [../CLAUDE.md](../CLAUDE.md): root symlink to `wiki/AGENTS.md`.
- [../PLANS.md](../PLANS.md): canonical active and recent plans.
- [../PROGRESS.md](../PROGRESS.md): canonical append-only progress.
- [../DECISIONS.md](../DECISIONS.md): canonical durable decisions.
- [../HANDOFF.md](../HANDOFF.md): canonical current next-agent state.
- [ledgers/PLANS.md](ledgers/PLANS.md), [ledgers/PROGRESS.md](ledgers/PROGRESS.md), [ledgers/DECISIONS.md](ledgers/DECISIONS.md), [ledgers/HANDOFF.md](ledgers/HANDOFF.md): wiki-side symlinks to root ledgers.

These four files are canonical ledgers. Wiki may summarize, cite, and link to them, but must not replace them.

## Directories

- [TASKS/](TASKS/): task contracts.
- [CHATS/](CHATS/): distilled chat decisions.
- [ledgers/](ledgers/): wiki-side links to canonical root ledgers.
- [errors/](errors/): confirmed agent errors.
- [docs/](docs/): project documentation.
- [../errors/](../errors/), [../docs/](../docs/): root compatibility symlinks.
- [knowledge/](knowledge/): compiled knowledge and reusable methodology.
- [raw/](raw/): original source material.
""",
    "wiki/log.md": """# Project Memory Log

## Entries

""",
    "wiki/raw/README.md": """# Raw Sources

Original source material goes here.

Raw files are not automatically wiki pages. Classify each source before ingesting it.

- Direct read: Markdown, text, JSON, YAML, TOML, CSV/TSV, logs, diffs, patches, small source files.
- Tool-required read: PDF, DOCX, XLSX, PPTX, HTML exports, screenshots that need OCR.
- Link-only by default: images, audio, video, archives, binaries, large generated outputs.

Agents may read these files but should not rewrite them as compiled knowledge.
Track source status in MANIFEST.md when useful.
""",
    "wiki/raw/MANIFEST.md": """# Raw Source Manifest

Track raw sources that have been added, parsed, summarized, linked, or intentionally skipped.

| Source | Type | Status | Output | Notes |
|---|---|---|---|---|
""",
    "wiki/errors/_INDEX.md": """# Error Index

Confirmed agent mistakes, repeated failures, and corrections that should change future behavior.

## High Priority Rules

- None yet.

## Recent Errors

- None yet.
""",
    "wiki/docs/README.md": """# Docs

Project documentation intended for users or developers goes here.

Prefer Markdown or small plain-text docs here. Put binary originals in wiki/raw/ and link to a summarized Markdown page when needed.
""",
    "wiki/ledgers/README.md": """# Ledgers

This directory exposes canonical project ledgers inside the wiki tree.

The actual canonical files live at the project root:

- ../../PLANS.md
- ../../PROGRESS.md
- ../../DECISIONS.md
- ../../HANDOFF.md

The matching files in this directory are symlinks back to those root ledgers.
""",
    "wiki/TASKS/README.md": """# Task Contracts

One non-trivial task gets one task card.

Use the card to record Goal, Boundaries, Evidence, Autonomy, and Handoff.
""",
    "wiki/CHATS/README.md": """# Chat Notes

Distilled chat decisions and user intent go here.

Do not save full transcripts unless the user explicitly asks.
""",
    "wiki/knowledge/README.md": """# Knowledge

Compiled project knowledge and reusable methodology go here.

Do not replace PLANS.md, PROGRESS.md, DECISIONS.md, or HANDOFF.md with knowledge pages.
""",
}


TASK_TEMPLATE = """# Task Contract: MYSUB-01 <name>

## Goal

## Boundaries

## Evidence

## Autonomy

## Handoff
"""


CHAT_TEMPLATE = """# Chat Notes - <date-topic>

## Context

## User Decisions

## Scope Changes

## Quotes

## Follow-up
"""


def write_if_missing(path: Path, content: str, force: bool, created: list[str], preserved: list[str]) -> None:
    if path.exists() and not force:
        preserved.append(str(path))
        return
    if path.is_symlink() and force:
        path.unlink()
    if path.is_dir():
        preserved.append(str(path))
        return
    path.write_text(content, encoding="utf-8")
    created.append(str(path))


def symlink_if_missing(path: Path, target: str, force: bool, created: list[str], preserved: list[str]) -> None:
    if path.exists() or path.is_symlink():
        if not force:
            preserved.append(str(path))
            return
        if path.is_dir() and not path.is_symlink():
            preserved.append(str(path))
            return
        path.unlink()
    path.symlink_to(target)
    created.append(str(path))


def main() -> int:
    parser = argparse.ArgumentParser(description="Create a full project memory scaffold.")
    parser.add_argument("project", nargs="?", default=".", help="Project directory. Defaults to current directory.")
    parser.add_argument("--force", action="store_true", help="Overwrite existing scaffold files.")
    args = parser.parse_args()

    root = Path(args.project).expanduser().resolve()
    root.mkdir(parents=True, exist_ok=True)

    created: list[str] = []
    preserved: list[str] = []

    for dirname in DIRS:
        path = root / dirname
        if path.exists():
            preserved.append(str(path))
        else:
            path.mkdir(parents=True)
            created.append(str(path))

    for filename, content in FILES.items():
        write_if_missing(root / filename, content, args.force, created, preserved)

    symlink_if_missing(root / "AGENTS.md", "wiki/AGENTS.md", args.force, created, preserved)
    symlink_if_missing(root / "CLAUDE.md", "wiki/AGENTS.md", args.force, created, preserved)
    symlink_if_missing(root / "errors", "wiki/errors", args.force, created, preserved)
    symlink_if_missing(root / "docs", "wiki/docs", args.force, created, preserved)
    symlink_if_missing(root / "wiki" / "ledgers" / "PLANS.md", "../../PLANS.md", args.force, created, preserved)
    symlink_if_missing(root / "wiki" / "ledgers" / "PROGRESS.md", "../../PROGRESS.md", args.force, created, preserved)
    symlink_if_missing(root / "wiki" / "ledgers" / "DECISIONS.md", "../../DECISIONS.md", args.force, created, preserved)
    symlink_if_missing(root / "wiki" / "ledgers" / "HANDOFF.md", "../../HANDOFF.md", args.force, created, preserved)

    today = date.today().isoformat()
    write_if_missing(root / "wiki" / "TASKS" / "MYSUB-01-task-card-template.md", TASK_TEMPLATE, args.force, created, preserved)
    write_if_missing(root / "wiki" / "CHATS" / f"{today}-chat-notes-template.md", CHAT_TEMPLATE, args.force, created, preserved)

    print("Created:")
    for item in created:
        print(f"  {item}")
    print("Preserved:")
    for item in preserved:
        print(f"  {item}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
