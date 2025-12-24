import sys
import os
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_dir)
if project_root not in sys.path:
    sys.path.append(project_root)
import pandas as pd
import numpy as np
import aegis_lob as lob
from strategy.stoikov_strategy import StoikovBot
from strategy.risk_analyzer import RiskAnalyzer
from visualizer import plot_session
from dashboard import LiveRiskDashboard
from data_logger import DataLogger



def run_real_backtest(file_path):
    ob = lob.OrderBook()
    
    # Bot Setup (Kelly ve Stoikov Parameters)
    bot = StoikovBot(gamma=0.7, sigma=0.005, k=1.5, stop_loss=-50.0)
    
    dashboard = LiveRiskDashboard()
    logger = DataLogger("real_data_backtest_log.csv")
    risk_engine = RiskAnalyzer()

    # 1. Veriyi Yükle
    df = pd.read_csv(file_path)
    results = []

    print(f"--- DYNAMIC RISK (KELLY) ANALYSIS HAS STARTED: {file_path} ---")

    for i, row in df.iterrows():
        mid = row['close']
        high = row['high']
        low = row['low']
        v_bid = row['bid_qty'] if 'bid_qty' in row else 1.0
        v_ask = row['ask_qty'] if 'ask_qty' in row else 1.0

        # --- 2. GET THE QUOTES FROM THE BOT ---
        my_bid, my_ask, qty_kelly = bot.calculate_quotes(mid, v_bid, v_ask)

        # 3. Pairing Simulation
        if not bot.is_stopped:
            # Is the buy order filled? (Kelly Qty amount)
            if low <= my_bid and my_bid > 0:
                bot.on_trade(lob.Side.BUY, my_bid, qty_kelly)
            # Did the sell order get filled? (Kelly Qty amount)
            elif high >= my_ask and my_ask > 0:
                bot.on_trade(lob.Side.SELL, my_ask, qty_kelly)

        # 4. Calculate P&L and Risk Metrics
        # P&L Calculation
        current_pnl = (bot.cash - bot.initial_balance) + (bot.inventory * mid)
        risk_engine.add_pnl(current_pnl)
        
        # Stop-Loss and Emergency Exit
        if bot.is_stopped and abs(bot.inventory) > 0.0001:
            side = lob.Side.SELL if bot.inventory > 0 else lob.Side.BUY
            bot.on_trade(side, mid, abs(bot.inventory))
            bot.inventory = 0
            current_pnl = (bot.cash - bot.initial_balance)

        # 5. Record Keeping
        results.append({
            "step": i, 
            "mid": mid, 
            "inv": bot.inventory, 
            "pnl": current_pnl, 
            "bid": my_bid, 
            "ask": my_ask
        })
        
        if i % 20 == 0:
            dashboard.update(i, mid, bot.inventory, bot.cash, current_pnl, bot.last_ai_adj)
            logger.log(i, mid, my_bid, my_ask, bot.inventory, current_pnl)

        if bot.is_stopped and abs(bot.inventory) < 0.0001:
            break

    logger.save()
    
    # --- REPORTING ---
    stats = risk_engine.calculate_metrics()
    print("\n" + "="*45)
    print(" 📈 FINAL STRATEGY SCORECARD (KELLY INTEGRATED)")
    print("="*45)
    print(f"💰 Total P&L             : {stats['total_pnl']:.2f} USDT")
    print(f"📊 Sharpe Ratio (Step) : {stats['sharpe_ratio']:.4f}")
    print(f"📉 Max Drawdown        : {stats['max_drawdown']:.2f} USDT")
    print(f"🎯 Win Rate            : %{stats['win_rate']*100:.2f}")
    print("="*45 + "\n")
    
    return results

if __name__ == "__main__":
    csv_path = "data/binance_BTC_USDT_1m.csv"
    if os.path.exists(csv_path):
        backtest_results = run_real_backtest(csv_path)
        if backtest_results:
            plot_session(backtest_results)
    else:
        print(f"Error: {csv_path} file cannot be found!")