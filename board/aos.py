#!/usr/bin/env python3
"""aos：从命令行操作面板。/agentos 那个 skill 只做一件事——调它。

  aos.py start [--root ~/Downloads]        面板没起就起，打印地址
  aos.py new "<话>" [--root DIR] [--mode 1|2|3] [--auto] [--perm edits|auto|bypass]
  aos.py ls                                 所有任务：id 阶段 标题 目录
  aos.py show ID [--tail 12]                一条任务：摘要 + 最近的事
  aos.py wait ID [--secs 1800]              等到轮到用户（等你答/批/定）、说完（等你说）或终态，把该看的打印出来
  aos.py say ID "<话>"   answer ID "<答>"   approve ID   adopt ID   revert ID   stop ID
  aos.py config ID [--mode N] [--auto|--manual] [--perm X]
端口默认 8765（环境变量 AOS_PORT 可改）。"""
import argparse, json, os, socket, subprocess, sys, time, urllib.error, urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
PORT = int(os.environ.get("AOS_PORT", 8765))
BASE = f"http://127.0.0.1:{PORT}"
PH = {"reading": "在办", "executing": "在办", "censoring": "在办", "queued": "排队", "compacting": "压缩中",
      "waiting_answer": "等你答", "waiting_contract": "等你批", "waiting_changes": "等改动决定", "idle": "等你说",
      "done": "完成", "failed": "失败", "interrupted": "中断", "stopped": "已停止"}
DONE = ("idle", "done", "failed", "interrupted", "stopped")


def up() -> bool:
    try:
        socket.create_connection(("127.0.0.1", PORT), timeout=0.5).close()
        return True
    except OSError:
        return False


