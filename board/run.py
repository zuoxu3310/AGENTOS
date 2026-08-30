"""三省六部固定链路：按死顺序叫角色，每次＝角色文档＋方法＋材料＋答案格子 → claude/codex 命令行 → JSON，记事件。"""
from __future__ import annotations
import json, os, random, re, subprocess, sys, threading, time
from concurrent.futures import ThreadPoolExecutor
from graphlib import TopologicalSorter
from pathlib import Path
import snapshot

HERE = Path(__file__).resolve().parent
KERNEL = Path(os.environ.get("AOS_KERNEL", HERE.parent / "kernel"))   # 工作流、schema、方法 skill 都在仓库的 kernel/
WORKFLOWS = KERNEL / "workflows"
SCHEMAS = KERNEL / "schemas"
TASKS = HERE / "tasks"
ROLE_TIMEOUT, EXEC_TIMEOUT = 1800, 2400            # 只防挂死；实测 opus xhigh 门下比对一步能想超过 10 分钟
SEATS = {
    "zhongshu": {"engine": "claude", "model": "opus", "effort": "xhigh"},
    "menxia_1": {"engine": "claude", "model": "opus", "effort": "xhigh"},
    "menxia_2": {"engine": "codex", "model": "", "effort": ""},
    "shangshu": {"engine": "claude", "model": "opus", "effort": "xhigh"},
    "executor": {"engine": "claude", "model": "opus", "effort": "xhigh"},
    "yushi": {"engine": "claude", "model": "opus", "effort": "xhigh"},
}
NAMES = {"zhongshu": "中书", "menxia_1": "门下甲", "menxia_2": "门下乙", "menxia_3": "门下丙", "menxia_4": "门下丁",
         "shangshu": "尚书", "executor": "执行体", "yushi": "御史"}
WF_FILE = {"zhongshu": "zhongshu.md", "menxia_1": "menxia.md", "menxia_2": "menxia.md", "menxia_3": "menxia.md",
           "menxia_4": "menxia.md", "shangshu": "shangshu.md", "executor": "executor.md", "yushi": "yushi.md"}
# 实测过的命令行参数（见 board/daemon.py 200–275 行的注释）：禁 MCP；执行体可写；禁碰任务记录目录
NO_MCP = ["--strict-mcp-config", "--mcp-config", '{"mcpServers":{}}']
EXEC_WRITE = ["--permission-mode", "acceptEdits", "--allowedTools", "Bash,Edit,Write,MultiEdit"]
# 执行权限档（只管执行体）：edits＝上面那套白名单；auto＝claude 自己的 auto 权限模式（分类器判每一步）；bypass＝全放
PERMS = ("edits", "auto", "bypass")
AUTO_NOTE = "自动：用户不在场看着，不要向用户提问；拿不准就选最稳的读法，把假设写进契约的 assumptions。"
AUTO_ANSWER = "自动模式：按你自己推荐的那个办，把这条假设写进契约。"
READ_TOOLS, EXEC_TOOLS = "Read,Grep,Glob", "Read,Grep,Glob,Edit,Write,Bash"
DENY = ["--settings", json.dumps({"permissions": {"deny": [
    f"{t}(//{TASKS}/**)" for t in ("Read", "Grep", "Glob", "Edit", "Write")]}})]
CODEX_NO_MCP = ["-c", "features.apps=false", "-c", "features.plugins=false", "-c", "features.remote_plugin=false"]


def perm_args(perm: str) -> list[str]:
    if perm == "bypass":
        return ["--permission-mode", "bypassPermissions"]
    if perm == "auto":
        return ["--permission-mode", "auto"]
    return EXEC_WRITE
REPO_LOCKS: dict[str, threading.Lock] = {}
_LOCK = threading.Lock()
TERMINAL = ("done", "failed", "interrupted", "stopped")


def codex_mcp_off() -> list[str]:
    out = list(CODEX_NO_MCP)
    cfg = Path(os.environ.get("CODEX_HOME") or Path.home() / ".codex") / "config.toml"
    if cfg.exists():
        import tomllib
        for name in (tomllib.loads(cfg.read_text(encoding="utf-8")).get("mcp_servers") or {}):
            out += ["-c", f"mcp_servers.{name}.enabled=false"]
    return out


def schema(name: str) -> tuple[Path, dict]:
    p = SCHEMAS / f"{name}.json"
    return p, json.loads(p.read_text(encoding="utf-8"))


class Failed(Exception):
    pass


