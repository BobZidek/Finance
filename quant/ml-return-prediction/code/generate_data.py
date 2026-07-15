"""
Generates 5 years of synthetic daily prices for a single asset where the
NEXT day's return is generated as a noisy function of the PRIOR day's
5-day momentum and mean-reversion (distance from its 20-day moving
average) - a genuine, if weak and noisy, predictive relationship for the
ML model to attempt to recover, in the same spirit as the multi-factor
ranking project. Live market data wasn't reachable in this environment;
see the README's data note.

Run:
    python generate_data.py
"""

import os
import numpy as np
import pandas as pd

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, "data")

np.random.seed(31)
N_DAYS = 1260  # 5 years
START_PRICE = 100.0
DAILY_VOL = 0.012

# True (unobserved in reality) relationship used to generate the data.
# Real single-asset return predictability is far weaker than this in
# practice - these weights are set generously so a reasonably-sized ML
# model can recover clear evidence of the relationship at all; see the
# theory doc for why this calibration choice matters.
MOMENTUM_WEIGHT = 0.09
MEAN_REVERSION_WEIGHT = -0.06


def main():
    os.makedirs(DATA_DIR, exist_ok=True)

    prices = [START_PRICE] * 25  # seed with enough history for the first rolling features
    for _ in range(25):
        prices.append(prices[-1] * (1 + np.random.normal(0, DAILY_VOL)))

    for _ in range(N_DAYS):
        recent = pd.Series(prices[-25:])
        returns_5d = recent.iloc[-1] / recent.iloc[-6] - 1
        sma_20 = recent.iloc[-20:].mean()
        mean_reversion_signal = (recent.iloc[-1] - sma_20) / sma_20

        predictable_component = MOMENTUM_WEIGHT * returns_5d + MEAN_REVERSION_WEIGHT * mean_reversion_signal
        next_return = predictable_component + np.random.normal(0, DAILY_VOL)
        prices.append(prices[-1] * (1 + next_return))

    prices = prices[25:]  # drop the seed window used only to compute initial features
    dates = pd.bdate_range(start="2021-01-04", periods=len(prices))
    df = pd.DataFrame({"Date": dates, "Close": prices})
    df.to_csv(os.path.join(DATA_DIR, "synthetic_prices.csv"), index=False)
    print(f"Generated {len(df)} days of synthetic price data with an injected momentum/"
          f"mean-reversion signal.")


if __name__ == "__main__":
    main()
