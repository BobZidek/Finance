"""
Portfolio Company Refinancing Analysis - Highland Building Materials LLC

Analyzes an opportunistic debt refinancing (lower rate, extended
maturity, no dividend extraction - distinct from a dividend recap):
computes annual interest savings, total cash refinancing costs (OID +
arrangement fees), the NPV of refinancing over the existing debt's
remaining life, the cash payback (breakeven) period, and a sensitivity
showing the achievable new-rate cushion before refinancing stops making
economic sense.

Run:
    python refinancing_model.py
"""

import os
import pandas as pd
import matplotlib.pyplot as plt

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, "data")
OUTPUT_DIR = os.path.join(BASE_DIR, "output")


def load_assumptions() -> dict:
    path = os.path.join(DATA_DIR, "refinancing_assumptions.csv")
    df = pd.read_csv(path, index_col="Field")
    a = {k: v for k, v in df["Value"].items()}
    for k in a:
        if k != "CompanyName":
            a[k] = float(a[k])
    a["ExistingRemainingMaturityYears"] = int(a["ExistingRemainingMaturityYears"])
    a["NewMaturityYears"] = int(a["NewMaturityYears"])
    return a


def npv_of_annuity(annual_cash_flow: float, discount_rate: float, years: int) -> float:
    if discount_rate == 0:
        return annual_cash_flow * years
    return annual_cash_flow * (1 - (1 + discount_rate) ** -years) / discount_rate


def compute_refinancing_economics(a: dict, new_rate: float = None) -> dict:
    new_rate = a["NewAllInRate"] if new_rate is None else new_rate

    annual_savings = a["OutstandingPrincipal_mm"] * (a["ExistingAllInRate"] - new_rate)
    oid_cost = a["OutstandingPrincipal_mm"] * a["NewOIDPct"]
    cash_refinancing_costs = oid_cost + a["NewArrangementFees_mm"]

    npv_savings = npv_of_annuity(annual_savings, new_rate, a["ExistingRemainingMaturityYears"])
    npv_refinancing = npv_savings - cash_refinancing_costs

    breakeven_years = cash_refinancing_costs / annual_savings if annual_savings > 0 else float("inf")

    return {"annual_savings": annual_savings, "oid_cost": oid_cost,
            "cash_refinancing_costs": cash_refinancing_costs, "npv_savings": npv_savings,
            "npv_refinancing": npv_refinancing, "breakeven_years": breakeven_years}


def rate_sensitivity(a: dict) -> pd.DataFrame:
    rates = [0.0725, 0.0750, 0.0775, 0.0800, 0.0825, 0.0850, 0.0875, 0.0900, 0.0925]
    rows = []
    for r in rates:
        res = compute_refinancing_economics(a, new_rate=r)
        rows.append({"NewRate": r, "AnnualSavings_mm": res["annual_savings"],
                     "NPVRefinancing_mm": res["npv_refinancing"], "BreakevenYears": res["breakeven_years"]})
    return pd.DataFrame(rows)


def find_breakeven_rate(a: dict) -> float:
    lo, hi = a["ExistingAllInRate"] - 0.05, a["ExistingAllInRate"]
    for _ in range(100):
        mid = (lo + hi) / 2
        npv = compute_refinancing_economics(a, new_rate=mid)["npv_refinancing"]
        if abs(npv) < 1e-6:
            return mid
        if npv > 0:
            lo = mid
        else:
            hi = mid
    return (lo + hi) / 2


def plot_npv_sensitivity(sens: pd.DataFrame, existing_rate: float):
    fig, ax = plt.subplots(figsize=(9, 6))
    ax.plot(sens["NewRate"] * 100, sens["NPVRefinancing_mm"], marker="o", color="#2E5090")
    ax.axhline(0, color="black", linewidth=0.8)
    ax.axvline(existing_rate * 100, color="#C0392B", linestyle="--", label=f"Existing Rate ({existing_rate:.2%})")
    ax.set_xlabel("New All-In Rate (%)")
    ax.set_ylabel("NPV of Refinancing ($mm)")
    ax.set_title("NPV of Refinancing vs. Achievable New Rate")
    ax.legend()
    fig.tight_layout()
    fig.savefig(os.path.join(OUTPUT_DIR, "npv_sensitivity.png"), dpi=150)
    plt.close(fig)


