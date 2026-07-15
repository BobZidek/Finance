"""
Generates a 40-stock x 36-month panel of Value/Momentum/Quality factor
scores and realized forward monthly returns, extending the single-
snapshot approach in quant/multi-factor-stock-ranking into a genuine
multi-period panel - addressing that project's own flagged limitation.
Each month's cross-section is drawn independently (a simplification -
real factor exposures are persistent across time; see the theory doc).
Live market/fundamental data wasn't reachable in this environment.

Run:
    python generate_data.py
"""

import os
import numpy as np
import pandas as pd

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, "data")

np.random.seed(17)
N_STOCKS = 40
N_MONTHS = 36

TRUE_WEIGHTS = {"value": 0.0022, "momentum": 0.0030, "quality": 0.0015}
NOISE_STD = 0.045


def main():
    os.makedirs(DATA_DIR, exist_ok=True)

    tickers = [f"STK{i:02d}" for i in range(1, N_STOCKS + 1)]
    dates = pd.date_range(start="2023-01-31", periods=N_MONTHS, freq="ME")

    rows = []
    for month_idx, date in enumerate(dates, start=1):
        value_z = np.random.normal(0, 1, N_STOCKS)
        momentum_z = np.random.normal(0, 1, N_STOCKS)
        quality_z = np.random.normal(0, 1, N_STOCKS)

        signal = (TRUE_WEIGHTS["value"] * value_z + TRUE_WEIGHTS["momentum"] * momentum_z
                  + TRUE_WEIGHTS["quality"] * quality_z)
        forward_return = signal + np.random.normal(0, NOISE_STD, N_STOCKS)

        for i, ticker in enumerate(tickers):
            rows.append({
                "Date": date, "Ticker": ticker, "ValueZ": value_z[i], "MomentumZ": momentum_z[i],
                "QualityZ": quality_z[i], "ForwardReturn_1m": forward_return[i],
            })

    df = pd.DataFrame(rows)
    df.to_csv(os.path.join(DATA_DIR, "factor_panel.csv"), index=False)
    print(f"Generated a {N_STOCKS}-stock x {N_MONTHS}-month factor panel "
          f"({len(df)} stock-month observations).")


if __name__ == "__main__":
    main()
