import sys
import os
# Project root directory setup
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_dir)
if project_root not in sys.path:
    sys.path.append(project_root)
import numpy as np
import matplotlib.pyplot as plt
import aegis_lob as lob
from strategy.stoikov_strategy import StoikovBot
from data_logger import DataLogger
from dashboard import LiveRiskDashboard



def run_final_grand_simulation(steps=10000, start_price=100.0, sigma=0.05, drift=0.002, slippage_factor=0.001):
    """
    Executes a high-fidelity Grand Final simulation with dynamic risk locking.
    """
    # 1. Initialization
    logger = DataLogger("grand_simulation_final.csv")
    dashboard = LiveRiskDashboard()
    
    # Champion parameters: Gamma=0.15, Sigma adjusted for 10k steps
    bot = StoikovBot(gamma=0.15, sigma=sigma, k=1.5, stop_loss=-250.0, comm_rate=0.0005)
    
    prices = [start_price]
    pnls = [10000.0] # Equity focus (Initial Cash)
    invs = [0.0]
    current_price = start_price

    print(f"--- 🏁 GRAND FINAL SIMULATION STARTED: {steps} STEPS ---")

    for i in range(steps):
        # 2. Stochastic Price Action (GBM)
        noise = np.random.normal(0, sigma)
        current_price += noise + drift
        prices.append(current_price)

        # 3. Generate Quotes & Capture Telemetry
        my_bid, my_ask, current_qty = bot.calculate_quotes(current_price, 1.0, 1.0)
        current_pnl = bot.cash + (bot.inventory * current_price)

        # TELEMETRY LOGGING: Essential for visualizer.py
        logger.log(i, current_price, my_bid, my_ask, bot.inventory, current_pnl)

        # 4. Risk Management: Trailing Profit Lock
        if bot.is_stopped:
            print(f"❌ CAPSULE BREACHED! Step {i}: Risk Lock engaged. Final Equity: {current_pnl:.2f}")
            break

        # 5. Trade Execution Simulation
        event = np.random.random()
        if event < 0.35: # Liquidity hit on Bid
            exec_price = my_bid * (1 + slippage_factor)
            bot.on_trade(lob.Side.BUY, exec_price, current_qty)
        elif event < 0.70: # Liquidity hit on Ask
            exec_price = my_ask * (1 - slippage_factor)
            bot.on_trade(lob.Side.SELL, exec_price, current_qty)

        # 6. Record Stats
        pnls.append(current_pnl)
        invs.append(bot.inventory)
        
        if i % 100 == 0:
            dashboard.update(i, current_price, bot.inventory, bot.cash, current_pnl, getattr(bot, 'last_ai_adj', 0.0))

    # 7. Persistence
    logger.save()
    print(f"--- ✅ SIMULATION FINISHED. Final P&L: {current_pnl:.2f} ---")
    return prices, pnls, invs

if __name__ == "__main__":
    # RUN SIMULATION
    raw_prices, raw_pnls, raw_invs = run_final_grand_simulation()
    
    # --- GRAPHING FIX: SYNCING LIST LENGTHS ---
    # Ensure all lists match the actual steps executed before the stop-loss
    actual_steps = len(raw_pnls)
    steps_range = np.arange(actual_steps)
    prices = raw_prices[:actual_steps]
    pnls = raw_pnls
    invs = raw_invs

    plt.figure(figsize=(14, 12), facecolor='#f7f7f7')
    
    # Subplot 1: BTC Mid-Price
    plt.subplot(3, 1, 1)
    plt.plot(steps_range, prices, color='#1f77b4', linewidth=1.5, label='BTC Mid-Price')
    plt.title(f'Aegis-LOB: Performance Report (Terminated at Step {actual_steps-1})', fontsize=14, fontweight='bold')
    plt.ylabel('Price (USDT)')
    plt.grid(True, alpha=0.3, linestyle='--')
    plt.legend()

    # Subplot 2: Equity Curve (Net P&L)
    plt.subplot(3, 1, 2)
    plt.fill_between(steps_range, pnls, 10000, color='green', alpha=0.2)
    plt.plot(steps_range, pnls, color='darkgreen', linewidth=2, label='Total Equity (Cash + Position)')
    plt.axhline(10000, color='red', linestyle='--', linewidth=1, label='Break-even')
    plt.ylabel('Equity (USDT)')
    plt.grid(True, alpha=0.3, linestyle='--')
    plt.legend()

    # Subplot 3: Inventory Exposure
    plt.subplot(3, 1, 3)
    plt.step(steps_range, invs, color='#ff7f0e', linewidth=1.5, label='Inventory (BTC)')
    plt.axhline(0, color='black', linewidth=0.8)
    plt.ylabel('Units')
    plt.xlabel('Simulation Steps')
    plt.grid(True, alpha=0.3, linestyle='--')
    plt.legend()

    plt.tight_layout()
    plt.show()