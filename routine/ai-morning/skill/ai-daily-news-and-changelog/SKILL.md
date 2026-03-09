---
name: ai-daily-news-and-changelog
description: Run the daily morning AI report workflow centered on 09:20 news generation with merged frontier updates. Use when the user asks to generate AI daily news, include substantive IDE/CLI and model updates, write one-file blog PR, send the report, and publish to Xiaohongshu via borrowed Agent-Reach OpenClaw skill (which includes MCP capability) with one retry.
---

# AI Daily News and Changelog Skill

## Purpose

Use this skill to execute the `09:20` morning report pipeline only, where AI daily news and frontier updates are produced in one report.

This skill does not orchestrate other morning tasks. Cross-task sequencing is owned by `daily/skill/SKILL.md`.

## Required Inputs

Provide or confirm the following runtime inputs before execution:

- timezone for schedule alignment (default: `Asia/Shanghai`)
- current date used by the daily report filename
- Blog repository path and daily file path template
- PR target branch and repository
- notification destination for sending generated content
- available Agent-Reach OpenClaw skill entry for Xiaohongshu publishing (includes MCP capability)
- IDE/CLI update sources for Claude Code, Codex, Cursor, OpenCode
- model update sources for frontier models

If any required input is missing, ask for it once and continue after it is provided.

## Execution Flow

### Step 1: Build 09:20 Daily Report (Merged)

1. Invoke the borrowed `daily-intelligence-news` skill from OpenClaw asset: `https://openclawmp.cc/asset/s-027065c89db7e63f`.
2. Pull frontier IDE/CLI updates (Claude Code, Codex, Cursor, OpenCode).
3. Pull frontier model updates (new releases and meaningful capability changes).
4. Keep only substantive updates and format each as:
   - overall summary
   - key change points
5. Merge AI daily news + IDE/CLI updates + model updates into one daily report.
6. Save the report to Blog daily file.
7. Create a PR with exactly one changed report file.
8. Send the report content to the user.
9. Publish the same report to Xiaohongshu through borrowed Agent-Reach OpenClaw skill (includes MCP capability): `https://github.com/Panniantong/Agent-Reach`.
10. If Xiaohongshu publish fails, retry exactly once.

## Failure Policy

- Daily report generation fails: stop downstream publishing and report the reason.
- IDE/CLI or model update retrieval fails: report source-specific errors; do not claim "no updates".
- Blog write or PR fails: report reason and include generated report content.
- Xiaohongshu publish fails twice: report second failure reason and mark partial failure.
- No substantive frontier updates: return `no_updates` for frontier update section, while keeping news content.

## Output Format

Return a case-specific human-readable report with:

1. Report outcome:
   - `SUCCESS`, `PARTIAL`, `FAILED`, or `NO_UPDATES`
2. One-line summary:
   - whether report generation, blog sync, and Xiaohongshu publish completed
3. Key details:
   - report title/date and short summary
   - blog file write result and PR result
   - Xiaohongshu publish result (first try + retry when used)
   - frontier update highlights (IDE/CLI + model)
4. If failed/partial:
   - failed stage and reason
   - suggested next action

Optional: append structured `details` object with report/blog/publish/update fields.

## References

Read [reference-map.md](references/reference-map.md) before execution to get external dependency mapping and migration notes.
