#!/bin/bash
# Auto-deploy script for dashboard.itgyani.com
# Runs on VPS, pulls latest from GitHub and restarts if changed
# Requires: GITHUB_TOKEN env var set in /etc/environment or systemd

REPO="https://${GITHUB_TOKEN}@github.com/shaashish1/open-claw-rony.git"
DEPLOY_DIR="/opt/itgyani-dashboard"
TMP_DIR="/tmp/rony-deploy"

if [ -z "$GITHUB_TOKEN" ]; then
  echo "[$(date)] ERROR: GITHUB_TOKEN not set"
  exit 1
fi

# Clone/pull latest
if [ ! -d "$TMP_DIR/.git" ]; then
  git clone --depth=1 "$REPO" "$TMP_DIR" 2>&1
else
  cd "$TMP_DIR" && git remote set-url origin "$REPO" && git pull --ff-only 2>&1
fi

# Check if dashboard changed
CURRENT=$(md5sum "$DEPLOY_DIR/main.py" 2>/dev/null | awk '{print $1}')
NEW=$(md5sum "$TMP_DIR/dashboard/backend/main.py" 2>/dev/null | awk '{print $1}')

if [ "$CURRENT" != "$NEW" ] || [ ! -f "$DEPLOY_DIR/main.py" ]; then
  echo "[$(date)] Changes detected — deploying..."
  cp "$TMP_DIR/dashboard/backend/"*.py "$DEPLOY_DIR/"
  cp "$TMP_DIR/dashboard/frontend/index.html" "$DEPLOY_DIR/frontend/index.html"
  mkdir -p "$DEPLOY_DIR/frontend/static"
  systemctl restart itgyani-dashboard
  echo "[$(date)] Deployed successfully"
else
  echo "[$(date)] No changes"
fi
