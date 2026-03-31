---
name: frontier-changelog
description: Track frontier AI IDE/CLI and model updates daily.
---

# Frontier Changelog Tracking

## Goal

Gather the latest updates from frontier AI coding tools and major model releases, and output a full changelog report.

## IDE/CLI Sources

| Tool           | Changelog URL                                                              |
|----------------|---------------------------------------------------------------------------|
| Claude Code    | `https://raw.githubusercontent.com/anthropics/claude-code/main/CHANGELOG.md` |
| Codex          | `https://developers.openai.com/codex/changelog`                           |
| Cursor         | `https://cursor.com/changelog`                                             |
| Gemini CLI     | `https://google-gemini.github.io/gemini-cli/docs/changelogs/`             |
| Antigravity    | `https://antigravity.google/changelog`                                     |
| OpenCode       | `https://opencode.ai/changelog`                                           |

## Model Updates

Search for major AI model releases and capability changes (e.g., new model versions from OpenAI, Anthropic, Google, Meta, etc.) within the time window.

## Time Window

Default: **yesterday 09:00 → today 09:00** (Beijing time, UTC+8).

If a source only provides a date without time, include it if the date is yesterday or today.

## Output

Output the full changelog report directly. For tools/models with no updates in the window, note briefly.

## Failure Policy

If a source fails or has no updates, skip it and continue with the others.
