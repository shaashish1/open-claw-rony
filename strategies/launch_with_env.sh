#!/bin/bash
# Launch all 10 strategies with proper environment
# Usage: docker exec openalgo-web bash /app/strategies/launch_with_env.sh

STRATEGIES_DIR="/app/strategies"
LOG_DIR="/app/log/strategies"
mkdir -p "$LOG_DIR"

export OPENALGO_API_KEY = os.getenv("OPENALGO_API_KEY", "")
export HOST_SERVER="http://127.0.0.1:5000"
export WEBSOCKET_URL="ws://127.0.0.1:8765"

echo "=== OpenAlgo Strategy Launcher ==="
echo "Time: $(date)"
echo "Strategies dir: $STRATEGIES_DIR"
echo ""

for strategy in "$STRATEGIES_DIR"/strategy_0*.py; do
    name=$(basename "$strategy" .py)
    if pgrep -f "$strategy" > /dev/null 2>&1; then
        echo "  [RUNNING] $name"
    else
        nohup python3 "$strategy" > "$LOG_DIR/$name.log" 2>&1 &
        pid=$!
        echo "  [STARTED] $name (PID: $pid)"
        sleep 0.5
    fi
done

echo ""
echo "All strategies launched."
echo ""
echo "Monitor logs:"
echo "  tail -f $LOG_DIR/strategy_01_vwap_rsi_ICICIBANK.log"
echo ""
echo "Stop all:"
echo "  pkill -f 'strategy_0'"
