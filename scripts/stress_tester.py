import sys
import os
# Project root directory configuration for relative imports
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_dir)
if project_root not in sys.path:
    sys.path.append(project_root)
import pandas as pd
import numpy as np
from strategy.stoikov_strategy import StoikovBot
from strategy.risk_analyzer import RiskAnalyzer



def run_stress_test(scenario_name, file_path):
    """
    Executes the bot against a specific historical market regime.
    Updated to handle the triple return value (bid, ask, current_qty).
    """
    print(f"--- TEST SCENARIO: {scenario_name} ---")
    df = pd.read_csv(file_path)
    
    # Locking in champion settings for validation
    bot = StoikovBot(gamma=0.1, sigma=0.002, k=1.5, stop_loss=-500.0)
    risk_engine = RiskAnalyzer()

    for i, row in df.iterrows():
        mid = row['close']
        v_bid = row['bid_qty'] if 'bid_qty' in row else 1.0
        v_ask = row['ask_qty'] if 'ask_qty' in row else 1.0

        # CRITICAL FIX: Unpacking 3 values (bid, ask, Kelly-calculated quantity)
        my_bid, my_ask, current_qty = bot.calculate_quotes(mid, v_bid, v_ask)

        if not bot.is_stopped:
            # Match simulation: Using dynamic 'current_qty' instead of hardcoded 0.01
            if row['low'] <= my_bid and my_bid > 0:
                bot.on_trade(1, my_bid, current_qty)
            elif row['high'] >= my_ask and my_ask > 0:
                bot.on_trade(0, my_ask, current_qty)

        # Equity tracking: Cash + Market Value of Inventory
        current_pnl = bot.cash + (bot.inventory * mid)
        risk_engine.add_pnl(current_pnl)
        
        if bot.is_stopped: break

    # Calculating final performance scorecard
    stats = risk_engine.calculate_metrics()
    return stats

def start_mega_test():
    """
    Iterates through different market regimes to validate strategy robustness.
    """
    scenarios = {
        "Sideways Market": "data/binance_BTC_USDT_sideways.csv",
        "Extreme Downtrend (Crash)": "data/binance_BTC_USDT_crash.csv",
        "Extreme Uptrend (Moon)": "data/binance_BTC_USDT_moon.csv"
    }
    
    summary = []
    for name, path in scenarios.items():
        if os.path.exists(path):
            res = run_stress_test(name, path)
            summary.append({
                "Scenario": name, 
                "PnL": res['total_pnl'], 
                "Sharpe": res['sharpe_ratio'], 
                "MDD": res['max_drawdown']
            })
        else:
            print(f"⚠️ Warning: {path} not found, skipping scenario.")

    if summary:
        print("\n" + "="*60)
        print("🏁 GLOBAL STRESS TEST SUMMARY REPORT")
        print("="*60)
        report_df = pd.DataFrame(summary)
        print(report_df.to_string(index=False))
        print("="*60)

if __name__ == "__main__":
    start_mega_test()