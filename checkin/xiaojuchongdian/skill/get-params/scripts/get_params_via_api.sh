#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
AUTH_CLIENT="${XJ_AUTH_CLIENT:-}"

usage() {
  cat <<'EOF'
Usage:
  export XJ_AUTH_CLIENT=/path/to/passport_auth_client.js
  get_params_via_api.sh send-code --phone <phone>
  get_params_via_api.sh login --phone <phone> --code <code> [--out /tmp/xj_auth_latest.json]
  get_params_via_api.sh export-env --json /tmp/xj_auth_latest.json
  get_params_via_api.sh full --phone <phone> [--out /tmp/xj_auth_latest.json]
EOF
}

require_auth_client() {
  local bundled="$SCRIPT_DIR/xj_auth_client.js"
  if [[ -z "$AUTH_CLIENT" && -f "$bundled" ]]; then
    AUTH_CLIENT="$bundled"
    return
  fi

  if [[ -n "$AUTH_CLIENT" && -f "$AUTH_CLIENT" ]]; then
    AUTH_CLIENT="$(cd "$(dirname "$AUTH_CLIENT")" && pwd)/$(basename "$AUTH_CLIENT")"
    return
  fi

  discover_from_base() {
    local base="$1"
    while [[ "$base" != "/" ]]; do
      local c1="$base/xj_sign_api/passport_auth_client.js"
      local c2="$base/passport_auth_client.js"
      if [[ -f "$c1" ]]; then
        AUTH_CLIENT="$(cd "$(dirname "$c1")" && pwd)/$(basename "$c1")"
        return 0
      fi
      if [[ -f "$c2" ]]; then
        AUTH_CLIENT="$(cd "$(dirname "$c2")" && pwd)/$(basename "$c2")"
        return 0
      fi
      base="$(dirname "$base")"
    done
    return 1
  }

  if discover_from_base "$PWD"; then
    return
  fi
  if discover_from_base "$SCRIPT_DIR"; then
    return
  fi
  if [[ -f "$HOME/xj_sign_api/passport_auth_client.js" ]]; then
    AUTH_CLIENT="$HOME/xj_sign_api/passport_auth_client.js"
    return
  fi

  echo "auth client not found." >&2
  echo "Set XJ_AUTH_CLIENT=/path/to/xj_auth_client.js (or passport_auth_client.js)" >&2
  exit 2
}

read_json_field() {
  local json_path="$1"
  local js_expr="$2"
  node -e "
const fs = require('fs');
const p = process.argv[1];
const expr = process.argv[2];
const obj = JSON.parse(fs.readFileSync(p, 'utf8'));
const val = eval(expr);
if (val === undefined || val === null) process.exit(3);
if (typeof val === 'object') console.log(JSON.stringify(val));
else console.log(String(val));
" "$json_path" "$js_expr"
}

resolve_existing_am_did() {
  if [[ -n "${DAILYHUB_XIAOJU_AM_DID:-}" ]]; then
    printf '%s\n' "$DAILYHUB_XIAOJU_AM_DID"
    return 0
  fi

  local candidate
  for candidate in \
    "$PWD/.env" \
    "$(dirname "$SCRIPT_DIR")/.env" \
    "$HOME/checkin/xiaojuchongdian/.env"
  do
    if [[ -f "$candidate" ]]; then
      local value
      value="$(grep -E '^DAILYHUB_XIAOJU_AM_DID=' "$candidate" | tail -n1 | sed 's/^[^=]*=//')"
      value="${value%\"}"
      value="${value#\"}"
      value="${value%\'}"
      value="${value#\'}"
      if [[ -n "$value" ]]; then
        printf '%s\n' "$value"
        return 0
      fi
    fi
  done

  return 1
}

subcmd="${1:-}"
shift || true

