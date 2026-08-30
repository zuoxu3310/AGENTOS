# kernel — 三省六部的内核：工作流、schema、方法 skill（2026-08-25 起草，2026-08-30 定为正体）

skill 是共享的方法，不属于任何角色；哪个角色在哪一步调用哪份，由该角色的工作流决定（见下面「工作流读什么」）。skill 正文里不出现角色名，语言按宪法「语言」一节：没看过本项目的人也能照做。

## 这里有什么

宪法（其余都按它写）：
- `writing-a-method-skill/` — 写方法 skill 的方法：一步一物、每个需要判断的步骤写全「怎么做」子步骤（像论文的方法一节，长度由方法决定）、三态字段、一句为什么、用产出代替禁令、出事故不追加规则、不写角色名、不用内部黑话。

方法 skill（十一份；2026-08-26 第五版：一门学科一份——第一性原理按调研 05 新写；逻辑推理/因果推断、论证/反谄媚各拆成两份；共约 1250 行）；复用阶梯归计划不归执行；读法加「值不值得做、有没有现成的」一步；第三版：无角色名、无黑话，每个判断步骤的「怎么做」按论文方法一节的深度写全；共约 1139 行，主线程逐份通读并机械扫过）：

| skill | 什么情形下用 | 替换现有 | 行数 |
|---|---|---|---|
| `first-principles/` 第一性原理 | 手上有一条（可能没想清楚的）请求，写目标之前要和用户一起想清楚：目的链、前提台账（事实/硬限制/资源限制/假设/惯例/不知道）、要求审计（马斯克第一二步，删是可逆提议）、最小必须发生集、该做与能做分开、最小用户决策包；类比是默认，四种情形才进 | 调研 05（KAOS、五问边界、价值工程功能分析、关键假设核查、假设规划、需求追溯） | 113 |
| `reading-and-contract/` 读法与契约 | 手上有用户的一条消息，要写出目标、完成条件、值不值得做／有没有现成的（Linus 第一问＋先查先例三层）、另一种读法、缺什么 | intent-contract-review、task-contract、reading.json 的 goal/assumption/rival/missing/done_when | 88 |
| `anti-sycophancy/` 反谄媚 | 手上有用户的消息、自己在没看过对方那份时写下的读法，以及同一条消息的两份读法匿名并排（A／B），要在下判断之前先把先入之见摆到纸面上 | anti-sycophancy-review、menxia.md Phase B 里的钢人与改口两段、verdict.json 新增 strong_request/reading_A/reading_B/real_disagreement/flip_variable/question/mind_change | 89 |
| `argumentation/` 论证 | 「反谄媚」那一遍走完、它留下的东西都在手上，要判 pass/modify/return；末节：写对方读法的人怎么处理反对意见 | menxia.md Phase B 的判词部分、verdict.json 的 why/diff/better | 81 |
| `report-to-user/` 呈报 | 手上有审读人的判词和自己的读法，要写用户读的那一屏 | delivery-review、daemon 里 p_reply 的要求、reply.json（加 annotations、contract 扩字段） | 102 |
| `logical-reasoning/` 逻辑推理 | 要写「所以／因此／这说明／建议」这类句子之前，或者要写一个靠推理撑着的判断 | reasoning-causality-review、reasoning-base.md（与「因果推断」合起来整体替换；七类断言九种角色退掉） | 57 |
| `causal-inference/` 因果推断 | 要写「导致／造成／根因／责任在／改 X 会修好 Y」这类句子之前，并且这句会导出改动或指向某个人 | 同上，与「逻辑推理」合起来整体替换 | 103 |
| `evidence-and-verification/` 证据与核验 | 要说「完成／通过／看到」之前；拿别人的结果当结论之前；核对交付是否满足完成条件时 | evidence-claim-review、evidence-to-claim-gate.md、completion-gate.md | 88 |
| `engineering-plan/` 工程计划 | 手上有批过的契约和预算，要出计划（三次翻译、每节点用什么现成的＝ponytail 复用阶梯、处女原则：坏根整个重写不打补丁）；各块活的结果回来要核（处女原则验收、Linus 三档评审、旧代码扫描）；预算用完时对账不交半成品 | engineering-plan-review、engineering-gate.md（去掉"是不是真问题"一问；到预算改为对账不交半成品） | 261 |
| `execute-node/` 照计划执行 | 领到计划派下的一块活（目标、允许改的文件、计划挑好的做法、一条验证命令），要照着做、验、交报告 | minimal-code-review、minimal-code-gate.md 的边界与 ponytail 标注、executor.md（加两败即停；做法由计划定，不在这里挑） | 77 |
| `reconciliation/` 逐项比（原名对账） | 交付已发出、或预算用完没交付、或用户说做错了之后，要逐项比这一轮工作偏在哪 | yushi.md 前段（权限检查与落地核对保留在第 6 步） | 102 |

