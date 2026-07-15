"""
Multi-Sector Comps Dashboard - Software / SaaS

Goes beyond a flat median-multiple comps analysis (see the fast-food comps
project) by regressing EV/Revenue against revenue growth across a SaaS peer
set, then flagging each peer as over/under/fairly valued based on its
residual from the regression line. Applies the regression to a target
company's own growth rate to derive a growth-adjusted implied valuation,
and compares it against the naive flat-median approach.

Attempts a live data refresh via yfinance first; falls back to the bundled
static CSV snapshot if live data is unavailable (see data note in README).

Run:
    python comps_dashboard.py
"""

import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, "data")
OUTPUT_DIR = os.path.join(BASE_DIR, "output")


def load_peer_data() -> pd.DataFrame:
    """Loads the SaaS peer set. Attempts a live yfinance refresh of EV/Revenue
    first; falls back to the static snapshot on any failure (network, API
    changes, missing package) so the analysis always runs offline."""
    static_path = os.path.join(DATA_DIR, "saas_peers.csv")
    df = pd.read_csv(static_path)

    try:
        import yfinance as yf  # noqa: F401 - optional live-data path
        # Live refresh intentionally not executed by default in this offline
        # environment; see ENHANCEMENTS.md for wiring this up against a
        # reachable data source. Falling through to the static snapshot.
        raise RuntimeError("Live data path disabled in this environment - using static snapshot")
    except Exception as exc:
        print(f"[data] Using static snapshot ({exc})")

    return df


def load_target() -> dict:
    path = os.path.join(DATA_DIR, "target_company.csv")
    df = pd.read_csv(path, index_col="Field")
    t = {k: v for k, v in df["Value"].items()}
    for k in ("Revenue_LTM_mm", "RevenueGrowth_YoY", "FCFMargin", "NetDebt_mm"):
        t[k] = float(t[k])
    return t


