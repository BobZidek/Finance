"""
Fund-Level Model - Capital Calls, Distributions, J-Curve, and GP Carry Waterfall

Simulates a 10-year buyout fund investing in 8 portfolio companies with
staggered entry/exit timing. Builds year-by-year capital calls (deal
investments + management fees) and gross distributions (deal exits), runs
a running European (whole-fund) waterfall with an 8% cumulative preferred
return and 20% GP carry with 100% catch-up, and computes fund-level LP
Net IRR, DPI, and TVPI - plus the classic J-curve chart.

Run:
    python fund_model.py
"""

import os
import pandas as pd
import matplotlib.pyplot as plt

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, "data")
OUTPUT_DIR = os.path.join(BASE_DIR, "output")


def load_fund_assumptions() -> dict:
    path = os.path.join(DATA_DIR, "fund_assumptions.csv")
    df = pd.read_csv(path, index_col="Field")
    a = {k: v for k, v in df["Value"].items()}
    for k in a:
        if k != "FundName":
            a[k] = float(a[k])
    a["InvestmentPeriodYears"] = int(a["InvestmentPeriodYears"])
    a["FundLifeYears"] = int(a["FundLifeYears"])
    return a


def load_deals() -> pd.DataFrame:
    df = pd.read_csv(os.path.join(DATA_DIR, "portfolio_deals.csv"))
    df["ExitYear"] = df["EntryYear"] + df["HoldYears"]
    df["ExitProceeds_mm"] = df["InvestedCapital_mm"] * df["DealMOIC"]
    return df


