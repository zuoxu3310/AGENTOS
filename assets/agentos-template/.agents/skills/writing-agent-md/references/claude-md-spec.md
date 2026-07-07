# CLAUDE.md 完整官方规范

来源（拉取于 2026-05-08）：
- https://code.claude.com/docs/en/memory
- https://code.claude.com/docs/en/best-practices

本文件是 Anthropic 官方 CLAUDE.md 文档的事实摘抄 + 关键原话保留，便于 skill 触发后直接对照。**禁止**在此文件里加 inferred 内容；只能保留官方原文 / 直接事实。

## 目录

- 是什么
- 何时加内容（4 条触发器）
- 长度（≤ 200 行硬建议）
- 文件位置（4 个层级）
- 写作规则（Size / Structure / Specificity / Consistency / Emphasis）
- ✅ Include / ❌ Exclude 对照表
- @import 语法
- 与 AGENTS.md 的关系（@AGENTS.md / symlink）
- .claude/rules/ 目录（path-specific 规则）
- Block-level HTML 注释
- Hooks vs CLAUDE.md
- 工具命令（/init / /memory / claudeMdExcludes）
- Auto memory（旁证）
- Compaction 行为
- --add-dir flag
- 调试链
- 团队 / 组织级 managed policy

---

## 是什么

> "CLAUDE.md files are markdown files that give Claude persistent instructions for a project, your personal workflow, or your entire organization. You write these files in plain text; Claude reads them at the start of every session."

> "CLAUDE.md content is delivered as a user message after the system prompt, not as part of the system prompt itself."

—— 关键：CLAUDE.md 不是 system prompt 的一部分，而是 session 开始时的 user message。所以**无法严格保证执行**，只能"努力 follow"。

## 何时往 CLAUDE.md 加内容（4 条触发器，原话）

> "Treat CLAUDE.md as the place you write down what you'd otherwise re-explain. Add to it when:
> - Claude makes the same mistake a second time
> - A code review catches something Claude should have known about this codebase
> - You type the same correction or clarification into chat that you typed last session
> - A new teammate would need the same context to be productive"

不满足 → 别加。

> "Keep it to facts Claude should hold in every session: build commands, conventions, project layout, 'always do X' rules. If an entry is a multi-step procedure or only matters for one part of the codebase, move it to a skill or a path-scoped rule instead."

## 长度（硬建议）

> "Target under 200 lines per CLAUDE.md file. Longer files consume more context and reduce adherence."

200 行是当前口径（旧版 best-practices 页是 300 行）。**超过 200 → 服从度下降**，规则被噪音淹没。

最新自检题：
> "Keep it concise. For each line, ask: 'Would removing this cause Claude to make mistakes?' If not, cut it."

## 文件位置（4 个层级）

| Scope | Location | Purpose | Use case | Shared with |
|---|---|---|---|---|
| **Managed policy** | macOS `/Library/Application Support/ClaudeCode/CLAUDE.md`<br>Linux `/etc/claude-code/CLAUDE.md`<br>Windows `C:\Program Files\ClaudeCode\CLAUDE.md` | 组织级别 IT/DevOps 推送 | 公司编码标准、安全策略、合规 | 全机器所有用户 |
| **Project** | `./CLAUDE.md` 或 `./.claude/CLAUDE.md` | 团队共享 | 项目架构、编码标准、工作流 | 进 git 与团队共享 |
| **User** | `~/.claude/CLAUDE.md` | 跨项目个人偏好 | 编码风格偏好、个人工具捷径 | 仅本人（所有项目）|
| **Local** | `./CLAUDE.local.md` | 项目级个人偏好 | 沙箱 URL、首选测试数据 | 仅本人（当前项目，需加 .gitignore）|

加载顺序：从 filesystem 根向下走，**全部 concat 进 context**（不是 override）。同目录内 `CLAUDE.local.md` 在 `CLAUDE.md` 之后追加。子目录的 CLAUDE.md 不在 launch 时加载，而是 Claude 读子目录文件时延迟加载。

managed policy CLAUDE.md **不能**被个人 `claudeMdExcludes` 排除。

## 写作规则（原话）

### Size（再强调一次）

> "Target under 200 lines per CLAUDE.md file. Longer files consume more context and reduce adherence. If your instructions are growing large, use path-scoped rules so instructions load only when Claude works with matching files. You can also split content into imports for organization, though imported files still load and enter the context window at launch."

