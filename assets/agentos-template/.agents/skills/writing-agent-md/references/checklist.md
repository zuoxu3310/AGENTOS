# 撰写 / 审计 checklist

适用 CLAUDE.md 和 AGENTS.md。每行都要过。

---

## 通用 checklist（两家都要过）

### 长度

- [ ] CLAUDE.md ≤ 200 行（`wc -l CLAUDE.md`）
- [ ] AGENTS.md 单文件 ≤ 32 KiB（`wc -c AGENTS.md`，约 300-400 行）
- [ ] **monorepo 时 AGENTS.md chain cumulative 字节数 ≤ 32 KiB**：`find . -name AGENTS.md -not -path './node_modules/*' | xargs wc -c | tail -1`，超过则最近、最 specific 的子目录 AGENTS.md 反而会被丢（Codex 从 root 向下加，超限即停）
- [ ] 每行通过自检题：**删了 agent 会不会犯错？** 不会 → 删

### 内容性质

- [ ] 没有时间敏感语句（"2025 年 8 月之前用 X"）
- [ ] 没有同义词漂移（同时用 "API endpoint" / "URL" / "API route" / "path"）
- [ ] 没有并列选项不给默认（"用 A 或 B 或 C"）
- [ ] 没有自明废话（"写干净代码" / "保持文件整洁"）
- [ ] 没有详细 API 文档（应贴外部链接）
- [ ] 没有文件级目录解释（"foo.py 干 X，bar.py 干 Y"——agent 读代码就知道）
- [ ] 没有 Windows 反斜杠路径

### 具体性

- [ ] 每条规则都能机械验证（可 grep / 可跑命令 / 可读路径）
- [ ] 命令有完整调用形式（含参数，如 `npm test --watch`）
- [ ] 路径用绝对或相对都明确无歧义

### 一致性

- [ ] 主文件内部无矛盾规则
- [ ] 主文件与 import / rules 子文件无矛盾
- [ ] CLAUDE.md 与 AGENTS.md 之间无矛盾（用 `@AGENTS.md` 单源化最稳）

### 触发性（反向迭代核心）

- [ ] 每条规则都有"为何加它"的依据：reproduce 过 ≥ 2 次？code review 抓到？
- [ ] 没有"未来可能要用"的预防性规则
- [ ] 没有"最佳实践"通用条款（这种应该删，agent 已经懂）

---

## CLAUDE.md 专属 checklist

- [ ] location 选对（managed policy / project / user / local）
- [ ] 长说明已用 `@.claude/spec-*.md` import 拆分（深度 ≤ 5 跳）
- [ ] path-specific 规则已用 `.claude/rules/<topic>.md` + `paths:` frontmatter
- [ ] "必须每次跑"的步骤已改 hook，不留在 CLAUDE.md
- [ ] 维护者笔记用 `<!-- HTML 注释 -->` 不耗 token
- [ ] 如果项目有 AGENTS.md，已用 `@AGENTS.md` 或 symlink 集成（避免漂移）
- [ ] 强调用 IMPORTANT / YOU MUST 而不是堆叠规则
- [ ] 跑 `/memory` 验证主文件确实被加载

---

## AGENTS.md 专属 checklist

- [ ] 文件名是 `AGENTS.md`（plural 大写，**不是** `AGENT.md` / `agents.md`）
- [ ] 在 repo 根，跟 README.md 并列
- [ ] 字节数 ≤ 32 KiB（`wc -c AGENTS.md`），且 monorepo 总 chain 也 ≤ 32 KiB（见通用 checklist）
- [ ] 子项目有差异时已嵌套 `<subproject>/AGENTS.md`（concat from root, later overrides earlier）
- [ ] 临时覆盖用 `AGENTS.override.md`，不删原文
- [ ] 跨 agent 平台测过（至少 Codex；Cursor / Aider / Copilot 视项目而定）

---

## 审计场景额外 checklist

### 删除候选（应该删 30-50%）

- [ ] 列出所有"agent 看代码就知道"的行 → 删
- [ ] 列出所有"标准约定"行（"用 git commit" / "写测试覆盖功能"）→ 删
- [ ] 列出所有"自明废话"行（"代码要清晰" / "命名要有意义"）→ 删
- [ ] 列出所有过期 / 时间敏感行 → 删
- [ ] 列出所有"未来可能用上"的预防性规则 → 删

### 拆分候选

- [ ] 列出所有 > 5 行的解释段 → 拆 import
- [ ] 列出所有 path-specific 内容 → 拆到 `.claude/rules/<topic>.md`
- [ ] 列出所有"具体能力"内容（带触发词 + 固定 I/O）→ 拆成 SKILL.md
- [ ] 列出所有"必须每次跑"的步骤 → 拆成 hook

### 强化候选

- [ ] 列出"agent 没遵守过"的规则 → 加 IMPORTANT；仍不守 → 改成 hook
- [ ] 列出含糊措辞 → 改具体（带阈值 / 命令 / 路径）
- [ ] 列出无 rationale 的规则 → 补"为何加它"（commit 时）

---

## 提交前最后确认

- [ ] 跑 1-2 个真任务，agent 行为符合预期
- [ ] 用户 approve 了所有改动（propose-before-execute）
- [ ] git commit 信息说明"为何改"（reproduce 了什么错？解决了什么观察到的问题？）
- [ ] 如改了 CLAUDE.md，跑 `/memory` 再确认一次加载
- [ ] 如改了 AGENTS.md，在 Codex / Cursor 等真 agent 上各跑一个小任务

---

## 触发本 checklist 的常见场景

- 用户要求"写 / 改 / 审 / 瘦身 / 体检 / 精简" CLAUDE.md / AGENTS.md
- `lint-wiki` 报 entry doc 超长
- code review 中其他人指出 entry doc 漂移
- 加新规则前过一遍（避免堆冗余）
- 删旧规则前过一遍（避免误删 still-needed 的规则）
