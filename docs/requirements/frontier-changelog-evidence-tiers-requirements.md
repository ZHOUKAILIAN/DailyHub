# Frontier Changelog Evidence Tiers Requirements

## 1. What

本需求为 `routine/ai-morning/skill/frontier-changelog/SKILL.md` 增加一套“多报但不错过”的结果判定规则。

核心变化：
1. 对每个 IDE/CLI 和模型更新都输出结构化判定层级；
2. 区分“确认在窗口内”“疑似在窗口内”“抓到但不在窗口内”“来源不可读”；
3. 最终汇总必须严格基于同一份结构化判定结果生成，避免前文与总结口径不一致。

## 2. Why

当前 skill 可能出现以下问题：
1. 抓取阶段看似发现了更新，但最终总结又写成 no_updates；
2. 某些来源只能抓到导航页、目录页或截断内容，容易把低质量证据误当成真实更新；
3. 为了不漏报，日期只有“天”没有“时分秒”的条目会被纳入候选，但若不分层展示，会与高置信度结果混淆。

因此需要把“发现了什么”和“最终是否纳入窗口播报”统一到一个结构化结果模型里。

## 3. Scope

### In Scope
- 更新 `frontier-changelog` skill 文案，明确证据层级与输出规则。
- 明确每个来源都要给出最新抓到的候选条目、窗口判断、证据质量与来源链接。
- 明确最终 Summary 只能基于结构化判定结果生成。

### Out of Scope
- 不新增新的抓取工具。
- 不改变既有固定来源列表。
- 不要求实现仓库级 parser 或独立执行器。

## 4. Functional Requirements

### FR-001: Structured Verdict Tiers

对每个工具/模型，必须归入以下 4 类之一：
- `confirmed_in_window`
- `likely_in_window`
- `found_but_out_of_window`
- `source_unreadable`

### FR-002: Evidence Quality Disclosure

每个条目必须说明证据质量，至少区分：
- high: 直接命中 changelog/release 正文且有清晰日期/时间
- medium: 命中正文但时间信息不完整，或需要一次可信 fallback
- low: 仅抓到弱证据，最多进入 likely/source_unreadable，不得伪装成 confirmed

### FR-003: Favor Recall Without Hiding Uncertainty

skill 应优先避免漏报：
- 若来源只给日期、不含具体时间，且日期属于昨天或今天，可先纳入候选；
- 但必须显式标记为 `likely_in_window`，除非有足够证据升级为 `confirmed_in_window`。

### FR-004: One Result Model, One Summary

最终 Summary 不得与前文逐项结果矛盾。
Summary 中的已确认更新、疑似更新、窗口外更新、不可读来源，必须分别来自同一份逐项判定结果。

### FR-005: Fallback Rule

固定官方来源优先。
若固定来源可访问但内容明显是导航页、目录页、壳页面或缺少实质更新正文，可使用一次补充 fallback 来提升可读性，但必须保留官方来源作为首要证据引用。

## 5. Acceptance Criteria

1. `frontier-changelog/SKILL.md` 明确列出 4 个 verdict tiers。
2. `SKILL.md` 明确要求输出 evidence quality、latest candidate、window verdict、source link。
3. `SKILL.md` 明确规定最终汇总必须与逐项判定一致。
4. `SKILL.md` 明确日期不完整时的“宽进严出”规则：可纳入候选，但要标注不确定性。
