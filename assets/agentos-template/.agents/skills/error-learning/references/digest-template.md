---
digest_id: NNN
date: YYYY-MM-DD
covers_errors: [list of error IDs]
error_count: N
---

# Error Digest #NNN

## Pattern: (一句话模式名)
- **规则**:一句话 do / don't
- **做什么**:遇到时的可执行动作
- **覆盖**:错误 ID 列表

(每 pattern 占 4 行;最多 ~5 个 pattern)

## 统计
- digested: N 条
- 抽出规则: M 条
- 压缩比: N → M

---

**硬约束**:整个 digest ≤50 行。

**抽象层级**:模式级输出 —— 代码标识符不该出现,除非是跨案例通用词(JWT / bcrypt / money-path / 守恒律 等协议名 / 算法名 / 项目级钱路概念)。

**禁**:百分比段 / N=1 N=2 计数交叉 / family / surface / sub-trigger 元评论。
