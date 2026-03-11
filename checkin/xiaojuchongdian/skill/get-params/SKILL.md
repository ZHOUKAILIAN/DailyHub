---
name: xiaoju-get-params
description: Get fresh Xiaoju Charging auth/runtime parameters through API login (phone + SMS code) and validate them for check-in.
---

# Xiaoju Charging Get-Params Skill

## Purpose

Use API only (no UI click automation) to get latest Xiaoju check-in credentials:

- send SMS code
- verify code
- get `ticket/token/tokenId`
- validate with check-in status API

## When To Use

Use this skill when:

- today's check-in fails with `ticket/token` expired
- user can provide phone number + SMS code
- you need a reusable API path for credential refresh

## Required Inputs

- phone number (must ask user each run; do not reuse cached value)
- SMS code (must ask user each run after send-code; do not infer)

## Runtime Dependencies

- Bundled Node auth client:
  `checkin/xiaojuchongdian/skill/get-params/scripts/xj_auth_client.js`
- Optional override:
  `XJ_AUTH_CLIENT=/path/to/xj_auth_client.js` (or `passport_auth_client.js`)
- DailyHub check-in CLI module:
  `checkin.xiaojuchongdian.src.main`
- helper script in this skill:
  `checkin/xiaojuchongdian/skill/get-params/scripts/get_params_via_api.sh`

Default auth client discovery order in script:

1. Bundled `scripts/xj_auth_client.js`
2. `XJ_AUTH_CLIENT`
3. 从当前工作目录向上逐级查找：
   - `<ancestor>/xj_sign_api/passport_auth_client.js`
   - `<ancestor>/passport_auth_client.js`
4. 从脚本目录向上逐级查找同上路径
5. `~/xj_sign_api/passport_auth_client.js`

## Collection Procedure

1. Ask user for phone number.
2. Send SMS code:

```bash
cd checkin/xiaojuchongdian/skill/get-params
bash scripts/get_params_via_api.sh send-code --phone <PHONE_FROM_USER>
```

3. Ask user for SMS code.
4. Login by SMS code and save latest auth JSON:

```bash
bash scripts/get_params_via_api.sh login --phone <PHONE_FROM_USER> --code <SMS_CODE_FROM_USER> --out /tmp/xj_auth_latest.json
```

5. Print exportable env values:

```bash
bash scripts/get_params_via_api.sh export-env --json /tmp/xj_auth_latest.json
```

6. Validate with Xiaoju check-in status:

```bash
cd <dailyhub_repo_root>
python3 -m checkin.xiaojuchongdian.src.main status --task xiaoju.checkin
```

## Expected Fields

Required:

- `DAILYHUB_XIAOJU_TICKET`
- `DAILYHUB_XIAOJU_TOKEN`
- `DAILYHUB_XIAOJU_TOKEN_ID`

Recommended:

- `DAILYHUB_XIAOJU_APP_ID`
- `DAILYHUB_XIAOJU_AM_CHANNEL`
- `DAILYHUB_XIAOJU_SOURCE`
- `DAILYHUB_XIAOJU_TTID`
- `DAILYHUB_XIAOJU_BIZ_LINE`
- `DAILYHUB_XIAOJU_CITY_ID`

## Validation Criteria

Auth is valid when:

- `login-by-code` returns `errno == 0`
- returned payload has `sign_auth`
- `status` command does not return auth error

## Output Format

Return a human-readable completion report first, with this structure:

1. `Result`: `SUCCESS`, `PARTIAL`, or `FAILED`
2. `Summary`: whether API auth refresh succeeded
3. `Key details`:
   - phone (masked)
   - source (`api_sms_login`)
   - `errno` and `traceid` (if present)
   - exported fields
   - status-check result
4. If not validated:
   - failure reason (`40002/40003/41002/network/parse`)
   - next action (re-send code / get captcha / retry)

Optional: append a structured `details` object for downstream chaining.