class Task:
    """一个任务＝一段多轮对话。turn：第几轮对话；attempt：这一轮读法第几次（插话作废重开就加一）。"""

    def __init__(self, tid: str, root: str, mode: int = 3, seats: dict | None = None, auto: bool = False, perm: str = "edits"):
        self.id, self.root, self.mode = tid, root, mode
        self.auto, self.perm = bool(auto), (perm if perm in PERMS else "edits")   # 审批自动档；执行权限档
        self.seats = {k: dict(v) for k, v in SEATS.items()}
        self.set_seats(seats or {})
        self.dir = TASKS / tid
        (self.dir / "prompts").mkdir(parents=True, exist_ok=True)
        self.seq = sum(1 for _ in self._lines())
        self.lock = threading.Lock()
        self.settle_lock = threading.Lock()              # 改动卡只能结算一次：认领、终态都在这把锁里
        self.cancel = threading.Event()
        self.procs: list[subprocess.Popen] = []
        self.words = ""
        self.turn, self.attempt = 0, 0
        self.asked = False
        self.answer: str | None = None
        self.decision: str | None = None
        self.last_reply: dict | None = None
        self.mats: dict[str, str] = {}
        self.pending: list[str] = []
        self.open_changes: dict | None = None            # 停止/失败时留下的未决改动卡：{tree0, tree_end, seq}
        self.final_phase = ""                            # 线程收场时卡还没定：定完再落这个终态
        self.compacting = False
        self.stopped = False
        self.thread: threading.Thread | None = None
        self.answered, self.approved, self.decided, self.spoke = (threading.Event() for _ in range(4))

    def set_seats(self, seats: dict) -> None:
        for k, v in seats.items():
            if k in NAMES:
                self.seats.setdefault(k, {"engine": "claude", "model": "", "effort": ""})
                self.seats[k].update({kk: str(vv) for kk, vv in v.items() if kk in ("engine", "model", "effort")})

    def menxia(self) -> list[str]:
        return sorted(k for k in self.seats if k.startswith("menxia_"))

    def _lines(self):
        f = self.dir / "events.jsonl"
        return f.read_text(encoding="utf-8").splitlines() if f.exists() else []

    def emit(self, kind: str, **d) -> dict:
        with self.lock:
            self.seq += 1
            ev = {"seq": self.seq, "t": round(time.time(), 3), "kind": kind, "turn": self.turn, "attempt": self.attempt, **d}
            with open(self.dir / "events.jsonl", "a", encoding="utf-8") as f:
                f.write(json.dumps(ev, ensure_ascii=False) + "\n")
        return ev

    def events(self, after: int = 0) -> list[dict]:
        return [json.loads(l) for l in self._lines()[after:]]

    def history(self) -> tuple[str, list[dict]]:
        """对话事实的唯一来源是事件：最近一次摘要之后的话、回答、回话与交付；作废的 attempt 不算。"""
        evs = self.events()
        last_attempt: dict[int, int] = {}
        for e in evs:
            if e["kind"] == "message" and e.get("what") == "words":
                last_attempt[e["turn"]] = max(last_attempt.get(e["turn"], 0), e["attempt"])
        summary_text, rows = "", []
        for e in evs:
            if e["kind"] == "message" and e.get("what") == "summary":
                summary_text, rows = e["text"], []
                continue
            live = e.get("attempt", 0) >= last_attempt.get(e.get("turn"), 0)
            if e["kind"] == "message" and e.get("what") in ("words", "reply", "delivery") and live:
                rows.append({"who": e["who"], "what": e["what"], "text": e["text"], "turn": e["turn"]})
            elif e["kind"] == "action" and e.get("action") == "answer" and live:
                rows.append({"who": "user", "what": "answer", "text": e["text"], "turn": e["turn"]})
        return summary_text, rows

    def kill(self) -> None:
        for p in list(self.procs):
            try:
                os.killpg(p.pid, 9)
            except ProcessLookupError:
                pass


def new_task(root: str, words: str, mode: int = 3, seats: dict | None = None, auto: bool = False, perm: str = "edits") -> Task:
    tid = time.strftime("%Y%m%d-%H%M%S") + f"-{random.randrange(16**4):04x}"
    t = Task(tid, root, mode, seats, auto, perm)
    t.pending = [words]
    t.emit("task", phase="reading", root=root, title=words.strip().splitlines()[0][:60], mode=mode, seats=t.seats,
           auto=t.auto, perm=t.perm)
    return t


def pending_card(evs: list) -> dict | None:
    """最后一张 stage=result 的改动卡，后面没有 adopt/revert 就是还没定的。"""
    for e in reversed(evs):
        if e["kind"] == "action" and e.get("action") in ("adopt", "revert"):
            return None
        if e["kind"] == "changes" and e.get("stage") == "result":
            return e
    return None


def load_tasks() -> dict[str, Task]:
    """重启后：完成一轮在等你说话的任务原样恢复（可以接着说）；正在跑或等你批的记成中断。"""
    out = {}
    for f in sorted(TASKS.glob("*/events.jsonl")):
        evs = [json.loads(l) for l in f.read_text(encoding="utf-8").splitlines()]
        head = next(e for e in evs if e["kind"] == "task")
        t = Task(f.parent.name, head["root"], head.get("mode", 3), head.get("seats"), head.get("auto", False), head.get("perm", "edits"))
        for e in evs:
            if e["kind"] == "task" and e.get("mode"):
                t.mode = e["mode"]
            if e["kind"] == "task" and "auto" in e:
                t.auto = bool(e["auto"])
            if e["kind"] == "task" and e.get("perm") in PERMS:
                t.perm = e["perm"]
            if e["kind"] == "task" and e.get("seats"):
                t.set_seats(e["seats"])
        t.turn = max((e.get("turn", 0) for e in evs), default=0)
        ph = summary(t)["phase"]
        if ph not in TERMINAL and ph != "idle":
            ch = pending_card(evs)
            if ch:                                       # 重启前有没定的改动卡：恢复它，门重新交给用户，定完落中断
                t.open_changes = {"tree0": ch["tree0"], "tree_end": ch["tree_end"], "seq": ch["seq"], "gated": False}
                gate_changes(t)
                t.final_phase = "interrupted"
            else:
                t.emit("task", phase="interrupted")
        out[t.id] = t
    return out


