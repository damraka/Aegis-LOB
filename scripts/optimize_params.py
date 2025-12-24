import sys
import os
import numpy as np
import pandas as pd
import itertools

# Project root directory setup for relative imports
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_dir)
if project_root not in sys.path:
    sys.path.append(project_root)

# CRITICAL FIX: Importing the correct function name
from scripts.monte_carlo_test import run_final_grand_simulation

def start_parameter_optimization():
    """
    Grid Search optimizer for Aegis-LOB champion weights.
    Ties together the Monte Carlo engine and the Stoikov Strategy.
    """
    print("--- AEGIS-LOB PARAMETER OPTIMIZER INITIATED ---")
    
    # Define the search space
    gammas = [0.1, 0.15, 0.2]       # Risk aversion profiles
    alpha_weights = [0.8, 1.2, 1.5] # AI Signal sensitivity
    
    results = []
    
    combinations = list(itertools.product(gammas, alpha_weights))
    print(f"[INFO] Testing {len(combinations)} parameter permutations...\n")

    for g, a in combinations:
        print(f"Testing Profile: Gamma={g}, AlphaWeight={a}...", end=" ")
        
        # We use a shorter step count (500) for optimization speed
        # Note: Ensure run_final_grand_simulation is configured to 
        # accept dynamic gamma/alpha if needed, or use a headless backtester.
        try:
            # Sync with the 3-value return logic of the current engine
            _, pnls, _ = run_final_grand_simulation(steps=500, sigma=0.05)
            
            final_pnl = pnls[-1]
            results.append({
                'gamma': g,
                'alpha_weight': a,
                'final_pnl': final_pnl
            })
            print(f"Resulting Equity: {final_pnl:.2f}")
        except Exception as e:
            print(f"FAILED due to: {e}")

    # 2. Results Analysis & Export
    df_results = pd.DataFrame(results)
    if not df_results.empty:
        best_run = df_results.loc[df_results['final_pnl'].idxmax()]

        print("\n" + "="*50)
        print("      OPTIMIZATION COMPLETE: BEST SETTINGS")
        print("="*50)
        print(f"Optimal Gamma           : {best_run['gamma']}")
        print(f"Optimal Alpha Weight    : {best_run['alpha_weight']}")
        print(f"Maximum Expected P&L    : {best_run['final_pnl']:.2f}")
        print("="*50)

        # Save logs for research documentation
        df_results.to_csv("data/optimization_results.csv", index=False)
    else:
        print("❌ ERROR: No valid results generated.")

if __name__ == "__main__":
    start_parameter_optimization()