不动：`memory-wiki-routing`。

## 工作流读什么（替换 agent-os/skills/seat-skills.json；这是角色与 skill 的唯一绑定处）

```json
{
  "zhongshu": ["first-principles", "reading-and-contract", "argumentation", "report-to-user", "evidence-and-verification", "logical-reasoning", "causal-inference"],
  "menxia":   ["first-principles", "reading-and-contract", "anti-sycophancy", "argumentation", "evidence-and-verification", "logical-reasoning", "causal-inference"],
  "shangshu": ["engineering-plan", "evidence-and-verification", "logical-reasoning", "causal-inference"],
  "executor": ["execute-node", "evidence-and-verification"],
  "yushi":    ["reconciliation", "memory-wiki-routing", "evidence-and-verification", "logical-reasoning", "causal-inference"]
}
```

从席位清单移出（文件保留，作他用）：route-promotion-review、prompt-craft-review（改作写 skill/提示词时的方法）、lifecycle-execution、completion-gate。工作流文件的 Load 段随之缩短。

## 这些 skill 隐含的程序侧改动（面板 daemon，另批另做）

1. 三份 schema 改三态：reading.json（六个新字段）、verdict.json（反谄媚留下的 strong_request/trace/reading_A/reading_B/real_disagreement/flip_variable/question/mind_change，论证留下的 field_map/live_diffs/objections/notes/verdict/verdict_basis/verdict_why/return_question）、reply.json（加 annotations[]，contract 加 assumptions/size/budget/not_doing，decisions ≤ 1）。
2. 门下比对：两份读法同格式、匿名、随机顺序并排递给门下（现在提示词写明"中书的候选"；要真匿名需比对开新会话）。
3. 去掉 `diverge()` 的字符串比对与面板"分歧"展示；改为并排展示两席的 `flip_item`。
4. 程序核：`quoted_spans` 与 `annotations[].quote` 做子串核验，核不过标红；`verdict` 按 objections/live_diffs 重算，对不上退回。
5. 到预算：看门狗从固定 600/1200 秒改为契约预算；到点停工、快照回退、走尚书"到预算"三步，不交付。

## 待定的结构调整（2026-08-26 用户指出）

- 一门学科一份方法：「推理与因果」已拆成「逻辑推理」和「因果推断」两份（2026-08-26 完成，只重组不重写）。「判词」已拆成「反谄媚」（`anti-sycophancy/`：最强完整重述、A/B 双向钢人、真实分歧与翻判变量、一个归用户定的问题、改口记录）和「论证」（`argumentation/`：逐字段对照、实质差异、够格的反对意见、判词规则，末节逐条处置）两份（2026-08-26 完成；论证一侧只重组不重写，反谄媚一侧按方向 06 的调研裁决写全，`verdict/` 已删）。
- 「第一性原理」已按调研 05 写成（`first-principles/`，113 行）。

## 还没做的

- 用户审阅九页。
- 实跑验证：改完程序侧后，用五个真实任务数三个数——pass 出现没有；每轮问题 ≤ 1 没有；目标有没有指不回原话的。哪个数不对，改走法，不加规则。
- 基线证据（改前）：t20260822-1142 五轮——判词 10/10 modify、分歧 6/6 轮全报、读法 goal 字段以"Master ZX，"开头（格式泄漏）。

## 2026-08-26 第六版：引用，不内联

