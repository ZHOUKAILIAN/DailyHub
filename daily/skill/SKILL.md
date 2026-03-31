---
name: morning-orchestrator
description: DailyHub daily task scheduler. Each row is an independent skill triggered by time.
---

# DailyHub — Daily Schedule

## Cron Registry

| Time  | Skill Name           | Goal                                                  |
|-------|----------------------|-------------------------------------------------------|
| 09:00 | xiaoju-overall       | Complete Xiaoju Charging daily check-in (idempotent)  |
| 09:25 | frontier-changelog   | Summarize AI IDE/CLI and model updates in last 24h    |
| 09:30 | personal-market-brief| Three-asset snapshot: CSI300, HK dividend, gold       |

## Installed Skills

| Skill Name           | Purpose                                              |
|----------------------|------------------------------------------------------|
| self-optimize        | Manage skill lifecycle — create, fix, and improve skills |

## Rules

- This file is a registry only — no execution logic.
- Each row maps to an independent skill, referenced by **skill name**.
- To add a new task: build the skill → add one row here.
