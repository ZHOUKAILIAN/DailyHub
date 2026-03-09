---
name: xiaoju-get-params
description: Collect and validate Xiaoju Charging auth/runtime parameters from direct user input or app traffic capture for check-in execution.
---

# Xiaoju Charging Get-Params Skill

## Purpose

Collect authentication/runtime parameters for Xiaoju Charging check-in.

## Parameters

Required:

- `DAILYHUB_XIAOJU_TICKET`
- `DAILYHUB_XIAOJU_TOKEN`
- `DAILYHUB_XIAOJU_TOKEN_ID`

Recommended:

- `DAILYHUB_XIAOJU_APP_ID`
- `DAILYHUB_XIAOJU_AM_CHANNEL`
- `DAILYHUB_XIAOJU_SOURCE`
- `DAILYHUB_XIAOJU_TTID`

## Collection Procedure

1. Ask user first:
   `Do you want to provide ticket/token/tokenId directly, or should I guide you to capture them from app traffic?`
2. If user provides values directly, skip traffic capture and validate immediately with `status` command.
3. If user needs guidance, continue with traffic capture.
4. Open Xiaoju Charging page in the official app (with signed-in account).
5. Capture HTTPS traffic with a trusted proxy tool (Charles, Proxyman, or HttpCanary).
6. Locate request:
   - `POST /am/marketing/api/member/charge/activity/sign/main`
7. Copy values from request body:
   - `ticket` -> `DAILYHUB_XIAOJU_TICKET`
   - `token` -> `DAILYHUB_XIAOJU_TOKEN`
   - `tokenId` -> `DAILYHUB_XIAOJU_TOKEN_ID`
   - `appId` -> `DAILYHUB_XIAOJU_APP_ID`
   - `amChannel` -> `DAILYHUB_XIAOJU_AM_CHANNEL`
   - `source` -> `DAILYHUB_XIAOJU_SOURCE`
   - `ttid` -> `DAILYHUB_XIAOJU_TTID`
8. Export them to env and run status command:

```bash
python3 -m checkin.xiaojuchongdian.src.main status --task xiaoju.checkin
```

## Validation

Parameter collection is valid when status command returns:

- `success: true`
- non-empty `data.main`
