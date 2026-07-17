"""
Kelly Criterion - Optimal Position Sizing & Risk of Ruin

Computes the Kelly-optimal bet fraction for a repeated favorable binary
bet, derives the analytical long-run geometric growth rate as a function
of bet fraction, and runs a Monte Carlo simulation (2,000 independent
paths of 500 sequential bets each) comparing Full Kelly, Half Kelly,
2x Kelly (overbetting), and a reckless fraction - demonstrating that
Kelly maximizes long-run growth but that overbetting can produce
near-zero or negative growth despite each individual bet still having
positive expected value.

Run:
    python kelly_model.py
"""

import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, "data")
OUTPUT_DIR = os.path.join(BASE_DIR, "output")

np.random.seed(101)


def load_assumptions() -> dict:
    path = os.path.join(DATA_DIR, "bet_assumptions.csv")
    df = pd.read_csv(path, index_col="Field")
    a = {k: float(v) for k, v in df["Value"].items()}
    a["NumberOfBets"] = int(a["NumberOfBets"])
    a["NumberOfSimulatedPaths"] = int(a["NumberOfSimulatedPaths"])
    return a


def kelly_fraction(p: float, b: float) -> float:
    q = 1 - p
    return p - q / b


def analytical_growth_rate(f: float, p: float, b: float) -> float:
    q = 1 - p
    if f * b >= 1 or f >= 1:
        return float("-inf")
    return p * np.log(1 + b * f) + q * np.log(1 - f)


def simulate_paths(a: dict, f: float) -> np.ndarray:
    n_paths, n_bets = a["NumberOfSimulatedPaths"], a["NumberOfBets"]
    outcomes = np.random.random((n_paths, n_bets)) < a["WinProbability"]
    multipliers = np.where(outcomes, 1 + f * a["PayoffRatio"], 1 - f)
    wealth_paths = a["StartingWealth"] * np.cumprod(multipliers, axis=1)
    return wealth_paths


def summarize_paths(wealth_paths: np.ndarray, starting_wealth: float, ruin_threshold: float = 0.05) -> dict:
    terminal_wealth = wealth_paths[:, -1]
    running_max = np.maximum.accumulate(wealth_paths, axis=1)
    drawdowns = wealth_paths / running_max - 1
    max_drawdowns = drawdowns.min(axis=1)

    ruin_pct = (terminal_wealth < ruin_threshold * starting_wealth).mean()

    return {
        "median_terminal_wealth": np.median(terminal_wealth),
        "mean_terminal_wealth": np.mean(terminal_wealth),
        "pct_paths_below_start": (terminal_wealth < starting_wealth).mean(),
        "avg_max_drawdown": np.mean(max_drawdowns),
        "worst_max_drawdown": np.min(max_drawdowns),
        "risk_of_ruin_pct": ruin_pct,
    }


def plot_growth_rate_curve(a: dict, kelly_f: float):
    fractions = np.linspace(0.001, 0.999 / a["PayoffRatio"], 300)
    growth_rates = [analytical_growth_rate(f, a["WinProbability"], a["PayoffRatio"]) for f in fractions]

    fig, ax = plt.subplots(figsize=(9, 6))
    ax.plot(fractions * 100, growth_rates, color="#2E5090", linewidth=2)
    ax.axhline(0, color="black", linewidth=0.8)
    ax.axvline(kelly_f * 100, color="#1E8449", linestyle="--", label=f"Full Kelly ({kelly_f:.1%})")
    ax.axvline(2 * kelly_f * 100, color="#C0392B", linestyle="--", label=f"2x Kelly ({2*kelly_f:.1%})")
    ax.set_xlabel("Bet Fraction (%)")
    ax.set_ylabel("Long-Run Geometric Growth Rate (log units per bet)")
    ax.set_title("Analytical Growth Rate vs. Bet Fraction")
    ax.legend()
    fig.tight_layout()
    fig.savefig(os.path.join(OUTPUT_DIR, "growth_rate_curve.png"), dpi=150)
    plt.close(fig)


