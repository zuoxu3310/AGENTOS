"""用假 claude/codex 跑整条链。python3 tests/test_board.py"""
import os, pathlib, shutil, subprocess, sys, tempfile, time
HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))
os.environ["PATH"] = f"{HERE / 'fake'}{os.pathsep}{os.environ['PATH']}"
import run, snapshot
WORK = pathlib.Path(tempfile.mkdtemp(prefix="board2-test-"))
run.TASKS, snapshot.SHADOW_DIR = WORK / "tasks", WORK / "shadow"
run.TASKS.mkdir()
os.environ["FAKE_LOG"] = str(WORK / "fake.log")


def repo() -> str:
    d = tempfile.mkdtemp(prefix="repo-", dir=WORK)
    subprocess.run(["git", "init", "-q"], cwd=d, check=True)
    (pathlib.Path(d) / "README.md").write_text("# demo\n")
    subprocess.run(["git", "add", "-A"], cwd=d, check=True)
    subprocess.run(["git", "-c", "user.email=a@b", "-c", "user.name=t", "commit", "-qm", "init"], cwd=d, check=True)
    return d


def wait(t, phase, secs=60):
    for _ in range(secs * 10):
        if run.summary(t)["phase"] == phase:
            return
        time.sleep(0.1)
    raise AssertionError(f"等 {phase} 超时，停在 {run.summary(t)['phase']}：{[e for e in t.events() if e['kind']=='error']}")


def start(words, root, mode=3, seats=None, auto=False, perm="edits"):
    t = run.new_task(root, words, mode, seats, auto, perm)
    run.start(t)
    return t


def lines(root):
    return (pathlib.Path(root) / "README.md").read_text().splitlines()


def steps(t, **kw):
    return [e for e in t.events() if e["kind"] == "step" and all(e.get(k) == v for k, v in kw.items())]


def tools(t, **kw):
    return [e for e in t.events() if e["kind"] == "tool" and all(e.get(k) == v for k, v in kw.items())]


def tools_closed(t):
    """每条 started 的工具事件都有同一 call、同一 id 的收尾事件（completed/failed/interrupted）。"""
    ends = {(e["call"], e["id"]) for e in tools(t) if e["status"] != "started"}
    return all((e["call"], e["id"]) in ends for e in tools(t, status="started"))


def test_adopt_then_second_turn_revert():
    r = repo()
    t = start("把 README 末尾加一行 hello", r)
    wait(t, "waiting_contract"); run.approve(t)
    wait(t, "waiting_changes"); run.decide(t, "adopt"); wait(t, "idle")
    done = steps(t, status="completed")
    assert sorted({e["step"] for e in done}) == [1, 2, 3, 4, 5, 6, 7, 8]
    assert [e["role"] for e in done if e["step"] == 5] == ["executor:n1", "executor:n2"], "执行体串行、按依赖"
    assert lines(r)[-1] == "hello" and len(lines(r)) == 3
    ch = next(e for e in t.events() if e["kind"] == "changes" and e.get("stage") == "result")
    assert ch["files"][0]["path"] == "README.md" and ch["verified"]
    n1 = next(e for e in done if e["role"] == "executor:n1")
    assert "README.md" in n1["changed"] and "trace" not in n1
    assert (t.dir / "prompts" / f"{done[0]['started']}.txt").exists(), "当时的提示词原样存了"
    tl = [(e["tool"], e["status"]) for e in tools(t, role="executor:n1") if e["status"] != "started"]
    assert tl == [("Read", "completed"), ("Edit", "completed"), ("Bash", "failed")], tl
    bash = tools(t, role="executor:n1", tool="Bash", status="failed")[0]
    assert bash["secs"] >= 0.2 and bash["call"] == n1["started"] and bash["text"] == "cat README.md"
    assert tools(t, id=bash["id"], status="started", call=n1["started"])[0]["seq"] == bash["started"]
    cx = [(e["tool"], e["status"]) for e in tools(t, role="menxia_2", step=2) if e["status"] != "started"]
    assert cx == [("command_execution", "completed"), ("command_execution", "failed")], cx
    assert tools_closed(t) and not tools(t, status="interrupted")
    yushi = steps(t, role="yushi", status="started")[-1]["inputs"]["materials"]
    assert "cat README.md" in yushi["各角色的动作记录（按先后）"] and "sed -n 1,5p" in yushi["各角色的动作记录（按先后）"]
    assert run.summary(t)["result"] == "done"
    # 第二轮：上一轮的采纳不该自动沿用
    run.interject(t, "再加一行"); wait(t, "reading"); wait(t, "waiting_contract"); run.approve(t)
    wait(t, "waiting_changes"); assert len(lines(r)) == 5
    run.decide(t, "revert"); wait(t, "idle")
    assert len(lines(r)) == 3 and t.turn == 2
    summ, rows = t.history()
    assert [(r["who"], r["what"]) for r in rows] == [("user", "words"), ("zhongshu", "reply"), ("zhongshu", "delivery"),
                                                     ("user", "words"), ("zhongshu", "reply"), ("zhongshu", "delivery")], rows
    print("adopt / second turn revert ok")


