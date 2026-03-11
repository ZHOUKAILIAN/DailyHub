---
name: ai-daily-news-and-changelog
description: Deprecated merged pipeline. Kept as archive-only alias; do not use for new runs.
---

# AI Daily News and Changelog Skill (Deprecated)

## Status

This skill is deprecated and kept only for historical compatibility.

Do not run the old merged pipeline anymore. Use the split workflow below.

## Replacement Workflow

1. Run `daily-news` to get AI daily news content.  
   Path: `routine/ai-morning/skill/daily-news/SKILL.md`
2. Run `frontier-changelog` to get IDE/CLI + model updates.  
   Path: `routine/ai-morning/skill/frontier-changelog/SKILL.md`
3. Run `morning-publish` to merge and distribute the final content.  
   Path: `routine/ai-morning/skill/morning-publish/SKILL.md`

Dependency direction is fixed:

`daily-news` + `frontier-changelog` -> `morning-publish`

## Notes

- This deprecated skill must not introduce new execution logic.
- This deprecated skill must not require external URL-based assets.
- If invoked accidentally, return a redirect message to the replacement workflow.

## Output Format

Return a short human-readable response:
1. Status: `DEPRECATED`
2. Message: use split skills (`daily-news`, `frontier-changelog`, `morning-publish`)
3. Next action: run the three skills in order
