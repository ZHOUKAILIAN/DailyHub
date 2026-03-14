---
name: frontier-changelog
description: Custom skill to gather IDE/CLI changelogs and model updates via search.
---

# Frontier Changelog Tracking Skill

## Purpose

Use this standalone custom skill to autonomously track and pull frontier IDE/CLI updates and major AI model updates.

## IDE/CLI Source Map (One Official Source per Tool)

- Claude Code:
  - `https://raw.githubusercontent.com/anthropics/claude-code/main/CHANGELOG.md`
- Codex:
  - `https://r.jina.ai/http://developers.openai.com/codex/changelog`
- Cursor:
  - `https://cursor.com/changelog`
- Gemini CLI:
  - `https://google-gemini.github.io/gemini-cli/docs/changelogs/`
- Antigravity:
  - `https://r.jina.ai/http://antigravity.google/changelog`
- OpenCode:
  - `https://opencode.ai/changelog`

## Execution Flow

1. Pull frontier IDE/CLI updates in this fixed order: Claude Code -> Codex -> Cursor -> Gemini CLI -> Antigravity -> OpenCode.
   - You MUST fetch from the single fixed URL per tool above first. Do not replace with other links unless that URL is unavailable.
2. Pull frontier model updates (new releases, major capability changes) sequentially using the available search tool.
3. Keep only substantive updates (ignore minor undocumented typos/fixes) and format each clearly.
4. **Time Window (default)**: Use **Beijing window** by default: `yesterday 09:00 -> today 09:00` (Asia/Shanghai, UTC+8).
   - Convert to UTC when filtering source entries.
   - If the source only provides a date (without a specific time), include it if the date is either yesterday or today to avoid missing updates.
   - If caller explicitly provides a custom range (e.g., today UTC, last 7 days), honor the caller range.
5. **Codex scope rule**: Codex source may contain both **Codex CLI** and **Codex app** updates. Include window-matching updates, and clearly label subtype (`Codex CLI` / `Codex app`) instead of silently dropping app entries.
6. If a tool/model has no in-window substantive update, output `no_updates` with a short reason (e.g., "no in-window update found").
7. Merge all collected logs into an "AI Frontier Changelog" Markdown report.
8. **Output the EXACT FULL Markdown content of the changelog report directly to the user. Do not ask the user if they want the full text or a summary.**

## Output Format

**The result returned to the user MUST contain the full, substantive content of the changelog. Do not ask the user if they want a summary or the full content - always output the full content directly.**

Return a human-readable report containing:
1. Status overview (SUCCESS, PARTIAL, NO_UPDATES).
2. Full IDE/CLI Changelog details — for each tool (Claude Code, Codex, Cursor, Gemini CLI, Antigravity, OpenCode):
   - If in-window update exists: tool name + version/date + change items + at least one source link.
   - For Codex, annotate subtype when applicable (`Codex CLI` / `Codex app`).
   - If no in-window update exists: output `no_updates` with a short reason.
3. Full Model Update details:
   - If in-window update exists: model name + release/update date + capability changes.
   - If no in-window update exists: output `no_updates` with a short reason.

## Failure Policy
- If a specific tool/model search fails or yields no substantive updates, skip it and continue processing the others. Simply note "No updates" for that tool in the final report.