def test_question_then_contract():
    r = repo()
    t = start("问我一下再做", r)
    wait(t, "waiting_answer")
    q = [e for e in t.events() if e["kind"] == "gate" and e["gate"] == "question"][-1]["decisions"]
    assert q[0]["opts"] == ["头", "尾"]
    run.answer(t, "尾")
    wait(t, "waiting_contract")
    st = steps(t, role="zhongshu", step=3, status="started")
    mats = "".join(st[-1]["inputs"]["materials"])
    assert len(st) == 2 and "用户对你上一问的回答" in mats and "门下甲的读法" in mats and "你上一条回话" in mats
    run.approve(t); wait(t, "waiting_changes"); run.decide(t, "adopt"); wait(t, "idle")
    print("question ok")


def test_interject_attempts_and_stop_everywhere():
    r = repo()
    t = start("第一句", r)
    time.sleep(0.3); run.interject(t, "补一句")
    wait(t, "waiting_contract")
    assert t.words == "第一句\n补一句" and t.turn == 1 and t.attempt == 2
    run.interject(t, "改主意")
    for _ in range(300):
        if t.attempt == 3:
            break
        time.sleep(0.1)
    wait(t, "waiting_contract")
    assert t.attempt == 3 and t.turn == 1
    run.approve(t); wait(t, "waiting_changes")
    run.interject(t, "执行时插话")
    assert t.pending == ["执行时插话"]
    run.stop(t); time.sleep(0.5)                          # 等改动决定时停止：不算采纳，卡还在、阶段还是等改动决定
    assert run.summary(t)["phase"] == "waiting_changes" and t.stopped and t.open_changes
    assert not any(e.get("action") in ("adopt", "revert") for e in t.events())
    run.interject(t, "再来"); assert t.pending == ["执行时插话", "再来"], "卡没定，不开新轮"
    run.decide(t, "adopt"); wait(t, "stopped")             # 线程停了也能定，定完落 stopped
    # 定完再说话＝重新起线程开下一轮
    run.interject(t, "再来"); wait(t, "reading"); wait(t, "waiting_contract")
    assert t.turn == 2 and t.words == "执行时插话\n再来\n再来"
    run.stop(t); wait(t, "stopped")
    # idle 时停止也落 stopped
    t2 = start("只聊", r, 1); wait(t2, "idle"); run.stop(t2); wait(t2, "stopped")
    print("interject / attempts / stop ok")


def test_second_question_fails_loudly():
    r = repo()
    t = start("问我一下，再问一次也行", r)
    wait(t, "waiting_answer"); run.answer(t, "尾"); wait(t, "failed")
    assert any("第二次" in e["text"] for e in t.events() if e["kind"] == "error")
    print("second question ok")


def test_modes_and_compact():
    r = repo()
    t = start("只跟中书聊", r, 1)
    wait(t, "idle")
    got = {(e["role"], e["step"]) for e in steps(t)}
    assert got == {("zhongshu", 1), ("zhongshu", 3)}, f"档位 1 中书先读再回，实际 {got}"
    run.interject(t, "再说一句"); wait(t, "reading"); wait(t, "idle")
    assert t.turn == 2
    s = run.compact(t)
    summ, rows = t.history()
    assert summ == s and [(r["who"], r["what"], r["turn"]) for r in rows] == [("user", "words", 2), ("zhongshu", "reply", 2)], rows
    run.interject(t, "第三句"); wait(t, "reading"); wait(t, "idle")
    mats = steps(t, step=3, status="started")[-1]["inputs"]["materials"]
    assert "更早对话的摘要" in mats and "再说一句" in mats["之前几轮的对话"], mats.keys()
    run.stop(t); wait(t, "stopped")
    t2 = start("门下看看，不执行", r, 2)
    wait(t2, "idle")
    assert {e["role"] for e in steps(t2)} == {"zhongshu", "menxia_1", "menxia_2"}
    assert not any(e["kind"] == "gate" and e["gate"] == "contract" for e in t2.events())
    print("modes / compact ok")