def summary(t: Task) -> dict:
    evs = t.events()
    phase = next((e["phase"] for e in reversed(evs) if e["kind"] == "task" and e.get("phase")), "idle")
    steps = [e for e in evs if e["kind"] == "step"]
    turn = max((e["turn"] for e in steps), default=0)
    attempt = max((e["attempt"] for e in steps if e["turn"] == turn), default=0)
    step = max((e["step"] for e in steps if e["turn"] == turn and e["attempt"] == attempt), default=0)
    gate = next((e for e in reversed(evs) if e["kind"] in ("gate", "action")), None)
    title = next((e["title"] for e in reversed(evs) if e["kind"] == "task" and e.get("title")), "")
    integ = next((e for e in reversed(steps) if e["turn"] == turn and e["step"] == 6 and e["status"] == "completed"), None)
    return {"id": t.id, "root": t.root, "title": title, "phase": phase, "turn": turn, "attempt": attempt, "mode": t.mode,
            "auto": t.auto, "perm": t.perm,
            "seats": t.seats, "step": step, "gate": gate["gate"] if gate and gate["kind"] == "gate" else None,
            "result": integ["output"].get("status") if integ else None,
            "preview": next((e["text"] for e in reversed(evs) if e["kind"] == "message"), ""),
            "can_compact": phase == "idle" and any(r["turn"] < turn for r in t.history()[1]),
            "updated": evs[-1]["t"] if evs else 0, "seq": t.seq}


# ---------------------------------------------------------------- 提示词 --
def workflow_text(role: str) -> tuple[str, list[tuple[str, str]]]:
    wf = (WORKFLOWS / WF_FILE[role]).read_text(encoding="utf-8")
    load = re.search(r"^##\s+Load\b(.*?)(?=^##\s|\Z)", wf, re.S | re.M)
    names = list(dict.fromkeys(re.findall(r"([A-Za-z0-9_\-.]+)/SKILL\.md", load.group(1) if load else "")))
    return wf, [(n, (KERNEL / n / "SKILL.md").read_text(encoding="utf-8")) for n in names]


def prompt_for(role: str, start: str, materials: dict[str, str]) -> tuple[str, dict]:
    wf, skills = workflow_text(role)
    parts = [f"你是{NAMES[role]}。下面依次是你的角色文档、你带的方法、这一次手上的东西。"
             f"照角色文档做{start}，交出那一步要交的东西就停；写句子时随手用带的方法。"
             f"最后只交一份按答案格子的 JSON。不要读取 {TASKS} 目录。",
             f"# 角色文档\n\n{wf}"]
    for n, s in skills:
        parts.append(f"# 方法：{n}\n\n{s}")
    parts.append("# 手上\n\n" + "\n\n".join(f"## {k}\n\n{v}" for k, v in materials.items()))
    return "\n\n---\n\n".join(parts), {"workflow": WF_FILE[role], "skills": [n for n, _ in skills], "materials": materials}


# ---------------------------------------------------------------- 叫一次角色 --
def call(t: Task, role: str, step: int, start: str, materials: dict[str, str], schema_name: str,
         *, write: bool = False, label: str = "") -> dict:
    base_role = "executor" if role.startswith("executor") else role
    seat = t.seats[base_role]
    prompt, inputs = prompt_for(base_role, start, materials)
    ev = t.emit("step", role=role, step=step, status="started", label=label or NAMES.get(role, role),
                engine=seat["engine"], schema=schema_name, start=start, inputs=inputs)
    (t.dir / "prompts" / f"{ev['seq']}.txt").write_text(prompt, encoding="utf-8")     # 当时的完整提示词，原样
    t0 = time.time()
    tools = Tools(t, role, step, ev["seq"])
    try:
        if t.cancel.is_set() or t.stopped:
            raise Failed("已停止" if t.stopped else "本轮作废")
        run = run_claude if seat["engine"] == "claude" else run_codex
        out = run(t, seat, prompt, schema_name, write, EXEC_TIMEOUT if write else ROLE_TIMEOUT, tools)
    except Failed as e:
        tools.close()
        t.emit("step", role=role, step=step, status="failed", label=ev["label"], started=ev["seq"],
               secs=round(time.time() - t0, 1), error=str(e), **tools.fields())
        raise
    tools.close()
    t.emit("step", role=role, step=step, status="completed", label=ev["label"], started=ev["seq"],
           secs=round(time.time() - t0, 1), output=out, **tools.fields())
    return out


def spawn(t: Task, cmd: list[str], cwd: str, feed: str, timeout: int) -> subprocess.Popen:
    p = subprocess.Popen(cmd, cwd=cwd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                         stdin=subprocess.PIPE, text=True, bufsize=1, start_new_session=True)
    t.procs.append(p)
    if t.cancel.is_set() or t.stopped:
        try:
            os.killpg(p.pid, 9)
        except ProcessLookupError:
            pass
    def feed_in():
        try:
            p.stdin.write(feed)
            p.stdin.close()
        except BrokenPipeError:
            pass                                          # 进程已经被杀，没人读
    threading.Thread(target=feed_in, daemon=True).start()
    p.timer = threading.Timer(timeout, lambda: p.poll() is None and os.killpg(p.pid, 9))
    p.timer.daemon = True
    p.timer.start()
    return p


def finish(t: Task, p: subprocess.Popen, kill: bool = False) -> None:
    if kill:
        try:
            os.killpg(p.pid, 9)
        except ProcessLookupError:
            pass
    p.wait()
    p.timer.cancel()
    t.procs.remove(p)
    if t.cancel.is_set() or t.stopped:
        raise Failed("已停止" if t.stopped else "本轮作废")


