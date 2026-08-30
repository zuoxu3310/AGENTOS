"""面板服务：静态页、字体、目录浏览、最近项目、轮询接口、用户动作。链路在 run.py，这里不重写状态机。"""
from __future__ import annotations
import json, os, shutil, socket, subprocess, sys, threading, time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, urlparse
import run, snapshot

HERE = Path(__file__).resolve().parent
PROJECTS = HERE / "projects.json"
TASKS: dict[str, run.Task] = run.load_tasks()
DEFAULT_ROOT = os.path.realpath(sys.argv[2] if len(sys.argv) > 2 else os.getcwd())


def host_name() -> str:
    """这台机器的名字（手机上看"家里哪台在线"）：先问系统设置里的电脑名，问不到用主机名。"""
    try:
        n = subprocess.run(["scutil", "--get", "ComputerName"], capture_output=True, text=True, timeout=3).stdout.strip()
    except (OSError, subprocess.SubprocessError):
        n = ""
    return n or socket.gethostname()


HOST = host_name()
# 模型下拉清单（与旧面板 board/daemon.py 同源）：claude 侧是 2026-08-21 逐个 `claude -p --model X` 实测过的名单；
# codex 侧起服时问 `codex app-server` 的 model/list（带各型号支持的强度档），问不到就用同日实测的快照。
MODELS = {
    "claude": [
        {"id": "fable", "label": "Fable 5"}, {"id": "opus", "label": "Opus 5"}, {"id": "sonnet", "label": "Sonnet 5"},
        {"id": "haiku", "label": "Haiku 4.5"}, {"id": "claude-opus-4-8", "label": "Opus 4.8"},
        {"id": "claude-opus-4-7", "label": "Opus 4.7"}, {"id": "claude-opus-4-6", "label": "Opus 4.6"},
        {"id": "claude-opus-4-5", "label": "Opus 4.5"}, {"id": "claude-opus-4-1", "label": "Opus 4.1"},
        {"id": "claude-sonnet-4-6", "label": "Sonnet 4.6"}, {"id": "claude-sonnet-4-5", "label": "Sonnet 4.5"},
    ],
    "codex": [
        {"id": "gpt-5.6-sol", "label": "GPT-5.6 Sol"}, {"id": "gpt-5.6-terra", "label": "GPT-5.6 Terra"},
        {"id": "gpt-5.6-luna", "label": "GPT-5.6 Luna"}, {"id": "gpt-5.5", "label": "GPT-5.5"}, {"id": "gpt-5.4", "label": "GPT-5.4"},
        {"id": "gpt-5.4-mini", "label": "GPT-5.4 Mini"}, {"id": "gpt-5.3-codex-spark", "label": "GPT-5.3 Codex Spark"},
    ],
}


def refresh_codex_models() -> None:
    """问 codex 本人拿在售模型：app-server 的 JSON-RPC model/list。后台跑一次；拿不到就保持快照。"""
    try:
        p = subprocess.Popen(["codex", "app-server"], stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                             stderr=subprocess.DEVNULL, text=True, bufsize=1, start_new_session=True)
    except OSError as e:
        print(f"codex app-server 起不来，模型清单用快照：{e}", file=sys.stderr)
        return
    dog = threading.Timer(20, lambda: p.poll() is None and os.killpg(p.pid, 9))
    dog.daemon = True
    dog.start()
    rows = []
    try:
        p.stdin.write(json.dumps({"jsonrpc": "2.0", "id": 1, "method": "initialize",
                                  "params": {"clientInfo": {"name": "aos", "title": "aos", "version": "0.1"}}}) + "\n")
        p.stdin.flush()
        time.sleep(1.2)                                   # initialize 没就绪就发 model/list 会被丢掉，实测要等
        p.stdin.write(json.dumps({"jsonrpc": "2.0", "method": "initialized"}) + "\n")
        p.stdin.write(json.dumps({"jsonrpc": "2.0", "id": 2, "method": "model/list", "params": {}}) + "\n")
        p.stdin.flush()
        for line in p.stdout:
            try:
                d = json.loads(line)
            except ValueError:
                continue
            if d.get("id") != 2:
                continue
            for m in (d.get("result") or {}).get("data") or []:
                if m.get("hidden") or not m.get("id"):
                    continue
                row = {"id": m["id"], "label": m.get("displayName") or m["id"]}
                efforts = [e["reasoningEffort"] for e in (m.get("supportedReasoningEfforts") or []) if e.get("reasoningEffort")]
                if efforts:
                    row["efforts"] = efforts
                if m.get("isDefault"):
                    row["default"] = True
                rows.append(row)
            break
    except (BrokenPipeError, OSError) as e:
        print(f"codex model/list 没问到：{e}", file=sys.stderr)
    finally:
        dog.cancel()
        if p.poll() is None:
            os.killpg(p.pid, 9)
    if rows:
        MODELS["codex"] = rows
        print(f"codex 模型清单已从 model/list 刷新：{len(rows)} 个", flush=True)


