# Reference Map

## External Assets

- Daily report generation skill (borrowed OpenClaw asset):
  `https://openclawmp.cc/asset/s-027065c89db7e63f`
- Xiaohongshu publishing skill (borrowed Agent-Reach OpenClaw skill, includes MCP capability):
  `https://github.com/Panniantong/Agent-Reach`

## Morning Schedule Mapping

- `09:00` Xiaoju check-in
  - existing skill: `checkin/xiaojuchongdian/skill/overall`
- `09:20` AI daily report
  - handled by this skill (merged with frontier IDE/CLI and model updates)

## Migration Checklist

1. Ensure `daily/skill` orchestration directory is present.
2. Ensure existing Xiaoju skill directory is present.
3. Ensure this skill directory is present.
4. Validate OpenClaw asset is accessible.
5. Validate Agent-Reach OpenClaw skill is available.
6. Rebind scheduler to the target times (`09:00`, `09:20`).