注意：`@import` 拆分**不省 context**，只是组织。

### Structure

> "Use markdown headers and bullets to group related instructions. Claude scans structure the same way readers do: organized sections are easier to follow than dense paragraphs."

### Specificity

> "Write instructions that are concrete enough to verify."
>
> Examples:
> - "Use 2-space indentation" instead of "Format code properly"
> - "Run `npm test` before committing" instead of "Test your changes"
> - "API handlers live in `src/api/handlers/`" instead of "Keep files organized"

### Consistency

> "If two rules contradict each other, Claude may pick one arbitrarily. Review your CLAUDE.md files, nested CLAUDE.md files in subdirectories, and `.claude/rules/` periodically to remove outdated or conflicting instructions."

### Emphasis

> "You can tune instructions by adding emphasis (e.g., 'IMPORTANT' or 'YOU MUST') to improve adherence."

## ✅ Include / ❌ Exclude（best-practices 页对照表）

| ✅ Include | ❌ Exclude |
|---|---|
| Bash commands Claude can't guess | Anything Claude can figure out by reading code |
| Code style rules that differ from defaults | Standard language conventions Claude already knows |
| Testing instructions and preferred test runners | Detailed API documentation (link to docs instead) |
| Repository etiquette (branch naming, PR conventions) | Information that changes frequently |
| Architectural decisions specific to your project | Long explanations or tutorials |
| Developer environment quirks (required env vars) | File-by-file descriptions of the codebase |
| Common gotchas or non-obvious behaviors | Self-evident practices like "write clean code" |

## @import 语法

```markdown
See @README.md for project overview and @package.json for available npm commands.

# Additional Instructions
- Git workflow: @docs/git-instructions.md
- Personal overrides: @~/.claude/my-project-instructions.md
```

- 相对路径相对于含 import 的文件（不是 cwd）
- 支持递归 import，深度上限 **5 跳**
- import 文件**仍然在 launch 时加载**（不省 context，只是组织）
- 首次遇到外部 import 会弹审批框；拒绝后该 import 永久禁用，不再弹

## 与 AGENTS.md 的关系（关键差异）

> "Claude Code reads CLAUDE.md, not AGENTS.md."

如果项目同时有：

```markdown
# CLAUDE.md
@AGENTS.md

## Claude Code Specific
Use plan mode for changes under `src/billing/`.
```

或者用 symlink（Windows 需 Administrator / Developer Mode）：
```bash
ln -s AGENTS.md CLAUDE.md
```

> "Running `/init` in a repo that already has an AGENTS.md reads it and incorporates the relevant parts into the generated CLAUDE.md. It also reads other tool configs like `.cursorrules` and `.windsurfrules`."

## .claude/rules/ 目录（path-specific 规则）

```
.claude/
├── CLAUDE.md
└── rules/
    ├── code-style.md
    ├── testing.md
    └── security.md
```

带 frontmatter 的 path-scoped rule：

```markdown
---
paths:
  - "src/api/**/*.ts"
---

# API Development Rules
- All API endpoints must include input validation
- Use the standard error response format
- Include OpenAPI documentation comments
```

无 `paths` 字段 → 每次 session 都加载（等价于 `.claude/CLAUDE.md`）。

支持 glob：`**/*.ts`, `src/**/*`, `*.md`, `src/**/*.{ts,tsx}`，多 pattern 同时存在。

`.claude/rules/` 支持 symlink → 跨项目共享同一套规则。

## Block-level HTML 注释

> "Block-level HTML comments (`<!-- maintainer notes -->`) in CLAUDE.md files are stripped before the content is injected into Claude's context. Use them to leave notes for human maintainers without spending context tokens on them. Comments inside code blocks are preserved. When you open a CLAUDE.md file directly with the Read tool, comments remain visible."

可以用来放维护者笔记不耗 token。

## Hooks vs CLAUDE.md（行为指引 vs 强制执行）

> "If the instruction is something that must run at a specific point, such as before every commit or after each file edit, write it as a hook instead. Hooks execute as shell commands at fixed lifecycle events and apply regardless of what Claude decides to do."

- CLAUDE.md = 行为指引（advisory）
- hook = 强制执行（deterministic）

> "For instructions you want at the system prompt level, use `--append-system-prompt`. This must be passed every invocation, so it's better suited to scripts and automation than interactive use."

