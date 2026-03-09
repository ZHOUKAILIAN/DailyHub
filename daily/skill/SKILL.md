---
name: morning-orchestrator
description: 晨间编排入口。执行此 skill 后，为下表每个任务注册一个 cron 定时任务，到点自动调用对应 skill。
---

# Morning Orchestrator Skill

## 任务清单

| Time  | Task             | Skill                       |
|-------|------------------|-----------------------------|
| 09:00 | 小桔充电签到      | xiaoju-overall              |
| 09:20 | AI 日报 + 前沿更新 | ai-daily-news-and-changelog |

## 执行说明

读取上表，为每一行注册一个 cron 定时任务：
- 时间取 `Time` 列
- 到点后调用 `Skill` 列对应的 skill
- 所有定时任务注册完成后，向用户汇报注册结果

## 新增任务

在上表添加一行（Time + Task + Skill），重新执行此 skill 即可更新定时计划。
