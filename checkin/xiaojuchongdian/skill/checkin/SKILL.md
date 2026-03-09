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

## Output Format

Return a human-readable completion report first, with this structure:

1. `Result`: `SUCCESS`, `PARTIAL`, or `FAILED`
2. `Summary`: one sentence about sign-in outcome
3. `Key details`:
   - sign status (`already_signed`, `signed`, `failed`)
   - `main_before`
   - `main_after` (if sign action was executed)
   - `record` (if `--verify-record` was enabled and request succeeded)
4. If failed:
   - failure reason
   - suggested next step (for example refresh credentials and retry once)

Optional: append a structured `details` object for downstream chaining.

## Verification Mismatch Handling

If sign action and verification results look inconsistent, do not hard-code branch logic here.

- Return the most complete evidence available (`main_before`, `main_after`, `record`, and raw error/warning fields).
- Keep the report factual and concise.
- Let the model infer the next best action from the returned evidence and current context.

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