case "$subcmd" in
  send-code)
    require_auth_client
    phone=""
    while [[ $# -gt 0 ]]; do
      case "$1" in
        --phone) phone="${2:-}"; shift 2 ;;
        *) echo "unknown arg: $1" >&2; usage; exit 2 ;;
      esac
    done
    [[ -n "$phone" ]] || { echo "--phone is required" >&2; exit 2; }
    node "$AUTH_CLIENT" send-code --phone "$phone"
    ;;

  login)
    require_auth_client
    phone=""
    code=""
    out="/tmp/xj_auth_latest.json"
    while [[ $# -gt 0 ]]; do
      case "$1" in
        --phone) phone="${2:-}"; shift 2 ;;
        --code) code="${2:-}"; shift 2 ;;
        --out) out="${2:-}"; shift 2 ;;
        *) echo "unknown arg: $1" >&2; usage; exit 2 ;;
      esac
    done
    [[ -n "$phone" ]] || { echo "--phone is required" >&2; exit 2; }
    [[ -n "$code" ]] || { echo "--code is required" >&2; exit 2; }

    node "$AUTH_CLIENT" login-by-code --phone "$phone" --code "$code" | tee "$out"
    errno="$(read_json_field "$out" "obj.result && obj.result.json && obj.result.json.errno")" || true
    if [[ "${errno:-}" != "0" ]]; then
      echo "login failed, errno=${errno:-unknown}" >&2
      exit 1
    fi
    ;;

  export-env)
    json=""
    while [[ $# -gt 0 ]]; do
      case "$1" in
        --json) json="${2:-}"; shift 2 ;;
        *) echo "unknown arg: $1" >&2; usage; exit 2 ;;
      esac
    done
    [[ -n "$json" ]] || { echo "--json is required" >&2; exit 2; }
    [[ -f "$json" ]] || { echo "file not found: $json" >&2; exit 2; }

    ticket="$(read_json_field "$json" "(obj.sign_auth && obj.sign_auth.ticket) || obj.ticket")"
    token="$(read_json_field "$json" "(obj.sign_auth && obj.sign_auth.token) || obj.token")"
    token_id="$(read_json_field "$json" "(obj.sign_auth && obj.sign_auth.tokenId) || obj.tokenId")"
    app_id="$(read_json_field "$json" "(obj.sign_auth && obj.sign_auth.appId) || obj.appId")"
    am_channel="$(read_json_field "$json" "(obj.sign_auth && obj.sign_auth.amChannel) || obj.amChannel")"
    source="$(read_json_field "$json" "(obj.sign_auth && obj.sign_auth.source) || obj.source")"
    ttid="$(read_json_field "$json" "(obj.sign_auth && obj.sign_auth.ttid) || obj.ttid")"
    biz_line="$(read_json_field "$json" "(obj.sign_auth && obj.sign_auth.bizLine) || obj.bizLine")"
    city_id="$(read_json_field "$json" "(obj.sign_auth && obj.sign_auth.cityId) || obj.cityId")"
    am_did="$(resolve_existing_am_did || true)"

    cat <<EOF
export DAILYHUB_XIAOJU_TICKET='$ticket'
export DAILYHUB_XIAOJU_TOKEN='$token'
export DAILYHUB_XIAOJU_TOKEN_ID='$token_id'
export DAILYHUB_XIAOJU_APP_ID='$app_id'
export DAILYHUB_XIAOJU_AM_CHANNEL='$am_channel'
export DAILYHUB_XIAOJU_SOURCE='$source'
export DAILYHUB_XIAOJU_TTID='$ttid'
export DAILYHUB_XIAOJU_BIZ_LINE='$biz_line'
export DAILYHUB_XIAOJU_CITY_ID='$city_id'
EOF
    if [[ -n "$am_did" ]]; then
      printf "export DAILYHUB_XIAOJU_AM_DID='%s'\n" "$am_did"
    else
      echo "# DAILYHUB_XIAOJU_AM_DID is not included here; preserve an existing value or capture it once from real app traffic" >&2
    fi
    ;;

  full)
    require_auth_client
    phone=""
    out="/tmp/xj_auth_latest.json"
    while [[ $# -gt 0 ]]; do
      case "$1" in
        --phone) phone="${2:-}"; shift 2 ;;
        --out) out="${2:-}"; shift 2 ;;
        *) echo "unknown arg: $1" >&2; usage; exit 2 ;;
      esac
    done
    [[ -n "$phone" ]] || { echo "--phone is required" >&2; exit 2; }

    node "$AUTH_CLIENT" send-code --phone "$phone"
    read -r -p "Input SMS code: " code
    [[ -n "$code" ]] || { echo "code is empty" >&2; exit 2; }
    node "$AUTH_CLIENT" login-by-code --phone "$phone" --code "$code" | tee "$out"
    "$0" export-env --json "$out"
    ;;

  *)
    usage
    exit 2
    ;;
esac
