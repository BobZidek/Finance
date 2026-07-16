"""
Generates a synthetic daily return series that genuinely exhibits
volatility clustering (via a real GARCH(1,1) data-generating process) -
periods of high volatility followed by more high volatility, and calm
periods followed by more calm, unlike a constant-volatility random walk.
This gives the GARCH model in garch_model.py a genuine time-varying
volatility process to recover. Live market data wasn't reachable in this
environment; see the README's data note.

Run:
    python generate_data.py
"""

import os
import numpy as np
import pandas as pd

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, "data")

np.random.seed(42)
N_DAYS = 1500

# True GARCH(1,1) parameters used to generate the data:
# sigma^2_t = omega + alpha * epsilon^2_(t-1) + beta * sigma^2_(t-1)
OMEGA = 0.000004
ALPHA = 0.09
BETA = 0.88   # alpha + beta = 0.97, high persistence - realistic for daily equity returns


def main():
    os.makedirs(DATA_DIR, exist_ok=True)

    returns = np.zeros(N_DAYS)
    sigma2 = np.zeros(N_DAYS)
    sigma2[0] = OMEGA / (1 - ALPHA - BETA)  # long-run unconditional variance

    for t in range(1, N_DAYS):
        sigma2[t] = OMEGA + ALPHA * returns[t - 1] ** 2 + BETA * sigma2[t - 1]
        returns[t] = np.random.normal(0, np.sqrt(sigma2[t]))

    dates = pd.bdate_range(start="2019-01-02", periods=N_DAYS)
    df = pd.DataFrame({"Date": dates, "Return": returns, "TrueVolatility": np.sqrt(sigma2)})
    df.to_csv(os.path.join(DATA_DIR, "returns_with_true_vol.csv"), index=False)
    print(f"Generated {N_DAYS} days of GARCH(1,1) synthetic returns "
          f"(true alpha={ALPHA}, beta={BETA}, persistence={ALPHA+BETA:.2f}).")


if __name__ == "__main__":
    main()
