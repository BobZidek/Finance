"""
Generates two synthetic daily price series that are genuinely cointegrated
by construction: both share a common non-stationary trend component, and
their log-price spread follows a stationary mean-reverting (AR(1))
process plus idiosyncratic noise. This lets the cointegration test in
pairs_trading_model.py verify a real, known relationship rather than
testing against arbitrary data. Live market data wasn't reachable in
this environment; see the README's data note.

Run:
    python generate_data.py
"""

import os
import numpy as np
import pandas as pd

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, "data")

np.random.seed(11)
N_DAYS = 500
A0, B0 = 100.0, 60.0
COMMON_TREND_VOL = 0.012
SPREAD_AR_PHI = 0.96
SPREAD_SHOCK_VOL = 0.015
IDIOSYNCRATIC_VOL = 0.006


def main():
    os.makedirs(DATA_DIR, exist_ok=True)

    common_trend = np.cumsum(np.random.normal(0, COMMON_TREND_VOL, N_DAYS))

    spread = np.zeros(N_DAYS)
    for t in range(1, N_DAYS):
        spread[t] = SPREAD_AR_PHI * spread[t - 1] + np.random.normal(0, SPREAD_SHOCK_VOL)

    idio_a = np.random.normal(0, IDIOSYNCRATIC_VOL, N_DAYS)

    log_price_a = np.log(A0) + common_trend + idio_a
    log_price_b = np.log(B0) + common_trend + spread

    dates = pd.bdate_range(start="2023-01-02", periods=N_DAYS)
    df = pd.DataFrame({"Date": dates, "Price_A": np.exp(log_price_a), "Price_B": np.exp(log_price_b)})
    df.to_csv(os.path.join(DATA_DIR, "pair_prices.csv"), index=False)
    print(f"Generated {N_DAYS} days of two cointegrated synthetic price series.")
    print(df.head())


if __name__ == "__main__":
    main()