def plot_sample_paths(paths_by_fraction: dict, n_show: int = 40):
    fig, axes = plt.subplots(2, 2, figsize=(13, 9), sharex=True)
    for ax, (label, wealth_paths) in zip(axes.flat, paths_by_fraction.items()):
        for i in range(min(n_show, wealth_paths.shape[0])):
            ax.plot(wealth_paths[i], color="#2E5090", alpha=0.15, linewidth=0.7)
        ax.plot(np.median(wealth_paths, axis=0), color="#C0392B", linewidth=2, label="Median path")
        ax.set_yscale("log")
        ax.set_title(label)
        ax.legend(fontsize=8)
    fig.tight_layout()
    fig.savefig(os.path.join(OUTPUT_DIR, "sample_paths.png"), dpi=150)
    plt.close(fig)


def plot_comparison(summary_df: pd.DataFrame):
    fig, axes = plt.subplots(1, 2, figsize=(13, 5))
    axes[0].bar(summary_df["Strategy"], summary_df["median_terminal_wealth"], color="#2E5090")
    axes[0].set_ylabel("Median Terminal Wealth (log scale)")
    axes[0].set_yscale("log")
    axes[0].set_title("Median Terminal Wealth by Strategy")
    plt.setp(axes[0].get_xticklabels(), rotation=20, ha="right", fontsize=8)

    axes[1].bar(summary_df["Strategy"], summary_df["risk_of_ruin_pct"] * 100, color="#C0392B")
    axes[1].set_ylabel("Risk of Ruin (%)")
    axes[1].set_title("Risk of Ruin (Terminal Wealth < 5% of Start) by Strategy")
    plt.setp(axes[1].get_xticklabels(), rotation=20, ha="right", fontsize=8)

    fig.tight_layout()
    fig.savefig(os.path.join(OUTPUT_DIR, "strategy_comparison.png"), dpi=150)
    plt.close(fig)


def main():
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    a = load_assumptions()

    kelly_f = kelly_fraction(a["WinProbability"], a["PayoffRatio"])

    strategies = {
        "Half Kelly": kelly_f / 2,
        "Full Kelly": kelly_f,
        "2x Kelly (overbet)": 2 * kelly_f,
        "Reckless (4x Kelly)": 4 * kelly_f,
    }

    rows = []
    paths_by_fraction = {}
    for name, f in strategies.items():
        f_capped = min(f, 0.99 / a["PayoffRatio"])
        wealth_paths = simulate_paths(a, f_capped)
        paths_by_fraction[f"{name} (f={f_capped:.1%})"] = wealth_paths
        summary = summarize_paths(wealth_paths, a["StartingWealth"])
        analytical_g = analytical_growth_rate(f_capped, a["WinProbability"], a["PayoffRatio"])
        rows.append({"Strategy": name, "BetFraction": f_capped, "AnalyticalGrowthRate": analytical_g, **summary})

    summary_df = pd.DataFrame(rows)
    summary_df.round(5).to_csv(os.path.join(OUTPUT_DIR, "strategy_comparison.csv"), index=False)

    with open(os.path.join(OUTPUT_DIR, "kelly_summary.txt"), "w") as f:
        f.write(f"Win Probability: {a['WinProbability']:.0%}  |  Payoff Ratio: {a['PayoffRatio']:.1f}:1\n")
        f.write(f"Kelly-Optimal Fraction: {kelly_f:.2%}\n\n")
        f.write(f"Simulation: {a['NumberOfSimulatedPaths']:,.0f} paths x {a['NumberOfBets']:,.0f} bets each\n\n")
        f.write(summary_df.round(5).to_string(index=False))
        f.write("\n\nNote: 2x Kelly and beyond can show near-zero or negative analytical growth rates despite "
                "each individual bet still having positive expected value - overbetting relative to the Kelly "
                "fraction destroys long-run compounding even when the underlying edge is genuinely favorable.\n")

    plot_growth_rate_curve(a, kelly_f)
    plot_sample_paths(paths_by_fraction)
    plot_comparison(summary_df)

    print("=== Kelly Criterion: Optimal Position Sizing ===")
    print(f"Win Probability: {a['WinProbability']:.0%}  |  Payoff Ratio: {a['PayoffRatio']:.1f}:1  |  "
          f"Kelly Fraction: {kelly_f:.2%}\n")
    print(summary_df[["Strategy", "BetFraction", "AnalyticalGrowthRate", "median_terminal_wealth",
                       "risk_of_ruin_pct"]].round(5).to_string(index=False))
    print(f"\nOutputs written to: {OUTPUT_DIR}")


if __name__ == "__main__":
    main()
