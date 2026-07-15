"""
Buy-and-Build (Add-On Acquisition) Model - Healthcare Staffing

Models a platform acquisition followed by 3 bolt-on acquisitions at
staggered years during the hold period, each bought at a lower multiple
than the platform's own exit multiple ("multiple arbitrage" - the core
buy-and-build thesis). Tracks combined EBITDA build-up (organic growth +
a 2-year integration synergy ramp per bolt-on), a combined debt schedule
across multiple draws, and computes sponsor MOIC/IRR on the full series
of staggered equity contributions using the same IRR solver as the fund
model.

Run:
    python buy_and_build_model.py
"""

import os
import pandas as pd
import matplotlib.pyplot as plt

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, "data")
OUTPUT_DIR = os.path.join(BASE_DIR, "output")


def load_assumptions() -> dict:
    path = os.path.join(DATA_DIR, "platform_and_deal_assumptions.csv")
    df = pd.read_csv(path, index_col="Field")
    a = {k: v for k, v in df["Value"].items()}
    for k in a:
        if k != "PlatformName":
            a[k] = float(a[k])
    a["HoldPeriodYears"] = int(a["HoldPeriodYears"])
    return a


def load_bolt_ons() -> pd.DataFrame:
    df = pd.read_csv(os.path.join(DATA_DIR, "bolt_on_acquisitions.csv"))
    df["AcquisitionYear"] = df["AcquisitionYear"].astype(int)
    return df


def synergy_ramp_pct(years_since_acq: int) -> float:
    if years_since_acq <= 0:
        return 0.0
    elif years_since_acq == 1:
        return 0.5
    return 1.0


def build_entity_list(a: dict, bolt_ons: pd.DataFrame) -> list:
    entities = [{
        "Name": a["PlatformName"], "AcquisitionYear": 0, "EBITDA_AtAcquisition_mm": a["PlatformEBITDA_mm"],
        "PurchaseMultiple": a["PlatformEntryMultiple"], "DebtTurns": a["PlatformDebtTurns"],
        "SynergyRunRate_mm": 0.0,
    }]
    for _, r in bolt_ons.iterrows():
        entities.append({
            "Name": r["BoltOnName"], "AcquisitionYear": int(r["AcquisitionYear"]),
            "EBITDA_AtAcquisition_mm": r["EBITDA_AtAcquisition_mm"], "PurchaseMultiple": r["PurchaseMultiple"],
            "DebtTurns": r["DebtTurns"],
            "SynergyRunRate_mm": r["SynergyRunRatePctOfEBITDA"] * r["EBITDA_AtAcquisition_mm"],
        })
    return entities


def combined_ebitda_at_year(entities: list, a: dict, year: int) -> float:
    total = 0.0
    for e in entities:
        if e["AcquisitionYear"] > year:
            continue
        years_since_acq = year - e["AcquisitionYear"]
        organic = e["EBITDA_AtAcquisition_mm"] * (1 + a["OrganicGrowthRate"]) ** years_since_acq
        synergy = e["SynergyRunRate_mm"] * synergy_ramp_pct(years_since_acq)
        total += organic + synergy
    return total


def run_model(a: dict, entities: list) -> dict:
    rows = []
    debt_balance = 0.0
    equity_contributions = []  # (year, amount)

    for year in range(0, a["HoldPeriodYears"] + 1):
        combined_ebitda = combined_ebitda_at_year(entities, a, year)

        new_debt_drawn = 0.0
        new_equity = 0.0
        acquired_this_year = [e for e in entities if e["AcquisitionYear"] == year]
        for e in acquired_this_year:
            entry_ev = e["PurchaseMultiple"] * e["EBITDA_AtAcquisition_mm"]
            fees = entry_ev * a["TransactionFeePct"]
            debt = e["DebtTurns"] * e["EBITDA_AtAcquisition_mm"]
            equity = entry_ev + fees - debt
            new_debt_drawn += debt
            new_equity += equity

        if new_equity > 0:
            equity_contributions.append((year, new_equity))

        beginning_debt = debt_balance + new_debt_drawn
        if year == 0:
            paydown = 0.0  # closing year - no sweep yet
        else:
            paydown = min(a["DebtPaydownPctEBITDA"] * combined_ebitda, beginning_debt)
        debt_balance = beginning_debt - paydown

        rows.append({
            "Year": year, "AcquisitionsThisYear": ", ".join(e["Name"] for e in acquired_this_year) or "-",
            "NewDebtDrawn_mm": new_debt_drawn, "NewEquityInvested_mm": new_equity,
            "CombinedEBITDA_mm": combined_ebitda, "BeginningDebt_mm": beginning_debt,
            "DebtPaydown_mm": paydown, "EndingDebt_mm": debt_balance,
        })

    schedule = pd.DataFrame(rows)
    exit_ebitda = schedule["CombinedEBITDA_mm"].iloc[-1]
    exit_ev = a["ExitMultiple"] * exit_ebitda
    exit_debt = schedule["EndingDebt_mm"].iloc[-1]
    exit_equity = exit_ev - exit_debt

    total_equity_invested = sum(amt for _, amt in equity_contributions)
    moic = exit_equity / total_equity_invested

    cf_series = [0.0] * (a["HoldPeriodYears"] + 1)
    for yr, amt in equity_contributions:
        cf_series[yr] -= amt
    cf_series[a["HoldPeriodYears"]] += exit_equity
    irr = compute_irr(cf_series)

    weighted_avg_entry_multiple = sum(e["PurchaseMultiple"] * e["EBITDA_AtAcquisition_mm"] for e in entities) / \
        sum(e["EBITDA_AtAcquisition_mm"] for e in entities)

    return {
        "schedule": schedule, "exit_ebitda": exit_ebitda, "exit_ev": exit_ev, "exit_debt": exit_debt,
        "exit_equity": exit_equity, "total_equity_invested": total_equity_invested, "moic": moic, "irr": irr,
        "weighted_avg_entry_multiple": weighted_avg_entry_multiple,
        "equity_contributions": equity_contributions,
    }


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