## 工具命令

### `/init`

> "Run `/init` to generate a starting CLAUDE.md automatically. Claude analyzes your codebase and creates a file with build commands, test instructions, and project conventions it discovers. If a CLAUDE.md already exists, `/init` suggests improvements rather than overwriting it."

`CLAUDE_CODE_NEW_INIT=1` 启用交互式多阶段流程：先问用户要 setup 哪些（CLAUDE.md / skills / hooks），再 subagent 探索代码库，最后给 reviewable proposal。

### `/memory`

列出当前 session 加载了哪些 CLAUDE.md / `CLAUDE.local.md` / rules 文件，可点开编辑。

### `claudeMdExcludes`

```json
// .claude/settings.local.json
{
  "claudeMdExcludes": [
    "**/monorepo/CLAUDE.md",
    "/home/user/monorepo/other-team/.claude/rules/**"
  ]
}
```

monorepo 里跳过其他团队不相关的 CLAUDE.md。可在 user / project / local / managed policy 任一层设置，数组合并。

## Auto memory（v2.1.59+，旁证非主体）

不是 CLAUDE.md，但相关：Claude 自己写的 memory，存 `~/.claude/projects/<project>/memory/`，由 `MEMORY.md` 索引（首 200 行 / 25 KB 加载）。

关闭：`autoMemoryEnabled: false` 或 `CLAUDE_CODE_DISABLE_AUTO_MEMORY=1`。

`autoMemoryDirectory` 可改存储位置（仅接受 user / managed / `--settings` flag，不接受 project / local 设置 —— 因为这俩 file 在项目目录里，clone repo 可能挟持）。

## Compaction 行为

> "Project-root CLAUDE.md survives compaction: after `/compact`, Claude re-reads it from disk and re-injects it into the session. Nested CLAUDE.md files in subdirectories are not re-injected automatically; they reload the next time Claude reads a file in that subdirectory."

—— 主 CLAUDE.md 在 compact 后会重新加载；嵌套的不会，要等 Claude 读对应子目录文件时才重载。

## --add-dir flag

`--add-dir` 给 Claude 额外目录读权限。**默认不加载**这些目录的 CLAUDE.md。如要加载：

```bash
CLAUDE_CODE_ADDITIONAL_DIRECTORIES_CLAUDE_MD=1 claude --add-dir ../shared-config
```

会加载 `CLAUDE.md`、`.claude/CLAUDE.md`、`.claude/rules/*.md`、`CLAUDE.local.md`。`CLAUDE.local.md` 在 `--setting-sources` 排除 `local` 时不加载。

## 调试链（CLAUDE.md 没生效时）

> "If Claude keeps doing something you don't want despite having a rule against it, the file is probably too long and the rule is getting lost. If Claude asks you questions that are answered in CLAUDE.md, the phrasing might be ambiguous."

debug 顺序：
1. 跑 `/memory` 确认主文件确实被加载（不在列表 = Claude 看不到）
2. 检查 location（是否在加载范围）
3. 加 specificity（"用 2 空格" 而不是"格式化代码"）
4. 找冲突指令
5. 加 emphasis（IMPORTANT / YOU MUST）
6. 仍失败 → 改 hook 强制执行

可用 `InstructionsLoaded` hook 记录加载详情，用于调试 path-specific / lazy-loaded 文件。

## 团队 / 组织级 CLAUDE.md（managed policy）

设置流程：
1. 把文件放在 managed policy location（按 OS 不同）
2. 用 MDM / Group Policy / Ansible 推送到所有开发机

managed policy CLAUDE.md vs managed settings 分工：

| 关注点 | 配置在 |
|---|---|
| 阻止特定工具 / 命令 / 文件路径 | `permissions.deny`（settings）|
| 强制 sandbox 隔离 | `sandbox.enabled`（settings）|
| 环境变量 / API provider | `env`（settings）|
| 强制登录方式 / 组织锁 | `forceLoginMethod`, `forceLoginOrgUUID`（settings）|
| 编码风格 / 质量 | managed CLAUDE.md |
| 数据处理 / 合规提醒 | managed CLAUDE.md |
| Claude 行为指引 | managed CLAUDE.md |

> "Settings rules are enforced by the client regardless of what Claude decides to do. CLAUDE.md instructions shape Claude's behavior but are not a hard enforcement layer."

—— settings = 强制；CLAUDE.md = 引导。
