# Quickstart

1. `python3 board/server.py 8765 ~/your-projects-root` → open http://127.0.0.1:8765/
2. Pick a directory (any project under your root), say what you want done.
3. The chain runs. It stops for you at three gates: a question from 中书 (rare, at most one), the contract (approve or send it back with a sentence), and the change set (adopt or revert, with per-file diffs).
4. Follow-ups go to the same task; each message is a new turn of the full chain. Interject any time — a running reading restarts with your words merged.
5. Modes (per task, in the panel): chain 1/2/3 · approval manual/auto · executor permission edits/auto/bypass.
6. Phone: same URL on your LAN; narrow screens get the two-level layout. The process rail under the title opens the full live graph with a replay slider.

CLI equivalent (what the `agentos` skill uses):

```bash
python3 board/aos.py start
python3 board/aos.py new "add a --name flag to hello.py" --root ~/proj
python3 board/aos.py wait <id>      # returns when it is your turn, prints what to look at
python3 board/aos.py approve <id> · adopt <id> · revert <id> · answer <id> "…" · say <id> "…" · stop <id>
```