class Tools:
    """一次上场里的工具调用：每次开始、结束各记一条 tool 事件。配对靠模型给的 id，耗时靠本机时钟差。"""
    LISTS = {"Read": "reads", "Grep": "reads", "Glob": "reads", "Bash": "cmds", "command_execution": "cmds",
             "Edit": "changed", "Write": "changed", "MultiEdit": "changed", "file_change": "changed"}

    def __init__(self, t: Task, role: str, step: int, call: int):
        self.t, self.role, self.step, self.call = t, role, step, call
        self.open: dict[str, tuple[int, float, str, str]] = {}
        self.reads, self.cmds, self.changed, self.model = [], [], [], ""

    def start(self, tid: str, name: str, text: str) -> None:
        if tid in self.open:
            return
        ev = self._emit("started", tid, name, text)
        self.open[tid] = (ev["seq"], time.monotonic(), name, text)
        if name in self.LISTS:
            getattr(self, self.LISTS[name]).append(text)

    def end(self, tid: str, ok: bool) -> None:
        if tid not in self.open:
            return
        seq, t0, name, text = self.open.pop(tid)
        self._emit("completed" if ok else "failed", tid, name, text, started=seq, secs=round(time.monotonic() - t0, 3))

    def close(self) -> None:
        for tid, (seq, t0, name, text) in self.open.items():
            self._emit("interrupted", tid, name, text, started=seq, secs=round(time.monotonic() - t0, 3))
        self.open.clear()

    def _emit(self, status: str, tid: str, name: str, text: str, **d) -> dict:
        return self.t.emit("tool", status=status, role=self.role, step=self.step, call=self.call, id=tid, tool=name,
                           text=text[:200], **d)

    def fields(self) -> dict:
        return {"reads": self.reads, "cmds": self.cmds, "changed": self.changed, "model": self.model}


def tool_text(name: str, inp: dict) -> str:
    if name in ("Read", "Edit", "Write", "MultiEdit"):
        return str(inp.get("file_path", ""))
    if name == "Bash":
        return str(inp.get("command", ""))
    if name in ("Grep", "Glob"):
        return " ".join(str(inp[k]) for k in ("pattern", "path") if inp.get(k))
    return json.dumps(inp, ensure_ascii=False)


def run_claude(t: Task, seat: dict, prompt: str, schema_name: str, write: bool, timeout: int, tools: Tools) -> dict:
    _, sch = schema(schema_name)
    cmd = ["claude", "-p", "--output-format", "stream-json", "--verbose", "--tools", EXEC_TOOLS if write else READ_TOOLS]
    if seat["model"]:
        cmd += ["--model", seat["model"]]
    if seat["effort"]:
        cmd += ["--effort", seat["effort"]]
    cmd += NO_MCP + (perm_args(t.perm) if write else []) + DENY + ["--json-schema", json.dumps(sch, ensure_ascii=False)]
    p = spawn(t, cmd, t.root, prompt, timeout)
    structured, tail = None, []
    for line in p.stdout:
        line = line.strip()
        if not line:
            continue
        tail = (tail + [line])[-6:]
        try:
            d = json.loads(line)
        except ValueError:
            continue
        if d.get("is_error") or (d.get("type") == "result" and d.get("subtype") != "success"):
            finish(t, p, kill=True)
            raise Failed(str(d.get("result") or d.get("error") or d)[:300])
        content = (d.get("message") or {}).get("content") or []
        if d.get("type") == "system" and d.get("subtype") == "init":
            tools.model = str(d.get("model") or "")
        elif d.get("type") == "assistant":
            for b in content:
                if b.get("type") == "tool_use":
                    tools.start(str(b.get("id", "")), str(b.get("name", "")), tool_text(b.get("name"), b.get("input") or {}))
        elif d.get("type") == "user" and isinstance(content, list):
            for b in content:
                if b.get("type") == "tool_result":
                    tools.end(str(b.get("tool_use_id", "")), not b.get("is_error"))
        elif d.get("type") == "result" and d.get("structured_output") is not None:
            structured = d["structured_output"]
    finish(t, p)
    if p.returncode != 0:
        raise Failed(f"claude 退出码 {p.returncode}{'（超时被杀）' if p.returncode == -9 else ''}。尾部：{' | '.join(tail)[:300]}")
    if structured is None:
        raise Failed(f"没有按格子交出 JSON。尾部：{' | '.join(tail)[:300]}")
    return structured


