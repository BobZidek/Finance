"""
Multi-Factor Stock Ranking System (Value / Momentum / Quality)

Computes standardized (z-score) Value, Momentum, and Quality factor
scores for a cross-section of stocks, combines them into an
equal-weighted composite score, ranks stocks into quintiles, and
backtests a long-short quintile portfolio against realized forward
returns. Reports the Information Coefficient (rank correlation between
score and forward return) for the composite and each individual factor.

Run:
    python generate_data.py   (first, if data/stock_factors.csv doesn't exist)
    python factor_model.py
"""

import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy.stats import spearmanr

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, "data")
OUTPUT_DIR = os.path.join(BASE_DIR, "output")


def load_data() -> pd.DataFrame:
    return pd.read_csv(os.path.join(DATA_DIR, "stock_factors.csv"))


def zscore(series: pd.Series) -> pd.Series:
    return (series - series.mean()) / series.std()


def compute_factor_scores(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df["EarningsYield"] = 1 / df["PE_Ratio"]  # invert P/E so higher = cheaper = better
    df["ValueScore"] = zscore(df["EarningsYield"])
    df["MomentumScore"] = zscore(df["TrailingReturn_12m"])
    df["QualityScore"] = zscore(df["ROE"])
    df["CompositeScore"] = (df["ValueScore"] + df["MomentumScore"] + df["QualityScore"]) / 3
    return df


def assign_quintiles(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df["Quintile"] = pd.qcut(df["CompositeScore"], 5, labels=["Q1 (Cheapest/Weakest)", "Q2", "Q3", "Q4",
                                                                "Q5 (Best)"])
    return df


def compute_information_coefficients(df: pd.DataFrame) -> pd.DataFrame:
    factors = {"Value": "ValueScore", "Momentum": "MomentumScore", "Quality": "QualityScore",
               "Composite": "CompositeScore"}
    rows = []
    for name, col in factors.items():
        ic, p_value = spearmanr(df[col], df["ForwardReturn_1m"])
        rows.append({"Factor": name, "InformationCoefficient": ic, "PValue": p_value})
    return pd.DataFrame(rows)


def quintile_returns(df: pd.DataFrame) -> pd.DataFrame:
    return df.groupby("Quintile", observed=True)["ForwardReturn_1m"].mean().reset_index()


def plot_quintile_returns(q_returns: pd.DataFrame):
    fig, ax = plt.subplots(figsize=(8, 5))
    colors = ["#C0392B", "#E67E22", "#F1C40F", "#7FA6D9", "#1E8449"]
    ax.bar(q_returns["Quintile"], q_returns["ForwardReturn_1m"] * 100, color=colors)
    ax.axhline(0, color="black", linewidth=0.8)
    ax.set_ylabel("Average Forward 1-Month Return (%)")
    ax.set_title("Forward Return by Composite Score Quintile")
    plt.xticks(rotation=20, ha="right")
    fig.tight_layout()
    fig.savefig(os.path.join(OUTPUT_DIR, "quintile_returns.png"), dpi=150)
    plt.close(fig)


def plot_ic_by_factor(ic_df: pd.DataFrame):
    fig, ax = plt.subplots(figsize=(7, 5))
    colors = ["#7FA6D9" if f != "Composite" else "#2E5090" for f in ic_df["Factor"]]
    ax.bar(ic_df["Factor"], ic_df["InformationCoefficient"], color=colors)
    ax.axhline(0, color="black", linewidth=0.8)
    ax.set_ylabel("Information Coefficient (Spearman rank correlation)")
    ax.set_title("Predictive Power by Factor")
    fig.tight_layout()
    fig.savefig(os.path.join(OUTPUT_DIR, "information_coefficient.png"), dpi=150)
    plt.close(fig)


def plot_score_vs_return(df: pd.DataFrame):
    fig, ax = plt.subplots(figsize=(8, 6))
    ax.scatter(df["CompositeScore"], df["ForwardReturn_1m"] * 100, color="#2E5090", s=40)
    z = df[["CompositeScore", "ForwardReturn_1m"]].dropna()
    coeffs = np.polyfit(z["CompositeScore"], z["ForwardReturn_1m"] * 100, 1)
    x_line = pd.Series([df["CompositeScore"].min(), df["CompositeScore"].max()])
    ax.plot(x_line, coeffs[0] * x_line + coeffs[1], color="#C0392B", linestyle="--", label="Fit line")
    ax.set_xlabel("Composite Factor Score")
    ax.set_ylabel("Forward 1-Month Return (%)")
    ax.set_title("Composite Score vs. Realized Forward Return")
    ax.legend()
    fig.tight_layout()
    fig.savefig(os.path.join(OUTPUT_DIR, "score_vs_return.png"), dpi=150)
    plt.close(fig)


def main():
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    raw = load_data()
    df = compute_factor_scores(raw)
    df = assign_quintiles(df)

    display_cols = ["Ticker", "ValueScore", "MomentumScore", "QualityScore", "CompositeScore",
                     "Quintile", "ForwardReturn_1m"]
    df[display_cols].sort_values("CompositeScore", ascending=False).round(3).to_csv(
        os.path.join(OUTPUT_DIR, "ranked_stocks.csv"), index=False)

    ic_df = compute_information_coefficients(df)
    ic_df.round(4).to_csv(os.path.join(OUTPUT_DIR, "information_coefficients.csv"), index=False)

    q_returns = quintile_returns(df)
    q_returns.round(4).to_csv(os.path.join(OUTPUT_DIR, "quintile_returns.csv"), index=False)

    long_short_return = (q_returns[q_returns["Quintile"] == "Q5 (Best)"]["ForwardReturn_1m"].values[0]
                          - q_returns[q_returns["Quintile"] == "Q1 (Cheapest/Weakest)"]["ForwardReturn_1m"].values[0])

    with open(os.path.join(OUTPUT_DIR, "factor_model_summary.txt"), "w") as f:
        f.write("=== Multi-Factor Stock Ranking ===\n\n")
        f.write(ic_df.round(4).to_string(index=False))
        f.write("\n\n=== Quintile Average Forward Returns ===\n")
        f.write(q_returns.round(4).to_string(index=False))
        f.write(f"\n\nLong-Short (Q5 - Q1) 1-month return: {long_short_return:.2%}\n")

    plot_quintile_returns(q_returns)
    plot_ic_by_factor(ic_df)
    plot_score_vs_return(df)

    print("=== Multi-Factor Stock Ranking ===")
    print(ic_df.round(4).to_string(index=False))
    print("\n=== Quintile Average Forward Returns ===")
    print(q_returns.round(4).to_string(index=False))
    print(f"\nLong-Short (Q5 - Q1) 1-month return: {long_short_return:.2%}")
    print(f"\nOutputs written to: {OUTPUT_DIR}")


if __name__ == "__main__":
    main()
