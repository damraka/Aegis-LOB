import os

class LiveRiskDashboard:
    def __init__(self):
        self.step = 0
        # Clear the terminal for a clean start (supports Windows 'cls' and Unix 'clear')
        os.system('cls' if os.name == 'nt' else 'clear')

    def update(self, step, mid, inv, cash, pnl, ai_adj):
        """
        Updates the terminal display with real-time portfolio and risk metrics.
        """
        self.step = step
        # Refresh the screen every 50 steps to ensure readability without terminal lag
        if step % 50 == 0:
            os.system('cls' if os.name == 'nt' else 'clear')
            print("="*60)
            print(f"      AEGIS-LOB: LIVE RISK DASHBOARD (Step: {step})")
            print("="*60)
            print(f"Market Mid-Price    : {mid:>15.2f}")
            print(f"Current Inventory   : {inv:>15.8f} Units")
            print(f"Cash Balance        : {cash:>15.2f} USDT")
            print(f"Cumulative P&L      : {pnl:>15.2f} USDT")
            print("-" * 60)
            
            # Dynamic Strategy Mode Detection based on AI Signal intensity
            # Determines if the bot is in trend-following or mean-reversion mode
            if abs(ai_adj) > 0.005:
                status = "AGGRESSIVE (Trend-Following)"
            else:
                status = "DEFENSIVE (Classical Stoikov)"
                
            print(f"Operating Mode      : {status}")
            print(f"AI Alpha Signal     : {ai_adj:>15.4f}")
            print("="*60)
            print("\nSimulation in progress...")