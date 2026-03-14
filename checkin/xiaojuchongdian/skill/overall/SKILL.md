---
name: xiaoju-overall
description: Orchestrate Xiaoju Charging daily check-in end-to-end, including auth readiness check, fallback to get-params, and final run verification.
---

# Xiaoju Charging Overall Skill

## Purpose

Use this skill as the single entry point for Xiaoju Charging automation.
It coordinates:

1. parameter readiness check
2. status query
3. idempotent check-in execution
4. post-run validation

## Preconditions

Required environment variables:

- `DAILYHUB_XIAOJU_TICKET`
- `DAILYHUB_XIAOJU_TOKEN`
- `DAILYHUB_XIAOJU_TOKEN_ID`

Recommended additional variables (can use defaults if omitted):

- `DAILYHUB_XIAOJU_APP_ID`
- `DAILYHUB_XIAOJU_AM_CHANNEL`
- `DAILYHUB_XIAOJU_SOURCE`
- `DAILYHUB_XIAOJU_TTID`

## Execution Flow

1. **Auth Check & Auto-Recovery**: Check if required auth variables are present (`DAILYHUB_XIAOJU_TICKET`, `DAILYHUB_XIAOJU_TOKEN`, `DAILYHUB_XIAOJU_TOKEN_ID`).
   - If any required credential is missing: automatically switch to `get-params` skill to initiate SMS login flow
   - Only request user interaction when the SMS flow explicitly needs phone number and verification code
2. Run status check:

```bash
python3 -m checkin.xiaojuchongdian.src.main status --task xiaoju.checkin
```

3. Run check-in:

```bash
python3 -m checkin.xiaojuchongdian.src.main run --task xiaoju.checkin --verify-record
```

4. **Auth Recovery on Runtime Failure**: If auth fails during execution (`401/403/TICKET ERROR`):
   - Automatically switch to `get-params` skill to refresh credentials via SMS login
   - After successful credential refresh, automatically retry the check-in
5. Return structured JSON result directly.

## Output Format

Return a case-specific human-readable report with:

1. Overall outcome:
   - `SUCCESS` when final sign status is `already_signed` or `signed`
   - `FAILED` when auth/network/business checks fail
   - `AUTH_RECOVERED` when auto-recovery via `get-params` was triggered and succeeded
2. One-line summary:
   - what was executed (`status` + `run`) and final sign result
   - mention if auth recovery was performed
3. Key execution facts:
   - auth readiness (ready / recovered / failed)
   - `main_before` snapshot
   - `main_after` snapshot when sign action executed
   - `record` verification result when enabled
4. If failed:
   - root reason
   - if auth recovery was attempted and failed, include those details

Optional: append structured `details` with raw command payloads.

## Workflow Ownership

Use these files as source of truth:

- Main orchestration behavior: this file (`skill/overall/SKILL.md`)
- Detailed sign/check-record sequence:
  `checkin/xiaojuchongdian/skill/checkin/SKILL.md`
- API sequence specification:
  `checkin/xiaojuchongdian/src/checkin_workflow.yaml`
- Runtime implementation:
  `checkin/xiaojuchongdian/src/checkin_task.py`

## Success Criteria

- `success` is `true`
- `status` is `already_signed` or `signed`
- if `--verify-record` is enabled, include `data.record` when available
