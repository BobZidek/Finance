"""
Generates synthetic daily returns from a genuine 2-state hidden Markov
process - a "Calm" regime (low vol, positive drift) and a "Turbulent"
regime (high vol, negative drift), with persistent transition
probabilities so regimes last for extended stretches rather than
flipping randomly day to day. This gives the HMM in hmm_model.py a real
underlying regime structure to recover. Live market data wasn't
reachable in this environment; see the README's data note.

Run:
    python generate_data.py
"""

import os
import numpy as np
import pandas as pd

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, "data")

np.random.seed(55)
N_DAYS = 1500

STATE_NAMES = ["Calm", "Turbulent"]
TRUE_MEANS = [0.0006, -0.0010]
TRUE_STDS = [0.008, 0.025]
TRANSITION_MATRIX = np.array([
    [0.980, 0.020],   # from Calm: 98% stay Calm, 2% switch to Turbulent
    [0.050, 0.950],   # from Turbulent: 5% switch to Calm, 95% stay Turbulent
])


def main():
    os.makedirs(DATA_DIR, exist_ok=True)

    state = 0  # start in Calm
    states, returns = [], []
    for _ in range(N_DAYS):
        states.append(state)
        ret = np.random.normal(TRUE_MEANS[state], TRUE_STDS[state])
        returns.append(ret)
        state = np.random.choice([0, 1], p=TRANSITION_MATRIX[state])

    dates = pd.bdate_range(start="2020-01-02", periods=N_DAYS)
    df = pd.DataFrame({"Date": dates, "Return": returns, "TrueState": states,
                        "TrueStateName": [STATE_NAMES[s] for s in states]})
    df.to_csv(os.path.join(DATA_DIR, "returns_with_true_regime.csv"), index=False)

    regime_pct = df["TrueStateName"].value_counts(normalize=True)
    print(f"Generated {N_DAYS} days of synthetic 2-regime returns.")
    print(regime_pct)


if __name__ == "__main__":
    main()
