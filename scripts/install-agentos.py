#!/usr/bin/env python3
"""把 AgentOS（面板版）装到这台机器。

做三件事：
1. 把源仓库的 board/ + kernel/ + README.md 拷到目标目录（默认 ~/AgentOS；不拷运行态和个人化的 remote/）。
2. 写全局 agentos skill（~/.claude/skills/agentos 与 ~/.agents/skills/agentos），让 /agentos（Codex 里 $agentos）
   在任何目录都能操作面板，--root 用当前目录。
3. 打印启动命令。

用法：python3 install-agentos.py [目标目录] [--source 源仓库路径]
源仓库默认取本脚本所在仓库（脚本在 <repo>/scripts/ 里时）。已存在的目标文件会被同名覆盖，
但 board/tasks、board/shadow、board/projects.json（运行态）永不触碰。
"""
import argparse, os, shutil, sys

SKIP = {"tasks", "shadow", "__pycache__", "projects.json", "server.log", "remote", ".DS_Store"}


def copytree(src: str, dst: str) -> None:
    os.makedirs(dst, exist_ok=True)
    for name in sorted(os.listdir(src)):
        if name in SKIP:
            continue
        s, d = os.path.join(src, name), os.path.join(dst, name)
        if os.path.isdir(s):
            copytree(s, d)
        else:
            shutil.copy2(s, d)


SKILL = '''---
name: agentos
description: Use when the user invokes /agentos ($agentos on Codex) with a task, or asks to run something through AgentOS / 三省六部 / 走链. The chain runs inside the AgentOS panel program; this session only operates that panel through aos.py and never plays a seat itself. Do not trigger on tasks that merely look big.
---

# AgentOS — 面板版（全局入口）

AgentOS 装在 `{home}`：`board/server.py` 跑三省六部（中书读法 → 门下盲审 → 契约 → 尚书计划 → 执行体 → 整合 → 中书交付 → 改动决定 → 御史逐项比），角色是它自己起的 `claude -p` / `codex exec` 子进程，方法在 `kernel/`。这个会话不是任何座位，是面板的操作员。

AOS=`python3 {home}/board/aos.py`

1. 起面板：`$AOS start`，把地址 http://127.0.0.1:8765/ 告诉用户（手机同一地址）。
2. 开任务：`$AOS new "<用户原话，一字不改>" --root <用户要动的目录，默认当前目录>`；用户点了档位加 `--mode 1|2|3`、`--auto`、`--perm edits|auto|bypass`。只有指令没有任务内容：问一句要做什么，不开任务。
3. 跟进：`$AOS wait <id>`，回来后把打印的内容原样转给用户——等你答（中书的问题）／等你批（契约要点）／等改动决定（改动清单）／等你说（交付原文）／失败（错误原文）。
4. 用户的话往回传：`answer`、`approve`、`adopt`/`revert`、`say`、`stop`。传原话，不替用户决定。
5. 旧任务：`ls` 找 id，`show <id>` 看最近的事。

不做：不当中书/门下/尚书/执行体，不读 kernel/ 工作流，不写契约，不改用户文件，不替任何人拿主意。
'''


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("target", nargs="?", default="~/AgentOS")
    ap.add_argument("--source", default="")
    a = ap.parse_args()
    here = os.path.dirname(os.path.abspath(__file__))
    src = os.path.expanduser(a.source) if a.source else os.path.dirname(here)
    for need in ("board", "kernel"):
        if not os.path.isdir(os.path.join(src, need)):
            sys.exit(f"源仓库 {src} 里没有 {need}/；用 --source 指到 AgentOS 仓库")
    dst = os.path.abspath(os.path.expanduser(a.target))
    for d in ("board", "kernel"):
        copytree(os.path.join(src, d), os.path.join(dst, d))
    rd = os.path.join(src, "README.md")
    if os.path.exists(rd):
        os.makedirs(dst, exist_ok=True)
        shutil.copy2(rd, os.path.join(dst, "README.md"))
    body = SKILL.replace("{home}", dst)
    for skdir in ("~/.claude/skills/agentos", "~/.agents/skills/agentos"):
        p = os.path.expanduser(skdir)
        os.makedirs(p, exist_ok=True)
        open(os.path.join(p, "SKILL.md"), "w", encoding="utf-8").write(body)
    print(f"装好了：{dst}")
    print(f"起面板：python3 {dst}/board/server.py 8765 ~/Downloads")
    print("会话入口：/agentos（Claude Code）、$agentos（Codex）——已写进全局 skills")


if __name__ == "__main__":
    main()
