# Frontier Changelog Parallel Fetch Design

## 1. Design Goal

在不改变 `frontier-changelog` 输出结构与来源优先级策略的前提下，缩短抓取阶段耗时：

1. 固定来源 URL 抓取改为并行。
2. 语义检索与更新判定仍按顺序执行。

## 2. Design Principles

1. **最小改动**：只修改 Skill 级执行策略说明，不引入新组件。
2. **边界清晰**：并行仅限 `web_fetch`；`web_search` 串行不变。
3. **结果一致**：输出字段、来源优先级、失败策略保持兼容。
4. **固定来源约束**：IDE/CLI 仅维护每工具 1 个官方 changelog URL，执行时先抓固定列表。

## 3. Execution Model

### Phase A: URL Fetch (Parallel)

- 输入：Skill 内固定 URL 列表（每个 IDE/CLI 仅 1 个官方 changelog URL）。
- 执行：按产品分组并行发起 `web_fetch` 请求。
- 目标：尽快获得候选原始页面内容。

### Phase B: Search & Validation (Sequential)

- 输入：Phase A 的抓取结果 + 必要补充查询。
- 执行：对每个工具、模型依次执行 `web_search`（如需要），并按来源优先级筛选。
- 目标：保持结果可审计性与优先级一致性。

### Phase C: Report Assembly

- 合并 IDE/CLI 与模型更新结果。
- 输出格式沿用现有 `Output Format` 约束。

## 4. Failure Handling

1. 某个 `web_fetch` 并行分支失败：记录该工具 “No updates” 或失败说明，不阻断其他分支。
2. 某个 `web_search` 顺序步骤失败：跳过该条继续后续项。
3. 若全部来源均不可用：返回 `NO_UPDATES` 并说明原因。
4. 固定 URL 可访问但无更新：标记为 “No updates”，不改用其他冗余来源。

## 5. Verification Plan

1. 文本校验：`frontier-changelog/SKILL.md` 必须包含并行/串行边界描述。
2. 来源校验：`SKILL.md` 中每个 IDE/CLI 只保留 1 个固定官方链接，并声明必须先抓该列表。
3. 兼容校验：`Output Format` 与 `Failure Policy` 章节仍存在且结构未破坏。

_Last updated: 2026-03-11_
