# Frontier Changelog Time Window Update Design

## 1. Design Goal

修改 `frontier-changelog` skill 中的 Prompt 提示词规则，将大模型过滤内容的时间段准确设定为“北京时间前一天 09:00 至今天 09:00”，从而解决因按“UTC 自然日”过滤导致前一天下午/夜间更新被漏掉的问题。

## 2. Design Principles

1. **精准的时间边界限定**：通过 Prompt 明确告知模型时间边界（昨天 09:00 到 今天 09:00，当前时区 UTC+8）。
2. **容错性**：考虑到很多官方 Release Notes 或 Changelog 只有日期（如 `Mar 11, 2026`）没有具体时间，Prompt 需指示模型：如果只有日期且日期为昨天或今天，则默认纳入考虑，防漏。
3. **最小化变更**：仅更改时间过滤规则的文案，不影响已有的 web_fetch 并行抓取控制和搜索逻辑。

## 3. Detailed Changes

### 3.1 更改 `routine/ai-morning/skill/frontier-changelog/SKILL.md`

将现有的 `CRITICAL (Time Window)`：
> 4. **CRITICAL (Time Window)**: Only include entries released/updated on the same UTC calendar day as the run date (today, UTC). Ignore older entries even if they are the latest visible on a page.

修改为：
> 4. **CRITICAL (Time Window)**: Only include entries released/updated between **09:00 AM yesterday and 09:00 AM today (Beijing Time, UTC+8)**. 
>    - If the source only provides a date (without a specific time), include it if the date is either yesterday or today to avoid missing updates.
>    - Ignore entries that are definitively older than 09:00 AM yesterday.

修改 Output Format 的条件说明，将 `If same-day (UTC) update exists` 替换为 `If update exists within the target time window (09:00 yesterday to 09:00 today)`。

## 4. Failure Handling

由于主要是纯 Prompt 修改，容错处理依赖于大模型的指令遵循能力。对于只标明日期的更新予以宽容纳入，是降低漏报风险的核心手段，即便偶尔出现重复播报（比如今天报了昨天的，明天又报了一次昨天的）也可接受，优于遗漏。

## 5. Verification Plan

1. 人工/Agent 审查 `routine/ai-morning/skill/frontier-changelog/SKILL.md`，确认改动与设计要求完全一致。
