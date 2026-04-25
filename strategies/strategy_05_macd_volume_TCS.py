#!/usr/bin/env python3
"""Strategy 05: MACD + Volume — TCS 15m | MIS | Qty:1"""
from openalgo import api
import pandas as pd
import time
from datetime import datetime, timedelta
import os

api_key = os.getenv('OPENALGO_API_KEY', '')
host = os.getenv('HOST_SERVER', 'http://127.0.0.1:5000')
ws_url = os.getenv('WEBSOCKET_URL', 'ws://127.0.0.1:8765')
strategy = "Yukti_macd_rsi_combo_TCS_15m"
symbol = 'TCS'; exchange = 'NSE'; product = 'MIS'; quantity = 1; interval = '15m'
client = api(api_key=api_key, host=host, ws_url=ws_url)

def is_market_hours():
    now = datetime.now()
    if now.weekday() >= 5: return False
    return now.replace(hour=9,minute=15,second=0,microsecond=0) <= now <= now.replace(hour=15,minute=15,second=0,microsecond=0)

def run():
    position = 0
    print(f"[{strategy}] Starting...")
    while True:
        try:
            if not is_market_hours():
                time.sleep(60); continue
            end = datetime.now().strftime("%Y-%m-%d")
            start = (datetime.now() - timedelta(days=5)).strftime("%Y-%m-%d")
            df = client.history(symbol=symbol, exchange=exchange, interval=interval, start_date=start, end_date=end)
            if df is None or df.empty or len(df) < 35:
                time.sleep(60); continue

            close = df['close']
            ema12 = close.ewm(span=12, adjust=False).mean()
            ema26 = close.ewm(span=26, adjust=False).mean()
            macd = ema12 - ema26
            signal = macd.ewm(span=9, adjust=False).mean()
            vol_avg = df['volume'].rolling(20).mean()

            macd_cross_up = (macd.iloc[-2] > signal.iloc[-2]) and (macd.iloc[-3] <= signal.iloc[-3])
            macd_cross_dn = (macd.iloc[-2] < signal.iloc[-2]) and (macd.iloc[-3] >= signal.iloc[-3])
            vol_surge = df['volume'].iloc[-2] > 1.5 * vol_avg.iloc[-2]

            buy_signal = macd_cross_up and vol_surge
            sell_signal = macd_cross_dn and vol_surge

            print(f"[{strategy}] MACD={macd.iloc[-2]:.2f} Sig={signal.iloc[-2]:.2f} Vol={df['volume'].iloc[-2]} Pos={position}")

            if buy_signal and position <= 0:
                position = quantity
                resp = client.placesmartorder(strategy=strategy, symbol=symbol, action="BUY",
                    exchange=exchange, price_type="MARKET", product=product, quantity=quantity, position_size=position)
                print(f"[{strategy}] BUY: {resp}")
            elif sell_signal and position >= 0:
                position = -quantity
                resp = client.placesmartorder(strategy=strategy, symbol=symbol, action="SELL",
                    exchange=exchange, price_type="MARKET", product=product, quantity=quantity, position_size=position)
                print(f"[{strategy}] SELL: {resp}")
        except Exception as e:
            print(f"[{strategy}] Error: {e}")
        time.sleep(60)

if __name__ == "__main__":
    run()