def run_codex(t: Task, seat: dict, prompt: str, schema_name: str, write: bool, timeout: int, tools: Tools) -> dict:
    path, _ = schema(schema_name)
    cmd = ["codex", "exec", "--json", "--sandbox", ("danger-full-access" if t.perm == "bypass" else "workspace-write") if write else "read-only",
           "--skip-git-repo-check"] + (["-c", "approval_policy=never"] if write else [])
    if seat["model"]:
        cmd += ["-m", seat["model"]]
    if seat["effort"]:
        cmd += ["-c", f"model_reasoning_effort={seat['effort']}"]
    cmd += ["--output-schema", str(path)] + codex_mcp_off() + ["-"]
    p = spawn(t, cmd, t.root, prompt, timeout)
    out, tail = [], []
    for line in p.stdout:
        line = line.strip()
        if not line.startswith("{"):
            if line:
                tail = (tail + [line])[-4:]
            continue
        try:
            d = json.loads(line)
        except ValueError:
            continue
        it, kind = d.get("item") or {}, d.get("type")
        if kind == "turn.failed":
            finish(t, p, kill=True)
            raise Failed(str((d.get("error") or {}).get("message") or d)[:300])
        if kind == "item.completed" and it.get("type") == "agent_message":
            out.append(it.get("text", ""))
        elif kind == "item.started" and it.get("type") == "file_change":
            continue                                          # 路径只在 completed 里，started 记了也是空的
        elif kind in ("item.started", "item.completed") and it.get("type") in ("command_execution", "file_change",
                                                                                 "mcp_tool_call", "web_search"):
            text = {"command_execution": str(it.get("command", "")),
                    "file_change": " ".join(str(c.get("path", "")) for c in (it.get("changes") or [])),
                    "mcp_tool_call": f"{it.get('server', '')}.{it.get('tool', '')}",
                    "web_search": str(it.get("query", ""))}[it["type"]]
            tools.start(str(it.get("id", "")), it["type"], text)          # 只有 completed 也记上，耗时 0
            if kind == "item.completed":
                tools.end(str(it.get("id", "")), it.get("status") != "failed" and not it.get("exit_code"))
    finish(t, p)
    if p.returncode != 0:
        raise Failed(f"codex 退出码 {p.returncode}{'（超时被杀）' if p.returncode == -9 else ''}。尾部：{' | '.join(tail)[:200]}")
    if not out:
        raise Failed(f"没有任何产出。尾部：{' | '.join(tail)[:200]}")
    try:
        return json.loads(out[-1])
    except ValueError:
        raise Failed(f"最后一条不是 JSON：{out[-1][:200]}")


# ---------------------------------------------------------------- 链路 --
def J(x) -> str:
    return json.dumps(x, ensure_ascii=False, indent=1)


def background(t: Task) -> dict[str, str]:
    summ, rows = t.history()
    out = {}
    if summ:
        out["更早对话的摘要"] = summ
    rows = [r for r in rows if r["turn"] < t.turn]
    if rows:
        out["之前几轮的对话"] = "\n\n".join(f"{'用户' if r['who'] == 'user' else '中书'}：{r['text']}" for r in rows)
    return out


def reading_round(t: Task) -> dict:
    """第 1–3 步：三路并行盲读 → 门下比对 → 中书回话。档位 1 只有中书自己读、自己回。"""
    base = {**background(t), "用户这一轮的原话": t.words}
    if t.auto:
        base["审批模式"] = AUTO_NOTE
    if t.mode == 1:
        cand = call(t, "zhongshu", 1, "第 1、2、3 步（交候选 reading.json）", base, "reading", label="中书读法")
        t.mats = {**base, "自己的读法": J(cand)}
        return zhongshu_reply(t)
    mx = t.menxia()
    with ThreadPoolExecutor(len(mx) + 1) as ex:
        fs = {m: ex.submit(call, t, m, 1, "第 1、2 步（交 reading.json）", base, "reading") for m in mx}
        fz = ex.submit(call, t, "zhongshu", 1, "第 1、2、3 步（交候选 reading.json）", base, "reading", label="中书候选")
        readings = {m: f.result() for m, f in fs.items()}
        cand = fz.result()
    verdicts = {}
    with ThreadPoolExecutor(len(mx)) as ex:
        futs = {}
        for m, own in readings.items():
            pair = [("自己的", own), ("中书候选", cand)]
            random.shuffle(pair)
            mats = {**base, "说法 A": J(pair[0][1]), "说法 B": J(pair[1][1])}
            futs[m] = (ex.submit(call, t, m, 2, "第 3、4 步（交 verdict.json）", mats, "verdict", label=f"{NAMES[m]}比对"),
                       {"A": pair[0][0], "B": pair[1][0]})
        for m, (f, mapping) in futs.items():
            verdicts[m] = {"verdict": f.result(), "AB": mapping}
    mats = {**base, "自己的候选读法": J(cand)}
    for m in readings:
        mats[f"{NAMES[m]}的读法"] = J(readings[m])
        mats[f"{NAMES[m]}的判词（A/B 对应：{J(verdicts[m]['AB'])}）"] = J(verdicts[m]["verdict"])
    t.mats = mats
    return zhongshu_reply(t)


def zhongshu_reply(t: Task) -> dict:
    mats = dict(t.mats)
    if t.answer:
        mats["你上一条回话（含你问的那一个问题）"] = J(t.last_reply)
        mats["用户对你上一问的回答（这一句话只能问这一次，这次要定下来）"] = t.answer
    reply = call(t, "zhongshu", 3, "第 4、5、6 步（交 reply.json）", mats, "reply", label="中书回话")
    t.last_reply = reply
    t.emit("message", who="zhongshu", what="reply", text=reply.get("reply", ""),
           decisions=reply.get("decisions") or [], contract=reply.get("contract"))
    if reply.get("decisions") and t.asked:
        raise Failed("中书对同一句话问了第二次，方法只允许问一次")
    return reply


def check_plan(plan: dict) -> dict[str, dict]:
    """模型交来的计划进调度前核一遍；不合法就失败，不悄悄修。"""
    nodes = plan.get("nodes") or []
    ids = [n.get("id") for n in nodes]
    if not 1 <= len(ids) <= 6:
        raise Failed(f"计划要 1–6 个节点，交来 {len(ids)} 个")
    if len(set(ids)) != len(ids):
        raise Failed(f"节点 id 重复：{ids}")
    bad_ids = [i for i in ids if not (isinstance(i, str) and re.fullmatch(r"[A-Za-z0-9_-]+", i))]
    if bad_ids:
        raise Failed(f"节点 id 只能是字母数字下划线连字符：{bad_ids}")
    for n in nodes:
        bad = [d for d in (n.get("depends") or []) if d not in ids]
        if bad:
            raise Failed(f"节点 {n['id']} 依赖不存在的节点 {bad}")
    if int(plan.get("budget_minutes") or 0) <= 0:
        raise Failed(f"预算要是正数，交来 {plan.get('budget_minutes')!r}")
    return {n["id"]: n for n in nodes}


