# 一条任务在 AgentOS 里的真实一生

标本：`threads-and-multiline-state`——2026-08-12 用户亲驾会话里真实跑完的任务。
下文每一步给出三样东西：触发它的具体文件、当时真实产生的字节（账本原行/
提示词原文/命令）、这一步的真实弱点。所有主张都能用文末命令亲手核验。

## 第 0 步：你打开会话——身份注入

机制：`.claude/settings.json` 第 2 行 `"agent": "agentos-entry"`。Claude Code 据此把
`.claude/agents/agentos-entry.md` 的正文作为这个会话的系统提示词——你对话的
"人"从出生就是中书省，不需要任何口令。同时 SessionStart 钩子
（`.claude/hooks/aos_session_start.py`）读 `agent-os/state/active-work/claude-<会话ID>.json`，
有未完长任务就把它的目标和下一步注回注意力。

弱点：身份挂载是结构性的（可靠），但人格本身是提示词——遵守是概率事件，
上下文越长概率越低。

## 第 1 步：你说话——每条消息的机械注入

UserPromptSubmit 钩子（`aos_turn_gate.py` + `aos_prompt_baseline.py`）注入注意力
基线文本；纯机械，不判断你的意图。中书此刻做第一个判断：小任务直接答（无账
无团队），非小任务立案走链。

弱点：小/非小判断纯靠模型，判错无机械检测。2026-08-12 真实发生过一次漏走链，
靠用户人眼抓住；修复是把路由写进规则卡第 23 条 + settings 默认身份，机械兜底
（Stop 终态提醒）排在 v1.1。

## 第 2 步：立案——账本诞生

真实命令（当晚实际执行）：

```text
python3 agent-os/tools/aos_task_record.py create --task threads-and-multiline-state \
  --goal "Answer through the chain: ..." --done-when "user receives...;;every load-bearing..."
```

账本文件 `agent-os/state/tasks/threads-and-multiline-state.jsonl`，真实第一行：

```json
{"kind": "header", "task_id": "threads-and-multiline-state", "goal": "Answer through the chain: Claude Code equivalent of Codex thread for the chain plus terminal visibility, and how active_work handles multiple concurrent work lines in one installed project", "done_when": ["user receives one final reply answering both questions with concrete recommendations", "every load-bearing factual claim in the reply is verified against repository files or live runtime facts with evidence references"], "ts": "2026-08-12T02:49:11.954937+00:00"}
```

第二行是你的原话逐字入账（`role: zhongshu, kind: user_message`）。写入机制是
`aos_task_record.py` 的 `emit()`：O_APPEND 打开、单次 `os.write`，没有读-改-写，
所以并发永不丢（实测 20 进程 20/20 存活）、永不拒写（O_CREAT：对不存在的任务
也能直接落 blocked）。

弱点：落账动作写在角色契约里（提示层）——角色忘了调 CLI 就没有账。自动落账
的观察钩子未建，是 v1.1 第一项。

## 第 3 步：生门下——人格注入与提示词门

中书调 Agent 工具（`subagent_type: "agentos-menxia"`），Claude Code 把
`.claude/agents/agentos-menxia.md` 全文作为新子会话的系统提示词：反谄媚、竞争
解释、两阶段审查是门下的出生设定，不是运行时"调用"的功能。当晚真实派发
提示词（节选）：

```text
<materials>
Project root: /path/to/project — an AgentOS-governed repository ...
Task id: agentos-status-ascii-map
Goal: deliver a verified ASCII-visualized map of the current AgentOS state ...
done_when, in order: 1. ... 2. ...
Raw user increment, verbatim (Chinese): 「查看现在的agentos的现状……」
Prior approved state: none — this is the first chain run for this task.
</materials>
<assignment> ... </assignment>
<output> ... </output>
```

要点：用户原话逐字引用、不带中书的读法（防审查污染）；至少三个 XML 段——这
是 PreToolUse 钩子 `aos_prompt_craft_guard.py` 的机械检查，不够格当场拒，真实
拒绝文案是 `subagent prompt has 0 XML section tag(s) (need >= 3 distinct)`。

