"""
Portfolio Power-Law Model - 20-Investment VC Fund

Analyzes a hypothetical 20-investment venture portfolio to demonstrate
the power-law return distribution central to VC portfolio construction:
computes each deal's proceeds and multiple, ranks investments by proceeds
contributed, and quantifies exactly how concentrated fund returns are in
a small number of outsized winners.

Run:
    python power_law_model.py
"""

import os
import pandas as pd
import matplotlib.pyplot as plt

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, "data")
OUTPUT_DIR = os.path.join(BASE_DIR, "output")


def load_portfolio() -> pd.DataFrame:
    return pd.read_csv(os.path.join(DATA_DIR, "portfolio_investments.csv"))


def compute_returns(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df["Proceeds_mm"] = df["InvestmentAmount_mm"] * df["ExitMultiple"]
    df = df.sort_values("Proceeds_mm", ascending=False).reset_index(drop=True)
    df["Rank"] = df.index + 1

    total_proceeds = df["Proceeds_mm"].sum()
    df["PctOfTotalProceeds"] = df["Proceeds_mm"] / total_proceeds
    df["CumulativePctOfProceeds"] = df["PctOfTotalProceeds"].cumsum()
    df["CumulativePctOfDeals"] = df["Rank"] / len(df)

    return df


def concentration_stats(df: pd.DataFrame) -> dict:
    total_proceeds = df["Proceeds_mm"].sum()
    total_invested = df["InvestmentAmount_mm"].sum()

    stats = {
        "total_invested": total_invested, "total_proceeds": total_proceeds,
        "fund_gross_moic": total_proceeds / total_invested,
        "top1_pct": df.iloc[0]["Proceeds_mm"] / total_proceeds,
        "top3_pct": df.iloc[:3]["Proceeds_mm"].sum() / total_proceeds,
        "top5_pct": df.iloc[:5]["Proceeds_mm"].sum() / total_proceeds,
        "pct_deals_below_1x": (df["ExitMultiple"] < 1.0).mean(),
        "pct_deals_above_5x": (df["ExitMultiple"] >= 5.0).mean(),
    }
    return stats


def plot_multiple_distribution(df: pd.DataFrame):
    fig, ax = plt.subplots(figsize=(10, 6))
    ordered = df.sort_values("ExitMultiple")
    colors = ["#C0392B" if m < 1.0 else "#F1C40F" if m < 5.0 else "#1E8449" for m in ordered["ExitMultiple"]]
    ax.bar(ordered["Company"], ordered["ExitMultiple"], color=colors)
    ax.axhline(1.0, color="black", linestyle="--", linewidth=1)
    ax.set_ylabel("Exit Multiple (x)")
    ax.set_title("Exit Multiple by Investment (red = loss, yellow = modest, green = winner)")
    plt.xticks(rotation=60, ha="right")
    fig.tight_layout()
    fig.savefig(os.path.join(OUTPUT_DIR, "multiple_distribution.png"), dpi=150)
    plt.close(fig)


def plot_concentration_curve(df: pd.DataFrame):
    fig, ax = plt.subplots(figsize=(8, 6))
    x = [0] + list(df["CumulativePctOfDeals"] * 100)
    y = [0] + list(df["CumulativePctOfProceeds"] * 100)
    ax.plot(x, y, marker="o", color="#2E5090", label="Actual fund concentration")
    ax.plot([0, 100], [0, 100], linestyle="--", color="grey", label="Equal contribution (no power law)")
    ax.set_xlabel("Cumulative % of Investments (ranked by proceeds)")
    ax.set_ylabel("Cumulative % of Total Proceeds")
    ax.set_title("Return Concentration Curve")
    ax.legend()
    fig.tight_layout()
    fig.savefig(os.path.join(OUTPUT_DIR, "concentration_curve.png"), dpi=150)
    plt.close(fig)


def plot_outcome_buckets(df: pd.DataFrame):
    bins = [(-0.01, 1.0, "Loss (<1x)"), (1.0, 3.0, "Return Capital (1-3x)"),
            (3.0, 10.0, "Good Outcome (3-10x)"), (10.0, 1000.0, "Major Winner (10x+)")]
    counts, proceeds = [], []
    labels = []
    for lo, hi, label in bins:
        mask = (df["ExitMultiple"] > lo) & (df["ExitMultiple"] <= hi)
        counts.append(mask.sum())
        proceeds.append(df.loc[mask, "Proceeds_mm"].sum())
        labels.append(label)

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))
    ax1.bar(labels, counts, color="#7FA6D9")
    ax1.set_title("Number of Deals by Outcome Bucket")
    ax1.set_ylabel("# of Investments")
    plt.setp(ax1.get_xticklabels(), rotation=20, ha="right")

    ax2.bar(labels, proceeds, color="#2E5090")
    ax2.set_title("Total Proceeds by Outcome Bucket ($mm)")
    ax2.set_ylabel("$mm")
    plt.setp(ax2.get_xticklabels(), rotation=20, ha="right")

    fig.tight_layout()
    fig.savefig(os.path.join(OUTPUT_DIR, "outcome_buckets.png"), dpi=150)
    plt.close(fig)


def main():
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    portfolio = load_portfolio()
    df = compute_returns(portfolio)
    stats = concentration_stats(df)

    df.round(3).to_csv(os.path.join(OUTPUT_DIR, "portfolio_returns_ranked.csv"), index=False)

    plot_multiple_distribution(df)
    plot_concentration_curve(df)
    plot_outcome_buckets(df)

    with open(os.path.join(OUTPUT_DIR, "power_law_summary.txt"), "w") as f:
        f.write("=== Portfolio Power-Law Summary ===\n\n")
        f.write(f"Total Invested (20 deals): ${stats['total_invested']:,.1f}mm\n")
        f.write(f"Total Proceeds: ${stats['total_proceeds']:,.1f}mm\n")
        f.write(f"Fund Gross MOIC: {stats['fund_gross_moic']:.2f}x\n\n")
        f.write(f"Top 1 investment contributes: {stats['top1_pct']:.1%} of total proceeds\n")
        f.write(f"Top 3 investments contribute: {stats['top3_pct']:.1%} of total proceeds\n")
        f.write(f"Top 5 investments contribute: {stats['top5_pct']:.1%} of total proceeds\n\n")
        f.write(f"% of deals returning below 1x (losses): {stats['pct_deals_below_1x']:.0%}\n")
        f.write(f"% of deals returning 5x or more: {stats['pct_deals_above_5x']:.0%}\n\n")
        f.write("=== Ranked Portfolio (by proceeds) ===\n")
        f.write(df[["Rank", "Company", "InvestmentAmount_mm", "ExitMultiple", "Proceeds_mm",
                     "PctOfTotalProceeds", "CumulativePctOfProceeds"]].round(3).to_string(index=False))

    print("=== Portfolio Power-Law Model ===")
    print(f"Fund Gross MOIC: {stats['fund_gross_moic']:.2f}x  "
          f"(${stats['total_proceeds']:,.1f}mm proceeds on ${stats['total_invested']:,.1f}mm invested)\n")
    print(f"Top 1 deal contributes {stats['top1_pct']:.1%} of total proceeds")
    print(f"Top 3 deals contribute {stats['top3_pct']:.1%} of total proceeds")
    print(f"Top 5 deals contribute {stats['top5_pct']:.1%} of total proceeds")
    print(f"{stats['pct_deals_below_1x']:.0%} of deals returned below 1x")
    print(f"\nOutputs written to: {OUTPUT_DIR}")


if __name__ == "__main__":
    main()
