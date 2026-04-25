"""
Create 10 ChartInk strategies in OpenAlgo DB.
Run inside container: python3 /tmp/create_chartink.py
"""
import sqlite3, uuid
from datetime import datetime

conn = sqlite3.connect("/app/db/openalgo.db")
c = conn.cursor()

USER_ID = "ashish.sharma14@gmail.com"
NOW = datetime.now().isoformat()

STRATEGIES = [
    {
        "name": "CI_EMA_Golden_Cross_Daily",
        "is_intraday": 0,
        "start_time": None, "end_time": None, "squareoff_time": None,
        "symbols": [
            # Top NSE large caps for swing trading
            ("RELIANCE", "NSE", 1, "CNC"),
            ("HDFCBANK", "NSE", 1, "CNC"),
            ("ICICIBANK", "NSE", 1, "CNC"),
            ("TCS", "NSE", 1, "CNC"),
            ("INFY", "NSE", 1, "CNC"),
        ],
        "scan": "( {cash} ( weekly ( [0]EMA( [0]C,50 ) < [0]EMA( [0]C,200 ) AND [1]EMA( [1]C,50 ) >= [1]EMA( [1]C,200 ) ) ) )",
        "description": "Weekly 50/200 EMA Golden Cross — Swing BUY signal"
    },
    {
        "name": "CI_RSI_Oversold_Bounce",
        "is_intraday": 1,
        "start_time": "09:15", "end_time": "15:00", "squareoff_time": "15:10",
        "symbols": [
            ("SBIN", "NSE", 1, "MIS"),
            ("AXISBANK", "NSE", 1, "MIS"),
            ("KOTAKBANK", "NSE", 1, "MIS"),
            ("BAJFINANCE", "NSE", 1, "MIS"),
            ("HDFCBANK", "NSE", 1, "MIS"),
        ],
        "scan": "( {cash} ( [0]RSI( [0]C,14 ) < 30 AND [0]RSI( [0]C,14 ) > [1]RSI( [1]C,14 ) ) )",
        "description": "RSI < 30 turning up — Intraday oversold bounce BUY"
    },
    {
        "name": "CI_Breakout_52W_High",
        "is_intraday": 0,
        "start_time": None, "end_time": None, "squareoff_time": None,
        "symbols": [
            ("NIFTY 50", "NSE", 1, "CNC"),
        ],
        "scan": "( {cash} ( latest high = Max( 52 , latest high ) ) )",
        "description": "52-week high breakout scan — Momentum BUY (all NSE stocks)"
    },
    {
        "name": "CI_MACD_Bullish_Crossover",
        "is_intraday": 1,
        "start_time": "09:15", "end_time": "15:00", "squareoff_time": "15:10",
        "symbols": [
            ("RELIANCE", "NSE", 1, "MIS"),
            ("LT", "NSE", 1, "MIS"),
            ("WIPRO", "NSE", 1, "MIS"),
            ("TECHM", "NSE", 1, "MIS"),
            ("HCLTECH", "NSE", 1, "MIS"),
        ],
        "scan": "( {cash} ( [0]MACD( [0]C,12,26,9 ) > [0]MACDsignal( [0]C,12,26,9 ) AND [1]MACD( [1]C,12,26,9 ) <= [1]MACDsignal( [1]C,12,26,9 ) ) )",
        "description": "MACD bullish crossover — Intraday momentum BUY"
    },
    {
        "name": "CI_Supertrend_Buy",
        "is_intraday": 1,
        "start_time": "09:15", "end_time": "15:00", "squareoff_time": "15:10",
        "symbols": [
            ("NIFTY", "NSE", 1, "MIS"),
            ("BANKNIFTY", "NSE", 1, "MIS"),
            ("FINNIFTY", "NSE", 1, "MIS"),
        ],
        "scan": "( {cash} ( [0]Supertrend( [0]H,[0]L,[0]C,7,3 ) = 1 AND [1]Supertrend( [1]H,[1]L,[1]C,7,3 ) = -1 ) )",
        "description": "Supertrend flip to bullish — Index intraday BUY"
    },
    {
        "name": "CI_Volume_Breakout",
        "is_intraday": 1,
        "start_time": "09:15", "end_time": "14:30", "squareoff_time": "15:10",
        "symbols": [
            ("ADANIENT", "NSE", 1, "MIS"),
            ("ADANIPORTS", "NSE", 1, "MIS"),
            ("VEDL", "NSE", 1, "MIS"),
            ("TATASTEEL", "NSE", 1, "MIS"),
            ("JSWSTEEL", "NSE", 1, "MIS"),
        ],
        "scan": "( {cash} ( [0]volume > 2 * [0]SMA( [0]volume,20 ) AND [0]C > [1]H ) )",
        "description": "Volume 2x avg + price above yesterday's high — BUY"
    },
    {
        "name": "CI_BB_Squeeze_Breakout",
        "is_intraday": 1,
        "start_time": "09:30", "end_time": "14:00", "squareoff_time": "15:10",
        "symbols": [
            ("TITAN", "NSE", 1, "MIS"),
            ("ASIANPAINT", "NSE", 1, "MIS"),
            ("NESTLEIND", "NSE", 1, "MIS"),
            ("HINDUNILVR", "NSE", 1, "MIS"),
            ("BRITANNIA", "NSE", 1, "MIS"),
        ],
        "scan": "( {cash} ( [0]C > [0]BBand-Upper( [0]C,20,2,1 ) AND [1]C <= [1]BBand-Upper( [1]C,20,2,1 ) ) )",
        "description": "Price closes above upper Bollinger Band — Breakout BUY"
    },
    {
        "name": "CI_CryptoGyani_Momentum",
        "is_intraday": 0,
        "start_time": None, "end_time": None, "squareoff_time": None,
        "symbols": [
            ("BAJFINANCE", "NSE", 1, "CNC"),
            ("BAJAJFINSV", "NSE", 1, "CNC"),
            ("HDFCLIFE", "NSE", 1, "CNC"),
            ("SBILIFE", "NSE", 1, "CNC"),
            ("ICICIPRULI", "NSE", 1, "CNC"),
        ],
        "scan": "( {cash} ( [0]RSI( [0]C,14 ) > 60 AND [0]EMA( [0]C,20 ) > [0]EMA( [0]C,50 ) AND [0]C > [0]EMA( [0]C,200 ) ) )",
        "description": "RSI>60 + EMA 20>50 + Price>200EMA — Strong uptrend BUY"
    },
    {
        "name": "CI_Intraday_OBV_Trend",
        "is_intraday": 1,
        "start_time": "09:15", "end_time": "15:00", "squareoff_time": "15:10",
        "symbols": [
            ("MARUTI", "NSE", 1, "MIS"),
            ("EICHERMOT", "NSE", 1, "MIS"),
            ("HEROMOTOCO", "NSE", 1, "MIS"),
            ("BAJAJ-AUTO", "NSE", 1, "MIS"),
            ("M&M", "NSE", 1, "MIS"),
        ],
        "scan": "( {cash} ( [0]OBV( [0]C,[0]volume ) > [0]EMA( [0]OBV( [0]C,[0]volume ),20 ) AND [0]C > [0]VWAP )",
        "description": "OBV above 20 EMA + Price above VWAP — Intraday BUY"
    },
    {
        "name": "CI_ADX_Strong_Trend",
        "is_intraday": 1,
        "start_time": "09:30", "end_time": "14:30", "squareoff_time": "15:10",
        "symbols": [
            ("COALINDIA", "NSE", 1, "MIS"),
            ("ONGC", "NSE", 1, "MIS"),
            ("BPCL", "NSE", 1, "MIS"),
            ("IOC", "NSE", 1, "MIS"),
            ("POWERGRID", "NSE", 1, "MIS"),
        ],
        "scan": "( {cash} ( [0]ADX( [0]H,[0]L,[0]C,14 ) > 25 AND [0]PLUSDI( [0]H,[0]L,[0]C,14 ) > [0]MINUSDI( [0]H,[0]L,[0]C,14 ) AND [1]PLUSDI( [1]H,[1]L,[1]C,14 ) <= [1]MINUSDI( [1]H,[1]L,[1]C,14 ) ) )",
        "description": "ADX>25 + +DI crosses above -DI — Strong trend BUY"
    },
]