弱点一：授权传导天花板——父会话的 Agent 授权清单是子代理的上限。2026-08-12
实测：入口授权漏了 executor，尚书整层被饿死（三段降级实验确认后修复）。机制
本身仍在，今后任何授权收窄都可能再饿死下层。弱点二：一次真实运行中门下报告
Grep/Glob 不在其工具单（运行时差异，根因未定），它越界用了 shell 并如实披露。

## 第 4 步：门下独立审——第一笔认知入账

真实账本行（节选）：

```json
{"role": "menxia", "kind": "independent_review", "status": "ok", "text": "Phase A independent reconstruction. Q1: ... (a) Claude Code equivalents exist — Agent tool spawning named background teammates ... (b) Visibility is mitigated, not equal: transcript shows coarse subagent lifecycle; durable visibility lives in append-only task records ..."}
```

门下审完用 SendMessage 回中书——你在终端里看到的彩色 teammate 消息块就是这条
消息本身，这就是你的"实时可视"界面。随后进对比阶段：中书把自己的候选发去，
门下对照它已入账的独立产物给裁决（pass/modify/return，return 必须带更好的替代）。

弱点：Agent 完成回执与 SendMessage 是两条通道，去重靠契约文字（提示层规则）。

## 第 5 步：PASS 之后——尚书与执行者

批准包只含四样：目标、有序 done_when、期限、权限边界。尚书自己用 Agent 工具
按节点生执行者（agentos-executor 人格全文注入），节点间真正独立且无共享写者
才许并行。执行者干完必落终态（execution_result：completed/failed/blocked——
结构上任何状态都写得进），然后向尚书发一次结果，生命周期即终。

弱点：期限是提示层约定，没有机械计时器强制停止，到点收敛靠尚书自觉。

## 第 6 步：集成、核验、交付——你看到什么

尚书整合为一段人话回中书；中书对照 done_when 自查后交付给你**一段自然语言**，
按契约必须点名塑造了结果的判断实质（哪个承重假设被测试、哪个竞争解释被否）。
内部 JSON、artifact、传输标记永不出现在你面前。账本落 `delivery` 行，团队关停
（TaskStop），无常驻。

## 第 7 步：事后——你随时能看的东西

```text
python3 agent-os/tools/aos_task_record.py board            # 全项目任务一行一个
python3 agent-os/tools/aos_task_record.py show --task threads-and-multiline-state
```

四本根账本按职责分工：HANDOFF（现在在哪、接着干什么）、PROGRESS（做成过什么
和证据边界）、DECISIONS（你拍板过什么和为什么）、PLANS（下一段路线）。

## 弱点总表（按危险排序）

1. 提示层概率性：所有角色守约无机械保证，上下文越长越不可靠。真正的解药是
   分层原则——能下沉为结构的持续下沉。
2. 落账靠自觉：观察钩子未建（v1.1 第一项）。
3. 小/非小误判无检测：漏走链目前只能人眼抓（v1.1 Stop 提醒兜底）。
4. 授权传导天花板：已修一例，机制永在。
5. 期限无机械执行。
6. 双通道结果去重靠契约文字。
7. 钩子只对本项目目录内的会话生效；Agent Teams 目前依赖实验开关。
8. Codex 侧三省链空缺；安装器未同步——现在装到别处的仍是不带链的 2.0。
9. 账本含用户原话，仅靠 gitignore 挡在版本库外，没有加密。
10. board 的状态是对最后一个终态事件的机械折叠，不代表业务健康。

## 亲手核验（一条主张一条命令）

```text
head -6 .claude/settings.json                      # 身份注入与钩子挂载
cat .claude/agents/agentos-entry.md                # 中书人格原文
cat agent-os/state/tasks/threads-and-multiline-state.jsonl   # 标本全账
python3 agent-os/tools/aos_task_record.py append --task ghost --role x \
  --kind execution_result --status blocked --text 试试拒不拒写   # 永不拒写
python3 agent-os/tools/aos_task_record.py board    # 派生状态板
python3 agent-os/tools/aos-lint.py                 # 结构警察全量检查
```
