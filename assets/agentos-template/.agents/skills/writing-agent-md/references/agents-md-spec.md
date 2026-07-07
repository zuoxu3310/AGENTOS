# AGENTS.md 完整官方规范

来源（拉取于 2026-05-08）：
- https://agents.md/
- https://github.com/agentsmd/agents.md
- https://developers.openai.com/codex/guides/agents-md
- https://developers.openai.com/codex/learn/best-practices
- https://github.com/openai/codex/blob/main/AGENTS.md（OpenAI 自家 canonical 范例）

本文件是 OpenAI / agents.md 标准的事实摘抄 + 关键原话保留。**禁止**在此文件里加 inferred 内容。

## 目录

- 是什么
- 兼容的 agent / 工具清单（23+，agents.md 主页现行版）
- 格式（几乎没有）
- 推荐章节（不强制）
- 加载机制
  - 文件位置
  - 优先级（concat from root，later overrides earlier）
  - 临时覆盖（AGENTS.override.md）
  - 大小限制（cumulative 32 KiB）
- 写作核心原则
- OpenAI 自家 AGENTS.md（canonical 范例）
- 与 CLAUDE.md 的关系
- Anti-patterns
- 与 SKILL.md / Codex Skills 的关系
- OpenAI 监督建议

---

## 是什么

> "AGENTS.md is a simple, open format for guiding coding agents."
>
> "Think of it as a README for agents: a dedicated, predictable place to provide context and instructions to help AI coding agents work on your project."
>
> "AGENTS.md is just standard Markdown. Use any headings you like; the agent simply parses the text you provide."

由 **Linux Foundation 旗下 Agentic AI Foundation** 维护。是开放标准。

> "AGENTS.md emerged from collaborative efforts across the AI software development ecosystem, including OpenAI Codex, Amp, Jules from Google, Cursor, and Factory."

## 兼容的 agent / 工具清单

agents.md 主页章节标题："**One AGENTS.md works across many agents**"

> "Your agent definitions are compatible with a growing ecosystem of AI coding agents and tools:"

主页 2026-05-08 列出 **23+ 个**兼容工具（按页面顺序）：

- Codex (OpenAI)
- Jules (Google)
- Factory
- Aider
- goose
- opencode
- Zed
- Warp
- VS Code
- Devin (Cognition)
- Autopilot & Coded Agents (UiPath)
- Junie (JetBrains)
- Amp
- Cursor
- RooCode
- Gemini CLI (Google)
- Kilo Code
- Phoenix
- Semgrep
- Coding agent (GitHub Copilot)
- Ona
- Windsurf (Cognition)
- Augment Code

完整列表 + "View all supported agents" 链接见 https://agents.md/。

⚠️ **关键 caveat**：列表中**不含 Anthropic Claude / Claude Code**。Anthropic 自己的 CLAUDE.md 文档明说 "Claude Code reads CLAUDE.md, not AGENTS.md"。要让两边共享同一份规则，需要在 CLAUDE.md 顶上写 `@AGENTS.md` import 或建 symlink。

## 格式（几乎没有）

> "AGENTS.md files use standard Markdown syntax with no required fields or sections. The format imposes no constraints on heading names, nesting levels, or section order."

- **无 YAML frontmatter**
- **无必填字段**
- **无指定章节**
- 纯 markdown 解析

## 推荐章节（不强制，OpenAI Codex 文档建议）

按 Codex 官方"什么是强 AGENTS.md"的描述：

- Repository layout and important directories
- How to run the project
- Build, test, and lint commands
- Engineering conventions and PR expectations
- Constraints and do-not rules
- What completion looks like and how to verify work

agents.md 主页给的最小例子展示这些 section：
- Dev environment tips —— setup 与工作流
- Testing instructions —— 测试执行与验证
- PR instructions —— PR 约定与 pre-commit 要求

## 加载机制

### 文件位置

主文件名：**`AGENTS.md`（plural，大写）**，放在 repo 根，跟 `README.md` 并列。

