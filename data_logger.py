import pandas as pd
import os

class DataLogger:
    def __init__(self, filename="market_data.csv"):
        """
        Initializes the Aegis-LOB telemetry service.
        Persists simulation data into the 'data/' directory for post-trade analysis.
        """
        self.filename = os.path.join("data", filename)
        self.buffer = []
        
        # Ensure the persistence directory exists
        if not os.path.exists("data"):
            os.makedirs("data")

    def log(self, step, mid, bid, ask, inv, pnl):
        """
        Captures real-time telemetry from the Stoikov Engine and Position Tracker.
        """
        self.buffer.append({
            "step": step,
            "mid": mid,
            "bid": bid,
            "ask": ask,
            "inv": inv,
            "pnl": pnl
        })

    def save(self):
        """
        Serializes buffered logs to CSV. Crucial for 'visualizer.py' analytics.
        """
        if not self.buffer:
            print(f"⚠️ [WARNING] No data captured for {self.filename}. Check log() calls.")
            return

        df = pd.DataFrame(self.buffer)
        df.to_csv(self.filename, index=False)
        print(f"--- ✅ TELEMETRY SECURED: {self.filename} ({len(self.buffer)} records) ---")

    def clear(self):
        """Clears the buffer for fresh simulation runs."""
        self.buffer = []