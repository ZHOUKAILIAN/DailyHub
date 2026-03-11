---
name: frontier-changelog
description: Custom skill to gather IDE/CLI changelogs and model updates via search.
---

# Frontier Changelog Tracking Skill

## Purpose

Use this standalone custom skill to autonomously track and pull frontier IDE/CLI updates and major AI model updates.

## IDE/CLI Source Map (Official First)

- Claude Code:
  - `https://github.com/anthropics/claude-code/blob/main/CHANGELOG.md`
  - `https://docs.anthropic.com/en/release-notes/claude-code`
- Codex:
  - `https://developers.openai.com/codex/changelog`
  - `https://github.com/openai/codex/releases`
- Cursor:
  - `https://cursor.com/changelog`
- Gemini CLI:
  - `https://google-gemini.github.io/gemini-cli/docs/releases.html`
  - `https://github.com/google-gemini/gemini-cli/releases`
- Antigravity:
  - `https://antigravity.google/releases`
  - `https://antigravity.google/download`
- OpenCode:
  - `https://opencode.ai/changelog`
  - `https://github.com/anomalyco/opencode/tags`

## Execution Flow

1. **CRITICAL**: Pull frontier IDE/CLI updates in this fixed order, and call `web_search` serially (one tool per search request): Claude Code -> Codex -> Cursor -> Gemini CLI -> Antigravity -> OpenCode. Do not fetch them in parallel or in a batch query.
   - Source priority:
     1) Official release notes/changelog pages
     2) GitHub official org/repo releases or official announcements
     3) Trusted secondary sources only when official sources are unavailable (must mark as non-official)
2. **CRITICAL**: Pull frontier model updates (new releases, major capability changes) **sequentially** using the available search tool.
3. Keep only substantive updates (ignore minor undocumented typos/fixes) and format each clearly.
4. Merge all collected logs into an "AI Frontier Changelog" Markdown report.
5. Return the exact Markdown content of the changelog report in the chat output.

## Output Format

**CRITICAL: The result returned to the user MUST contain the full, substantive content of the changelog.**

Return a human-readable report containing:
1. Status overview (SUCCESS, PARTIAL, NO_UPDATES).
2. Full IDE/CLI Changelog details — for each tool (Claude Code, Codex, Cursor, Gemini CLI, Antigravity, OpenCode):
   - Tool name and version/date
   - Each change item with description
   - At least one source link per tool item (prefer official website or GitHub official repo release page)
3. Full Model Update details:
   - Model name and release/update date
   - Capability changes

## Failure Policy
- If a specific tool/model search fails or yields no substantive updates, skip it and continue processing the others. Simply note "No updates" for that tool in the final report.
