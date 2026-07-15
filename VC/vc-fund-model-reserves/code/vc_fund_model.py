"""
VC Fund Model - Reserves, Follow-On Decisions, and Fund-Level DPI/TVPI

Simulates a 10-year seed-stage VC fund investing an initial check into 15
portfolio companies, then deploying reserved follow-on capital into the 5
companies that show enough traction to justify doubling down. Builds
year-by-year capital calls (initial checks + follow-ons + management
fees) and distributions (company exits), and computes fund-level Gross
MOIC, LP Net DPI/TVPI, and LP Net IRR under a straight no-hurdle 80/20
waterfall - common for VC funds, unlike the preferred-return waterfall
used in PE/fund-model-waterfall.

Run:
    python vc_fund_model.py
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


def load_portfolio() -> pd.DataFrame:
    df = pd.read_csv(os.path.join(DATA_DIR, "portfolio_companies.csv"))
    df["InitialProceeds_mm"] = df["InitialCheck_mm"] * df["InitialMultiple"]
    df["FollowOnProceeds_mm"] = df.apply(
        lambda r: r["FollowOnCheck_mm"] * r["FollowOnMultiple"] if r["GetsFollowOn"] else 0.0, axis=1)
    df["TotalInvested_mm"] = df["InitialCheck_mm"] + df["FollowOnCheck_mm"].fillna(0)
    df["TotalProceeds_mm"] = df["InitialProceeds_mm"] + df["FollowOnProceeds_mm"]
    df["CompanyMOIC"] = df["TotalProceeds_mm"] / df["TotalInvested_mm"]
    return df


def build_capital_calls_and_distributions(a: dict, portfolio: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for year in range(1, a["FundLifeYears"] + 1):
        initial_calls = portfolio.loc[portfolio["InitialEntryYear"] == year, "InitialCheck_mm"].sum()
        followon_calls = portfolio.loc[
            (portfolio["GetsFollowOn"]) & (portfolio["FollowOnYear"] == year), "FollowOnCheck_mm"].sum()
        deal_calls = initial_calls + followon_calls

        if year <= a["InvestmentPeriodYears"]:
            fee = a["ManagementFeePct"] * a["CommittedCapital_mm"]
        else:
            unrealized_cost = portfolio.loc[portfolio["ExitYear"] > year, "TotalInvested_mm"].sum()
            fee = a["ManagementFeePct"] * unrealized_cost

        distributions = portfolio.loc[portfolio["ExitYear"] == year, "TotalProceeds_mm"].sum()

        rows.append({"Year": year, "InitialCalls_mm": initial_calls, "FollowOnCalls_mm": followon_calls,
                     "ManagementFee_mm": fee, "TotalCapitalCalls_mm": deal_calls + fee,
                     "GrossDistributions_mm": distributions})
    return pd.DataFrame(rows)


def run_waterfall(a: dict, cashflows: pd.DataFrame) -> pd.DataFrame:
    """No-hurdle waterfall (common for VC funds): 100% return of capital to LP first,
    then a straight 80/20 LP/GP split on everything above that - no preferred return,
    no GP catch-up tier (contrast with the PE fund model's European hurdle waterfall)."""
    unreturned_capital = 0.0
    rows = []
    for _, r in cashflows.iterrows():
        unreturned_capital += r["TotalCapitalCalls_mm"]
        distributable = r["GrossDistributions_mm"]

        tier1 = min(distributable, unreturned_capital)
        unreturned_capital -= tier1
        distributable -= tier1

        tier2_lp = distributable * (1 - a["CarryPct"])
        tier2_gp = distributable * a["CarryPct"]

        lp_distribution = tier1 + tier2_lp
        gp_carry = tier2_gp
        lp_net_cf = lp_distribution - r["TotalCapitalCalls_mm"]

        rows.append({"Year": int(r["Year"]), "TotalCapitalCalls_mm": r["TotalCapitalCalls_mm"],
                     "GrossDistributions_mm": r["GrossDistributions_mm"], "ReturnOfCapital_mm": tier1,
                     "ResidualSplit_LP_mm": tier2_lp, "ResidualSplit_GP_mm": tier2_gp,
                     "LP_TotalDistribution_mm": lp_distribution, "GP_TotalCarry_mm": gp_carry,
                     "LP_NetCashFlow_mm": lp_net_cf, "RemainingUnreturnedCapital_mm": unreturned_capital})

    df = pd.DataFrame(rows)
    df["CumulativeLPNetCashFlow_mm"] = df["LP_NetCashFlow_mm"].cumsum()
    return df


def compute_irr(cashflows: list, guess_lo=-0.99, guess_hi=5.0, tol=1e-6, max_iter=200) -> float:
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


def plot_followon_impact(portfolio: pd.DataFrame):
    fig, ax = plt.subplots(figsize=(10, 6))
    ordered = portfolio.sort_values("TotalProceeds_mm")
    ax.barh(ordered["Company"], ordered["InitialProceeds_mm"], label="Initial Check Proceeds", color="#7FA6D9")
    ax.barh(ordered["Company"], ordered["FollowOnProceeds_mm"], left=ordered["InitialProceeds_mm"],
            label="Follow-On Check Proceeds", color="#1E8449")
    ax.set_xlabel("Proceeds ($mm)")
    ax.set_title("Proceeds by Company: Initial Check vs. Follow-On Capital")
    ax.legend()
    fig.tight_layout()
    fig.savefig(os.path.join(OUTPUT_DIR, "followon_impact.png"), dpi=150)
    plt.close(fig)


def main():
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    a = load_fund_assumptions()
    portfolio = load_portfolio()

    cashflows = build_capital_calls_and_distributions(a, portfolio)
    waterfall = run_waterfall(a, cashflows)

    portfolio.round(2).to_csv(os.path.join(OUTPUT_DIR, "portfolio_detail.csv"), index=False)
    waterfall.round(2).to_csv(os.path.join(OUTPUT_DIR, "fund_waterfall.csv"), index=False)

    total_lp_contributions = waterfall["TotalCapitalCalls_mm"].sum()
    total_lp_distributions = waterfall["LP_TotalDistribution_mm"].sum()
    total_gp_carry = waterfall["GP_TotalCarry_mm"].sum()

    lp_dpi = total_lp_distributions / total_lp_contributions
    lp_cashflow_series = [0.0] + waterfall["LP_NetCashFlow_mm"].tolist()
    lp_net_irr = compute_irr(lp_cashflow_series)

    gross_fund_moic = portfolio["TotalProceeds_mm"].sum() / portfolio["TotalInvested_mm"].sum()

    followon_companies = portfolio[portfolio["GetsFollowOn"]]
    followon_contribution_pct = followon_companies["TotalProceeds_mm"].sum() / portfolio["TotalProceeds_mm"].sum()

    with open(os.path.join(OUTPUT_DIR, "fund_summary.txt"), "w") as f:
        f.write(f"Fund: {a['FundName']}\n")
        f.write(f"Committed Capital: ${a['CommittedCapital_mm']:,.0f}mm  |  {a['CarryPct']:.0%} carry, "
                f"no preferred return (straight 80/20 after return of capital)\n\n")
        f.write(f"15 initial checks (${portfolio['InitialCheck_mm'].sum():,.1f}mm total) + "
                f"{followon_companies.shape[0]} follow-on checks "
                f"(${followon_companies['FollowOnCheck_mm'].sum():,.1f}mm total) = "
                f"${portfolio['TotalInvested_mm'].sum():,.1f}mm total invested\n\n")
        f.write(f"Total LP Capital Contributed (deals + fees): ${total_lp_contributions:,.1f}mm\n")
        f.write(f"Total LP Distributions: ${total_lp_distributions:,.1f}mm\n")
        f.write(f"Total GP Carry Earned: ${total_gp_carry:,.1f}mm\n\n")
        f.write(f"Gross Fund MOIC (deal-level, pre-fee/carry): {gross_fund_moic:.2f}x\n")
        f.write(f"LP Net DPI/TVPI: {lp_dpi:.2f}x\n")
        f.write(f"LP Net IRR: {lp_net_irr:.1%}\n\n")
        f.write(f"The 5 companies that received follow-on capital contribute "
                f"{followon_contribution_pct:.1%} of total fund proceeds, despite being only "
                f"33% of the portfolio by company count.\n")

    plot_j_curve(waterfall, a["FundName"])
    plot_followon_impact(portfolio)

    print(f"=== VC Fund Model: {a['FundName']} ===")
    print(waterfall[["Year", "TotalCapitalCalls_mm", "GrossDistributions_mm", "LP_TotalDistribution_mm",
                      "GP_TotalCarry_mm", "CumulativeLPNetCashFlow_mm"]].round(1).to_string(index=False))
    print(f"\nGross Fund MOIC: {gross_fund_moic:.2f}x")
    print(f"LP Net DPI/TVPI: {lp_dpi:.2f}x  |  LP Net IRR: {lp_net_irr:.1%}")
    print(f"Follow-on companies (5 of 15) contribute {followon_contribution_pct:.1%} of total proceeds")
    print(f"\nOutputs written to: {OUTPUT_DIR}")


if __name__ == "__main__":
    main()