def projects() -> list[dict]:
    rows = json.loads(PROJECTS.read_text(encoding="utf-8")) if PROJECTS.exists() else []
    return [{"path": p, "name": Path(p).name or p, "exists": Path(p).is_dir(), "git": (Path(p) / ".git").exists()} for p in rows]


def remember(root: str) -> None:
    ps = [root] + [p for p in (json.loads(PROJECTS.read_text(encoding="utf-8")) if PROJECTS.exists() else []) if p != root]
    PROJECTS.write_text(json.dumps(ps[:20], ensure_ascii=False, indent=1), encoding="utf-8")


def listdir(path: str, show_all: bool) -> dict:
    p = Path(os.path.expanduser(path or "~")).resolve()
    if not p.is_dir():
        return {"path": str(p), "exists": False, "dirs": [], "error": "不是目录"}
    dirs = []
    for d in sorted(p.iterdir()):
        if d.is_dir() and (show_all or not d.name.startswith(".")):
            dirs.append({"name": d.name, "git": (d / ".git").exists(), "agentos": (d / "agent-os").exists()})
    return {"path": str(p), "exists": True, "parent": str(p.parent), "dirs": dirs[:300],
            "git": (p / ".git").exists(), "agentos": (p / "agent-os").exists()}


def payload(t: run.Task, seq: int) -> dict:
    """某一次上场：当时原样存下的完整提示词，和它对应的那次返回。"""
    prompt = (t.dir / "prompts" / f"{seq}.txt").read_text(encoding="utf-8")
    done = next((e for e in t.events() if e["kind"] == "step" and e.get("started") == seq), None)
    return {"prompt": prompt, "output": done and (done.get("output") if done["status"] == "completed" else done.get("error")),
            "tools": [e for e in t.events() if e["kind"] == "tool" and e.get("call") == seq and e["status"] != "started"]}