def test_stop_during_execution_leaves_changes_card():
    r = repo()
    t = start("执行到一半停", r)
    wait(t, "waiting_contract"); run.approve(t)
    for _ in range(300):                                 # 等第一个执行体真的落了改动
        if len(lines(r)) >= 2:
            break
        time.sleep(0.05)
    run.stop(t); wait(t, "waiting_changes")
    card = [e for e in t.events() if e["kind"] == "changes" and e.get("stage") == "result"][-1]
    assert card["files"] and "没走完" in card["note"], card
    assert tools_closed(t) and tools(t, status="interrupted"), "杀在工具调用中途：那条工具记成 interrupted"
    assert run.summary(t)["result"] is None
    run.interject(t, "先别动"); assert t.pending == ["先别动"] and t.open_changes, "有未决改动卡时不开新轮"
    run.decide(t, "revert")
    assert len(lines(r)) == 1 and t.open_changes is None
    run.interject(t, "现在再来"); wait(t, "reading"); wait(t, "waiting_contract")
    assert t.words == "先别动\n现在再来"
    run.stop(t); wait(t, "stopped")
    print("stop during execution ok")


def test_history_ignores_stale_attempts_and_compact_with_question():
    r = repo()
    t = start("问我一下再做", r, 1)
    wait(t, "waiting_answer"); run.answer(t, "尾"); wait(t, "idle")
    run.interject(t, "第二轮开头"); time.sleep(0.3); run.interject(t, "补充")
    wait(t, "idle")
    summ, rows = t.history()
    assert [(r["who"], r["what"], r["turn"]) for r in rows] == [("user", "words", 1), ("zhongshu", "reply", 1), ("user", "answer", 1),
                                                                 ("zhongshu", "reply", 1), ("user", "words", 2), ("zhongshu", "reply", 2)], rows
    assert rows[4]["text"] == "第二轮开头\n补充"
    run.compact(t)
    summ, rows = t.history()
    assert [(r["who"], r["turn"]) for r in rows] == [("user", 2), ("zhongshu", 2)] and summ
    run.stop(t); wait(t, "stopped")
    print("stale attempts / compact with question ok")


def test_three_menxia():
    r = repo()
    t = start("三个门下", r, 3, {"menxia_3": {"engine": "claude", "model": "", "effort": ""}})
    wait(t, "waiting_contract")
    assert {e["role"] for e in steps(t, step=2)} == {"menxia_1", "menxia_2", "menxia_3"}
    run.stop(t); wait(t, "stopped")
    print("three menxia ok")


def test_bad_plan_fails_loudly():
    r = repo()
    orig = run.check_plan
    run.check_plan = lambda plan: orig({**plan, "nodes": plan["nodes"] + [{"id": "n1"}]})
    try:
        t = start("坏计划", r)
        wait(t, "waiting_contract"); run.approve(t); wait(t, "failed")
        assert any("重复" in e["text"] for e in t.events() if e["kind"] == "error")
        print("bad plan ok")
    finally:
        run.check_plan = orig


def test_nonzero_exit_and_compact_failure():
    r = repo()
    t = start("退出码坏也得算失败", r, 1); wait(t, "failed")
    st = steps(t, status="failed")[-1]
    assert "退出码 1" in st["error"] and tools_closed(t) and not steps(t, status="completed"), st
    t2 = start("压缩要坏", r, 1); wait(t2, "idle")
    assert run.summary(t2)["can_compact"] is False
    run.interject(t2, "第二轮"); wait(t2, "reading"); wait(t2, "idle")
    assert run.summary(t2)["can_compact"] is True
    try:
        run.compact(t2); raise AssertionError("压缩该失败")
    except run.Failed as e:
        assert "退出码 1" in str(e)
    assert run.summary(t2)["phase"] == "idle" and tools_closed(t2) and not t2.compacting
    run.interject(t2, "压缩坏了还能接着说"); wait(t2, "reading"); wait(t2, "idle"); assert t2.turn == 3
    run.stop(t2); wait(t2, "stopped")
    print("nonzero exit / compact failure ok")


def test_reload():
    r = repo()
    t = start("完成后重启", r, 1); wait(t, "idle")
    loaded = run.load_tasks()[t.id]
    assert run.summary(loaded)["phase"] == "idle" and loaded.turn == 1
    run.interject(loaded, "重启后接着说"); wait(loaded, "reading"); wait(loaded, "idle")
    assert loaded.turn == 2
    run.stop(loaded); wait(loaded, "stopped")
    print("reload ok")


