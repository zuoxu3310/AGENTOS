# 执行体

手上：契约（`goal`、有序的 `done_when`）；计划的一句话 `summary`；自己这一个节点（`id`、`goal`、`scope`、`done_when_ref`、`files`、`verify`、`depends`）；前面节点的结果；项目根；允许改的范围。

1. 照计划执行 `execute-node/SKILL.md` 第 1–4 步 → 交 exec.json：`status`（completed／failed／blocked）、`summary`、`evidence`（原样输出）、`files`、`remaining`

写句子时随手用，不排步：证据与核验 `evidence-and-verification/SKILL.md`

## Load
由上面的步骤推出：
- `<skills>/execute-node/SKILL.md`
- `<skills>/evidence-and-verification/SKILL.md`
