---
name: morning-orchestrator
description: Single orchestration entry for the morning routine only. Orchestrates all morning tasks in order using sub-agents for memory efficiency.
---

# Morning Orchestrator Skill

## Purpose

This is the **single entry point** for the full morning automation routine.
It defines what tasks run, in what order, and delegates each to a dedicated sub-agent.

Do not implement task logic here. This skill only orchestrates — each task's execution
details live in its own skill file (linked below).

## Responsibility Boundary

- This skill owns orchestration only: sequence, optional switches, failure policy, and merged output.
- `checkin/*` and `routine/*` sub-skills own task execution only.
- Do not duplicate task logic across sub-skills.

---

## Morning Task Schedule

晨间任务清单。新增任务时，在下表添加一行，并在 Execution Flow 和 Failure Policy 中补充对应步骤。

| Order | Task               | Skill                       | Status   |
| ----- | ------------------ | --------------------------- | -------- |
| 1     | 小桔充电签到       | xiaoju-overall              | existing |
| 2     | AI 日报 + 前沿更新 | ai-daily-news-and-changelog | existing |

---

## Sub-Agent Execution Model

**To conserve memory and prevent context overflow, you MUST launch a brand-new sub-agent for every step.**

Rules:

1. **Never execute a checkin or routine skill directly in the main agent context.**
2. For each step, start a fresh sub-agent and instruct it to invoke the target skill.
3. Wait for the sub-agent to finish before proceeding.
4. **Do not batch replies until all steps finish.** Each step must be reported immediately after completion.
5. The fixed cycle for each step is: launch sub-agent -> wait for completion -> send standalone step report -> auto-start next step.
6. After Step 1 report is sent, automatically proceed to Step 2 without waiting for user confirmation.
7. After Step 2 report is sent, immediately send one final global summary message.

---

## Execution Flow

Tasks run in the order defined in the Morning Task Schedule table above. Execute each step by launching a sub-agent.

### Step 1 — Xiaoju Charging Check-in (Order 1)

Launch a sub-agent to invoke skill: `xiaoju-overall`
→ See: [`checkin/xiaojuchongdian/skill/overall/SKILL.md`](../../checkin/xiaojuchongdian/skill/overall/SKILL.md)

After sub-agent completes:

- Send `Step 1 Report` as a standalone message containing:
  - Step status (`SUCCESS` / `FAILED`)
  - one-line summary
  - the full detailed result returned by the Step 1 sub-agent
  - final line (required): `接下来将开始执行 Step 2 (AI 日报 + 前沿更新)...`
- Once the message is sent, auto-start Step 2 immediately.
- Do not pause for additional user input.

### Step 2 — AI Daily Report (Order 2)

Launch a sub-agent to invoke skill: `ai-daily-news-and-changelog`
→ See: [`routine/ai-morning/skill/ai-daily-news-and-changelog/SKILL.md`](../../routine/ai-morning/skill/ai-daily-news-and-changelog/SKILL.md)

After sub-agent completes:

- Send `Step 2 Report` as a standalone message containing:
  - Step status (`SUCCESS` / `FAILED` / `PARTIAL`)
  - one-line summary
  - the full detailed result returned by the Step 2 sub-agent
- Immediately after Step 2 report, send `Final Global Summary`.

---

## Failure Policy

| Step                | On failure                                                      |
| ------------------- | --------------------------------------------------------------- |
| Step 1 Check-in     | Report failure reason to user; continue to Step 2               |
| Step 2 Daily Report | Report failure reason to user; mark overall as `partial_failed` |
| Step Report Delivery | Retry the report message once; if still failed, record `report_send_failed` and continue |

---

## Output Format

This orchestration MUST produce three separate messages in order:

1. **Message A: Step 1 Report**
   - header: `Step 1 Completed - Xiaoju Charging Check-in`
   - Step 1 status + one-line summary
   - full Step 1 detailed result
   - required trailing line: `接下来将开始执行 Step 2 (AI 日报 + 前沿更新)...`
2. **Message B: Step 2 Report**
   - header: `Step 2 Completed - AI Daily Report`
   - Step 2 status + one-line summary
   - full Step 2 detailed result
3. **Message C: Final Global Summary**
   - overall status:
     - `SUCCESS` when all steps complete
     - `PARTIAL` when some steps succeed and others fail
     - `FAILED` when all steps fail
   - one-line overall summary
   - step-by-step outcome list (Step 1 / Step 2)
   - for `PARTIAL` or `FAILED`: failed step(s), reason, suggested next action

---

## How to Add a New Task

1. Add a row to the Morning Task Schedule table above with the next Order number
2. If the task has no skill yet: create a vertical skill directory first (e.g. `checkin/<platform>/skill/` or `routine/<name>/skill/`)
3. Add a step to the **Execution Flow** section above
4. Add a row to the **Failure Policy** table above
