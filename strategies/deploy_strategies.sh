#!/bin/bash
# Deploy and launch all 10 Yukti strategies persistently
# Run as: bash deploy_strategies.sh

STRAT_DIR="/app/strategies/yukti"
LOG_DIR="/app/log/strategies"
API_KEY = os.getenv("OPENALGO_API_KEY", "")

mkdir -p $STRAT_DIR $LOG_DIR

echo "=== Testing API connectivity ==="
curl -s -X POST http://127.0.0.1:5000/api/v1/funds \
  -H "Content-Type: application/json" \
  -d "{\"apikey\": \"$API_KEY\"}" | python3 -m json.tool

echo ""
echo "=== Killing any existing strategy processes ==="
pkill -f "strategy_0" 2>/dev/null || true
sleep 2

echo "=== Launching 10 strategies ==="
for f in /app/strategies/yukti/strategy_0*.py; do
    name=$(basename $f .py)
    OPENALGO_API_KEY=$API_KEY nohup python3 $f > $LOG_DIR/${name}.log 2>&1 &
    echo "Started $name (PID: $!)"
    sleep 1
done

echo ""
echo "=== Verifying running processes ==="
sleep 3
ps aux | grep "strategy_0" | grep -v grep

echo ""
echo "=== Log tails ==="
for f in $LOG_DIR/strategy_0*.log; do
    echo "--- $(basename $f) ---"
    tail -3 $f 2>/dev/null
done
