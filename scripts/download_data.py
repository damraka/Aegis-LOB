import sys
import os
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_dir)
if project_root not in sys.path:
    sys.path.append(project_root)
import ccxt
import pandas as pd
from datetime import datetime

def download_binance_data(symbol, timeframe, start_str, end_str, filename):
    """
    Downloads historical OHLCV data from Binance.
    Mocks Bid/Ask quantities as 1.0 for Stoikov backtesting compatibility.
    """
    exchange = ccxt.binance()
    start_ts = exchange.parse8601(start_str)
    end_ts = exchange.parse8601(end_str)
    
    print(f"📥 Downloading: {filename}...")
    all_ohlcv = []
    
    while start_ts < end_ts:
        ohlcv = exchange.fetch_ohlcv(symbol, timeframe, start_ts, limit=1000)
        if not ohlcv: break
        start_ts = ohlcv[-1][0] + 1
        all_ohlcv.extend(ohlcv)
        if len(ohlcv) < 1000: break

    df = pd.DataFrame(all_ohlcv, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
    
    # Expected format: Historical OHLCV does not include LOB imbalance (OBI).
    # We mock bid_qty and ask_qty as 1.0 for backtest consistency.
    df['bid_qty'] = 1.0
    df['ask_qty'] = 1.0
    
    os.makedirs('data', exist_ok=True)
    df.to_csv(f"data/{filename}", index=False)
    print(f"✅ Saved Successfully: data/{filename}")

if __name__ == "__main__":
    # 1. CRASH SCENARIO: August 2024 Nikkei Shock (Extreme Downtrend)
    download_binance_data('BTC/USDT', '1m', '2024-08-05T00:00:00Z', '2024-08-06T00:00:00Z', 'binance_BTC_USDT_crash.csv')
    
    # 2. MOON SCENARIO: November 2024 Post-Election Rally (Extreme Uptrend)
    download_binance_data('BTC/USDT', '1m', '2024-11-06T00:00:00Z', '2024-11-08T00:00:00Z', 'binance_BTC_USDT_moon.csv')
    
    # 3. SIDEWAYS SCENARIO: September 2024 Consolidation (Sideways Market)
    download_binance_data('BTC/USDT', '1m', '2024-09-15T00:00:00Z', '2024-09-17T00:00:00Z', 'binance_BTC_USDT_sideways.csv')