# Morning Routines Handover

## Goal

Record daily morning automation in-repo so the workflow can be restored on a new server without repeating manual explanations.

## Task Timeline

| Time | Task | Current Strategy |
|------|------|------------------|
| 09:00 | Xiaoju check-in | status check + sign + record verification |
| 09:20 | AI daily report | generate report, merge frontier IDE/CLI + model updates, write blog daily file, one-file PR, send content, publish to Xiaohongshu |

## Skill Mapping

- Orchestration entry uses:
  - `daily/skill/SKILL.md`
- Task 1 (`09:00`) uses existing skill:
  - `checkin/xiaojuchongdian/skill/overall`
- Task 2 (`09:20`) uses:
  - `routine/ai-morning/skill/ai-daily-news-and-changelog`

## External Dependencies

- Daily report skill asset:
  `https://openclawmp.cc/asset/s-027065c89db7e63f`
- Xiaohongshu publishing skill (Agent-Reach OpenClaw skill, includes MCP capability):
  `https://github.com/Panniantong/Agent-Reach`
- Note: both links are borrowed external capabilities (not newly implemented in this repository).

## Delivery Expectations

### 09:00 Xiaoju Check-in

- success: send check-in result
- failure: send reason only; troubleshooting waits for manual decision

### 09:20 AI Daily Report

- generate by borrowed `daily-intelligence-news` skill asset (`https://openclawmp.cc/asset/s-027065c89db7e63f`)
- include frontier IDE/CLI updates (Claude Code / Codex / Cursor / OpenCode)
- include frontier model updates (new model releases and meaningful changes)
- keep only substantive update entries (overview + key points)
- write blog daily file and open PR
- PR must include report file only
- send report content to user
- publish to Xiaohongshu via borrowed Agent-Reach OpenClaw skill (includes MCP capability) (`https://github.com/Panniantong/Agent-Reach`), retry once on failure

## Migration Notes

When moving to a new server, restore in this order:

1. pull this repository
2. restore runtime secrets/environment outside git
3. verify external links above are reachable
4. verify all skill paths exist (`daily`, `checkin`, `ai-daily`)
5. rebind scheduler to fixed times (`09:00`, `09:20`)

_Last updated: 2026-03-09_