def api(path: str, body=None):
    data = json.dumps(body, ensure_ascii=False).encode() if body is not None else None
    req = urllib.request.Request(BASE + path, data=data, method="POST" if data else "GET",
                                 headers={"Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=15) as r:
            return json.load(r)
    except urllib.error.HTTPError as e:
        sys.exit("面板说：" + (json.load(e).get("error") or e.reason))
    except urllib.error.URLError:
        sys.exit(f"面板没在 {BASE}。先 `python3 {sys.argv[0]} start`")


def fmt(s: dict) -> str:
    tag = " · 自动档" if s.get("auto") else ""
    return f"{s['id']}  {PH.get(s['phase'], s['phase'])}{tag}  {s.get('title', '')}  ({s.get('root', '')})"


def line(e: dict) -> str:
    k = e["kind"]
    if k == "message":
        return ("你" if e.get("who") == "user" else "中书") + "：" + e.get("text", "")
    if k == "gate":
        g = e["gate"]
        if g == "question":
            return "门·问：" + "；".join(f"{d.get('q', '')}（{'/'.join(map(str, d.get('opts') or []))}）" for d in e.get("decisions") or [])
        if g == "contract":
            c = e.get("contract") or {}
            return "门·契约：" + str(c.get("goal", "")) + " · 完成条件：" + "；".join(map(str, c.get("done_when") or []))
        return "门·改动：等你定采纳还是撤回"
    if k == "action":
        return "动作：" + e["action"] + ("（自动档）" if e.get("auto") else "") + ("：" + e["text"] if e.get("text") else "")
    if k == "step" and e.get("status") != "started":
        return f"步·{e['role']} {e.get('label', '')} {e['status']}" + (f" {e['secs']}s" if e.get("secs") else "") + ("：" + e["error"] if e.get("error") else "")
    if k == "changes" and e.get("stage") == "result":
        fs = e.get("files") or []
        return "改动：" + f"{len(fs)} 个文件 " + " ".join(f"{f.get('path')}(+{f.get('add', 0)}/-{f.get('del', 0)})" for f in fs)
    if k == "error":
        return "错：" + e.get("text", "")
    if k == "task" and e.get("phase"):
        return "阶段：" + PH.get(e["phase"], e["phase"])
    return ""


def start(a):
    if not up():
        log = open(os.path.join(HERE, "server.log"), "a")
        subprocess.Popen([sys.executable, os.path.join(HERE, "server.py"), str(PORT), os.path.expanduser(a.root)],
                         cwd=HERE, stdout=log, stderr=subprocess.STDOUT, start_new_session=True)
        for _ in range(50):
            if up():
                break
            time.sleep(0.2)
        else:
            sys.exit("面板起不来，看 board/server.log")
    print(BASE + "/")


def new(a):
    s = api("/api/tasks", {"words": a.words, "root": os.path.abspath(os.path.expanduser(a.root)), "mode": a.mode,
                           "auto": a.auto, "perm": a.perm})
    print(fmt(s))
    print(BASE + "/")


def ls(a):
    for s in api("/api/tasks")["tasks"]:
        print(fmt(s))


def show(a):
    d = api(f"/api/tasks/{a.id}")
    print(fmt(d["summary"]))
    for e in d["events"][-a.tail:]:
        t = line(e)
        if t:
            print("  " + t)


def wait(a):
    t0 = time.time()
    while True:
        d = api(f"/api/tasks/{a.id}")
        ph = d["summary"]["phase"]
        if ph.startswith("waiting_") or ph in DONE or time.time() - t0 > a.secs:
            break
        time.sleep(2)
    print(fmt(d["summary"]))
    evs = d["events"]
    if ph == "waiting_answer" or ph == "waiting_contract":
        g = next(e for e in reversed(evs) if e["kind"] == "gate")
        print("  " + line(g))
        m = next((e for e in reversed(evs) if e["kind"] == "message" and e.get("who") == "zhongshu"), None)
        if m:
            print("  " + line(m))
    elif ph == "waiting_changes":
        c = next(e for e in reversed(evs) if e["kind"] == "changes" and e.get("stage") == "result")
        print("  " + line(c))
    elif ph in DONE:
        for e in evs[-6:]:
            t = line(e)
            if t:
                print("  " + t)


def post(a, act, body):
    print(fmt(api(f"/api/tasks/{a.id}/{act}", body)))


def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = p.add_subparsers(dest="cmd", required=True)
    s = sub.add_parser("start"); s.add_argument("--root", default="~/Downloads"); s.set_defaults(f=start)
    s = sub.add_parser("new"); s.add_argument("words"); s.add_argument("--root", default=".")
    s.add_argument("--mode", type=int, default=3, choices=(1, 2, 3)); s.add_argument("--auto", action="store_true")
    s.add_argument("--perm", default="edits", choices=("edits", "auto", "bypass")); s.set_defaults(f=new)
    sub.add_parser("ls").set_defaults(f=ls)
    s = sub.add_parser("show"); s.add_argument("id"); s.add_argument("--tail", type=int, default=12); s.set_defaults(f=show)
    s = sub.add_parser("wait"); s.add_argument("id"); s.add_argument("--secs", type=int, default=1800); s.set_defaults(f=wait)
    for name, act, key in (("say", "message", "text"), ("answer", "answer", "text")):
        s = sub.add_parser(name); s.add_argument("id"); s.add_argument("text")
        s.set_defaults(f=lambda a, act=act, key=key: post(a, act, {key: a.text}))
    s = sub.add_parser("approve"); s.add_argument("id"); s.set_defaults(f=lambda a: post(a, "contract", {}))
    for name in ("adopt", "revert"):
        s = sub.add_parser(name); s.add_argument("id"); s.set_defaults(f=lambda a, name=name: post(a, "changes", {"action": name}))
    s = sub.add_parser("stop"); s.add_argument("id"); s.set_defaults(f=lambda a: post(a, "stop", {}))
    s = sub.add_parser("config"); s.add_argument("id"); s.add_argument("--mode", type=int, choices=(1, 2, 3))
    g = s.add_mutually_exclusive_group(); g.add_argument("--auto", action="store_true"); g.add_argument("--manual", action="store_true")
    s.add_argument("--perm", choices=("edits", "auto", "bypass"))
    s.set_defaults(f=lambda a: post(a, "config", {k: v for k, v in (("mode", a.mode), ("perm", a.perm),
                                                                   ("auto", True if a.auto else False if a.manual else None)) if v is not None}))
    a = p.parse_args()
    a.f(a)


if __name__ == "__main__":
    main()
