import sys
import os
# Project root directory setup for relative imports
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_dir)
if project_root not in sys.path:
    sys.path.append(project_root)
import numpy as np
import torch
import aegis_lob as lob
from strategy.ai_model import PricePredictorLSTM



class StoikovBot:
    def __init__(self, gamma=0.1, sigma=0.002, k=1.5, stop_loss=-50.0, comm_rate=0.0005, slippage=0.0001):
        # --- Core Strategy Parameters ---
        self.base_gamma = gamma 
        self.sigma = sigma      
        self.k = k              
        self.stop_loss_limit = stop_loss
        self.comm_rate = comm_rate
        self.slippage_rate = slippage
        
        # --- Portfolio and Bankroll Management ---
        self.initial_balance = 10000.0  
        self.cash = 10000.0
        self.inventory = 0.0
        self.max_inventory = 0.03       
        self.is_stopped = False
        
        # --- Kelly Criterion Settings ---
        self.win_rate = 0.4631   
        self.profit_factor = 1.25 
        self.kelly_fraction = 0.20 
        
        # --- Profit Protection ---
        self.max_pnl = -np.inf
        self.profit_lock_threshold = 10.0 
        self.drawdown_limit = 0.20        
        
        # --- Signal Modules ---
        self.base_alpha_weight = 0.8
        self.last_ai_adj = 0.0
        
        # --- MOON SHIELD PARAMETERS ---
        self.momentum_threshold = 0.0015 # Vertical rally detection (0.15% move)
        
        # --- AI Engine Initialization ---
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.model = PricePredictorLSTM().to(self.device)
        self.model.eval()
        self.price_history = []

    def _calculate_kelly_qty(self, mid_price):
        """Calculates dynamic order size based on Kelly Criterion."""
        p = self.win_rate
        b = self.profit_factor
        f_star = (p * (b + 1) - 1) / b
        safe_f = max(0, f_star) * self.kelly_fraction
        equity = self.cash + (self.inventory * mid_price)
        target_qty = (equity * safe_f) / mid_price
        return np.clip(target_qty, 0.005, self.max_inventory)

    def calculate_quotes(self, mid_price, best_bid_qty, best_ask_qty):
        if self.is_stopped: return 0.0, 0.0, 0.0
        self.price_history.append(mid_price)
        if len(self.price_history) > 100: self.price_history.pop(0)

        # 1. P&L AND RISK MONITORING
        current_pnl = (self.cash - self.initial_balance) + (self.inventory * mid_price)
        if current_pnl < self.stop_loss_limit:
            self.is_stopped = True
            return 0.0, 0.0, 0.0
        if current_pnl > self.max_pnl: self.max_pnl = current_pnl
        if self.max_pnl > self.profit_lock_threshold:
            if current_pnl < self.max_pnl * (1 - self.drawdown_limit):
                self.is_stopped = True
                return 0.0, 0.0, 0.0

        # 2. DYNAMIC POSITION SIZING
        order_qty = self._calculate_kelly_qty(mid_price)

        # 3. ALPHA SIGNAL AND TREND ANALYSIS
        raw_ai_signal = self._get_ai_signal(mid_price)
        trend_strength = raw_ai_signal / mid_price 
        inv_ratio = self.inventory / self.max_inventory
        
        bid_bias, ask_bias = 1.0, 1.0
        
        # 4. SPREAD CALCULATION
        market_vol = np.std(self.price_history[-30:]) / mid_price if len(self.price_history) > 30 else self.sigma
        vol_multiplier = np.clip(market_vol / 0.0002, 1.0, 6.0)
        min_barrier = mid_price * self.comm_rate * 4.0 
        base_spread = (2 / self.base_gamma) * np.log(1 + self.base_gamma / self.k)
        final_spread = max(base_spread, min_barrier) * vol_multiplier

        # 5. MOON & CRASH SHIELD LOGIC
        if trend_strength > self.momentum_threshold: # AGGRESSIVE MOON (Vertical Rally)
            # CEASE-FIRE: Halt all sell orders to prevent short-squeezing
            my_ask = 0.0 
            my_bid = mid_price - (final_spread * 2.0) # Move bid significantly lower
            return my_bid, my_ask, order_qty

        elif trend_strength > 0.0005: # MODERATE MOON
            ask_bias, bid_bias = 15.0, 0.2 # Extreme skew to discourage sells
            reservation_price = mid_price + (abs(inv_ratio) * mid_price * 0.002)
        elif trend_strength < -0.0005: # CRASH PROTECTION
            bid_bias, ask_bias = 10.0, 0.5
            reservation_price = mid_price + raw_ai_signal
        else: # NORMAL MEAN-REVERTING REGIME
            dynamic_gamma = self.base_gamma * np.clip(np.exp(abs(inv_ratio) * 4), 1.0, 50.0)
            reservation_price = mid_price - (self.inventory * dynamic_gamma * (self.sigma**2)) + (raw_ai_signal * 0.8)

        # 6. FINAL QUOTE GENERATION
        my_bid = reservation_price - (final_spread / 2) * bid_bias
        my_ask = reservation_price + (final_spread / 2) * ask_bias

        # Inventory Cap Enforcement
        if self.inventory >= self.max_inventory * 0.95: my_bid = 0.0
        if self.inventory <= -self.max_inventory * 0.95: my_ask = 0.0

        return my_bid, my_ask, order_qty

    def on_trade(self, side, price, qty):
        """Updates bankroll and inventory with execution data."""
        slippage = 1.0 + self.slippage_rate if (side == lob.Side.BUY or side == 1) else 1.0 - self.slippage_rate
        exec_price = price * slippage
        val = exec_price * qty
        fee = val * self.comm_rate
        if side == lob.Side.BUY or side == 1:
            self.inventory += qty
            self.cash -= (val + fee)
        else:
            self.inventory -= qty
            self.cash += (val - fee)

    def _get_ai_signal(self, mid_price):
        """Fetches trend signal from LSTM model."""
        if len(self.price_history) < 50: return 0.0
        recent = np.array(self.price_history[-50:]).reshape(-1, 1)
        p_min, p_max = np.min(recent), np.max(recent)
        scaled = (recent - p_min) / (p_max - p_min + 1e-8)
        tensor = torch.from_numpy(scaled).float().unsqueeze(0).to(self.device)
        with torch.no_grad():
            pred = self.model(tensor).item()
        return (pred * (p_max - p_min + 1e-8) + p_min - mid_price) * self.base_alpha_weight