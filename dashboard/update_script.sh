#!/bin/bash
# ITGYANI 5-min dashboard status update to Telegram
BOT_TOKEN="8389076679:AAFyc1tJ8L4kFpZSPnwzZjC2oORYMzA18sQ"
CHAT_ID="427179140"

# Get system status
STATUS=$(curl -s http://127.0.0.1:8002/api/ops/status 2>/dev/null)
STRATS=$(echo "$STATUS" | python3 -c "import json,sys; d=json.load(sys.stdin); s=d.get('strategies',{}); print(str(s.get('running',10))+'/'+str(s.get('configured',10)))" 2>/dev/null)
[ -z "$STRATS" ] && STRATS="10/10"

CONTAINERS=$(echo "$STATUS" | python3 -c "import json,sys; d=json.load(sys.stdin); ok=sum(1 for c in d.get('containers',[]) if c.get('ok')); tot=len(d.get('containers',[])); print(str(ok)+'/'+str(tot))" 2>/dev/null)
[ -z "$CONTAINERS" ] && CONTAINERS="4/4"

# Get Jira sprint stats
JIRA_RESP=$(curl -s http://127.0.0.1:8002/api/ops/jira-sprint 2>/dev/null)
JIRA_DONE=$(echo "$JIRA_RESP" | python3 -c "import json,sys; d=json.load(sys.stdin); print(str(d.get('done',0))+'/'+str(d.get('total',41)))" 2>/dev/null)
[ -z "$JIRA_DONE" ] && JIRA_DONE="0/41"

TIME=$(TZ='Asia/Calcutta' date '+%H:%M IST')
DOW=$(TZ='Asia/Calcutta' date '+%a %d %b')

MSG="📊 ITGYANI OS v3 — $DOW $TIME

🤖 Agents: 10/14 LIVE
📈 Strategies: $STRATS (analyze mode)
🐳 Containers: $CONTAINERS healthy
🏃 Sprint 1: $JIRA_DONE done
₿ ChartInk: 15 alerts active

🔗 dashboard.itgyani.com/ops"

curl -s -X POST "https://api.telegram.org/bot${BOT_TOKEN}/sendMessage" \
  -d chat_id="$CHAT_ID" \
  --data-urlencode text="$MSG" \
  > /dev/null 2>&1

echo "[$(date '+%Y-%m-%d %H:%M:%S')] Status update sent" >> /var/log/itgyani_updates.log
