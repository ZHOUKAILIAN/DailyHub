---
name: morning-orchestrator
description: Top-level entry point for DailyHub. Defines all scheduled tasks as a cron registry. Each row is an independent skill invocation — no logic lives here.
---

# DailyHub — Daily Schedule

## Cron Registry

| Time  | Task                     | Skill                                                                               |
|-------|--------------------------|-------------------------------------------------------------------------------------|
| 09:00 | Xiaoju Charging Check-in | [xiaoju-overall](../../checkin/xiaojuchongdian/skill/overall/SKILL.md)              |
| 09:20 | AI Daily News            | [daily-news](../../routine/ai-morning/skill/daily-news/SKILL.md)                   |
| 09:25 | Frontier Changelog       | [frontier-changelog](../../routine/ai-morning/skill/frontier-changelog/SKILL.md)   |
| 09:30 | Morning Publish          | [morning-publish](../../routine/ai-morning/skill/morning-publish/SKILL.md)         |

## Rules

- **This file is a registry only.** No execution logic, no failure handling — those belong in each skill.
- Each row maps to exactly one independent vertical skill.
- To register all jobs: read this table and create one cron job per row using the `Time` and `Skill` columns.

## Adding a New Task

1. Build the vertical skill under `checkin/<platform>/skill/` or `routine/<name>/skill/`.
2. Add one row here: `Time | Task name | relative path to SKILL.md`.
3. Re-run this skill to update the schedule.