def plot_cost_savings_bridge(res: dict, a: dict):
    fig, ax = plt.subplots(figsize=(8, 6))
    labels = ["NPV of Interest\nSavings", "Cash Refinancing\nCosts", "Net NPV of\nRefinancing"]
    values = [res["npv_savings"], -res["cash_refinancing_costs"], None]
    cumulative = 0
    bottoms, heights, colors = [], [], []
    for val in values:
        if val is None:
            bottoms.append(0)
            heights.append(cumulative)
            colors.append("#2E5090")
        else:
            bottoms.append(min(cumulative, cumulative + val))
            heights.append(abs(val))
            colors.append("#1E8449" if val >= 0 else "#C0392B")
            cumulative += val
    ax.bar(labels, heights, bottom=bottoms, color=colors)
    ax.set_ylabel("$mm")
    ax.set_title(f"Refinancing NPV Bridge - {a['CompanyName']}")
    fig.tight_layout()
    fig.savefig(os.path.join(OUTPUT_DIR, "npv_bridge.png"), dpi=150)
    plt.close(fig)


def main():
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    a = load_assumptions()

    base = compute_refinancing_economics(a)
    sens = rate_sensitivity(a)
    sens.round(2).to_csv(os.path.join(OUTPUT_DIR, "rate_sensitivity.csv"), index=False)
    breakeven_rate = find_breakeven_rate(a)

    with open(os.path.join(OUTPUT_DIR, "refinancing_summary.txt"), "w") as f:
        f.write(f"Company: {a['CompanyName']}\n\n")
        f.write(f"Outstanding Principal: ${a['OutstandingPrincipal_mm']:,.0f}mm\n")
        f.write(f"Existing Rate: {a['ExistingAllInRate']:.2%}  |  Remaining Maturity: "
                f"{a['ExistingRemainingMaturityYears']:.0f} years\n")
        f.write(f"New Rate: {a['NewAllInRate']:.2%}  |  New Maturity: {a['NewMaturityYears']:.0f} years "
                f"(extended)\n\n")
        f.write(f"Annual Interest Savings: ${base['annual_savings']:,.2f}mm\n")
        f.write(f"Cash Refinancing Costs (OID + Arrangement Fees): ${base['cash_refinancing_costs']:,.2f}mm\n")
        f.write(f"  (Note: ${a['UnamortizedOldFees_mm']:,.1f}mm of unamortized fees on the old debt would also "
                f"be written off as a non-cash charge - not a new cash cost, but relevant to total GAAP "
                f"refinancing expense.)\n\n")
        f.write(f"NPV of Interest Savings (over {a['ExistingRemainingMaturityYears']:.0f}-year remaining term, "
                f"discounted at the new rate): ${base['npv_savings']:,.2f}mm\n")
        f.write(f"NPV of Refinancing: ${base['npv_refinancing']:,.2f}mm\n")
        f.write(f"Cash Payback (Breakeven) Period: {base['breakeven_years']:.2f} years\n\n")
        f.write(f"Breakeven New Rate (where NPV = 0): {breakeven_rate:.2%} "
                f"({a['ExistingAllInRate'] - breakeven_rate:.2%} of rate cushion below the existing rate)\n\n")
        f.write("=== Rate Sensitivity ===\n")
        f.write(sens.round(2).to_string(index=False))

    plot_npv_sensitivity(sens, a["ExistingAllInRate"])
    plot_cost_savings_bridge(base, a)

    print(f"=== Portfolio Company Refinancing: {a['CompanyName']} ===")
    print(f"Annual Interest Savings: ${base['annual_savings']:,.2f}mm")
    print(f"Cash Refinancing Costs: ${base['cash_refinancing_costs']:,.2f}mm")
    print(f"NPV of Refinancing: ${base['npv_refinancing']:,.2f}mm")
    print(f"Breakeven Period: {base['breakeven_years']:.2f} years")
    print(f"Breakeven New Rate: {breakeven_rate:.2%}")
    print(f"\nOutputs written to: {OUTPUT_DIR}")


if __name__ == "__main__":
    main()
