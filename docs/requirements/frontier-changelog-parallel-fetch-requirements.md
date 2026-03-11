# Frontier Changelog Parallel Fetch Requirements

## 1. What

本需求仅包含一项变更：调整 `routine/ai-morning/skill/frontier-changelog/SKILL.md` 的抓取策略：

1. 对显式 `web_fetch` 链接允许并行抓取；
2. `web_search` 保持顺序执行。
3. IDE/CLI 来源清单按“每个工具仅 1 个官方 changelog 链接”维护，并强制优先抓取该固定列表。

## 2. Why

1. `web_fetch` 对固定 URL 的抓取不存在顺序依赖，串行会拉长任务耗时。
2. `web_search` 仍需顺序执行以维持来源优先级与结果可追溯性。

## 3. Scope

### In Scope

- 更新 `frontier-changelog` skill 的执行说明，明确并行/串行边界。
- 需求与设计文档落地到 `docs/requirements/` 与 `docs/design/`。

### Out of Scope

- 不新增新的抓取工具或执行框架。
- 不改动 `daily-news`、`morning-publish` 的业务行为。

## 4. Functional Requirements

### FR-001: Parallelize Fixed URL Fetches

- `frontier-changelog` 在处理“已给定 URL 的抓取”时，允许并行执行。
- 并行只适用于 `web_fetch` 类型请求，不适用于 `web_search`。
- 固定 URL 列表按以下 6 个链接维护（每个工具仅 1 个）：
  - Claude Code: `https://docs.anthropic.com/en/release-notes/claude-code`
  - Codex: `https://developers.openai.com/codex/changelog`
  - Cursor: `https://cursor.com/changelog`
  - Gemini CLI: `https://google-gemini.github.io/gemini-cli/docs/changelogs/`
  - Antigravity: `https://antigravity.google/changelog`
  - OpenCode: `https://opencode.ai/changelog`
- 执行时必须先抓取以上固定列表，不得自行替换或扩展来源（除非该链接不可访问）。

### FR-002: Keep Search Sequential

- IDE/CLI 与模型更新的 `web_search` 继续顺序执行。
- 结果整理与输出格式不变。

## 5. Acceptance Criteria

1. `routine/ai-morning/skill/frontier-changelog/SKILL.md` 明确写明：`web_fetch` 并行、`web_search` 顺序。
2. `SKILL.md` 的 IDE/CLI 来源清单为每工具 1 个链接，且有“必须先抓固定列表”的约束。
3. Skill 输出格式章节与失败策略保持可用且无冲突。

_Last updated: 2026-03-11_
