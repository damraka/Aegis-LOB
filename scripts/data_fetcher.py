import sys
import os
import ccxt
import pandas as pd
from datetime import datetime

# Project root directory setup for relative imports
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_dir)
if project_root not in sys.path:
    sys.path.append(project_root)

def fetch_binance_data(symbol='BTC/USDT', timeframe='1m', limit=1000):
    """
    Fetches historical market data from Binance and saves it to a CSV file.
    Utilizes ccxt for standardized exchange interaction.
    """
    print(f"\n--- 📥 DATA ACQUISITION STARTED: {symbol} ---")
    
    # 1. Establish Binance Connection
    # enableRateLimit is crucial to prevent IP bans during high-frequency requests
    exchange = ccxt.binance({
        'enableRateLimit': True, 
    })

    try:
        # 2. Fetch OHLCV (Open, High, Low, Close, Volume) Data
        print(f"[INFO] Fetching {limit} '{timeframe}' candle sticks...")
        ohlcv = exchange.fetch_ohlcv(symbol, timeframe=timeframe, limit=limit)
        
        # 3. DataFrame Construction
        df = pd.DataFrame(ohlcv, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
        
        # Convert Unix timestamp (ms) to a human-readable datetime format
        df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
        
        # 4. Directory and File Path Management
        if not os.path.exists("data"):
            os.makedirs("data")
            print("[INFO] 'data/' directory created.")
            
        file_name = f"binance_{symbol.replace('/', '_')}_{timeframe}.csv"
        file_path = os.path.join("data", file_name)
        
        # 5. Export to CSV
        df.to_csv(file_path, index=False)
        print(f"✅ SUCCESS! Data archived at: {file_path}")
        print(f"📊 Series Start: {df['timestamp'].iloc[0]}")
        print(f"📊 Series End  : {df['timestamp'].iloc[-1]}")
        
        return file_path

    except Exception as e:
        print(f"❌ ERROR: Failed to fetch market data: {e}")
        return None

if __name__ == "__main__":
    # Example: Fetching the last 1000 minutes for the backtester
    fetch_binance_data(symbol='BTC/USDT', timeframe='1m', limit=1000)