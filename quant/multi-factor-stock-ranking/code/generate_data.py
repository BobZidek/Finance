"""
Generates synthetic cross-sectional factor data for 30 stocks (P/E,
12-month trailing return, ROE) plus a forward 1-month return that is
DELIBERATELY generated as a noisy function of each stock's true factor
exposures - so the backtest has a genuine (if imperfect) signal to
recover, rather than being pure noise. Live market/fundamental data
wasn't reachable in this environment; see the README's data note.

Run:
    python generate_data.py
"""

import os
import numpy as np
import pandas as pd

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, "data")

np.random.seed(7)
N_STOCKS = 80

# True (unobserved in reality, known here since we're generating the data)
# factor weights used to generate forward returns - the backtest's job is
# to recover evidence of this relationship from noisy realized data. The
# signal-to-noise ratio here is deliberately generous (larger than a real
# single-month cross-section would show) so the recovered Information
# Coefficients clearly demonstrate the methodology on a small, static
# dataset - see the theory doc for why real factor research needs far
# more data (many stocks x many periods) to detect realistically weaker signals.
TRUE_WEIGHTS = {"value": 0.018, "momentum": 0.022, "quality": 0.014}
NOISE_STD = 0.05


def main():
    os.makedirs(DATA_DIR, exist_ok=True)

    tickers = [f"STK{i:02d}" for i in range(1, N_STOCKS + 1)]

    value_z = np.random.normal(0, 1, N_STOCKS)
    momentum_z = np.random.normal(0, 1, N_STOCKS)
    quality_z = np.random.normal(0, 1, N_STOCKS)

    pe_ratio = np.clip(18 - value_z * 6, 4, 60)          # lower P/E = cheaper = higher value_z
    trailing_return = momentum_z * 0.15 + np.random.normal(0, 0.05, N_STOCKS)
    roe = np.clip(0.12 + quality_z * 0.06, -0.05, 0.40)

    signal = (TRUE_WEIGHTS["value"] * value_z + TRUE_WEIGHTS["momentum"] * momentum_z
              + TRUE_WEIGHTS["quality"] * quality_z)
    forward_return = signal + np.random.normal(0, NOISE_STD, N_STOCKS)

    df = pd.DataFrame({
        "Ticker": tickers, "PE_Ratio": pe_ratio.round(2),
        "TrailingReturn_12m": trailing_return.round(4), "ROE": roe.round(4),
        "ForwardReturn_1m": forward_return.round(4),
    })
    df.to_csv(os.path.join(DATA_DIR, "stock_factors.csv"), index=False)
    print(f"Generated factor data for {N_STOCKS} synthetic stocks.")
    print(df.head())


if __name__ == "__main__":
    main()
