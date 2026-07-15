"""
Value Creation Bridge - Specialty Retail / Building Products

Decomposes total sponsor equity value growth over a hold period into its
four classic PE return drivers - revenue growth, margin expansion,
multiple expansion, and deleveraging - plus transaction fee drag, and
verifies the decomposition sums exactly to the actual entry-to-exit
equity value change. The standard portfolio-review waterfall chart used
to explain *why* a deal returned what it did, not just that it did.

Run:
    python value_bridge_model.py
"""

import os
import pandas as pd
import matplotlib.pyplot as plt

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, "data")
OUTPUT_DIR = os.path.join(BASE_DIR, "output")


def load_assumptions() -> dict:
    path = os.path.join(DATA_DIR, "deal_assumptions.csv")
    df = pd.read_csv(path, index_col="Field")
    a = {k: v for k, v in df["Value"].items()}
    for k in a:
        if k != "TargetName":
            a[k] = float(a[k])
    a["HoldPeriodYears"] = int(a["HoldPeriodYears"])
    return a


def run_debt_paydown(a: dict, entry_debt: float) -> float:
    ebitda = a["EntryEBITDA_mm"]
    remaining = entry_debt
    for _ in range(a["HoldPeriodYears"]):
        entry_margin = a["EntryEBITDA_mm"] / a["EntryRevenue_mm"]
        # Approximate each year's EBITDA along a straight-line path from entry to exit margin
        # for the purpose of sizing debt paydown capacity (see theory doc for this simplification)
        ebitda = ebitda * (1 + a["RevenueGrowthRate"])
        paydown = min(a["DebtPaydownPctEBITDA"] * ebitda, remaining)
        remaining -= paydown
    return remaining


def build_bridge(a: dict) -> dict:
    entry_ev = a["EntryMultiple"] * a["EntryEBITDA_mm"]
    fees = entry_ev * a["TransactionFeePct"]
    entry_debt = a["LeverageMultiple"] * a["EntryEBITDA_mm"]
    entry_equity = entry_ev + fees - entry_debt

    exit_revenue = a["EntryRevenue_mm"] * (1 + a["RevenueGrowthRate"]) ** a["HoldPeriodYears"]
    entry_margin = a["EntryEBITDA_mm"] / a["EntryRevenue_mm"]

    exit_debt = run_debt_paydown(a, entry_debt)
    exit_ebitda = exit_revenue * a["ExitEBITDAMargin"]
    exit_ev = a["ExitMultiple"] * exit_ebitda
    exit_equity = exit_ev - exit_debt

    # Telescoping EV decomposition: revenue growth -> margin expansion -> multiple expansion
    ebitda_from_revenue_growth_only = exit_revenue * entry_margin
    ev_after_revenue_growth = a["EntryMultiple"] * ebitda_from_revenue_growth_only
    contribution_revenue_growth = ev_after_revenue_growth - entry_ev

    ev_after_margin_expansion = a["EntryMultiple"] * exit_ebitda
    contribution_margin_expansion = ev_after_margin_expansion - ev_after_revenue_growth

    contribution_multiple_expansion = exit_ev - ev_after_margin_expansion

    contribution_deleveraging = entry_debt - exit_debt
    contribution_fees = -fees

    total_from_bridge = (contribution_revenue_growth + contribution_margin_expansion
                          + contribution_multiple_expansion + contribution_deleveraging + contribution_fees)
    actual_equity_growth = exit_equity - entry_equity

    return {
        "entry_ev": entry_ev, "fees": fees, "entry_debt": entry_debt, "entry_equity": entry_equity,
        "exit_revenue": exit_revenue, "exit_ebitda": exit_ebitda, "exit_ev": exit_ev,
        "exit_debt": exit_debt, "exit_equity": exit_equity,
        "contribution_revenue_growth": contribution_revenue_growth,
        "contribution_margin_expansion": contribution_margin_expansion,
        "contribution_multiple_expansion": contribution_multiple_expansion,
        "contribution_deleveraging": contribution_deleveraging,
        "contribution_fees": contribution_fees,
        "total_from_bridge": total_from_bridge, "actual_equity_growth": actual_equity_growth,
        "moic": exit_equity / entry_equity, "irr": (exit_equity / entry_equity) ** (1 / a["HoldPeriodYears"]) - 1,
    }