monorepo / 子项目：每个子目录可放自己的 `AGENTS.md`。OpenAI 主仓有 88 个 AGENTS.md。

### 优先级（按 Codex 官方文档现行措辞）

Codex 官方加载机制（developers.openai.com/codex/guides/agents-md）：

> "Codex builds an instruction chain when it starts (once per run; in the TUI this usually means once per launched session). Discovery follows this precedence order:
>
> 1. **Global scope:** In your Codex home directory (defaults to `~/.codex`, unless you set `CODEX_HOME`), Codex reads `AGENTS.override.md` if it exists. Otherwise, Codex reads `AGENTS.md`. Codex uses only the first non-empty file at this level.
>
> 2. **Project scope:** Starting at the project root (typically the Git root), Codex walks down to your current working directory. If Codex cannot find a project root, it only checks the current directory. In each directory along the path, it checks for `AGENTS.override.md`, then `AGENTS.md`, then any fallback names in `project_doc_fallback_filenames`. Codex includes at most one file per directory.
>
> 3. **Merge order:** Codex concatenates files from the root down, joining them with blank lines. Files closer to your current directory override earlier guidance because they appear later in the combined prompt."

—— **关键事实**：Codex 是 **concat（串接）不是 override**。所有相关 AGENTS.md 都进 prompt，越近的越靠后，"override" 是因为后出现的内容覆盖前面。

agents.md 主页较早期的简化措辞（见 https://agents.md/）：
> "Agents automatically read the nearest file in the directory tree, so the closest one takes precedence and every subproject can ship tailored instructions."

—— 这只是对 concat 行为的简化描述，不要据此误以为只加载一份文件。

用户在 chat 中的显式 prompt 永远在 AGENTS.md 链之后被处理，因此 prompt 在实际行为上 override AGENTS.md。

### 临时覆盖

> "In your Codex home directory, Codex reads `AGENTS.override.md` if it exists; otherwise, Codex reads AGENTS.md."
>
> "Use `~/.codex/AGENTS.override.md` when you need a temporary global override without deleting the base file."

`AGENTS.override.md` 优先于 `AGENTS.md`，可放：
- `~/.codex/AGENTS.override.md`（全局）
- 项目目录里的 override 文件（项目级）

### 大小限制（cumulative，不是 per-file）

Codex 官方原话：

> "Codex skips empty files and stops adding files once the combined size reaches the limit defined by `project_doc_max_bytes` (32 KiB by default)."

—— **关键澄清**：

- **空文件**：直接跳过
- **32 KiB 是 cumulative 上限**（所有相关 AGENTS.md 加起来），不是单文件上限
- 总大小达到 32 KiB 后，**剩余文件不再加入** chain
- Codex 从根向下串接，所以达到上限时丢失的是离 cwd 最近、最 specific 的那份（最后才被加进 chain）—— 这是反直觉的，要警觉
- `project_doc_max_bytes` 在 Codex config 可调

→ AGENTS.md 实务软上限：**单文件 ≤ 32 KiB**（保险），多文件总和也尽量 ≤ 32 KiB（避免最 specific 的反而被丢）。

## 写作核心原则（OpenAI 原话）

### 短 > 长

> "A short, accurate AGENTS.md is more useful than a long file full of vague rules."

### 反向迭代

> "When Codex makes the same mistake twice, ask it for a retrospective and update AGENTS.md."

—— 从最少规则起步，**犯错才追加**。

### 三者分工（durable / ephemeral / repeatable）

OpenAI Codex best practices 在 "common mistakes" 段提到的反模式：

> "Overloading the prompt with durable rules" —— 应该挪到 AGENTS.md 或 skill 里

另一段（关于 quality standards）补充：

> "That guidance can come from either the prompt or AGENTS.md."

→ 用户的临时质量偏好可临时进 prompt；只有反复出现才升级到 AGENTS.md。

