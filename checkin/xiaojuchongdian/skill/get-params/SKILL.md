---
name: xiaoju-get-params
description: Refresh Xiaoju Charging auth credentials via SMS verification
---

# Refresh Xiaoju Auth Credentials

## Goal

Obtain fresh Xiaoju Charging auth credentials (ticket/token/tokenId) via phone number + SMS verification code, while preserving the account's existing device fingerprint (`DAILYHUB_XIAOJU_AM_DID`) when available.

## Flow

1. Ask user for phone number
2. Send SMS verification code
3. Ask user for the received code
4. Login with code to obtain auth credentials
5. Preserve existing `DAILYHUB_XIAOJU_AM_DID` for this account if it already exists in env/local config
6. Validate new credentials by calling the check-in status API

## Available Tools

### Shell Scripts (auth flow)

Located in the `scripts/` directory of this skill:

- `get_params_via_api.sh` — complete flow for sending code, login, and exporting env vars
- `xj_auth_client.js` — underlying Node.js auth client

Read `get_params_via_api.sh` to understand the invocation.

## Key Constraints

- Must ask user for phone number and SMS code every time — never cache
- Requires Node.js runtime
- Login success indicator: `errno == 0` and response contains `sign_auth` field
- SMS login refreshes auth credentials only; it does not mint a new `DAILYHUB_XIAOJU_AM_DID`

## Output

Exports the following environment variables for check-in use:
- `DAILYHUB_XIAOJU_TICKET`
- `DAILYHUB_XIAOJU_TOKEN`
- `DAILYHUB_XIAOJU_TOKEN_ID`
- `DAILYHUB_XIAOJU_AM_DID` when an existing value is already available in env/local config
- Plus recommended variables (APP_ID, AM_CHANNEL, etc.)
