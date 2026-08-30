"""git 快照、改动清单、撤回。搬自 board/daemon.py 2782–2879，去掉线程局部状态：任务号显式传入。"""
from __future__ import annotations
import os, shutil, subprocess, sys, tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
SHADOW_DIR = HERE / "shadow"                      # 非 git 目录用影子裸库
SHADOW_IGNORE = ".git\nnode_modules\n.venv\n__pycache__\ndist\nbuild\n.DS_Store\n*.pyc\n"
IGNORE_GLOBS = ("**/__pycache__/**", "**/*.pyc", "**/.DS_Store", "**/node_modules/**",
                "**/.venv/**", "**/dist/**", "**/build/**")
EXCLUDE_DIRS = (HERE / "tasks", SHADOW_DIR)       # 任务记录和影子库不进快照


def git_base(root: str, task_id: str, create: bool = True) -> list[str] | None:
    """root 本身是 git 仓库根 → 用它自己的 .git；否则用影子裸库（create=False 时没有就给 None）。"""
    r = subprocess.run(["git", "-C", root, "rev-parse", "--show-toplevel"],
                       capture_output=True, text=True, timeout=30)
    if r.returncode == 0 and os.path.realpath(r.stdout.strip()) == os.path.realpath(root):
        return ["git", "-C", root]
    gd = SHADOW_DIR / f"{task_id}.git"
    if not (gd / "HEAD").exists():
        if not create:
            return None
        gd.mkdir(parents=True, exist_ok=True)
        subprocess.run(["git", "init", "-q", "--bare", str(gd)], check=True,
                       capture_output=True, text=True, timeout=30)
        (gd / "info").mkdir(exist_ok=True)
        (gd / "info" / "exclude").write_text(SHADOW_IGNORE, encoding="utf-8")
    return ["git", f"--git-dir={gd}", f"--work-tree={root}", "-C", root]


def _git(base: list[str], *args: str, env: dict | None = None, feed: str | None = None) -> str:
    r = subprocess.run([*base, *args], capture_output=True, text=True, timeout=600,
                       env=env, input=feed)
    if r.returncode != 0:
        raise RuntimeError(f"git {args[0]} 失败：{(r.stderr or r.stdout).strip()[:300]}")
    return r.stdout


def _excludes(root: str) -> list[str]:
    out = [f":(exclude,glob){g}" for g in IGNORE_GLOBS]
    for d in EXCLUDE_DIRS:
        try:
            out.append(f":(exclude){Path(d).relative_to(root)}")
        except ValueError:
            pass                                  # 不在这个 root 下
    return out


def snapshot_tree(root: str, task_id: str) -> str:
    """拍当前工作树：返回树 sha，并用 refs/agentos/<task>/<sha> 钉住防 gc。"""
    base = git_base(root, task_id)
    d = tempfile.mkdtemp(prefix="aos-index-")
    env = {**os.environ, "GIT_INDEX_FILE": os.path.join(d, "index")}
    try:
        _git(base, "add", "-A", "--", ".", *_excludes(root), env=env)
        sha = _git(base, "write-tree", env=env).strip()
    finally:
        shutil.rmtree(d, ignore_errors=True)
    _git(base, "update-ref", f"refs/agentos/{task_id}/{sha}", sha)
    return sha


def diff_files(root: str, task_id: str, a: str, b: str) -> list[dict]:
    """两棵树之间的文件清单：{path, status A|M|D, add, del, binary}，路径相对 root。"""
    if a == b:
        return []
    base = git_base(root, task_id)
    st: dict[str, str] = {}
    it = iter(_git(base, "diff-tree", "-r", "-z", "--name-status", a, b).split("\0"))
    for s in it:
        if s:
            st[next(it, "")] = s[:1]
    out = []
    for row in _git(base, "diff-tree", "-r", "-z", "--numstat", a, b).split("\0"):
        if not row:
            continue
        add, dele, p = row.split("\t", 2)
        out.append({"path": p, "status": st.get(p, "M"),
                    "add": int(add) if add.isdigit() else 0,
                    "del": int(dele) if dele.isdigit() else 0,
                    "binary": add == "-"})
    return out


def file_patch(root: str, task_id: str, a: str, b: str, path: str) -> str:
    return _git(git_base(root, task_id), "diff-tree", "-r", "-p", a, b, "--", path)


def revert_tree(root: str, task_id: str, tree_end: str, tree0: str) -> int:
    """把工作树从 tree_end 恢复到 tree0：反向补丁 + git apply。用户之后又改过、补丁打不上就抛错，工作树一字不动。"""
    base = git_base(root, task_id)
    patch = _git(base, "diff-tree", "-r", "-p", "--binary", tree_end, tree0)
    if not patch.strip():
        return 0
    _git(base, "apply", "--whitespace=nowarn", feed=patch)
    return len(diff_files(root, task_id, tree_end, tree0))


def drop_refs(root: str, task_id: str) -> None:
    """采纳或撤回之后松开防 gc 的 ref。"""
    base = git_base(root, task_id, create=False)
    if base is None:
        return
    for line in _git(base, "for-each-ref", "--format=%(refname)", f"refs/agentos/{task_id}/").splitlines():
        if line.strip():
            _git(base, "update-ref", "-d", line.strip())
