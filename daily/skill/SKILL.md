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

| Order | Task             | Skill                  | Status   |
|-------|------------------|------------------------|----------|
| 1     | 小桔充电签到      | xiaoju-overall         | existing |
| 2     | AI 日报 + 前沿更新 | ai-daily-news-and-changelog | existing |

---

## Sub-Agent Execution Model

**To conserve memory and prevent context overflow, you MUST launch a brand-new sub-agent for every step.**

Rules:
1. **Never execute a checkin or routine skill directly in the main agent context.**
2. For each step, start a fresh sub-agent and instruct it to invoke the target skill.
3. Wait for the sub-agent to finish before proceeding.
4. After the sub-agent returns, **immediately forward its full detailed result as a standalone message to the user**, then start the next sub-agent.
5. Continue sequentially through all steps until all tasks are complete.

---

## Execution Flow

Tasks run in the order defined in the Morning Task Schedule table above. Execute each step by launching a sub-agent.

### Step 1 — Xiaoju Charging Check-in (Order 1)

Launch a sub-agent to invoke skill: `xiaoju-overall`
→ See: [`checkin/xiaojuchongdian/skill/overall/SKILL.md`](../../checkin/xiaojuchongdian/skill/overall/SKILL.md)

After sub-agent completes:
- Forward the sub-agent's full detailed result to the user as a standalone message.
- Then proceed to Step 2.

### Step 2 — AI Daily Report (Order 2)

Launch a sub-agent to invoke skill: `ai-daily-news-and-changelog`
→ See: [`routine/ai-morning/skill/ai-daily-news-and-changelog/SKILL.md`](../../routine/ai-morning/skill/ai-daily-news-and-changelog/SKILL.md)

After sub-agent completes:
- Forward the sub-agent's full detailed result to the user as a standalone message.

---

## Failure Policy

| Step               | On failure                                                               |
|--------------------|--------------------------------------------------------------------------|
| Step 1 Check-in    | Report failure reason to user; continue to Step 2                        |
| Step 2 Daily Report| Report failure reason to user; mark overall as `partial_failed`          |

---

## Output Format

After all sub-agents have completed, return a final orchestration summary with:

1. Overall morning status:
   - `SUCCESS` when all steps complete
   - `PARTIAL` when some steps succeed and others fail
   - `FAILED` when all steps fail
2. One-line summary of overall execution result
3. Step-by-step outcome list (one line per step, referencing each sub-agent's reported result)
4. If failed/partial:
   - failed step(s) and reason
   - suggested next action

Note: Each sub-agent's full detailed result has already been forwarded to the user individually. The final summary here is for overall status only.

---

## How to Add a New Task

1. Add a row to the Morning Task Schedule table above with the next Order number
2. If the task has no skill yet: create a vertical skill directory first (e.g. `checkin/<platform>/skill/` or `routine/<name>/skill/`)
3. Add a step to the **Execution Flow** section above
4. Add a row to the **Failure Policy** table above
