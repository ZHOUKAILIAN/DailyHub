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

1. **CRITICAL**: Pull frontier IDE/CLI updates in this fixed order: Claude Code -> Codex -> Cursor -> Gemini CLI -> Antigravity -> OpenCode.
   - **CRITICAL**: You MUST fetch from the single fixed URL per tool above first. Do not replace with other links unless that URL is unavailable.
   - For the fixed URLs listed in this skill, use `web_fetch` in parallel to collect raw changelog pages.
   - For discovery/verification queries, keep `web_search` serial (one tool per search request). Do not batch `web_search` queries.
   - Source priority:
     1) Official release notes/changelog pages
     2) GitHub official org/repo releases or official announcements
     3) Trusted secondary sources only when official sources are unavailable (must mark as non-official)
   - **Codex fallback rule (mandatory)**: if Codex changelog fetch returns navigation shell / TOC-like content without concrete release entries (version + date + bullet changes), immediately fetch GitHub official Codex release/compare pages and use them to fill missing details. In fallback mode, still keep `Codex CLI` and `Codex app` as separate sub-sections and mark each with its own source link.
2. **CRITICAL**: Pull frontier model updates (new releases, major capability changes) **sequentially** using the available search tool.
3. Keep only substantive updates (ignore minor undocumented typos/fixes) and format each clearly.
4. **CRITICAL (Time Window, default)**: Use **Beijing window** by default: `昨天 09:00 -> 今天 09:00` (Asia/Shanghai).  
   - Convert to UTC when filtering source entries.
   - If caller explicitly provides a custom range (e.g., today UTC, last 7 days), honor the caller range.
5. **Codex scope rule (mandatory split)**: Codex source may contain both **Codex CLI** and **Codex app** updates. You MUST always output two separate sub-sections under Codex: `Codex CLI` and `Codex app`.
   - If one subtype has in-window updates, include details for that subtype.
   - If one subtype has no in-window update, still output `no_updates` for that subtype with a short reason.
   - Never merge both into one undifferentiated "Codex" block.
6. If a tool/model has no in-window substantive update, output `no_updates` with a short reason (e.g., "no in-window update found").
7. **Codex parsing quality gate**: never claim Codex subtype updates from menu/TOC text alone. Require at least one concrete evidence item per subtype (version tag, dated release note, compare diff, or explicit changelog bullet). If evidence is missing for one subtype, output `no_updates` for that subtype and explain that Codex changelog content was non-structured in this run.
8. Merge all collected logs into an "AI Frontier Changelog" Markdown report.
9. Return the exact Markdown content of the changelog report in the chat output.

## Output Format

**CRITICAL: The result returned to the user MUST contain the full, substantive content of the changelog.**

Return a human-readable report containing:
1. Status overview (SUCCESS, PARTIAL, NO_UPDATES).
2. Full IDE/CLI Changelog details — for each tool (Claude Code, Codex, Cursor, Gemini CLI, Antigravity, OpenCode):
   - If in-window update exists: tool name + version/date + change items + at least one source link.
   - For Codex, ALWAYS render two fixed sub-sections:
     - `Codex CLI`: details or `no_updates`
     - `Codex app`: details or `no_updates`
   - If no in-window update exists: output `no_updates` with a short reason.
3. Full Model Update details:
   - If in-window update exists: model name + release/update date + capability changes.
   - If no in-window update exists: output `no_updates` with a short reason.

## Failure Policy
- If a specific tool/model search fails or yields no substantive updates, skip it and continue processing the others. Simply note "No updates" for that tool in the final report.