class H(BaseHTTPRequestHandler):
    def log_message(self, *a):
        pass

    def send(self, code: int, body, ctype="application/json"):
        data = body if isinstance(body, bytes) else json.dumps(body, ensure_ascii=False).encode()
        self.send_response(code)
        self.send_header("Content-Type", f"{ctype}; charset=utf-8" if ctype.startswith(("text", "application")) else ctype)
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def body(self) -> dict:
        n = int(self.headers.get("Content-Length") or 0)
        return json.loads(self.rfile.read(n) or b"{}")

    def do_GET(self):
        u = urlparse(self.path)
        q = {k: v[0] for k, v in parse_qs(u.query).items()}
        parts = u.path.strip("/").split("/")
        if u.path in ("/", "/panel.html"):
            return self.send(200, (HERE / "panel.html").read_bytes(), "text/html")
        if parts[0] == "fonts" and len(parts) == 2 and (HERE / "fonts" / parts[1]).exists():
            return self.send(200, (HERE / "fonts" / parts[1]).read_bytes(), "font/woff2")
        if parts == ["api", "ls"]:
            return self.send(200, listdir(q.get("path", ""), q.get("all") == "1"))
        if parts == ["api", "projects"]:
            return self.send(200, {"projects": projects(), "default": DEFAULT_ROOT, "seats": run.SEATS,
                                   "home": os.path.expanduser("~"), "models": MODELS, "host": HOST, "perms": run.PERMS})
        if parts[:2] == ["api", "tasks"] and len(parts) == 2:
            rows = sorted((run.summary(t) for t in TASKS.values()), key=lambda r: -r["updated"])
            return self.send(200, {"tasks": rows})
        if parts[:2] == ["api", "tasks"] and len(parts) >= 3:
            t = TASKS.get(parts[2])
            if not t:
                return self.send(404, {"error": "没有这个任务"})
            if len(parts) == 3:
                return self.send(200, {"summary": run.summary(t), "events": t.events(int(q.get("after") or 0))})
            if parts[3] == "diff":
                seq = int(q.get("seq") or 0)
                ch = next((e for e in reversed(t.events()) if e["kind"] == "changes" and e.get("stage") == "result"
                           and (not seq or e["seq"] == seq)), None)
                if not ch:
                    return self.send(404, {"error": "没有这张改动卡"})
                return self.send(200, {"patch": snapshot.file_patch(t.root, t.id, ch["tree0"], ch["tree_end"], q.get("path", ""))})
            if parts[3] == "payload":
                return self.send(200, payload(t, int(q["seq"])))
        self.send(404, {"error": "no route"})

    def do_POST(self):
        parts = urlparse(self.path).path.strip("/").split("/")
        b = self.body()
        if parts == ["api", "tasks"]:
            root = os.path.realpath(os.path.expanduser(b.get("root") or DEFAULT_ROOT))
            remember(root)
            t = run.new_task(root, b["words"], int(b.get("mode") or 3), b.get("seats"), bool(b.get("auto")), b.get("perm") or "edits")
            TASKS[t.id] = t
            run.start(t)
            return self.send(200, run.summary(t))
        t = TASKS.get(parts[2]) if len(parts) == 4 and parts[:2] == ["api", "tasks"] else None
        if not t:
            return self.send(404, {"error": "没有这个任务"})
        act = parts[3]
        try:
            if act == "message":
                run.interject(t, b["text"])
            elif act == "answer":
                run.answer(t, b["text"])
            elif act == "contract":
                run.approve(t)
            elif act == "changes":
                run.decide(t, "revert" if b.get("action") == "revert" else "adopt")
            elif act == "stop":
                run.stop(t)
            elif act == "rename":
                run.rename(t, b["title"])
            elif act == "config":
                if b.get("mode"):
                    t.mode = int(b["mode"])
                if b.get("seats"):
                    t.set_seats(b["seats"])
                if "auto" in b:
                    t.auto = bool(b["auto"])
                if b.get("perm") in run.PERMS:
                    t.perm = b["perm"]
                t.emit("task", phase=run.summary(t)["phase"], mode=t.mode, seats=t.seats, auto=t.auto, perm=t.perm)
            elif act == "compact":
                return self.send(200, {"summary": run.compact(t)})
            elif act == "delete":
                run.stop(t)
                if t.thread:
                    t.thread.join(10)
                try:
                    snapshot.drop_refs(t.root, t.id)
                except Exception:
                    pass
                shutil.rmtree(snapshot.SHADOW_DIR / f"{t.id}.git", ignore_errors=True)
                TASKS.pop(t.id, None)
                shutil.rmtree(t.dir, ignore_errors=True)
                return self.send(200, {"deleted": t.id})
            else:
                return self.send(404, {"error": "no route"})
        except run.Failed as e:
            return self.send(409, {"error": str(e)})
        self.send(200, run.summary(t))


if __name__ == "__main__":
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 8765
    print(f"面板：http://127.0.0.1:{port}/  默认项目根：{DEFAULT_ROOT}")
    threading.Thread(target=refresh_codex_models, daemon=True).start()
    ThreadingHTTPServer(("127.0.0.1", port), H).serve_forever()
