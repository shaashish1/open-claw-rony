#!/bin/bash
# ITGYANI Strategy Watchdog — runs via cron every 10 minutes
# Restarts 10 Yukti strategies if they die

COUNT=$(docker exec openalgo-web ps aux 2>/dev/null | grep "strategy_" | grep -v grep | wc -l)
if [ "$COUNT" -lt 5 ]; then
    echo "$(date +%Y-%m-%dT%H:%M:%S): Restarting strategies (was $COUNT)" >> /var/log/strategy_watch.log
    docker exec openalgo-web python3 /tmp/rs.py >> /var/log/strategy_watch.log 2>&1
    echo "$(date +%Y-%m-%dT%H:%M:%S): Done" >> /var/log/strategy_watch.log
fi
