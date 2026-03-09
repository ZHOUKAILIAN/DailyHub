---
name: morning-orchestrator
description: Morning automation entry point. Registers one cron job per task in the schedule table. Each job fires at its specified time and invokes the corresponding skill.
---

# Morning Orchestrator Skill

## Task Schedule

| Time  | Task                        | Skill                                                                                                                                              |
|-------|-----------------------------|----------------------------------------------------------------------------------------------------------------------------------------------------|
| 09:00 | Xiaoju Charging Check-in    | [xiaoju-overall](../../checkin/xiaojuchongdian/skill/overall/SKILL.md)                                                                             |
| 09:20 | AI Daily Report             | [ai-daily-news-and-changelog](../../routine/ai-morning/skill/ai-daily-news-and-changelog/SKILL.md)                                                 |

## Execution

Read the table above and register one cron job for each row:
- Use the `Time` column as the schedule.
- Invoke the skill in the `Skill` column when the job fires.
- Report all registered jobs to the user after setup is complete.

## Adding a New Task

Add a row to the table (Time + Task + Skill) and re-run this skill to update the schedule.
