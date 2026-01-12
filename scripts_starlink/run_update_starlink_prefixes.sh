#!/usr/bin/env bash
set -euo pipefail

# Runs the Django management command to refresh Starlink prefixes.
# Recommended to run on the Django server.

APP_DIR="/var/www/sreadmin"
PY="$APP_DIR/venv/bin/python"
MANAGE="$APP_DIR/manage.py"

LOG_DIR="/var/log/poppfire"
mkdir -p "$LOG_DIR"

# Fast mode (no RDAP): safe for frequent runs
"$PY" "$MANAGE" update_starlink_prefixes --no-rdap >> "$LOG_DIR/starlink_prefixes.log" 2>&1
