"""
Generates a 3-year synthetic daily price series with three distinct
regimes (uptrend, choppy/sideways, strong uptrend) via geometric Brownian
motion with regime-specific drift and volatility. Live market data
wasn't reachable in this environment (network/SSL restriction) - this
produces a reproducible, clearly-labeled synthetic substitute so the
backtest logic can be verified end-to-end. See the README's data note.

Run:
    python generate_data.py
"""

import os
import numpy as np
import pandas as pd

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, "data")

np.random.seed(42)

TRADING_DAYS_PER_YEAR = 252
START_PRICE = 100.0

regimes = [
    {"name": "Uptrend", "days": TRADING_DAYS_PER_YEAR, "annual_drift": 0.15, "annual_vol": 0.18},
    {"name": "Choppy/Sideways", "days": TRADING_DAYS_PER_YEAR, "annual_drift": 0.00, "annual_vol": 0.22},
    {"name": "Strong Uptrend", "days": TRADING_DAYS_PER_YEAR, "annual_drift": 0.25, "annual_vol": 0.16},
]


def main():
    os.makedirs(DATA_DIR, exist_ok=True)

    prices = [START_PRICE]
    regime_labels = []
    dates = pd.bdate_range(start="2023-01-02", periods=sum(r["days"] for r in regimes))

    for regime in regimes:
        daily_drift = regime["annual_drift"] / TRADING_DAYS_PER_YEAR
        daily_vol = regime["annual_vol"] / np.sqrt(TRADING_DAYS_PER_YEAR)
        for _ in range(regime["days"]):
            shock = np.random.normal(daily_drift - 0.5 * daily_vol ** 2, daily_vol)
            prices.append(prices[-1] * np.exp(shock))
            regime_labels.append(regime["name"])

    df = pd.DataFrame({"Date": dates, "Close": prices[1:], "Regime": regime_labels})
    df.to_csv(os.path.join(DATA_DIR, "synthetic_prices.csv"), index=False)
    print(f"Generated {len(df)} days of synthetic price data across {len(regimes)} regimes.")
    print(df.groupby("Regime")["Close"].agg(["first", "last"]))


if __name__ == "__main__":
    main()
