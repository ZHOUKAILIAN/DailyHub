---
name: xiaoju-checkin
description: Execute Xiaoju Charging daily check-in with idempotency, status verification, and auth-failure branching to credential input or get-params guidance.
---

# Xiaoju Charging Check-in Skill

## Purpose

Execute Xiaoju Charging daily check-in with idempotency and verification.

## Required Inputs

- valid environment variables:
  - `DAILYHUB_XIAOJU_TICKET`
  - `DAILYHUB_XIAOJU_TOKEN`
  - `DAILYHUB_XIAOJU_TOKEN_ID`

## Auth Recovery Decision Gate

If auth fails (or required auth env is missing), ask this first:

- `Do you want to provide the Xiaoju credentials directly, or should I guide you to capture them from app traffic?`

Then branch:

- if user provides credentials directly: apply values and retry `status`/`run`
- if user wants guidance: switch to `get-params` skill

## Commands

Check status first:

```bash
python3 -m checkin.xiaojuchongdian.src.main status --task xiaoju.checkin
```

Run check-in:

```bash
python3 -m checkin.xiaojuchongdian.src.main run --task xiaoju.checkin --verify-record
```

## Deterministic Workflow

Follow these steps in order:

1. Call `sign/main` to fetch current sign status.
2. If today's date is already in sign records, return `already_signed`.
3. If not signed, extract `excitationId` from `sign/main` response.
4. Call `sign/doSign` with `excitationId`.
5. Call `sign/main` again and confirm today's date exists in sign records.
6. If `--verify-record` is enabled, call `signRecord` and return it in `data.record`.

API paths used:

- `POST /am/marketing/api/member/charge/activity/sign/main`
- `POST /am/marketing/api/member/charge/activity/sign/doSign`
- `POST /excitation/api/excitation/signRecord`

## Expected Result

Return JSON with:

- `success`
- `status` (`already_signed`, `signed`, `failed`)
- `message`
- `data.main_before`
- `data.main_after` (if sign action was executed)
- `data.record` (if `--verify-record` was enabled and request succeeded)

## When Record Is Missing After doSign

If `doSign` was called but today's record is still missing:

1. Check `data.do_sign` first.
2. If `data.do_sign.success != true`, treat as sign API rejection and stop.
3. If `data.do_sign.success == true` but `data.signed_after == false`, inspect `data.main_after`.
4. If `data.record` is missing or contains `_error`/`_warning`, check auth/network issues first.
5. Retry once after refreshing credentials.

## Failure Handling

- `authentication failed` (ticket/token/tokenId, sometimes called "cookie"):
  ask user whether to provide credentials directly or follow guided capture via `get-params`
- network/http errors: keep failure context and return raw error message
- business failure: return payload-level signals for triage

## File Map (Source of Truth)

- Sign-in execution logic:
  `checkin/xiaojuchongdian/src/checkin_task.py`
  (`execute`, `_call_sign_main`, `_call_do_sign`)
- Sign record retrieval and return payload (`data.record`):
  `checkin/xiaojuchongdian/src/checkin_task.py`
  (`_call_sign_record`, `_safe_record`)
- Workflow-level API sequence document:
  `checkin/xiaojuchongdian/src/checkin_workflow.yaml`
- CLI entry for status/check-in commands:
  `checkin/xiaojuchongdian/src/main.py`
