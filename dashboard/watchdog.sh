#!/bin/bash
# ITGYANI Strategy Watchdog
COUNT=$(docker exec openalgo-web ps aux 2>/dev/null | grep "strategy_0" | grep -v grep | wc -l)
if [ "$COUNT" -lt 5 ]; then
    echo "$(date +%Y-%m-%dT%H:%M:%S) Restarting strategies (was $COUNT)" >> /var/log/strategy_watch.log
    docker exec openalgo-web python3 /app/autostart_strategies.py >> /var/log/strategy_watch.log 2>&1
    echo "$(date +%Y-%m-%dT%H:%M:%S) Done" >> /var/log/strategy_watch.log
fi
