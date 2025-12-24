import matplotlib.pyplot as plt

def plot_session(results):
    steps = [r['step'] for r in results]
    mids = [r['mid'] for r in results]
    invs = [r['inv'] for r in results]
    pnls = [r['pnl'] for r in results]

    fig, (ax1, ax2, ax3) = plt.subplots(3, 1, figsize=(10, 12), sharex=True)

    # 1. Price Chart
    ax1.plot(steps, mids, label='Mid Price', color='blue', marker='o')
    ax1.set_ylabel('Price')
    ax1.legend()
    ax1.grid(True)

    # 2. Inventory Chart
    ax2.bar(steps, invs, color='orange', alpha=0.6, label='Inventory')
    ax2.axhline(0, color='black', linestyle='--')
    ax2.set_ylabel('Position Size')
    ax2.legend()
    ax2.grid(True)

    # 3. Cumulative P&L Chart
    ax3.plot(steps, pnls, label='Total P&L', color='green', linewidth=2)
    ax3.set_ylabel('Profit / Loss')
    ax3.set_xlabel('Step')
    ax3.legend()
    ax3.grid(True)

    plt.suptitle('Aegis-LOB: Stoikov Strategy Performance', fontsize=16)
    plt.tight_layout()
    plt.show()