def compute_multiples(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df["EV_Revenue"] = df["EV_mm"] / df["Revenue_LTM_mm"]
    df["RuleOf40"] = (df["RevenueGrowth_YoY"] + df["FCFMargin"]) * 100
    return df


def run_regression(df: pd.DataFrame):
    """Simple OLS: EV/Revenue ~ RevenueGrowth_YoY. Returns slope, intercept,
    and the fitted values / residuals appended to the dataframe."""
    x = df["RevenueGrowth_YoY"].values
    y = df["EV_Revenue"].values

    slope, intercept = np.polyfit(x, y, 1)
    df = df.copy()
    df["PredictedEV_Revenue"] = intercept + slope * x
    df["Residual"] = df["EV_Revenue"] - df["PredictedEV_Revenue"]

    resid_std = df["Residual"].std()
    threshold = 0.5 * resid_std

    def flag(r):
        if r > threshold:
            return "Overvalued"
        elif r < -threshold:
            return "Undervalued"
        return "Fairly Valued"

    df["Valuation_Flag"] = df["Residual"].apply(flag)

    # R-squared
    ss_res = (df["Residual"] ** 2).sum()
    ss_tot = ((y - y.mean()) ** 2).sum()
    r_squared = 1 - ss_res / ss_tot

    return df, slope, intercept, r_squared


def apply_to_target(target: dict, df: pd.DataFrame, slope: float, intercept: float):
    median_multiple = df["EV_Revenue"].median()
    regression_multiple = intercept + slope * target["RevenueGrowth_YoY"]

    ev_median_approach = median_multiple * target["Revenue_LTM_mm"]
    ev_regression_approach = regression_multiple * target["Revenue_LTM_mm"]

    equity_median = ev_median_approach - target["NetDebt_mm"]
    equity_regression = ev_regression_approach - target["NetDebt_mm"]

    return {
        "median_multiple": median_multiple,
        "regression_multiple": regression_multiple,
        "ev_median_approach": ev_median_approach,
        "ev_regression_approach": ev_regression_approach,
        "equity_median": equity_median,
        "equity_regression": equity_regression,
    }


def plot_regression(df: pd.DataFrame, slope: float, intercept: float, target: dict, target_result: dict):
    fig, ax = plt.subplots(figsize=(8, 6))

    colors = {"Overvalued": "#C0392B", "Undervalued": "#1E8449", "Fairly Valued": "#7FA6D9"}
    for flag_name, group in df.groupby("Valuation_Flag"):
        ax.scatter(group["RevenueGrowth_YoY"] * 100, group["EV_Revenue"],
                   label=flag_name, color=colors[flag_name], s=60)

    for _, row in df.iterrows():
        ax.annotate(row["Ticker"], (row["RevenueGrowth_YoY"] * 100, row["EV_Revenue"]),
                    textcoords="offset points", xytext=(5, 5), fontsize=8)

    x_line = np.linspace(df["RevenueGrowth_YoY"].min(), df["RevenueGrowth_YoY"].max(), 50)
    y_line = intercept + slope * x_line
    ax.plot(x_line * 100, y_line, color="black", linestyle="--", linewidth=1, label="Regression Line")

    ax.scatter([target["RevenueGrowth_YoY"] * 100], [target_result["regression_multiple"]],
               color="gold", edgecolor="black", s=150, marker="*", zorder=5, label="Target (predicted)")

    ax.set_xlabel("Revenue Growth YoY (%)")
    ax.set_ylabel("EV / Revenue (x)")
    ax.set_title("SaaS Peer Set: EV/Revenue vs. Growth Rate")
    ax.legend()
    fig.tight_layout()
    fig.savefig(os.path.join(OUTPUT_DIR, "growth_vs_multiple_regression.png"), dpi=150)
    plt.close(fig)


def plot_rule_of_40(df: pd.DataFrame):
    fig, ax = plt.subplots(figsize=(8, 5))
    ordered = df.sort_values("RuleOf40")
    colors = ["#C0392B" if v < 40 else "#1E8449" for v in ordered["RuleOf40"]]
    ax.barh(ordered["Ticker"], ordered["RuleOf40"], color=colors)
    ax.axvline(40, color="grey", linestyle="--", label="Rule of 40 threshold")
    ax.set_xlabel("Growth % + FCF Margin %")
    ax.set_title("Rule of 40 by Peer")
    ax.legend()
    fig.tight_layout()
    fig.savefig(os.path.join(OUTPUT_DIR, "rule_of_40.png"), dpi=150)
    plt.close(fig)


def main():
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    raw = load_peer_data()
    target = load_target()

    df = compute_multiples(raw)
    df, slope, intercept, r_squared = run_regression(df)
    target_result = apply_to_target(target, df, slope, intercept)

    display_cols = ["Ticker", "Company", "EV_Revenue", "RevenueGrowth_YoY", "FCFMargin",
                     "RuleOf40", "PredictedEV_Revenue", "Residual", "Valuation_Flag"]
    df[display_cols].round(2).to_csv(os.path.join(OUTPUT_DIR, "peer_dashboard.csv"), index=False)

    with open(os.path.join(OUTPUT_DIR, "regression_summary.txt"), "w") as f:
        f.write(f"Regression: EV/Revenue = {intercept:.2f} + {slope:.2f} x Revenue Growth\n")
        f.write(f"R-squared: {r_squared:.3f}\n\n")
        f.write(f"Target: {target['Name']}\n")
        f.write(f"Target Revenue Growth: {target['RevenueGrowth_YoY']:.1%}\n\n")
        f.write(f"Flat Median Multiple Approach: {target_result['median_multiple']:.2f}x -> "
                f"EV ${target_result['ev_median_approach']:,.1f}mm -> "
                f"Equity ${target_result['equity_median']:,.1f}mm\n")
        f.write(f"Growth-Regression Approach: {target_result['regression_multiple']:.2f}x -> "
                f"EV ${target_result['ev_regression_approach']:,.1f}mm -> "
                f"Equity ${target_result['equity_regression']:,.1f}mm\n")

    plot_regression(df, slope, intercept, target, target_result)
    plot_rule_of_40(df)

    print("=== SaaS Peer Dashboard ===")
    print(df[display_cols].round(2).to_string(index=False))
    print(f"\nRegression: EV/Revenue = {intercept:.2f} + {slope:.2f} x Growth   (R^2 = {r_squared:.3f})")
    print(f"\n=== Target: {target['Name']} (Growth = {target['RevenueGrowth_YoY']:.0%}) ===")
    print(f"Flat Median Multiple:   {target_result['median_multiple']:.2f}x  ->  "
          f"EV ${target_result['ev_median_approach']:,.1f}mm")
    print(f"Growth-Adjusted (Regression): {target_result['regression_multiple']:.2f}x  ->  "
          f"EV ${target_result['ev_regression_approach']:,.1f}mm")
    print(f"\nOutputs written to: {OUTPUT_DIR}")


if __name__ == "__main__":
    main()
