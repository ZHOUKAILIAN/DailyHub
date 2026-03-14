# Frontier Changelog Time Window Update Requirements

## 1. What

本需求旨在调整 `routine/ai-morning/skill/frontier-changelog/SKILL.md` 中的时间窗口策略：
将抓取和过滤的目标时间范围，从“当前 UTC 自然日（当天）”修改为“北京时间（UTC+8）前一天上午 09:00 到今天上午 09:00”。

## 2. Why

目前的策略是仅抓取当天的更新。由于 changelog 播报的执行时间是每天早上 9 点，而很多海外工具的更新（如 Cursor, Claude 等）通常发生在北京时间的下午或夜间，这导致第二天早上 9 点执行任务时，前一天下午到夜间的更新由于不属于“今天”，从而被遗漏。
通过将时间范围明确定义为“前一天 09:00 至今天 09:00”，可以无缝衔接每日的播报，确保没有任何更新被漏掉。

## 3. Scope

### In Scope
- 更新 `frontier-changelog` skill 的执行说明 `SKILL.md`，修改时间过滤规则。
- 明确指定以北京时间（UTC+8）为基准的时间窗口。

### Out of Scope
- 不改变现有的并行抓取与串行搜索逻辑。
- 不改变输出报告的格式和结构。
- 不改变来源列表。

## 4. Functional Requirements

### FR-001: 调整时间窗口为 24 小时滚动窗口
- 在提取更新记录时，大模型需要判断记录的发布/更新时间。
- 包含标准：发布时间必须在**北京时间（UTC+8）前一天 09:00 到今天 09:00**之间。
- 如果记录时间在这 24 小时窗口内，予以保留；否则忽略。

### FR-002: 兼容时区转换
- 由于部分网页来源的时区可能不是 UTC+8（如 EST 或 PST），提示词中必须要求大模型在比较时间前，将原始时区正确转换为或者对齐到北京时间的判断基准。
- 如果更新只精确到“日”（没有具体几点），且该日期是昨天或今天，则应默认包含以防遗漏，但需在报告中合理呈现。

## 5. Acceptance Criteria

1. `routine/ai-morning/skill/frontier-changelog/SKILL.md` 中 `CRITICAL (Time Window)` 规则明确改为“前一天 09:00 到今天 09:00 (UTC+8)”。
2. `SKILL.md` 中的输出格式条件从“若存在当天 (same-day UTC) 更新”改为“若存在该 24 小时窗口内的更新”。
3. 需求和设计文档在 `docs/` 目录下正确归档。