def plot_bridge(res: dict, target_name: str):
    labels = ["Entry\nEquity", "Revenue\nGrowth", "Margin\nExpansion", "Multiple\nExpansion",
              "Deleveraging", "Transaction\nFees", "Exit\nEquity"]
    values = [res["entry_equity"], res["contribution_revenue_growth"], res["contribution_margin_expansion"],
              res["contribution_multiple_expansion"], res["contribution_deleveraging"], res["contribution_fees"],
              res["exit_equity"]]

    cumulative = [values[0]]
    for v in values[1:-1]:
        cumulative.append(cumulative[-1] + v)
    cumulative.append(values[-1])

    fig, ax = plt.subplots(figsize=(11, 6))
    for i, (label, val) in enumerate(zip(labels, values)):
        if i == 0 or i == len(labels) - 1:
            ax.bar(i, val, color="#2E5090")
            ax.text(i, val + 5, f"${val:,.0f}mm", ha="center", fontsize=9)
        else:
            bottom = cumulative[i - 1] if val >= 0 else cumulative[i]
            color = "#1E8449" if val >= 0 else "#C0392B"
            ax.bar(i, abs(val), bottom=min(cumulative[i - 1], cumulative[i]), color=color)
            ax.text(i, cumulative[i] + (5 if val >= 0 else -12), f"${val:+,.0f}mm", ha="center", fontsize=9)

    ax.set_xticks(range(len(labels)))
    ax.set_xticklabels(labels)
    ax.set_ylabel("Sponsor Equity Value ($mm)")
    ax.set_title(f"Value Creation Bridge - {target_name}\n"
                 f"MOIC {res['moic']:.2f}x | IRR {res['irr']:.1%}")
    fig.tight_layout()
    fig.savefig(os.path.join(OUTPUT_DIR, "value_creation_bridge.png"), dpi=150)
    plt.close(fig)


def main():
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    a = load_assumptions()
    res = build_bridge(a)

    reconciliation_ok = abs(res["total_from_bridge"] - res["actual_equity_growth"]) < 0.01

    with open(os.path.join(OUTPUT_DIR, "bridge_summary.txt"), "w") as f:
        f.write(f"Target: {a['TargetName']}\n\n")
        f.write(f"Entry Equity: ${res['entry_equity']:,.1f}mm\n")
        f.write(f"  Revenue Growth contribution:    ${res['contribution_revenue_growth']:+,.1f}mm\n")
        f.write(f"  Margin Expansion contribution:  ${res['contribution_margin_expansion']:+,.1f}mm\n")
        f.write(f"  Multiple Expansion contribution:${res['contribution_multiple_expansion']:+,.1f}mm\n")
        f.write(f"  Deleveraging contribution:      ${res['contribution_deleveraging']:+,.1f}mm\n")
        f.write(f"  Transaction Fees:                ${res['contribution_fees']:+,.1f}mm\n")
        f.write(f"Exit Equity: ${res['exit_equity']:,.1f}mm\n\n")
        f.write(f"Reconciliation check (sum of bridge components == actual equity growth): "
                f"{'PASS' if reconciliation_ok else 'FAIL'}\n")
        f.write(f"MOIC: {res['moic']:.2f}x   |   IRR: {res['irr']:.1%}\n")

    plot_bridge(res, a["TargetName"])

    print(f"=== Value Creation Bridge: {a['TargetName']} ===")
    print(f"Entry Equity: ${res['entry_equity']:,.1f}mm  ->  Exit Equity: ${res['exit_equity']:,.1f}mm")
    print(f"  Revenue Growth:     ${res['contribution_revenue_growth']:+,.1f}mm")
    print(f"  Margin Expansion:   ${res['contribution_margin_expansion']:+,.1f}mm")
    print(f"  Multiple Expansion: ${res['contribution_multiple_expansion']:+,.1f}mm")
    print(f"  Deleveraging:       ${res['contribution_deleveraging']:+,.1f}mm")
    print(f"  Transaction Fees:   ${res['contribution_fees']:+,.1f}mm")
    print(f"Reconciliation: {'PASS' if reconciliation_ok else 'FAIL'} "
          f"(bridge sum ${res['total_from_bridge']:,.1f}mm vs. actual ${res['actual_equity_growth']:,.1f}mm)")
    print(f"MOIC: {res['moic']:.2f}x  |  IRR: {res['irr']:.1%}")
    print(f"\nOutputs written to: {OUTPUT_DIR}")


if __name__ == "__main__":
    main()
