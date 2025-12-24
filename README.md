# Aegis-LOB: Hybrid High-Frequency Trading Framework

Aegis-LOB is a modular quantitative trading framework designed for high-frequency market making. It bridges a high-performance **C++ Limit Order Book (LOB)** core with a flexible **Python Alpha Layer**. The system implements a modified **Avellaneda-Stoikov** inventory model, enhanced by LSTM-driven price signals and dynamic risk sizing via the Kelly Criterion.

---

## Technical Architecture

The framework is divided into two distinct layers to balance execution speed with research flexibility:

* **Execution Core (C++):** Optimized for $O(1)$ order management. It utilizes iterator mapping to achieve near-instantaneous order cancellations and matching.
* **Strategy Layer (Python):** Handles high-level logic, including LSTM signal processing (via PyTorch), dynamic spread calculation, and real-time risk management.
* **Bridge (Pybind11):** Provides a low-latency interface between the C++ matching engine and the Python strategy module.

---

## Build and Installation

To deploy the framework, follow the multi-stage build process:

1.  **Dependencies:** Ensure all quantitative and deep learning libraries are installed via the requirements file.
2.  **Core Compilation:** Compile the C++ matching engine into a Python-accessible module:
    ```bash
    python setup.py build_ext --inplace
    ```
3.  **Alpha Training:** Initialize the LSTM signal module by training on historical OHLCV data:
    ```bash
    python scripts/train_ai.py
    ```

---

## Configuration Parameters

The behavior of the Market Maker is governed by several key parameters within the `StoikovBot` engine:

| Parameter | Symbol | Function |
| :--- | :--- | :--- |
| **Risk Aversion** | $\gamma$ | Controls the intensity of inventory skewing. Higher $\gamma$ leads to more aggressive price adjustments to offload inventory. |
| **Market Volatility** | $\sigma$ | Represents the standard deviation of price returns. It directly scales the inventory risk premium in the reservation price formula. |
| **Liquidity Density** | $k$ | Simulates market depth. It determines the probability of a limit order being filled at a certain distance from the mid-price. |
| **Alpha Weight** | $w$ | The sensitivity multiplier for the LSTM signal. High values shift the bot from mean-reversion toward trend-following. |
| **Momentum Threshold** | $\tau$ | Trigger for the "Moon Shield." Halts sell-side quoting during extreme vertical price action to prevent adverse selection. |

---

## Mathematical Foundation

The bot calculates the **Reservation Price** ($r$)—the price at which the market maker is indifferent to their current inventory—using the following derivation:

$$r(s, t, q) = s - (q \cdot \gamma \cdot \sigma^2 \cdot (T - t)) + \alpha$$

Where:
* $s$ = Current Mid-Price
* $q$ = Current Inventory (Position)
* $\alpha$ = AI-derived micro-price trend signal

Dynamic position sizing is governed by the **Fractional Kelly Criterion** to ensure long-term bankroll preservation:

$$f^* = \left( \frac{p(b+1) - 1}{b} \right) \cdot \text{fraction}$$

---

## Risk Disclosure and Limitations

As an HFT framework, Aegis-LOB is susceptible to several specific quantitative risks:

* **Adverse Selection:** The "Toxic Flow" risk where the bot provides liquidity to informed traders (whales), leading to inventory being filled at prices that immediately move against the position.
* **Inventory Risk (Short Squeeze):** In high-momentum "Moon" regimes, the bot may accumulate a large short position while prices continue to rise, resulting in significant drawdowns despite the "Shield" logic.
* **Latency Sensitivity:** While the core is C++, the Python strategy overhead and network round-trip times (RTT) can lead to "stale quotes," where orders are filled at outdated prices.
* **Regime Drift:** The LSTM model is trained on historical data. If market conditions change (e.g., a volatility spike or liquidity crunch), the alpha signal may become uncorrelated, leading to sub-optimal quoting.