#!/bin/bash
# ITGYANI Dashboard — Start Script
# RULE: DRAFT ONLY - Never send emails

mkdir -p /root/.openclaw/workspace/dashboard/data

cd /root/.openclaw/workspace/dashboard/backend

exec env \
  GMAIL_PERSONAL_PASS="eysg infz zxja srtl" \
  GMAIL_ITGYANI_PASS="ozdi cwfy hncm nkzl" \
  VPS_CRYPTOGYANI_PASS="Itgyani@123" \
  "VPS_CRYPTOGYANI_INFO_PASS=BlockTrade5$" \
  VPS_CRYPTOGYANI_TRADING_PASS="Itgyani@123" \
  "VPS_TEF_PASS=BlockTrade5$" \
  "VPS_TEF_SUPPORT_PASS=BlockTrade5$" \
  "VPS_TECHNOFLAIRLAB_PASS=BlockTrade5$" \
  VPS_KHARADI_PASS="Itgyani@123" \
  DASH_USER="ashish" \
  "DASH_PASS=ITGyani@2026!" \
  TELEGRAM_BOT_TOKEN="${TELEGRAM_BOT_TOKEN:-placeholder}" \
  /root/.openclaw/workspace/dashboard/venv/bin/uvicorn main:app \
  --host 0.0.0.0 --port 8000 --log-level info