def wait_gate(t: Task, ev: threading.Event) -> None:
    ev.wait()
    ev.clear()
    if t.stopped:
        raise Failed("已停止")


def execution(t: Task, contract: dict, tree0: str) -> str:
    """第 4–8 步：尚书计划 → 执行体逐节点（串行，每节点前后快照）→ 尚书整合 → 中书交付 → 改动卡 → 御史。返回交付正文。"""
    root, t0 = t.root, time.time()
    t.emit("changes", stage="snapshot", tree0=tree0)
    pkg = {**background(t), "契约": J(contract), "项目根": root,
           "权限边界": "尚书只读；执行体可读可改可跑命令；谁都不碰任务记录目录，不 git commit/stash/checkout/reset"}
    plan = call(t, "shangshu", 4, "第 1 步「出计划」（交 plan.json）", pkg, "plan", label="尚书计划")
    nodes = check_plan(plan)
    order = list(TopologicalSorter({i: set(n.get("depends") or []) for i, n in nodes.items()}).static_order())
    budget = 60 * int(plan["budget_minutes"])
    results: dict[str, dict] = {}
    for i in order:
        n, before = nodes[i], snapshot.snapshot_tree(root, t.id)
        upstream = [results[d] for d in (n.get("depends") or [])]
        if any(r["status"] != "completed" for r in upstream):
            results[i] = {"id": i, "status": "skipped", "summary": "上游节点没完成", "evidence": "", "files": [], "remaining": "", "files_actual": []}
            continue
        if time.time() - t0 > budget:
            results[i] = {"id": i, "status": "skipped", "summary": "到预算，没派", "evidence": "", "files": [], "remaining": "", "files_actual": []}
            continue
        mats = {**pkg, "计划一句话": plan.get("summary", ""), "本节点": J(n),
                "前面节点的结果": J(upstream) if upstream else "（这是第一个节点）"}
        try:
            r = call(t, f"executor:{i}", 5, "第 1 步（交 exec.json）", mats, "exec", write=True, label=f"执行体 {i}")
        except Failed as e:
            if t.stopped:
                raise
            r = {"status": "failed", "summary": str(e), "evidence": "", "files": [], "remaining": ""}
        after = snapshot.snapshot_tree(root, t.id)
        results[i] = {"id": i, **r, "files_actual": snapshot.diff_files(root, t.id, before, after)}
    over = time.time() - t0 > budget
    tree1 = snapshot.snapshot_tree(root, t.id)
    stat = snapshot.diff_files(root, t.id, tree0, tree1)
    mats = {**pkg, "计划": J(plan), "各节点结果（files_actual 是程序按快照算出的实际改动）": J(list(results.values())),
            "工作树改动": J(stat)}
    if over:
        mats["计时"] = f"已用 {int((time.time() - t0) / 60)} 分钟，超过预算 {plan['budget_minutes']} 分钟"
    integ = call(t, "shangshu", 6, "「到预算」那一段（交 integration.json）" if over else "第 2 步「整合」（交 integration.json）",
                 mats, "integration", label="尚书整合")
    mats = {**background(t), "契约": J(contract), "尚书整合": J(integ), "各节点结果": J(list(results.values())), "改动清单": J(stat)}
    reply = call(t, "zhongshu", 7, "「交付时」那两步（交 reply.json）", mats, "reply", label="中书交付")
    t.emit("message", who="zhongshu", what="delivery", text=reply.get("reply", ""))
    tree_end = snapshot.snapshot_tree(root, t.id)
    files = snapshot.diff_files(root, t.id, tree0, tree_end)
    checks = list(integ.get("checks") or [])
    if t.auto:                                           # 自动档：卡先摆出来，御史先审，无偏离就自动采纳
        hold_changes(t, tree0, tree_end, files, checks)
    else:
        offer_changes(t, tree0, tree_end, files, checks)
        wait_gate(t, t.decided)
    t.emit("task", phase="censoring")
    evs = [e for e in t.events() if e.get("status") != "started" and e["turn"] == t.turn and e["attempt"] == t.attempt]
    steps, tools = [e for e in evs if e["kind"] == "step"], [e for e in evs if e["kind"] == "tool"]
    mats = {"用户原话": t.words, "契约": J(contract), "计划": J(plan), "各节点结果": J(list(results.values())),
            "尚书整合": J(integ), "中书交付原文": reply.get("reply", ""), "改动清单": J(files),
            "用户的决定": "自动模式：御史无偏离就自动采纳，有偏离交用户定" if t.auto else (t.decision or "adopt"),
            "各角色的读法、判词与产出（完整）": J([{k: e.get(k) for k in ("role", "step", "label", "status", "output", "error")} for e in steps]),
            "各角色的动作记录（按先后）": J([{k: e.get(k) for k in ("role", "step", "tool", "text", "status", "secs")} for e in tools])}
    censor = call(t, "yushi", 8, "第 1 步（交 censor.json）", mats, "censor", label="御史")
    oc = t.open_changes
    if t.auto and oc and not oc["gated"]:
        bad = [d for d in (censor.get("deviations") or []) if isinstance(d, dict) and d.get("state") == "filled"]
        if bad or t.stopped:
            gate_changes(t)
            wait_gate(t, t.decided)
        else:
            t.decision = "adopt"
            settle_changes(t, "adopt", auto=True)
    return reply.get("reply", "")