def test_auto_mode_and_perm():
    """自动档：问题自答、合同自批、御史无偏离自动采纳；有偏离才停下等你。执行权限档改的是执行体的命令行。"""
    r = repo()
    t = start("问我一下再做", r, 3, auto=True); wait(t, "idle")
    evs = t.events()
    assert not any(e["kind"] == "task" and str(e.get("phase", "")).startswith("waiting_") for e in evs), "自动档不该有等人的阶段"
    assert [e["gate"] for e in evs if e["kind"] == "gate"] == ["question", "contract"]
    assert [(e["action"], e.get("auto")) for e in evs if e["kind"] == "action"] == [("answer", True), ("approve", True), ("adopt", True)]
    assert lines(r)[-1] == "hello" and run.summary(t)["result"] == "done" and run.summary(t)["auto"] is True
    zs = steps(t, role="zhongshu", step=1, status="started")[0]
    assert "审批模式" in (t.dir / "prompts" / f"{zs['seq']}.txt").read_text(), "中书读法要知道现在是自动档"
    ys = steps(t, role="yushi", status="started")[0]
    assert "自动模式" in (t.dir / "prompts" / f"{ys['seq']}.txt").read_text()
    t2 = start("御史要挑刺", r, 3, auto=True); wait(t2, "waiting_changes")
    assert [e["gate"] for e in t2.events() if e["kind"] == "gate"] == ["contract", "changes"]
    assert steps(t2, role="yushi", status="completed"), "御史先审完才停下"
    run.decide(t2, "revert"); wait(t2, "idle")
    assert lines(r)[-1] == "hello" and run.summary(t2)["result"] == "done"
    log = (WORK / "fake.log").read_text()
    assert "--permission-mode acceptEdits" in log and "bypassPermissions" not in log
    t3 = start("全放试试", r, 3, auto=True, perm="bypass"); wait(t3, "idle")
    log = (WORK / "fake.log").read_text()
    assert "--permission-mode bypassPermissions" in log
    assert [e["perm"] for e in t3.events() if e["kind"] == "task" and e.get("perm")][0] == "bypass"
    fresh = run.load_tasks()[t3.id]
    assert fresh.auto is True and fresh.perm == "bypass"
    t4 = start("御史要坏", r, 3, auto=True); wait(t4, "waiting_changes")     # 自动档御史挂了：卡不能捏在手里，得交给用户定
    assert [e["gate"] for e in t4.events() if e["kind"] == "gate"] == ["contract", "changes"]
    run.decide(t4, "adopt"); wait(t4, "failed")
    assert run.summary(t4)["gate"] is None and t4.open_changes is None
    t4b = start("再跑一遍", r, 3, auto=True); wait(t4b, "idle")             # 御史还在审的卡不归用户定
    t4b.open_changes = {"tree0": "x", "tree_end": "y", "seq": 1, "gated": False}
    try:
        run.decide(t4b, "adopt"); raise AssertionError("没门的卡不该能定")
    except run.Failed:
        pass
    t4b.open_changes = None
    print("auto mode / perm ok")


def test_reload_restores_pending_card():
    """重启时有没定的改动卡：恢复它、门重新交给用户，定完落中断，撤回真的能恢复文件。"""
    r = repo()
    t = start("把 README 末尾加一行 hello", r); wait(t, "waiting_contract"); run.approve(t); wait(t, "waiting_changes")
    fresh = run.load_tasks()[t.id]
    assert fresh.open_changes and fresh.open_changes["seq"] == t.open_changes["seq"] and fresh.open_changes["gated"]
    assert run.summary(fresh)["phase"] == "waiting_changes" and run.summary(fresh)["gate"] == "changes"
    run.decide(fresh, "revert"); wait(fresh, "interrupted")
    assert lines(r) == ["# demo"], lines(r)
    print("reload restores pending card ok")


if __name__ == "__main__":
    for f in (test_adopt_then_second_turn_revert, test_question_then_contract, test_interject_attempts_and_stop_everywhere,
              test_second_question_fails_loudly, test_modes_and_compact, test_stop_during_execution_leaves_changes_card,
              test_history_ignores_stale_attempts_and_compact_with_question, test_three_menxia, test_bad_plan_fails_loudly,
              test_nonzero_exit_and_compact_failure, test_reload, test_auto_mode_and_perm, test_reload_restores_pending_card):
        f()
    shutil.rmtree(WORK, ignore_errors=True)
    print("全部通过")
