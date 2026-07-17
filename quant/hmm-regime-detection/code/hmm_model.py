"""
Hidden Markov Model (HMM) Regime Detection

Fits a 2-state Gaussian HMM to a synthetic return series generated from
a genuine (known) 2-regime Markov process, recovers the hidden state
parameters and transition matrix via the Baum-Welch algorithm, decodes
the most likely regime path via the Viterbi algorithm, and checks
decoding accuracy against the known true regime labels (after aligning
the HMM's arbitrary state labels to the true Calm/Turbulent labels).
Also demonstrates a simple regime-aware exposure strategy using the
decoded (in-sample) regimes.

Run:
    python generate_data.py   (first, if data/returns_with_true_regime.csv doesn't exist)
    python hmm_model.py
"""

import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from hmmlearn.hmm import GaussianHMM

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, "data")
OUTPUT_DIR = os.path.join(BASE_DIR, "output")

TRADING_DAYS_PER_YEAR = 252
TURBULENT_EXPOSURE = 0.50  # regime-aware strategy: cut exposure in half when decoded as Turbulent


def load_data() -> pd.DataFrame:
    return pd.read_csv(os.path.join(DATA_DIR, "returns_with_true_regime.csv"), parse_dates=["Date"])


def fit_hmm(returns: np.ndarray, n_states: int = 2) -> GaussianHMM:
    model = GaussianHMM(n_components=n_states, covariance_type="diag", n_iter=200, random_state=42)
    model.fit(returns.reshape(-1, 1))
    return model


def align_states_to_labels(model: GaussianHMM) -> dict:
    """HMM state indices are arbitrary - map them to Calm/Turbulent by
    comparing fitted means (Calm = higher mean, Turbulent = lower mean)."""
    means = model.means_.flatten()
    calm_idx = int(np.argmax(means))
    turbulent_idx = int(np.argmin(means))
    return {calm_idx: "Calm", turbulent_idx: "Turbulent"}


def decode_regimes(model: GaussianHMM, returns: np.ndarray, label_map: dict) -> np.ndarray:
    decoded_states = model.predict(returns.reshape(-1, 1))
    return np.array([label_map[s] for s in decoded_states])


def evaluate_accuracy(df: pd.DataFrame) -> float:
    return (df["TrueStateName"] == df["DecodedStateName"]).mean()