def build_capital_calls_and_distributions(a: dict, deals: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for year in range(1, a["FundLifeYears"] + 1):
        deal_calls = deals.loc[deals["EntryYear"] == year, "InvestedCapital_mm"].sum()

        if year <= a["InvestmentPeriodYears"]:
            fee = a["ManagementFeePct"] * a["CommittedCapital_mm"]
        else:
            unrealized_cost = deals.loc[deals["ExitYear"] > year, "InvestedCapital_mm"].sum()
            fee = a["ManagementFeePct"] * unrealized_cost

        distributions = deals.loc[deals["ExitYear"] == year, "ExitProceeds_mm"].sum()

        rows.append({"Year": year, "DealCapitalCalls_mm": deal_calls, "ManagementFee_mm": fee,
                     "TotalCapitalCalls_mm": deal_calls + fee, "GrossDistributions_mm": distributions})
    return pd.DataFrame(rows)


def run_waterfall(a: dict, cashflows: pd.DataFrame) -> pd.DataFrame:
    unreturned_capital = 0.0
    accrued_pref = 0.0
    cumulative_pref_paid = 0.0
    cumulative_catchup_paid = 0.0

    rows = []
    for _, r in cashflows.iterrows():
        accrued_pref += unreturned_capital * a["PreferredReturnRate"]
        unreturned_capital += r["TotalCapitalCalls_mm"]

        distributable = r["GrossDistributions_mm"]

        tier1 = min(distributable, unreturned_capital)
        unreturned_capital -= tier1
        distributable -= tier1

        tier2 = min(distributable, accrued_pref)
        accrued_pref -= tier2
        distributable -= tier2
        cumulative_pref_paid += tier2

        catchup_target_total = (a["CarryPct"] / (1 - a["CarryPct"])) * cumulative_pref_paid
        remaining_catchup_needed = max(catchup_target_total - cumulative_catchup_paid, 0)
        tier3 = min(distributable, remaining_catchup_needed)
        cumulative_catchup_paid += tier3
        distributable -= tier3

        tier4_lp = distributable * (1 - a["CarryPct"])
        tier4_gp = distributable * a["CarryPct"]

        lp_distribution = tier1 + tier2 + tier4_lp
        gp_carry = tier3 + tier4_gp
        lp_net_cf = lp_distribution - r["TotalCapitalCalls_mm"]

        rows.append({
            "Year": int(r["Year"]), "TotalCapitalCalls_mm": r["TotalCapitalCalls_mm"],
            "GrossDistributions_mm": r["GrossDistributions_mm"],
            "ReturnOfCapital_mm": tier1, "PreferredReturn_mm": tier2,
            "GPCatchup_mm": tier3, "ResidualSplit_LP_mm": tier4_lp, "ResidualSplit_GP_mm": tier4_gp,
            "LP_TotalDistribution_mm": lp_distribution, "GP_TotalCarry_mm": gp_carry,
            "LP_NetCashFlow_mm": lp_net_cf,
            "RemainingUnreturnedCapital_mm": unreturned_capital, "RemainingAccruedPref_mm": accrued_pref,
        })

    df = pd.DataFrame(rows)
    df["CumulativeLPNetCashFlow_mm"] = df["LP_NetCashFlow_mm"].cumsum()
    return df


def compute_irr(cashflows: list, guess_lo=-0.99, guess_hi=5.0, tol=1e-6, max_iter=200) -> float:
    """Bisection search for the annual IRR of a series of yearly net cash flows
    (index 0 = year 0). Assumes exactly one sign change (typical for a fund)."""
    def npv(rate):
        return sum(cf / (1 + rate) ** t for t, cf in enumerate(cashflows))

    lo, hi = guess_lo, guess_hi
    if npv(lo) * npv(hi) > 0:
        return float("nan")
    for _ in range(max_iter):
        mid = (lo + hi) / 2
        if abs(npv(mid)) < tol:
            return mid
        if npv(lo) * npv(mid) < 0:
            hi = mid
        else:
            lo = mid
    return (lo + hi) / 2


def plot_j_curve(waterfall: pd.DataFrame, fund_name: str):
    fig, ax = plt.subplots(figsize=(9, 5))
    ax.plot(waterfall["Year"], waterfall["CumulativeLPNetCashFlow_mm"], marker="o", color="#2E5090")
    ax.axhline(0, color="grey", linestyle="--", linewidth=1)
    ax.fill_between(waterfall["Year"], waterfall["CumulativeLPNetCashFlow_mm"], 0,
                     where=waterfall["CumulativeLPNetCashFlow_mm"] < 0, color="#C0392B", alpha=0.3)
    ax.fill_between(waterfall["Year"], waterfall["CumulativeLPNetCashFlow_mm"], 0,
                     where=waterfall["CumulativeLPNetCashFlow_mm"] >= 0, color="#1E8449", alpha=0.3)
    ax.set_xlabel("Fund Year")
    ax.set_ylabel("Cumulative Net Cash Flow to LPs ($mm)")
    ax.set_title(f"J-Curve - {fund_name}")
    fig.tight_layout()
    fig.savefig(os.path.join(OUTPUT_DIR, "j_curve.png"), dpi=150)
    plt.close(fig)


def plot_calls_vs_distributions(cashflows: pd.DataFrame):
    fig, ax = plt.subplots(figsize=(9, 5))
    ax.bar(cashflows["Year"] - 0.2, -cashflows["TotalCapitalCalls_mm"], width=0.4,
           label="Capital Calls", color="#C0392B")
    ax.bar(cashflows["Year"] + 0.2, cashflows["GrossDistributions_mm"], width=0.4,
           label="Gross Distributions", color="#1E8449")
    ax.axhline(0, color="black", linewidth=0.8)
    ax.set_xlabel("Fund Year")
    ax.set_ylabel("$mm")
    ax.set_title("Capital Calls vs. Gross Distributions by Year")
    ax.legend()
    fig.tight_layout()
    fig.savefig(os.path.join(OUTPUT_DIR, "calls_vs_distributions.png"), dpi=150)
    plt.close(fig)


def main():
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    a = load_fund_assumptions()
    deals = load_deals()

    cashflows = build_capital_calls_and_distributions(a, deals)
    waterfall = run_waterfall(a, cashflows)

    deals.round(2).to_csv(os.path.join(OUTPUT_DIR, "portfolio_deals_detail.csv"), index=False)
    waterfall.round(2).to_csv(os.path.join(OUTPUT_DIR, "fund_waterfall.csv"), index=False)

    total_lp_contributions = waterfall["TotalCapitalCalls_mm"].sum()
    total_lp_distributions = waterfall["LP_TotalDistribution_mm"].sum()
    total_gp_carry = waterfall["GP_TotalCarry_mm"].sum()

    lp_dpi = total_lp_distributions / total_lp_contributions
    lp_tvpi = lp_dpi  # no remaining NAV - all deals exited within the fund life modeled here

    lp_cashflow_series = [0.0] + (waterfall["LP_NetCashFlow_mm"]).tolist()
    lp_net_irr = compute_irr(lp_cashflow_series)

    gross_fund_moic = deals["ExitProceeds_mm"].sum() / deals["InvestedCapital_mm"].sum()

    with open(os.path.join(OUTPUT_DIR, "fund_summary.txt"), "w") as f:
        f.write(f"Fund: {a['FundName']}\n")
        f.write(f"Committed Capital: ${a['CommittedCapital_mm']:,.0f}mm  |  "
                f"{a['CarryPct']:.0%} carry / {a['PreferredReturnRate']:.0%} preferred return, "
                f"European (whole-fund) waterfall\n\n")
        f.write(f"Total LP Capital Contributed (deals + fees): ${total_lp_contributions:,.1f}mm\n")
        f.write(f"Total LP Distributions: ${total_lp_distributions:,.1f}mm\n")
        f.write(f"Total GP Carry Earned: ${total_gp_carry:,.1f}mm\n\n")
        f.write(f"Gross Fund MOIC (deal-level, pre-fee/carry): {gross_fund_moic:.2f}x\n")
        f.write(f"LP Net DPI: {lp_dpi:.2f}x\n")
        f.write(f"LP Net TVPI: {lp_tvpi:.2f}x\n")
        f.write(f"LP Net IRR: {lp_net_irr:.1%}\n\n")
        f.write(f"Fee + Carry drag (Gross MOIC - LP Net TVPI): {gross_fund_moic - lp_tvpi:.2f}x\n")

    plot_j_curve(waterfall, a["FundName"])
    plot_calls_vs_distributions(cashflows)

    print(f"=== Fund Model: {a['FundName']} ===")
    print(waterfall[["Year", "TotalCapitalCalls_mm", "GrossDistributions_mm", "LP_TotalDistribution_mm",
                      "GP_TotalCarry_mm", "LP_NetCashFlow_mm", "CumulativeLPNetCashFlow_mm"]]
          .round(1).to_string(index=False))
    print(f"\nGross Fund MOIC: {gross_fund_moic:.2f}x")
    print(f"LP Net DPI/TVPI: {lp_tvpi:.2f}x  |  LP Net IRR: {lp_net_irr:.1%}")
    print(f"Total GP Carry Earned: ${total_gp_carry:,.1f}mm")
    print(f"\nOutputs written to: {OUTPUT_DIR}")


if __name__ == "__main__":
    main()
