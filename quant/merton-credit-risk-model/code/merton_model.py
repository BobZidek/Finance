"""
Merton Structural Credit Risk Model - Distance-to-Default

Treats each firm's equity as a call option on its (unobservable) asset
value, with the debt face value as the strike - the classic Merton
(1974) / Moody's KMV framework. Solves simultaneously for the implied
asset value and asset volatility from observable equity market cap and
equity volatility, then computes Distance-to-Default and an implied
risk-neutral probability of default for three companies spanning
healthy to distressed. One company deliberately matches the capital
structure of IB/distressed-debt-recovery-waterfall's post-filing
analysis, showing how equity markets can signal distress before a
company actually files.

Run:
    python merton_model.py
"""

import os
import numpy as np
import pandas as pd
from scipy.stats import norm
from scipy.optimize import fsolve
import matplotlib.pyplot as plt

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, "data")
OUTPUT_DIR = os.path.join(BASE_DIR, "output")


def load_companies() -> pd.DataFrame:
    return pd.read_csv(os.path.join(DATA_DIR, "companies.csv"))


def merton_equations(unknowns, E, sigma_E, D, r, T):
    V, sigma_V = unknowns
    if V <= 0 or sigma_V <= 0:
        return [1e10, 1e10]
    d1 = (np.log(V / D) + (r + 0.5 * sigma_V ** 2) * T) / (sigma_V * np.sqrt(T))
    d2 = d1 - sigma_V * np.sqrt(T)

    implied_equity = V * norm.cdf(d1) - D * np.exp(-r * T) * norm.cdf(d2)
    implied_equity_vol_eq = norm.cdf(d1) * sigma_V * V - sigma_E * E

    return [implied_equity - E, implied_equity_vol_eq]


def solve_merton(E, sigma_E, D, r, T):
    initial_guess = [E + D, sigma_E * E / (E + D)]
    solution = fsolve(merton_equations, initial_guess, args=(E, sigma_E, D, r, T), full_output=True)
    (V, sigma_V), info, ier, msg = solution
    converged = ier == 1
    return V, sigma_V, converged


def compute_distance_to_default(V, sigma_V, D, r, T):
    d1 = (np.log(V / D) + (r + 0.5 * sigma_V ** 2) * T) / (sigma_V * np.sqrt(T))
    d2 = d1 - sigma_V * np.sqrt(T)
    dd = d2  # Distance-to-Default, risk-neutral convention (drift = r)
    pd_riskneutral = norm.cdf(-d2)
    return dd, pd_riskneutral, d1, d2


def analyze_company(row) -> dict:
    E, sigma_E, D = row["EquityMarketCap_mm"], row["EquityVolatility"], row["TotalDebt_mm"]
    r, T = row["RiskFreeRate"], row["TimeHorizonYears"]

    V, sigma_V, converged = solve_merton(E, sigma_E, D, r, T)
    dd, pd_rn, d1, d2 = compute_distance_to_default(V, sigma_V, D, r, T)

    return {"Company": row["Company"], "EquityMarketCap_mm": E, "EquityVolatility": sigma_E,
            "TotalDebt_mm": D, "ImpliedAssetValue_mm": V, "ImpliedAssetVolatility": sigma_V,
            "AssetToDebtRatio": V / D, "DistanceToDefault": dd,
            "ImpliedDefaultProbability_1yr": pd_rn, "Converged": converged}


def plot_dd_comparison(results: pd.DataFrame):
    fig, ax1 = plt.subplots(figsize=(10, 6))
    ax2 = ax1.twinx()
    colors = ["#1E8449", "#F1C40F", "#C0392B"]

    ax1.bar(results["Company"], results["DistanceToDefault"], color=colors, alpha=0.8)
    ax2.plot(results["Company"], results["ImpliedDefaultProbability_1yr"] * 100, color="black",
             marker="o", linewidth=2, markersize=10)

    ax1.set_ylabel("Distance-to-Default (standard deviations)")
    ax2.set_ylabel("Implied 1-Year Default Probability (%)")
    ax1.set_title("Distance-to-Default and Implied Default Probability by Company")
    plt.setp(ax1.get_xticklabels(), rotation=15, ha="right", fontsize=8)
    fig.tight_layout()
    fig.savefig(os.path.join(OUTPUT_DIR, "distance_to_default.png"), dpi=150)
    plt.close(fig)


def plot_asset_vs_debt(results: pd.DataFrame):
    fig, ax = plt.subplots(figsize=(10, 6))
    x = range(len(results))
    width = 0.35
    ax.bar([i - width / 2 for i in x], results["ImpliedAssetValue_mm"], width, label="Implied Asset Value",
           color="#2E5090")
    ax.bar([i + width / 2 for i in x], results["TotalDebt_mm"], width, label="Total Debt (default point)",
           color="#C0392B")
    ax.set_xticks(list(x))
    ax.set_xticklabels(results["Company"], rotation=15, ha="right", fontsize=8)
    ax.set_ylabel("$mm")
    ax.set_title("Implied Asset Value vs. Debt (Default Point)")
    ax.legend()
    fig.tight_layout()
    fig.savefig(os.path.join(OUTPUT_DIR, "asset_vs_debt.png"), dpi=150)
    plt.close(fig)


def main():
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    companies = load_companies()

    results = pd.DataFrame([analyze_company(row) for _, row in companies.iterrows()])
    results.round(4).to_csv(os.path.join(OUTPUT_DIR, "merton_analysis.csv"), index=False)

    with open(os.path.join(OUTPUT_DIR, "merton_summary.txt"), "w") as f:
        f.write("=== Merton Structural Credit Risk Model ===\n\n")
        f.write(results.round(4).to_string(index=False))
        f.write("\n\nNote: 'Anchorage Retail Holdings' here uses the same $850mm total debt figure as "
                "IB/distressed-debt-recovery-waterfall's post-filing capital structure - this project "
                "shows what the EQUITY MARKET was implying about default risk before any bankruptcy filing, "
                "using only observable equity market cap and equity volatility.\n")

    plot_dd_comparison(results)
    plot_asset_vs_debt(results)

    print("=== Merton Structural Credit Risk Model ===")
    print(results.round(4).to_string(index=False))
    print(f"\nOutputs written to: {OUTPUT_DIR}")


if __name__ == "__main__":
    main()
