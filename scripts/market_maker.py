import sys
import os
# Project root setup for relative imports
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_dir)
if project_root not in sys.path:
    sys.path.append(project_root)
import time
import aegis_lob as lob

class PositionTracker:
    def __init__(self):
        self.position = 0      # Current inventory (net position)
        self.cash = 0.0        # Cash balance
        self.realized_pnl = 0.0

    def update_position(self, side, quantity, price):
        """
        Updates inventory and cash balance based on trade execution.
        """
        if side == lob.Side.BUY:
            self.position += quantity
            self.cash -= quantity * price
        else:
            self.position -= quantity
            self.cash += quantity * price
        
        print(f"--- UPDATE --- Position: {self.position} | Cash: {self.cash:.2f}")

tracker = PositionTracker()
ob = lob.OrderBook()

# The core strategy/trade logic resides here
def trade_loop():
    # 1. Provide initial liquidity to the book
    # Resting Bid at 100.0, Resting Ask at 105.0
    ob.add_order(lob.Order(1, 100.0, 10, lob.Side.BUY, int(time.time())))
    ob.add_order(lob.Order(2, 105.0, 10, lob.Side.SELL, int(time.time())))
    
    # SCENARIO: An aggressive sell order arrives (hitting our resting bid)
    print("\n[Market] Aggressive Market Sell order received!")
    ob.add_order(lob.Order(3, 100.0, 4, lob.Side.SELL, int(time.time())))
    
    # Simulating a Fill Event:
    # Our Buy Order (Order ID: 1) was partially filled for 4 units.
    # Note: In production, this is triggered by a real-time matching event.
    print("[Fill] Our Buy Order ID: 1 filled for 4 units @ 100.0")
    tracker.update_position(lob.Side.BUY, 4, 100.0)

    # Calculate real-time portfolio metrics
    mid_price = ob.get_mid_price()
    
    # Unrealized PnL (Equity) = Cash + (Position * Mid Price)
    # Formally: $$TotalValue = Cash + (q \times Mid)$$
    total_value = tracker.cash + (tracker.position * mid_price)
    
    print(f"\nTotal Portfolio Value (Equity): {total_value:.2f}")

if __name__ == "__main__":
    trade_loop()