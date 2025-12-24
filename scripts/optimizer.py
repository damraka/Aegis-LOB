import sys
import os
# Project root directory configuration for relative imports
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_dir)
if project_root not in sys.path:
    sys.path.append(project_root)
import pandas as pd
import numpy as np
import itertools
from strategy.stoikov_strategy import StoikovBot
from strategy.risk_analyzer import RiskAnalyzer



def run_headless_backtest(df, gamma, sigma, alpha_w):
    """
    Executes a high-speed backtest without visualization.
    Updated to handle the triple return value (bid, ask, qty) from StoikovBot.
    """
    bot = StoikovBot(gamma=gamma, sigma=sigma, k=1.5, stop_loss=-1500.0) 
    bot.base_alpha_weight = alpha_w
    risk_engine = RiskAnalyzer()
    
    trade_count = 0 

    for _, row in df.iterrows():
        mid = row['close']
        v_bid = row['bid_qty'] if 'bid_qty' in row else 1.0
        v_ask = row['ask_qty'] if 'ask_qty' in row else 1.0

        # CRITICAL FIX: Unpacking 3 values instead of 2
        my_bid, my_ask, current_qty = bot.calculate_quotes(mid, v_bid, v_ask)

        if not bot.is_stopped:
            # Match simulation: Using dynamic 'current_qty' calculated by Kelly Engine
            if row['low'] <= my_bid and my_bid > 0:
                bot.on_trade(1, my_bid, current_qty)
                trade_count += 1
            elif row['high'] >= my_ask and my_ask > 0:
                bot.on_trade(0, my_ask, current_qty)
                trade_count += 1

        # Real-time PnL calculation
        current_pnl = bot.cash + (bot.inventory * mid)
        risk_engine.add_pnl(current_pnl)
    
    metrics = risk_engine.calculate_metrics()
    metrics['trade_count'] = trade_count
    return metrics

def start_optimization(csv_path):
    print("🚀 OPTIMIZATION V3: ROBUST ZONE SCANNING INITIATED...")
    
    if not os.path.exists(csv_path):
        print(f"❌ ERROR: File not found at {csv_path}")
        return

    df = pd.read_csv(csv_path).head(2000)
    
    # --- Robust Parameter Space Configuration ---
    gammas = [0.1, 0.2, 0.3]
    sigmas = [0.002, 0.005, 0.01]
    alpha_weights = [0.3, 0.6, 0.9]
    
    combinations = list(itertools.product(gammas, sigmas, alpha_weights))
    best_sharpe = -np.inf
    best_params = None

    for g, s, a in combinations:
        stats = run_headless_backtest(df, g, s, a)
        
        if stats['trade_count'] > 5:
            print(f"⚙️ G:{g} S:{s} A:{a} | Trades: {stats['trade_count']} | PnL: {stats['total_pnl']:.2f} | Sharpe: {stats['sharpe_ratio']:.6f}")
            
            if stats['sharpe_ratio'] > best_sharpe:
                best_sharpe = stats['sharpe_ratio']
                best_params = (g, s, a)

    if best_params:
        print("\n" + "="*55)
        print(f"🏆 CHAMPION PROFILE: G:{best_params[0]} S:{best_params[1]} A:{best_params[2]}")
        print(f"📊 Best Sharpe Ratio: {best_sharpe:.6f}")
        print("="*55 + "\n")

if __name__ == "__main__":
    start_optimization("data/binance_BTC_USDT_1m.csv")