def hold_changes(t: Task, tree0: str, tree_end: str, files: list, verified: list, note: str = "") -> dict:
    ch = t.emit("changes", stage="result", tree0=tree0, tree_end=tree_end, files=files, verified=verified, note=note)
    t.decision = None
    t.open_changes = {"tree0": tree0, "tree_end": tree_end, "seq": ch["seq"], "gated": False}   # gated：门已经发给用户了
    return ch


def gate_changes(t: Task) -> None:
    """把手里这张改动卡正式交给用户定：发门、进 waiting_changes。"""
    t.open_changes["gated"] = True
    t.emit("gate", gate="changes", changes=t.open_changes["seq"])
    t.emit("task", phase="waiting_changes")


def offer_changes(t: Task, tree0: str, tree_end: str, files: list, verified: list, note: str = "") -> None:
    hold_changes(t, tree0, tree_end, files, verified, note)
    gate_changes(t)


def settle_changes(t: Task, action: str, auto: bool = False) -> None:
    """采纳或撤回未决的改动卡；线程停了也能做。auto：自动档替用户定的。一张卡只结算一次：先在锁里认领。"""
    with t.settle_lock:
        oc, t.open_changes = t.open_changes, None
    if not oc:
        raise Failed("现在没有等你定的改动")
    flag = {"auto": True} if auto else {}
    if action == "revert":
        n = snapshot.revert_tree(t.root, t.id, oc["tree_end"], oc["tree0"])
        t.emit("action", action="revert", text=f"恢复了 {n} 个文件", **flag)
    else:
        t.emit("action", action="adopt", **flag)
    try:
        snapshot.drop_refs(t.root, t.id)
    except Exception as e:
        t.emit("error", where="drop_refs", text=str(e))


def acquire(t: Task, lock: threading.Lock) -> None:
    while not lock.acquire(timeout=0.5):
        if t.stopped:
            raise Failed("已停止")


def one_turn(t: Task) -> None:
    """一轮：读法（可能作废重开几次）→ 问一次 → 契约 → 执行 → 交付。"""
    for ev in (t.answered, t.approved, t.decided):
        ev.clear()
    if t.open_changes:
        t.emit("task", phase="waiting_changes")
        wait_gate(t, t.decided)
        t.decided.clear()
    t.turn += 1
    t.attempt, t.asked, t.answer, t.last_reply = 0, False, None, None
    t.emit("message", who="user", what="words", text=t.words)
    while True:
        t.cancel.clear()
        t.attempt += 1
        t.emit("task", phase="reading")
        try:
            reply = reading_round(t)
        except Failed:
            if t.cancel.is_set() and not t.stopped:
                t.emit("message", who="user", what="words", text=t.words)      # 并进了新话，作为新一次读法的原话
                continue
            raise
        if reply.get("decisions"):
            t.asked = True
            t.emit("gate", gate="question", decisions=reply["decisions"])
            if t.auto:                                   # 自动档：不等人，按中书自己的推荐答，假设记进契约
                t.answer = AUTO_ANSWER
                t.emit("action", action="answer", text=AUTO_ANSWER, auto=True)
            else:
                t.emit("task", phase="waiting_answer")
                wait_gate(t, t.answered)
                if t.cancel.is_set():
                    continue
            t.emit("task", phase="reading")
            try:
                reply = zhongshu_reply(t)
            except Failed:
                if t.cancel.is_set() and not t.stopped:
                    t.emit("message", who="user", what="words", text=t.words)
                    continue
                raise
        if t.cancel.is_set():
            continue
        contract = reply.get("contract") if t.mode == 3 else None
        if not contract:
            return
        t.emit("gate", gate="contract", contract=contract)
        if t.auto:
            t.emit("action", action="approve", auto=True)
            t.emit("task", phase="executing")            # 立刻离开 reading：这之后的插话归下一轮，不再作废读法
            if t.cancel.is_set():
                continue
            break
        t.emit("task", phase="waiting_contract")
        wait_gate(t, t.approved)
        if t.cancel.is_set():
            continue
        break
    with _LOCK:
        lock = REPO_LOCKS.setdefault(os.path.realpath(t.root), threading.Lock())
    if not lock.acquire(blocking=False):
        t.emit("task", phase="queued")
        acquire(t, lock)
    tree0 = snapshot.snapshot_tree(t.root, t.id)
    try:
        t.emit("task", phase="executing")
        execution(t, contract, tree0)
    except Failed as e:
        tree_now = snapshot.snapshot_tree(t.root, t.id)
        files = snapshot.diff_files(t.root, t.id, tree0, tree_now)
        if files and t.open_changes is None:
            offer_changes(t, tree0, tree_now, files, [], note=f"执行没走完（{e}），这是已经落下的改动，先定采纳还是撤回")
        raise
    finally:
        lock.release()


