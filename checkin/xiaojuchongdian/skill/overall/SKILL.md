---
name: xiaoju-overall
description: Xiaoju Charging daily check-in (idempotent)
---

# Xiaoju Charging Check-in

## Goal

Complete the daily check-in for Xiaoju Charging app, then fetch the sign record to verify.

## Available Tools

This repo contains ready-to-use programmatic assets:

### Python CLI (check-in execution)

Located in the `src/` directory alongside this skill (under `checkin/xiaojuchongdian/`).

Capabilities:
- Query check-in status
- Execute check-in (idempotent)
- Verify sign record

Entry point: `main.py`. Read the file to understand usage.

### Auth Refresh (when credentials expire)

If check-in fails due to authentication error, use the `xiaoju-get-params` skill to refresh credentials.

## Environment Variables

Required:
- `DAILYHUB_XIAOJU_TICKET`
- `DAILYHUB_XIAOJU_TOKEN`
- `DAILYHUB_XIAOJU_TOKEN_ID`

When missing or expired, switch to `xiaoju-get-params` to refresh.

## Output

Tell the user whether check-in succeeded and the consecutive sign-in dates.