- skill 是承担一件活的人一上手就全读、全带的本事，哪一步用哪份由他自己判断；工作流只写谁出场、交什么。「何时」只写"要做某件事之前"，不写"谁在哪个阶段递来什么"（反谄媚、呈报、论证的「何时」已照此改）。
- 一步里要用另一门学科的方法，写一句固定格式的引用：「这一格照『某份』第 N 步写，写出 `字段`」，那一步的字段进本步的「留下」；多步方法只在它的学科里写一遍。已改的引用：反谄媚第 2、3、5 步→逻辑推理第 2、3 步；论证第 3 步→逻辑推理第 2 步；因果推断第 3 步→逻辑推理第 3 步；逐项比第 4 步→逻辑推理第 1–3 步、因果推断；证据与核验的"支持／因果／根因"三格→逻辑推理第 3 步、因果推断第 4、5 步。
- 问不问用户只有一处规则：呈报第 3 步。反谄媚第 4 步、第一性原理第 6 步、读法与契约第 7 步只交候选。
- 三张措辞阶梯同时触发时按最低一级写（宪法、三份各加一句）。
- 改动前的版本在 scratchpad `drafts-before-xref/`。
- 引用形式试过一次（2026-08-26，同一条真实消息、同样两份读法、各一个不带对话上下文的 opus）：读引用版的写出了逻辑推理第 2、3 步要求的 `warrant`（前提三查）和 `counter`（相反解释＋区分观察）；读改前内联版的只自带了"删掉结论仍成立"一个碎片。各一次，派工提示里有一句"照引用写"的提醒，没测不提醒的情形。记录在 scratchpad `xref-test-*-output.md`。

## 2026-08-27 第七版：skill 通用，三省六部的用法写在工作流里

skill 的 description／用于／何时只写通用情形（要下结论之前、要开口回提要求的人之前……）；每份第一行「用到：」列出它引用的别的 skill（目录名＋第几步），程序可据此核对必读清单。下面这些话属于工作流文件（`agent-os/workflows/*.md`），不写进 skill：

- 门下 Phase A（盲读）：对用户这一轮原话走第一性原理（四种情形才进）和读法与契约，交 reading.json；第二个说法＝自己写的 `alternative_reading`。
- 门下 Phase B（比对）：第二个说法＝中书候选，匿名标成 A／B、顺序随机；走反谄媚、论证；论证的〔通过／改一处／退回〕在 verdict.json 里写成 pass／modify／return；反谄媚第 4 步的 `question` 候选随判词交中书。
- 中书回话：审读意见＝两席门下的判词；走论证末节处置每条意见，走呈报；呈报第 3 步的 `decisions` 至多一条，进 reply.json。
- 尚书／执行体／御史：契约＝用户点开工的 goal＋done_when；节点＝plan.json 里的一块活；记录＝任务账本。

## 2026-08-29 角色工作流草稿：`workflows/`

一个角色一份，只写三样：手上有什么；第几步调用哪份 skill、交什么；写句子时随手用哪几份。内容都在 skill 里，工作流不解释也不复述。Load 段由步骤推出（程序 `load_list()` 从这段算必读清单）。上一节"用法草稿"那几行已并进这五份。
- 8-29 第二版：五份按 daemon 里各席实际拿到的东西（p_blind/p_candidate/p_compare/p_reply/p_package/p_dispatch/p_integrate/p_deliver）、各 skill 的「留下」字段、schemas/*.json 逐项核过；机械核对通过：Load 集合＝步骤里的 skill 集合；步骤里每个字段名都在被引 skill 或 schema 里；每个 .json 都存在。前提：reading.json／verdict.json 换成新字段（程序侧待做）。发现一处 skill 级重叠待处理：读法与契约第 6 步 `flip_item` 与反谄媚第 3 步 `flip_variable` 是同一件事写了两遍。

## 2026-08-30 新面板 `work/board2/`

按 PANEL.md／SYSTEM.md 写成：`run.py`（固定链路）、`server.py`、`panel.html`、`snapshot.py`、`tests/`。Codex 三轮审查后签收。SYSTEM.md 第三节"程序侧要改的九处"由 board2 整体替代，不再逐条改旧 daemon.py。格子七份在 `schemas/`（含御史的 censor.json）。
- 8-30 晚 面板第二版：按 claude.ai 抽出的配色变量（深浅两套）、本地 anthropic-sans/serif 字体、尺寸 1:1 重画；补回旧面板功能：目录选择与最近项目、任务搜索、每任务席位配置（可加门下）、三个档位、停止、改名/删除、原始递交查看、压缩、多轮对话；右栏加流程图（任务→各步节点＋工具刻度）和按事件编号的时间轴回放。八个场景测试全过。