def run_task(t: Task) -> None:
    """任务线程：等你说话 → 跑一轮 → 回到等你说话。停止就收工。"""
    try:
        while True:
            if not t.pending:
                t.spoke.wait()
                t.spoke.clear()
            if t.stopped:
                t.emit("task", phase="stopped")
                return
            t.words, t.pending = "\n".join(t.pending), []
            one_turn(t)
            t.emit("task", phase="idle")
    except Failed as e:
        if not t.stopped:
            t.emit("error", where="chain", text=str(e))
        end(t, "stopped" if t.stopped else "failed")
    except Exception as e:
        t.emit("error", where="program", text=f"{type(e).__name__}: {e}")
        end(t, "failed")


def end(t: Task, phase: str) -> None:
    """线程收场：手里还捏着没交出去的卡先交给用户；有没定的卡就把终态留到定完那一刻（与 decide 同一把锁，不会两边都落或都不落）。"""
    with t.settle_lock:
        oc = t.open_changes
        if oc and not oc["gated"]:
            gate_changes(t)
        if oc:
            t.final_phase = phase
            return
    t.emit("task", phase=phase)


def start(t: Task) -> None:
    t.stopped, t.final_phase = False, ""
    for ev in (t.answered, t.approved, t.decided, t.spoke, t.cancel):
        ev.clear()
    t.thread = threading.Thread(target=run_task, args=(t,), daemon=True, name=f"task-{t.id}")
    t.thread.start()


def interject(t: Task, words: str) -> None:
    """读法阶段：作废本次读法，新话并进原话重开。等答：当答案。等批：重开读法。执行中：攒到下一轮。等你说／已停／已完／中断：开下一轮。"""
    phase = summary(t)["phase"]
    t.emit("action", action="interject", text=words)
    if phase == "reading":
        t.words = t.words.rstrip() + "\n" + words
        t.asked, t.answer = False, None
        t.cancel.set()
        t.kill()
    elif phase == "waiting_answer":
        answer(t, words)
    elif phase == "waiting_contract":
        t.words = t.words.rstrip() + "\n" + words
        t.asked, t.answer = False, None
        t.cancel.set()
        t.approved.set()
    elif t.compacting or t.open_changes:
        t.pending.append(words)
    elif phase == "idle" and t.thread and t.thread.is_alive():
        t.pending.append(words)
        t.spoke.set()
    elif phase in ("idle", "stopped", "failed", "interrupted"):
        t.pending.append(words)
        start(t)
    else:                                               # executing / queued / waiting_changes / censoring
        t.pending.append(words)


def stop(t: Task) -> None:
    t.stopped = True
    t.cancel.set()
    t.kill()
    for ev in (t.answered, t.approved, t.decided, t.spoke):
        ev.set()
    t.emit("action", action="stop")


def compact(t: Task) -> str:
    """只在等你说话时做：把最近一轮之前的对话压成摘要；最近一轮原样留在摘要之后。"""
    if summary(t)["phase"] != "idle" or t.compacting:
        raise Failed("只有一轮做完、在等你说话的时候才能压缩")
    summ, rows = t.history()
    last = max((r["turn"] for r in rows), default=0)
    older = [r for r in rows if r["turn"] < last]
    if not older:
        raise Failed("没有更早的对话可压")
    t.compacting = True
    try:
        t.emit("task", phase="compacting")
        text = (summ + "\n\n" if summ else "") + "\n\n".join(f"{'用户' if r['who'] == 'user' else '中书'}：{r['text']}" for r in older)
        seat = t.seats["zhongshu"]
        prompt = ("把下面这段用户与中书的对话压缩成不超过 800 字的摘要。保留：用户的目标、已定下的决定、未决的问题。"
                  "用第三人称陈述，按格子交 JSON。\n\n" + text)
        tools = Tools(t, "zhongshu", 0, 0)
        run = run_claude if seat["engine"] == "claude" else run_codex
        try:
            out = run(t, seat, prompt, "summary", False, ROLE_TIMEOUT, tools)
        except Failed:
            tools.close()
            t.emit("task", phase="idle")
            raise
        tools.close()
        t.emit("message", who="zhongshu", what="summary", text=out["summary"])
        keep_turn, keep_attempt = t.turn, t.attempt
        t.turn, t.attempt = last, max((e["attempt"] for e in t.events() if e.get("turn") == last), default=0)
        for r in rows:
            if r["turn"] == last:
                if r["what"] == "answer":
                    t.emit("action", action="answer", text=r["text"])
                else:
                    t.emit("message", who=r["who"], what=r["what"], text=r["text"])
        t.turn, t.attempt = keep_turn, keep_attempt
        t.emit("task", phase="idle")
        return out["summary"]
    finally:
        t.compacting = False
        if t.pending:
            t.spoke.set()


def rename(t: Task, title: str) -> None:
    t.emit("task", title=title.strip()[:60], phase=summary(t)["phase"])


def answer(t: Task, text: str) -> None:
    if summary(t)["phase"] != "waiting_answer":
        raise Failed("现在不在等你答")
    t.answer = text
    t.emit("action", action="answer", text=text)
    t.answered.set()


def approve(t: Task) -> None:
    if summary(t)["phase"] != "waiting_contract":
        raise Failed("现在不在等你批")
    t.emit("action", action="approve")
    t.approved.set()


def decide(t: Task, action: str) -> None:
    oc = t.open_changes
    if not oc or not oc["gated"]:                        # 自动档御史还在审的卡不归用户定
        raise Failed("现在没有等你定的改动")
    t.decision = action
    settle_changes(t, action)
    with t.settle_lock:
        fp, t.final_phase = t.final_phase, ""
    if fp:
        t.emit("task", phase=fp)
    t.decided.set()
