---
name: morning-orchestrator
description: Single orchestration entry for the morning routine only. Orchestrates 09:00 check-in and 09:20 AI daily report.
---

# Morning Orchestrator Skill

## Purpose

This is the **single entry point** for the full morning automation routine.
It defines what tasks run, in what order, and delegates each to the responsible skill.

Do not implement task logic here. This skill only orchestrates — each task's execution
details live in its own skill file (linked below).

## Responsibility Boundary

- This skill owns orchestration only: sequence, optional switches, failure policy, and merged output.
- `checkin/*` and `routine/*` sub-skills own task execution only.
- Do not duplicate task logic across sub-skills.

---

## Morning Task Schedule

→ See: [`morning-task-schedule.md`](./morning-task-schedule.md)

This is the authoritative list of all morning tasks. To add a new task, edit that file first,
then add the corresponding step below.

---

## Execution Flow

### Step 1 - 09:00 Xiaoju Charging Check-in

Invoke skill: `xiaoju-overall`
→ See: [`checkin/xiaojuchongdian/skill/overall/SKILL.md`](../../checkin/xiaojuchongdian/skill/overall/SKILL.md)

Wait for result before proceeding.

### Step 2 - 09:20 AI Daily Report

Invoke skill: `ai-daily-news-and-changelog`
→ See: [`routine/ai-morning/skill/ai-daily-news-and-changelog/SKILL.md`](../../routine/ai-morning/skill/ai-daily-news-and-changelog/SKILL.md)

---

## Failure Policy

| Step        | On failure                                               |
|-------------|----------------------------------------------------------|
| 09:00 Check-in  | Report failure reason; continue to Step 2                |
| 09:20 Daily Report | Report failure reason; mark overall as `partial_failed`  |

---

## Output Format

Return a case-specific human-readable orchestration summary with:

1. Overall morning status:
   - `SUCCESS` when both steps complete
   - `PARTIAL` when check-in succeeds but daily report fails (or vice versa)
   - `FAILED` when both steps fail
2. One-line summary:
   - overall execution result for `09:00` and `09:20`
3. Step-by-step details:
   - `09:00` check-in outcome (from `xiaoju-overall`)
   - `09:20` daily-report outcome (from `ai-daily-news-and-changelog`)
4. If failed/partial:
   - failed step(s)
   - suggested next action

Optional: append structured `details` object with `checkin` and `daily_report`.

---

## How to Add a New Task

1. Add a row to [`morning-task-schedule.md`](./morning-task-schedule.md)
2. If the task has no skill yet: create a vertical skill directory first (e.g. `checkin/<platform>/skill/` or `routine/<name>/skill/`)
3. Add a step to the **Execution Flow** section above
4. Add a row to the **Failure Policy** table above
