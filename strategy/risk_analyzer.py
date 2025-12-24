import numpy as np

class RiskAnalyzer:
    def __init__(self):
        self.pnl_history = []
        self.returns = []

    def add_pnl(self, current_pnl):
        if len(self.pnl_history) > 0:
            # Calculate return 
            ret = current_pnl - self.pnl_history[-1]
            self.returns.append(ret)
        self.pnl_history.append(current_pnl)

    def calculate_metrics(self):
        if not self.returns:
            return {}

        returns_arr = np.array(self.returns)
        pnl_arr = np.array(self.pnl_history)

        # 1. Total P&L
        total_pnl = pnl_arr[-1]

        # 2. Sharpe Ratio
        # Formula: mean(returns) / std(returns)
        sharpe = np.mean(returns_arr) / (np.std(returns_arr) + 1e-8)

        # 3. Maximum Drawdown (MDD)
        peak = np.maximum.accumulate(pnl_arr)
        drawdown = peak - pnl_arr
        max_drawdown = np.max(drawdown)

        # 4. Win Rate
        win_rate = np.sum(returns_arr > 0) / len(returns_arr)

        return {
            "total_pnl": total_pnl,
            "sharpe_ratio": sharpe,
            "max_drawdown": max_drawdown,
            "win_rate": win_rate
        }