| 写在哪 | 适用 |
|---|---|
| **AGENTS.md** | 跨多 task 的持久（durable）规则、仓库标准、约定 |
| **Prompt** | 单次任务上下文（goal / constraints / done criteria）|
| **Skill** | 可重复（repeatable）工作流，有固定 trigger 和 I/O |

### Living documentation

agents.md FAQ 现行措辞（两条独立 FAQ 答案）：

> "Absolutely. Treat AGENTS.md as living documentation."

> "The closest AGENTS.md to the edited file wins; explicit user chat prompts override everything."

—— 第二条是 FAQ 的简化措辞，与本节早前引用的 Codex 官方 3-step Discovery 全文是同一机制的不同表述层。在 multi-AGENTS.md 项目里，按 Codex 官方"concat from root down, later overrides earlier" 理解，更精确。

## OpenAI 自家 AGENTS.md（canonical 范例）

`github.com/openai/codex/blob/main/AGENTS.md` 是 AGENTS.md 格式作者自家在 codex 仓库用的版本，约 **219 行**（超出 200 行但在 32 KiB 之内）。

### 结构

1. **Rust/codex-rs** —— 基础规则
2. **The codex-core crate** —— anti-pattern guidance（resist bloat）
3. **TUI style & code conventions** —— UI-specific 标准
4. **Tests** —— snapshot / assertion / integration 模式
5. **App-server API Development** —— protocol 与 RPC 标准

### 风格特征

- **Prescriptive & direct**："Always collapse if statements", "Never add or modify"
- **Rationale-driven**：解释 *why*（如 sandbox 限制、性能）
- **Practical examples**：代码片段 + 命令调用
- **Cross-references**：链接外部 linter（Clippy）/ 文档 / 相关文件
- **Nested bullet hierarchies**：缩进显示规则间关系

—— 风格上**强 prescriptive**（"always X / never Y"），不是建议式。

## Section 的 fallback 配置

仓库使用其他文件名作 agent 文档时（如 `.cursorrules`、`AGENT.md`、`AI_INSTRUCTIONS.md`），可在 Codex config 配 fallback 文件名清单。

## 与 CLAUDE.md 的关系（再次强调）

Claude Code 不读 AGENTS.md。共用方式（在 CLAUDE.md 顶部）：

```markdown
# CLAUDE.md
@AGENTS.md

## Claude Code Specific
（只放 Claude 特有的）
```

或者：

```bash
ln -s AGENTS.md CLAUDE.md
```

→ Claude `/init` 在 repo 已有 AGENTS.md / `.cursorrules` / `.windsurfrules` 时会读取并融合到生成的 CLAUDE.md。

## Anti-patterns（implicit / 推断）

OpenAI 文档**没有明确禁止清单**，但暗示避免：

- 空文件（Codex 自动跳过）
- chain 累计字节数超 `project_doc_max_bytes`（默认 32 KiB）—— Codex stops adding files once combined size reaches the limit；超限后剩余 AGENTS.md 不再加入 chain（详见上文"大小限制（cumulative）"段）
- 同目录多份重复规则
- 把单次任务指令塞进来（应走 prompt）
- 把 durable 规则散在 prompt 而不集中到 AGENTS.md
- 长篇 vague 规则（"A short, accurate AGENTS.md is more useful than a long file full of vague rules"）

## 与 SKILL.md / Codex Skills 的关系

OpenAI Codex 也有 skill 系统（`developers.openai.com/codex/skills`），用 `SKILL.md` 文件，**和 Anthropic 的格式高度兼容**。

→ 同一份 SKILL.md 可两家共用。但 AGENTS.md 和 CLAUDE.md 是**独立的入口文件**，不要试图合并 —— 共享规则用 `@AGENTS.md` import 即可。

## OpenAI 监督建议

> "Guidance about quality standards can come from either the prompt or AGENTS.md."

→ 用户的临时偏好可临时进 prompt；只有反复出现才升级到 AGENTS.md。

> "Place overrides as close to specialized work as possible."

→ 嵌套 AGENTS.md 的优势就是 path-specific override。
