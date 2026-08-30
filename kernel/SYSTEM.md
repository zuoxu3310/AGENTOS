# 整个系统怎么串起来（草稿，2026-08-29）

一句话：用户说一句话 → 程序（`board/run.py`）在固定的几个点把某个角色叫上来 → 角色照自己那份工作流（`workflows/<角色>.md`）按顺序调 skill（`<skill>/SKILL.md`）→ skill 留下的字段填进这一步的 JSON（`schemas/*.json`）→ 程序把 JSON 递给下一个角色 → 最后一条回话到用户。角色名只出现在工作流和程序里；skill 通用。

两条运行路径读的是同一份工作流文件：面板路径由 `run.py` 拼提示词（"按 workflows/menxia.md 走"＋从它的 Load 段算出的必读清单，`read_check` 核读没读）；不开面板时 `/agentos` 把当前会话绑成中书，中书按 `.claude/agents/agentos-menxia.md` 起子代理，子代理第一句就是读 `workflows/menxia.md`。

## 一、一条消息从头到尾

| # | 程序在哪一步把谁叫上来 | 角色照哪份工作流的哪几步 | 调哪些 skill（按顺序） | 交出什么 | 递给谁 |
|---|---|---|---|---|---|
| 1 | `_mode2` 第 1 段，并行三路 | 门下甲、门下乙：`menxia.md` 第 1–2 步 | 第一性原理 → 读法与契约 | reading.json | 程序留着，第 3 步用 |
| 1 | 同上 | 中书：`zhongshu.md` 第 1–3 步 | 第一性原理 → 读法与契约 → 反谄媚（第二个说法＝自己的 `alternative_reading`） | reading.json（候选） | 程序匿名送门下 |
| 2 | `_mode2` 第 2 段 `diverge()` | — | — | 删掉 | — |
| 3 | `_mode2` 第 3 段 `p_compare`，每席一路 | 门下：`menxia.md` 第 3–4 步（续第 1 步那条会话） | 反谄媚（A、B＝自己第 2 步那份和中书候选，匿名随机） → 论证第 1–4 步 | verdict.json（含 `question` 候选） | 程序送中书 |
| 4 | `_mode2` 第 4 段 `p_reply` | 中书：`zhongshu.md` 第 4–6 步 | 反谄媚（第二个说法＝门下读法） → 论证末节 → 呈报 | reply.json：`reply`、`decisions`≤1、`contract` | 用户 |
| 5 | 用户点开工 → `execute` → `p_plan` | 尚书：`shangshu.md` 第 1 步 | 工程计划·出计划 | plan.json | 程序按 `depends` 派工 |
| 6 | `schedule_nodes` → `p_dispatch`，一节点一路 | 执行体：`executor.md` 第 1 步 | 照计划执行 | exec.json；程序另算 diff | 程序送尚书 |
| 7 | `p_integrate`；计时到 `budget_minutes` 走"到预算" | 尚书：`shangshu.md` 第 2 步／到预算 | 工程计划·整合／到预算 | integration.json | 程序送中书 |
| 8 | `p_deliver` | 中书：`zhongshu.md` 交付段 | 证据与核验第 1 步 → 呈报 | reply.json＋改动卡 | 用户 |
| 9 | `censor_round`／`censor_exec`（现为纯程序） | 御史：`yushi.md`（若改成模型调用） | 逐项比 | 偏差清单；`wiki/errors/` | 记录 |

每一路写句子时随手用逻辑推理、因果推断、证据与核验，不排步。用户在第 4 步和第 8 步各看到一条话；第 4 步之后等用户点开工，尚书才存在。

## 二、每个 JSON 的字段从哪份 skill 来

- reading.json ← 读法与契约的七个字段（`quoted_spans`、`target_state`、`acceptance_checks`、`worth_and_precedent`、`alternative_reading`、`flip_item`、`ask_or_decide`）＋ 第一性原理的 `pre_contract_packet`（没进第一性原理就是不适用）＋ 中书候选另带反谄媚的 `mind_change`。
- verdict.json ← 反谄媚的五样（`strong_request`、`reading_A`、`reading_B`、`real_disagreement`＋`flip_variable`、`question`、`mind_change`）＋ 论证的五样（`field_map`、`live_diffs`、`objections`、`verdict`＋`verdict_basis`＋`verdict_why`、`return_question`）。`verdict` 三个词：pass／modify／return。
- reply.json ← 呈报的五样（`understood`、`annotations`、`decisions`、`contract`、`reply`）；`annotations` 里的处置来自论证末节的 `disposition`。
- plan.json、exec.json、integration.json 现有字段够用，不改：出计划留下的东西就是 `nodes`（含 `mechanism` 写进每节点的 `scope`）、`refused`、`budget_minutes`；照计划执行的 `wrapup` 就是 `status`／`remaining`，`verify_output` 就是 `evidence`；整合的逐条核对就是 `checks`。
- 每个字段三态：`state` 取 filled／could_not／not_applicable，`content` 装内容，`source` 装来源或原因。草稿在 `schemas/`。

## 三、程序侧要改的每一处（都在 `board/run.py`）

1. `p_blind`、`p_candidate`、`p_compare`、`p_reply`、`p_plan`、`p_dispatch`、`p_integrate`、`p_deliver`：提示词改成"按 `workflows/<角色>.md` 走，从第 N 步起"；`load_block` 照旧从该文件 Load 段算必读清单（`LOAD_SKILL_RE` 已能读 `<名>/SKILL.md`）。
2. `p_compare`：把"你自己的读法／中书的候选"改成匿名 A、B、顺序随机（`random.shuffle` 一次，记下映射供程序还原）；必读清单由 `menxia.md` 算出，不再单点 `anti-sycophancy-gate.md`。
3. `_mode2` 第 2 段：删 `diverge()`、`splits` 的 state 行与事件、面板"分歧"卡片。
4. `p_reply`：除判词外把门下各席第 1 步的读法原文一并送中书（第 4 步反谄媚要它）。
5. `schemas/reading.json`、`verdict.json`、`reply.json` 换成三态新字段（草稿在 `schemas/`）；`grab_json`／`reply_with_decisions` 里取 `decisions`、`contract` 的位置随之改。
6. `GATE_SHANGSHU`、`GATE_EXECUTOR` 和 `p_reply`／`p_deliver` 里点名的 `review/*-gate.md` 删掉；六份 gate 文档退休（对应关系见 README）。
7. `watchdog`：固定 600／1200 秒改为契约的 `budget_minutes`；到点不杀，改成让尚书走"到预算"。
8. `seat-skills.json` 退休：清单只从工作流文件 Load 段算。
9. 御史：留程序，或改成交付后一次后台模型调用走 `yushi.md`——用户定。

## 四、谁指向谁

`run.py` → `workflows/<角色>.md` → `<skill>/SKILL.md`；`<skill>/SKILL.md` 的「留下」→ `schemas/*.json`；`schemas/*.json` → 下一个角色的"手上"。`.claude/agents/agentos-*.md` → 同一份 `workflows/<角色>.md`。README 里的席位绑定表作废，绑定就是工作流文件本身。
