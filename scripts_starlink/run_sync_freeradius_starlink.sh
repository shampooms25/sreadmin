#!/usr/bin/env bash
set -euo pipefail

# Syncs FreeRADIUS Starlink clients include from POPPFIRE API.
# Designed to run as root (needs to write into /etc/freeradius and reload service).

APP_DIR="/var/www/sreadmin"
PY="$APP_DIR/venv/bin/python"
SCRIPT="$APP_DIR/scripts_starlink/sync_freeradius_starlink.py"

ENV_FILE="${ENV_FILE:-/etc/poppfire/starlink_sync.env}"
LOG_DIR="/var/log/poppfire"
LOCK_FILE="/var/lock/poppfire_sync_freeradius_starlink.lock"

mkdir -p "$LOG_DIR"

if [[ ! -f "$ENV_FILE" ]]; then
  echo "Missing env file: $ENV_FILE" >&2
  exit 2
fi

# shellcheck disable=SC1090
source "$ENV_FILE"

if [[ -z "${API_URL:-}" || -z "${API_TOKEN:-}" || -z "${RADIUS_SECRET:-}" ]]; then
  echo "ENV_FILE must define API_URL, API_TOKEN, RADIUS_SECRET" >&2
  exit 2
fi

RADIUS_OUTPUT_FILE="${RADIUS_OUTPUT_FILE:-/etc/freeradius/clients_starlink.conf}"

REQUIRE_MESSAGE_AUTHENTICATOR="${REQUIRE_MESSAGE_AUTHENTICATOR:-unset}"
LIMIT_PROXY_STATE="${LIMIT_PROXY_STATE:-unset}"

INCLUDE_CUSTOM_FLAG=()
if [[ "${INCLUDE_CUSTOM:-0}" == "1" ]]; then
  INCLUDE_CUSTOM_FLAG=(--include-custom)
fi

INCLUDE_NON_AMERICAS_FLAG=()
if [[ "${INCLUDE_NON_AMERICAS:-0}" == "1" ]]; then
  INCLUDE_NON_AMERICAS_FLAG=(--include-non-americas)
fi

# Avoid concurrent runs
exec 9>"$LOCK_FILE"
if ! flock -n 9; then
  echo "Another run is in progress; exiting" >&2
  exit 0
fi

"$PY" "$SCRIPT" \
  --api-url "$API_URL" \
  --api-token "$API_TOKEN" \
  --secret "$RADIUS_SECRET" \
  --output-file "$RADIUS_OUTPUT_FILE" \
  --backup \
  --require-message-authenticator "$REQUIRE_MESSAGE_AUTHENTICATOR" \
  --limit-proxy-state "$LIMIT_PROXY_STATE" \
  "${INCLUDE_CUSTOM_FLAG[@]}" \
  "${INCLUDE_NON_AMERICAS_FLAG[@]}" \
  --validate-cmd "freeradius -XC" \
  --reload-cmd "systemctl reload freeradius" \
  >> "$LOG_DIR/freeradius_starlink_sync.log" 2>&1