def regime_aware_backtest(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df["Exposure"] = np.where(df["DecodedStateName"] == "Turbulent", TURBULENT_EXPOSURE, 1.0)
    df["StrategyReturn"] = df["Exposure"] * df["Return"]
    df["StrategyEquity"] = (1 + df["StrategyReturn"]).cumprod()
    df["BuyHoldEquity"] = (1 + df["Return"]).cumprod()
    return df


def performance_stats(returns: pd.Series, equity: pd.Series, rf: float = 0.04) -> dict:
    ann_return = returns.mean() * TRADING_DAYS_PER_YEAR
    ann_vol = returns.std() * np.sqrt(TRADING_DAYS_PER_YEAR)
    sharpe = (ann_return - rf) / ann_vol if ann_vol > 0 else float("nan")
    max_dd = (equity / equity.cummax() - 1).min()
    return {"TotalReturn": equity.iloc[-1] - 1, "AnnReturn": ann_return, "AnnVol": ann_vol,
            "Sharpe": sharpe, "MaxDrawdown": max_dd}


def plot_regimes(df: pd.DataFrame):
    fig, axes = plt.subplots(2, 1, figsize=(11, 8), sharex=True)
    equity = (1 + df["Return"]).cumprod()
    axes[0].plot(df["Date"], equity, color="black", linewidth=1)
    for state, color in [("Calm", "#1E8449"), ("Turbulent", "#C0392B")]:
        mask = df["DecodedStateName"] == state
        axes[0].scatter(df.loc[mask, "Date"], equity[mask], color=color, s=8, label=f"Decoded: {state}")
    axes[0].set_title("Cumulative Return, Colored by HMM-Decoded Regime")
    axes[0].legend(fontsize=8)

    axes[1].plot(df["Date"], df["TrueState"], color="grey", label="True Regime", alpha=0.5, linewidth=1)
    decoded_numeric = (df["DecodedStateName"] == "Turbulent").astype(int)
    axes[1].plot(df["Date"], decoded_numeric, color="#2E5090", label="Decoded Regime", linewidth=1, linestyle="--")
    axes[1].set_yticks([0, 1])
    axes[1].set_yticklabels(["Calm", "Turbulent"])
    axes[1].set_title("True vs. HMM-Decoded Regime")
    axes[1].legend(fontsize=8)

    fig.tight_layout()
    fig.savefig(os.path.join(OUTPUT_DIR, "regime_detection.png"), dpi=150)
    plt.close(fig)


def plot_backtest(df: pd.DataFrame):
    fig, ax = plt.subplots(figsize=(10, 6))
    ax.plot(df["Date"], df["StrategyEquity"], label="Regime-Aware Strategy", color="#2E5090")
    ax.plot(df["Date"], df["BuyHoldEquity"], label="Buy & Hold", color="#7FA6D9", linestyle="--")
    ax.set_ylabel("Growth of $1")
    ax.set_title("Regime-Aware Exposure Strategy vs. Buy & Hold (in-sample decoded regimes)")
    ax.legend()
    fig.tight_layout()
    fig.savefig(os.path.join(OUTPUT_DIR, "regime_aware_backtest.png"), dpi=150)
    plt.close(fig)


def main():
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    raw = load_data()
    returns = raw["Return"].values

    model = fit_hmm(returns)
    label_map = align_states_to_labels(model)
    raw["DecodedStateName"] = decode_regimes(model, returns, label_map)

    accuracy = evaluate_accuracy(raw)

    fitted_means = {label_map[i]: model.means_.flatten()[i] for i in range(2)}
    fitted_stds = {label_map[i]: np.sqrt(model.covars_.flatten()[i]) for i in range(2)}
    fitted_transition = model.transmat_

    backtest = regime_aware_backtest(raw)
    strategy_stats = performance_stats(backtest["StrategyReturn"], backtest["StrategyEquity"])
    buyhold_stats = performance_stats(backtest["Return"], backtest["BuyHoldEquity"])

    raw.round(6).to_csv(os.path.join(OUTPUT_DIR, "regime_detection_detail.csv"), index=False)
    stats_df = pd.DataFrame([{"Strategy": "Regime-Aware", **strategy_stats},
                              {"Strategy": "Buy & Hold", **buyhold_stats}])
    stats_df.round(4).to_csv(os.path.join(OUTPUT_DIR, "backtest_performance.csv"), index=False)

    with open(os.path.join(OUTPUT_DIR, "hmm_summary.txt"), "w") as f:
        f.write("=== HMM Fitted Parameters (vs. true generating values) ===\n")
        f.write(f"Calm:      fitted mean {fitted_means['Calm']:.6f} (true 0.000600)  |  "
                f"fitted std {fitted_stds['Calm']:.6f} (true 0.008000)\n")
        f.write(f"Turbulent: fitted mean {fitted_means['Turbulent']:.6f} (true -0.001000)  |  "
                f"fitted std {fitted_stds['Turbulent']:.6f} (true 0.025000)\n\n")
        f.write(f"Fitted Transition Matrix:\n{fitted_transition}\n\n")
        f.write(f"Regime Decoding Accuracy (vs. known true regime labels): {accuracy:.1%}\n\n")
        f.write("=== Regime-Aware Strategy Backtest (in-sample decoded regimes) ===\n")
        f.write(stats_df.round(4).to_string(index=False))

    plot_regimes(raw)
    plot_backtest(backtest)

    print("=== HMM Regime Detection ===")
    print(f"Calm:      fitted mean {fitted_means['Calm']:.6f} (true 0.000600)  |  "
          f"fitted std {fitted_stds['Calm']:.6f} (true 0.008000)")
    print(f"Turbulent: fitted mean {fitted_means['Turbulent']:.6f} (true -0.001000)  |  "
          f"fitted std {fitted_stds['Turbulent']:.6f} (true 0.025000)")
    print(f"\nRegime Decoding Accuracy: {accuracy:.1%}\n")
    print(stats_df.round(4).to_string(index=False))
    print(f"\nOutputs written to: {OUTPUT_DIR}")


if __name__ == "__main__":
    main()
