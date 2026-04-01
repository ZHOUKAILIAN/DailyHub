# Frontier Changelog Evidence Tiers Design

## 1. Design Goal

把 `frontier-changelog` 从“边抓边口头归纳”的松散模式，升级为“先逐项判定，再统一汇总”的稳定模式，从而实现：
- 多报但不错过；
- 不把弱证据误报成 confirmed；
- 最终汇总不再和前文打架。

## 2. Design Principles

1. **Recall-first**：优先不漏报，但必须暴露不确定性。
2. **Single source of truth**：先形成逐项 verdict，再生成最终 summary。
3. **Official-source-first**：固定官方 changelog 仍是第一来源。
4. **Evidence-aware**：正文 > 导航页/目录页；精确时间 > 仅日期；官方正文 > fallback 摘要。

## 3. Verdict Model

对每个工具/模型，先形成结构化判定：
- latest_candidate
- source_link
- evidence_quality (`high` / `medium` / `low`)
- window_verdict (`confirmed_in_window` / `likely_in_window` / `found_but_out_of_window` / `source_unreadable`)
- short_reason

## 4. Decision Rules

### 4.1 confirmed_in_window

满足以下条件之一：
- 官方或可信 fallback 正文中存在实质更新条目，且时间可明确落在窗口内；
- 或虽无具体时间，但正文日期与窗口匹配，且页面上下文足够清晰，不是导航/目录文本。

### 4.2 likely_in_window

适用于：
- 发现了高相关更新正文；
- 日期信息不完整、时区不完整、或页面抽取质量一般；
- 为了避免漏报，先纳入候选，但不能提升为 confirmed。

### 4.3 found_but_out_of_window

适用于：
- 确实抓到了最近更新；
- 但能判断该更新明确早于目标窗口。

### 4.4 source_unreadable

适用于：
- 官方源可访问，但只提取到导航、目录、壳页面、营销文案或截断内容；
- 或搜索/fetch 失败，导致无法得到可判定正文。

## 5. Report Assembly

### Phase A: Fetch
- 固定 URL 的 `web_fetch` 可并行。

### Phase B: Per-source Verdict
- 逐个来源形成 verdict。
- 如官方页面仅为导航页，可补一次 fallback，但不能抹掉官方来源地位。

### Phase C: Final Summary
- Confirmed updates：仅汇总 `confirmed_in_window`
- Likely updates：单列 `likely_in_window`
- Out-of-window findings：单列 `found_but_out_of_window`
- Unreadable/failed sources：单列 `source_unreadable`

这样最终总结与逐项结果天然一致。

## 6. Verification Plan

1. 人工检查 `SKILL.md` 是否包含 4 个 verdict tiers。
2. 人工检查输出规范是否要求 latest candidate / evidence quality / source link / short reason。
3. 人工检查最终 summary 是否被约束为基于同一套 verdict 结果生成。