print(f"Creating {len(STRATEGIES)} ChartInk strategies...")

for strat in STRATEGIES:
    webhook_id = str(uuid.uuid4())
    
    # Insert strategy
    c.execute("""
        INSERT INTO chartink_strategies 
        (name, webhook_id, user_id, is_active, is_intraday, start_time, end_time, squareoff_time, created_at, updated_at)
        VALUES (?, ?, ?, 1, ?, ?, ?, ?, ?, ?)
    """, (
        strat["name"], webhook_id, USER_ID,
        strat["is_intraday"],
        strat["start_time"], strat["end_time"], strat["squareoff_time"],
        NOW, NOW
    ))
    strategy_db_id = c.lastrowid
    
    # Insert symbol mappings
    for sym_data in strat["symbols"]:
        symbol, exchange, qty, product = sym_data
        c.execute("""
            INSERT INTO chartink_symbol_mappings
            (strategy_id, chartink_symbol, exchange, quantity, product_type, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (strategy_db_id, symbol, exchange, qty, product, NOW, NOW))
    
    webhook_url = f"https://openalgo.cryptogyani.com/chartink/webhook/{webhook_id}"
    print(f"\n✅ {strat['name']}")
    print(f"   ID: {strategy_db_id} | Webhook: {webhook_url}")
    print(f"   Type: {'Intraday' if strat['is_intraday'] else 'Positional'} | Symbols: {len(strat['symbols'])}")
    print(f"   Scan: {strat['scan'][:80]}...")
    print(f"   ChartInk URL to configure: https://chartink.com/scan_dashboard")
    print(f"   Use this webhook in ChartInk alert: {webhook_url}")

conn.commit()
conn.close()

print(f"\n\n{'='*60}")
print("ALL CHARTINK STRATEGIES CREATED")
print("="*60)
print("\nNEXT STEPS FOR EACH STRATEGY:")
print("1. Login to https://chartink.com with ashish.sharma14@gmail.com")
print("2. Create a new scan with the condition above")
print("3. Set alert -> Webhook -> paste the webhook URL")
print("4. ChartInk fires -> OpenAlgo executes in analyze/live mode")
