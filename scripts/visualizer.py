import matplotlib.pyplot as plt

def plot_session(results):
    steps = [r['step'] for r in results]
    mids = [r['mid'] for r in results]
    invs = [r['inv'] for r in results]
    pnls = [r['pnl'] for r in results]

    fig, (ax1, ax2, ax3) = plt.subplots(3, 1, figsize=(10, 12), sharex=True)

    # 1. Fiyat Grafiği
    ax1.plot(steps, mids, label='Orta Fiyat (Mid)', color='blue', marker='o')
    ax1.set_ylabel('Fiyat')
    ax1.legend()
    ax1.grid(True)

    # 2. Envanter Grafiği (Risk Takibi)
    ax2.bar(steps, invs, color='orange', alpha=0.6, label='Envanter (Inventory)')
    ax2.axhline(0, color='black', linestyle='--')
    ax2.set_ylabel('Pozisyon Adedi')
    ax2.legend()
    ax2.grid(True)

    # 3. Kümülatif P&L Grafiği (Performans)
    ax3.plot(steps, pnls, label='Toplam P&L', color='green', linewidth=2)
    ax3.set_ylabel('Kâr / Zarar')
    ax3.set_xlabel('İşlem Adımı')
    ax3.legend()
    ax3.grid(True)

    plt.suptitle('Aegis-LOB: Stoikov Strateji Performansı', fontsize=16)
    plt.tight_layout()
    plt.show()