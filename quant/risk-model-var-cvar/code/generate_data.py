"""
Generates 3 years of synthetic daily returns for a 5-asset portfolio using
a multivariate Student-t distribution (fat tails - more realistic than
normal for real asset returns) with a hand-specified correlation
structure. Live market data wasn't reachable in this environment; see
the README's data note.

Run:
    python generate_data.py
"""

import os
import numpy as np
import pandas as pd
from scipy.stats import t as student_t

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, "data")

np.random.seed(23)
N_DAYS = 756  # 3 years

ASSETS = ["US Equity", "Intl Equity", "Bonds", "High Yield", "Commodities"]
ANNUAL_RETURNS = np.array([0.09, 0.075, 0.045, 0.065, 0.05])
ANNUAL_VOLS = np.array([0.16, 0.18, 0.06, 0.10, 0.17])
CORRELATION = np.array([
    [1.00, 0.80, -0.05, 0.35, 0.20],
    [0.80, 1.00, 0.00, 0.35, 0.25],
    [-0.05, 0.00, 1.00, 0.55, 0.05],
    [0.35, 0.35, 0.55, 1.00, 0.20],
    [0.20, 0.25, 0.05, 0.20, 1.00],
])
DEGREES_OF_FREEDOM = 3  # low df = pronounced fat tails


def simulate_multivariate_t(n_rows: int, correlation: np.ndarray, df: float) -> np.ndarray:
    """Correct construction of a multivariate Student-t: X = Z_correlated / sqrt(W/df),
    where Z_correlated ~ N(0, correlation) and W ~ Chi-square(df) is drawn ONCE PER ROW
    and shared across all columns in that row - this is what makes the tails fat while
    preserving the target correlation structure between assets."""
    n_assets = correlation.shape[0]
    L = np.linalg.cholesky(correlation)
    z = np.random.normal(0, 1, (n_rows, n_assets)) @ L.T
    w = np.random.chisquare(df, size=(n_rows, 1))
    return z / np.sqrt(w / df)


def main():
    os.makedirs(DATA_DIR, exist_ok=True)

    daily_mean = ANNUAL_RETURNS / 252
    daily_vol = ANNUAL_VOLS / np.sqrt(252)

    t_correlated = simulate_multivariate_t(N_DAYS, CORRELATION, DEGREES_OF_FREEDOM)
    # Scale to unit variance per asset (Student-t has variance df/(df-2) at scale 1)
    t_correlated = t_correlated / np.sqrt(DEGREES_OF_FREEDOM / (DEGREES_OF_FREEDOM - 2))

    returns = daily_mean + t_correlated * daily_vol

    dates = pd.bdate_range(start="2023-01-02", periods=N_DAYS)
    df = pd.DataFrame(returns, columns=ASSETS)
    df.insert(0, "Date", dates)
    df.to_csv(os.path.join(DATA_DIR, "asset_returns.csv"), index=False)

    weights = pd.DataFrame({"Asset": ASSETS, "Weight": [0.35, 0.20, 0.25, 0.10, 0.10]})
    weights.to_csv(os.path.join(DATA_DIR, "portfolio_weights.csv"), index=False)

    print(f"Generated {N_DAYS} days of fat-tailed synthetic returns for {len(ASSETS)} assets.")
    print(df.describe().round(4))


if __name__ == "__main__":
    main()