def plot_ebitda_buildup(schedule: pd.DataFrame, entities: list, a: dict):
    fig, ax = plt.subplots(figsize=(9, 5))
    bottom = pd.Series([0.0] * len(schedule))
    colors = ["#2E5090", "#7FA6D9", "#1E8449", "#F1C40F"]
    for i, e in enumerate(entities):
        contrib = []
        for _, row in schedule.iterrows():
            year = row["Year"]
            if year < e["AcquisitionYear"]:
                contrib.append(0.0)
            else:
                years_since = year - e["AcquisitionYear"]
                organic = e["EBITDA_AtAcquisition_mm"] * (1 + a["OrganicGrowthRate"]) ** years_since
                synergy = e["SynergyRunRate_mm"] * synergy_ramp_pct(years_since)
                contrib.append(organic + synergy)
        ax.bar(schedule["Year"], contrib, bottom=bottom, label=e["Name"], color=colors[i % len(colors)])
        bottom += pd.Series(contrib)

    ax.set_xlabel("Year")
    ax.set_ylabel("EBITDA ($mm)")
    ax.set_title("Combined EBITDA Build-Up by Entity")
    ax.legend(fontsize=8)
    fig.tight_layout()
    fig.savefig(os.path.join(OUTPUT_DIR, "ebitda_buildup.png"), dpi=150)
    plt.close(fig)


def plot_debt_and_equity(schedule: pd.DataFrame):
    fig, ax = plt.subplots(figsize=(9, 5))
    ax.bar(schedule["Year"] - 0.2, schedule["EndingDebt_mm"], width=0.4, label="Ending Debt Balance",
           color="#C0392B")
    ax.bar(schedule["Year"] + 0.2, schedule["NewEquityInvested_mm"], width=0.4, label="New Equity Invested",
           color="#2E5090")
    ax.set_xlabel("Year")
    ax.set_ylabel("$mm")
    ax.set_title("Debt Balance vs. New Equity Invested by Year")
    ax.legend()
    fig.tight_layout()
    fig.savefig(os.path.join(OUTPUT_DIR, "debt_and_equity.png"), dpi=150)
    plt.close(fig)


def main():
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    a = load_assumptions()
    bolt_ons = load_bolt_ons()
    entities = build_entity_list(a, bolt_ons)

    res = run_model(a, entities)
    res["schedule"].round(2).to_csv(os.path.join(OUTPUT_DIR, "buildup_schedule.csv"), index=False)

    with open(os.path.join(OUTPUT_DIR, "buy_and_build_summary.txt"), "w") as f:
        f.write(f"Platform: {a['PlatformName']}\n\n")
        f.write(f"Weighted-average entry multiple across platform + 3 bolt-ons: "
                f"{res['weighted_avg_entry_multiple']:.2f}x\n")
        f.write(f"Exit multiple (platform/scale premium): {a['ExitMultiple']:.1f}x\n")
        f.write(f"Multiple arbitrage: {a['ExitMultiple'] - res['weighted_avg_entry_multiple']:+.2f}x\n\n")
        f.write(f"Combined Exit EBITDA (Year {a['HoldPeriodYears']:.0f}): ${res['exit_ebitda']:,.1f}mm\n")
        f.write(f"Exit EV: ${res['exit_ev']:,.1f}mm\n")
        f.write(f"Exit Debt: ${res['exit_debt']:,.1f}mm\n")
        f.write(f"Exit Equity: ${res['exit_equity']:,.1f}mm\n\n")
        f.write(f"Total Equity Invested (across all 4 acquisitions): ${res['total_equity_invested']:,.1f}mm\n")
        for yr, amt in res["equity_contributions"]:
            f.write(f"  Year {yr}: ${amt:,.1f}mm\n")
        f.write(f"\nMOIC: {res['moic']:.2f}x   |   IRR: {res['irr']:.1%}\n")

    plot_ebitda_buildup(res["schedule"], entities, a)
    plot_debt_and_equity(res["schedule"])

    print(f"=== Buy-and-Build Model: {a['PlatformName']} ===")
    print(res["schedule"].round(2).to_string(index=False))
    print(f"\nWeighted-avg entry multiple: {res['weighted_avg_entry_multiple']:.2f}x  ->  "
          f"Exit multiple: {a['ExitMultiple']:.1f}x  (multiple arbitrage: "
          f"{a['ExitMultiple'] - res['weighted_avg_entry_multiple']:+.2f}x)")
    print(f"Total Equity Invested: ${res['total_equity_invested']:,.1f}mm  |  Exit Equity: ${res['exit_equity']:,.1f}mm")
    print(f"MOIC: {res['moic']:.2f}x  |  IRR: {res['irr']:.1%}")
    print(f"\nOutputs written to: {OUTPUT_DIR}")


if __name__ == "__main__":
    main()
