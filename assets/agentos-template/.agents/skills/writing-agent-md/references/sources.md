# 官方文档来源

本 skill 引用的所有官方文档，便于遇到争议或 spec 漂移时查证。

拉取时间：**2026-05-08**（首次创建本 skill 时）。

如果发现以下 URL 内容跟 references/ 里的摘抄不一致，**信任最新拉取**，并更新本 skill 的 references/。

---

## Anthropic CLAUDE.md（主要）

| 文档 | URL |
|---|---|
| **How Claude remembers your project**（CLAUDE.md 主页）| https://code.claude.com/docs/en/memory |
| **Best practices for Claude Code**（含 CLAUDE.md 专章）| https://code.claude.com/docs/en/best-practices |

⚠️ 注：`docs.claude.com/en/...` 旧 URL 在 2026 年初已 302 重定向到 `platform.claude.com/docs/en/...` 或 `code.claude.com/docs/en/...`。本 skill 使用最终目标 URL。

## Anthropic Skills（旁证，不在本 skill 主体范围但相关）

| 文档 | URL |
|---|---|
| Skill authoring best practices | https://platform.claude.com/docs/en/agents-and-tools/agent-skills/best-practices |
| Skills overview | https://platform.claude.com/docs/en/agents-and-tools/agent-skills/overview |
| Equipping agents for the real world with Agent Skills | https://www.anthropic.com/engineering/equipping-agents-for-the-real-world-with-agent-skills |
| Skills in Claude Code | https://code.claude.com/docs/en/skills |
| The Complete Guide to Building Skills for Claude (PDF) | https://resources.anthropic.com/hubfs/The-Complete-Guide-to-Building-Skill-for-Claude.pdf |
| skill-creator 范例 SKILL.md | https://github.com/anthropics/skills/blob/main/skills/skill-creator/SKILL.md |

—— 这些是 SKILL.md 撰写规范，**不是 CLAUDE.md 撰写规范**。本 skill 主体不引用，但项目内部 SKILL.md 文件本身的设计需对照这些。

## OpenAI / AGENTS.md（主要）

| 文档 | URL |
|---|---|
| **agents.md 官方主页**（Linux Foundation / Agentic AI Foundation）| https://agents.md/ |
| **agentsmd/agents.md** spec 仓库 | https://github.com/agentsmd/agents.md |
| **Custom instructions with AGENTS.md** —— Codex 文档 | https://developers.openai.com/codex/guides/agents-md |
| **Best practices** —— Codex 文档 | https://developers.openai.com/codex/learn/best-practices |
| **OpenAI 自家 AGENTS.md 范例**（codex 仓库）| https://github.com/openai/codex/blob/main/AGENTS.md |

## OpenAI Skills（旁证，跨厂商互通）

| 文档 | URL |
|---|---|
| Codex Agent Skills | https://developers.openai.com/codex/skills |

—— OpenAI Codex 也用 SKILL.md，与 Anthropic 格式高度兼容。**但 AGENTS.md 与 CLAUDE.md 是独立的入口文件，不能合并**。

---

## 已知 spec 变更点（warning）

记录 spec 漂移可能踩坑的地方，便于触发 skill 时优先核对：

- **CLAUDE.md 长度建议**：旧版 best-practices 给的是 300 行；2026-05-08 拉取的 `code.claude.com/docs/en/memory` 改成 200 行（adherence 实测证据驱动）。本 skill 取**当前 200 行**。
- **`docs.claude.com` URL 重定向**：所有 `docs.claude.com/en/...` 已重定向到 `platform.claude.com/docs/en/...` 或 `code.claude.com/docs/en/...`。
- **AGENTS.md `project_doc_max_bytes`**：默认 32 KiB，可在 Codex config 调整。本 skill 默认 32 KiB。
- **AGENTS.md 维护方**：早期由 OpenAI 主导，2025 年下半年起转交给 **Linux Foundation 旗下 Agentic AI Foundation**。本 skill 引用最新 stewardship 信息。
- **Claude Code 不读 AGENTS.md**：长期容易踩的坑，需用 `@AGENTS.md` import 或 symlink 解决。

---

## 维护建议

- **半年一审**：本 skill 触发频次较低（agent doc 改动稀）。建议每 6 个月对照一次 source URL 看 spec 是否变更。
- **触发即审**：每次本 skill 被调用时，可顺手 spot-check 1-2 个原话条款，看是否需更新。
- **新 source 加入**：发现新的官方 source（如 Cursor / Aider 自己的 AGENTS.md 写法补充文档），加入本表。
