"""
SaaS Metrics Dashboard - Fieldwork (hypothetical B2B field service management SaaS)

Computes the standard SaaS unit-economics and efficiency metrics venture
investors screen on - CAC, LTV, LTV:CAC, gross/net revenue retention, CAC
payback period, burn multiple, and the SaaS magic number - from 8 quarters
of ARR, customer count, spend, and burn data, and charts their trajectory.

Run:
    python saas_metrics_model.py
"""

import os
import pandas as pd
import matplotlib.pyplot as plt

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, "data")
OUTPUT_DIR = os.path.join(BASE_DIR, "output")

COMPANY_NAME = "Fieldwork (hypothetical B2B field service management SaaS)"


def load_data() -> pd.DataFrame:
    return pd.read_csv(os.path.join(DATA_DIR, "quarterly_metrics.csv"))


def compute_metrics(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df["EndingARR"] = df["StartingARR"] + df["NewARR"] + df["ExpansionARR"] - df["ChurnedARR"]
    df["EndingCustomers"] = df["StartingCustomers"] + df["NewCustomers"] - df["ChurnedCustomers"]
    df["NetNewARR"] = df["NewARR"] + df["ExpansionARR"] - df["ChurnedARR"]

    df["GRR"] = (df["StartingARR"] - df["ChurnedARR"]) / df["StartingARR"]
    df["NRR"] = (df["StartingARR"] - df["ChurnedARR"] + df["ExpansionARR"]) / df["StartingARR"]

    df["QuarterlyARPA"] = df["EndingARR"] / df["EndingCustomers"] / 4
    df["CustomerChurnRate"] = df["ChurnedCustomers"] / df["StartingCustomers"]
    df["CAC"] = df["SM_Spend"] / df["NewCustomers"]

    df["LTV"] = (df["QuarterlyARPA"] * df["GrossMarginPct"]) / df["CustomerChurnRate"]
    df["LTV_CAC"] = df["LTV"] / df["CAC"]

    monthly_gross_profit_per_account = (df["QuarterlyARPA"] / 3) * df["GrossMarginPct"]
    df["CACPaybackMonths"] = df["CAC"] / monthly_gross_profit_per_account

    df["BurnMultiple"] = df["NetBurn"] / df["NetNewARR"]

    prior_arr = df["EndingARR"].shift(1).fillna(df["StartingARR"].iloc[0])
    annualized_net_new_arr = (df["EndingARR"] - prior_arr) * 4
    prior_sm = df["SM_Spend"].shift(1)
    df["MagicNumber"] = annualized_net_new_arr / prior_sm

    return df


def plot_arr_growth(df: pd.DataFrame):
    fig, ax = plt.subplots(figsize=(9, 5))
    ax.bar(df["Quarter"], df["EndingARR"] / 1000, color="#2E5090")
    ax.set_ylabel("ARR ($000s)")
    ax.set_title(f"ARR Growth - {COMPANY_NAME}")
    fig.tight_layout()
    fig.savefig(os.path.join(OUTPUT_DIR, "arr_growth.png"), dpi=150)
    plt.close(fig)


def plot_retention(df: pd.DataFrame):
    fig, ax = plt.subplots(figsize=(9, 5))
    ax.plot(df["Quarter"], df["GRR"] * 100, marker="o", label="Gross Revenue Retention", color="#C0392B")
    ax.plot(df["Quarter"], df["NRR"] * 100, marker="o", label="Net Revenue Retention", color="#1E8449")
    ax.axhline(100, color="grey", linestyle="--", linewidth=1)
    ax.set_ylabel("Retention (%)")
    ax.set_title("Gross vs. Net Revenue Retention")
    ax.legend()
    fig.tight_layout()
    fig.savefig(os.path.join(OUTPUT_DIR, "retention.png"), dpi=150)
    plt.close(fig)


def plot_efficiency(df: pd.DataFrame):
    fig, ax1 = plt.subplots(figsize=(9, 5))
    ax2 = ax1.twinx()
    ax1.bar(df["Quarter"], df["LTV_CAC"], color="#7FA6D9", label="LTV:CAC")
    ax2.plot(df["Quarter"], df["BurnMultiple"], color="#C0392B", marker="o", label="Burn Multiple")
    ax1.axhline(3, color="#1E8449", linestyle="--", linewidth=1, label="LTV:CAC = 3x benchmark")
    ax1.set_ylabel("LTV : CAC (x)")
    ax2.set_ylabel("Burn Multiple (x, lower is better)")
    ax1.set_title("Capital Efficiency: LTV:CAC vs. Burn Multiple")
    lines1, labels1 = ax1.get_legend_handles_labels()
    lines2, labels2 = ax2.get_legend_handles_labels()
    ax1.legend(lines1 + lines2, labels1 + labels2, loc="upper left", fontsize=8)
    fig.tight_layout()
    fig.savefig(os.path.join(OUTPUT_DIR, "efficiency.png"), dpi=150)
    plt.close(fig)


def main():
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    df = load_data()
    metrics = compute_metrics(df)

    display_cols = ["Quarter", "EndingARR", "EndingCustomers", "GRR", "NRR", "CAC", "LTV",
                     "LTV_CAC", "CACPaybackMonths", "BurnMultiple", "MagicNumber"]
    metrics[display_cols].round(2).to_csv(os.path.join(OUTPUT_DIR, "saas_metrics_dashboard.csv"), index=False)

    plot_arr_growth(metrics)
    plot_retention(metrics)
    plot_efficiency(metrics)

    latest = metrics.iloc[-1]
    with open(os.path.join(OUTPUT_DIR, "metrics_summary.txt"), "w") as f:
        f.write(f"Company: {COMPANY_NAME}\n\n")
        f.write(f"ARR growth: ${metrics['EndingARR'].iloc[0]:,.0f} (Q1) -> "
                f"${metrics['EndingARR'].iloc[-1]:,.0f} (Q8)\n")
        f.write(f"Latest quarter (Q8):\n")
        f.write(f"  GRR: {latest['GRR']:.1%}   |   NRR: {latest['NRR']:.1%}\n")
        f.write(f"  CAC: ${latest['CAC']:,.0f}   |   LTV: ${latest['LTV']:,.0f}   |   "
                f"LTV:CAC: {latest['LTV_CAC']:.1f}x\n")
        f.write(f"  CAC Payback: {latest['CACPaybackMonths']:.1f} months\n")
        f.write(f"  Burn Multiple: {latest['BurnMultiple']:.2f}x\n")
        f.write(f"  Magic Number: {latest['MagicNumber']:.2f}\n")

    print(f"=== SaaS Metrics Dashboard: {COMPANY_NAME} ===")
    print(metrics[display_cols].round(2).to_string(index=False))
    print(f"\nLatest quarter: NRR {latest['NRR']:.1%}  |  LTV:CAC {latest['LTV_CAC']:.1f}x  |  "
          f"CAC Payback {latest['CACPaybackMonths']:.1f}mo  |  Burn Multiple {latest['BurnMultiple']:.2f}x  |  "
          f"Magic Number {latest['MagicNumber']:.2f}")
    print(f"\nOutputs written to: {OUTPUT_DIR}")


if __name__ == "__main__":
    main()
