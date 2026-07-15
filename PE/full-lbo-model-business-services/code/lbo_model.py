"""
Full LBO Model with Revolver - Business Services

The detailed version of an LBO debt schedule: three tranches (revolving
credit facility, Term Loan, Subordinated Notes), a cash flow sweep
waterfall that draws the revolver to cover shortfalls and repays it first
when cash is available, and a comparison of sponsor returns across
multiple candidate exit years (3 / 5 / 7) from a single 7-year forecast.

Run:
    python lbo_model.py
"""

import os
import pandas as pd
import matplotlib.pyplot as plt

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, "data")
OUTPUT_DIR = os.path.join(BASE_DIR, "output")


def load_assumptions() -> dict:
    path = os.path.join(DATA_DIR, "lbo_assumptions.csv")
    df = pd.read_csv(path, index_col="Field")
    a = {k: v for k, v in df["Value"].items()}
    for k in a:
        if k != "TargetName":
            a[k] = float(a[k])
    a["MaxForecastYears"] = int(a["MaxForecastYears"])
    return a


def load_drivers() -> pd.DataFrame:
    return pd.read_csv(os.path.join(DATA_DIR, "forecast_drivers.csv"))


def sources_and_uses(a: dict):
    entry_ev = a["EntryMultiple"] * a["EntryEBITDA_mm"]
    fees = entry_ev * a["TransactionFeePct"]
    term_loan = a["TermLoanTurns"] * a["EntryEBITDA_mm"]
    sub_notes = a["SubNotesTurns"] * a["EntryEBITDA_mm"]
    total_funded_debt = term_loan + sub_notes  # revolver assumed undrawn at close
    total_uses = entry_ev + fees
    sponsor_equity = total_uses - total_funded_debt
    return {
        "entry_ev": entry_ev, "fees": fees, "term_loan_0": term_loan, "sub_notes_0": sub_notes,
        "total_funded_debt": total_funded_debt, "total_uses": total_uses, "sponsor_equity": sponsor_equity,
    }


def run_debt_schedule(a: dict, drivers: pd.DataFrame, term_loan_0: float, sub_notes_0: float) -> pd.DataFrame:
    rows = []
    revenue = a["EntryRevenue_mm"]
    prev_nwc = a["EntryRevenue_mm"] * drivers["NWC_pctRevenue"].iloc[0]
    tl_balance, sub_balance, revolver_balance = term_loan_0, sub_notes_0, 0.0
    tl_mandatory_amort = term_loan_0 * a["TermLoanMandatoryAmortPct"]

    for _, d in drivers.iterrows():
        revenue = revenue * (1 + d["RevenueGrowth"])
        ebitda = revenue * d["EBITDAMargin"]
        da = revenue * d["DA_pctRevenue"]
        ebit = ebitda - da

        # Interest on beginning-of-year balances (avoids circularity)
        interest_tl = tl_balance * a["TermLoanRate"]
        interest_sub = sub_balance * a["SubNotesRate"]
        interest_revolver = revolver_balance * a["RevolverRate"]
        undrawn_revolver = a["RevolverCapacity_mm"] - revolver_balance
        commitment_fee = undrawn_revolver * a["RevolverCommitmentFee"]
        total_interest = interest_tl + interest_sub + interest_revolver + commitment_fee

        ebt = ebit - total_interest
        taxes = max(ebt, 0) * a["TaxRate"]
        net_income = ebt - taxes

        capex = revenue * d["Capex_pctRevenue"]
        nwc_balance = revenue * d["NWC_pctRevenue"]
        delta_nwc = nwc_balance - prev_nwc
        prev_nwc = nwc_balance

        fcf_pre_debt_service = net_income + da - capex - delta_nwc

        mandatory_amort = min(tl_mandatory_amort, tl_balance)
        fcf_after_mandatory = fcf_pre_debt_service - mandatory_amort
        tl_balance_after_mandatory = tl_balance - mandatory_amort

        revolver_draw = 0.0
        revolver_paydown = 0.0
        tl_sweep = 0.0

        if fcf_after_mandatory < 0:
            shortfall = -fcf_after_mandatory
            revolver_draw = min(shortfall, a["RevolverCapacity_mm"] - revolver_balance)
            revolver_balance += revolver_draw
        else:
            cash_available = fcf_after_mandatory
            revolver_paydown = min(cash_available, revolver_balance)
            revolver_balance -= revolver_paydown
            cash_available -= revolver_paydown

            tl_sweep = min(cash_available, tl_balance_after_mandatory)
            tl_balance_after_mandatory -= tl_sweep
            cash_available -= tl_sweep

            sub_paydown = min(cash_available, sub_balance)
            sub_balance -= sub_paydown

        tl_balance = tl_balance_after_mandatory

        rows.append({
            "Year": int(d["Year"]), "Revenue_mm": revenue, "EBITDA_mm": ebitda, "EBIT_mm": ebit,
            "InterestExpense_mm": total_interest, "NetIncome_mm": net_income,
            "FCF_PreDebtService_mm": fcf_pre_debt_service,
            "RevolverDraw_mm": revolver_draw, "RevolverPaydown_mm": revolver_paydown,
            "MandatoryAmort_mm": mandatory_amort, "TermLoanSweep_mm": tl_sweep,
            "Revolver_EOY_mm": revolver_balance, "TermLoan_EOY_mm": tl_balance, "SubNotes_EOY_mm": sub_balance,
            "TotalDebt_EOY_mm": revolver_balance + tl_balance + sub_balance,
        })

    return pd.DataFrame(rows)


def exit_scenarios(schedule: pd.DataFrame, sponsor_equity: float, exit_multiple: float,
                    exit_years: list) -> pd.DataFrame:
    rows = []
    for year in exit_years:
        row = schedule[schedule["Year"] == year].iloc[0]
        exit_ev = exit_multiple * row["EBITDA_mm"]
        exit_equity = exit_ev - row["TotalDebt_EOY_mm"]
        moic = exit_equity / sponsor_equity
        irr = moic ** (1 / year) - 1
        rows.append({"ExitYear": year, "ExitEBITDA_mm": row["EBITDA_mm"], "ExitEV_mm": exit_ev,
                     "RemainingDebt_mm": row["TotalDebt_EOY_mm"], "ExitEquity_mm": exit_equity,
                     "MOIC": moic, "IRR": irr * 100})
    return pd.DataFrame(rows)


def plot_debt_paydown(schedule: pd.DataFrame):
    fig, ax = plt.subplots(figsize=(9, 5))
    ax.bar(schedule["Year"], schedule["TermLoan_EOY_mm"], label="Term Loan", color="#2E5090")
    ax.bar(schedule["Year"], schedule["SubNotes_EOY_mm"], bottom=schedule["TermLoan_EOY_mm"],
           label="Subordinated Notes", color="#7FA6D9")
    ax.bar(schedule["Year"], schedule["Revolver_EOY_mm"],
           bottom=schedule["TermLoan_EOY_mm"] + schedule["SubNotes_EOY_mm"],
           label="Revolver Drawn", color="#C0392B")
    ax.set_xlabel("Year")
    ax.set_ylabel("Debt Balance ($mm)")
    ax.set_title("Debt Paydown Schedule (incl. Revolver)")
    ax.legend()
    fig.tight_layout()
    fig.savefig(os.path.join(OUTPUT_DIR, "debt_paydown.png"), dpi=150)
    plt.close(fig)


def plot_exit_scenarios(exits: pd.DataFrame):
    fig, ax1 = plt.subplots(figsize=(8, 5))
    ax2 = ax1.twinx()

    ax1.bar(exits["ExitYear"].astype(str) + "-yr", exits["MOIC"], color="#7FA6D9", label="MOIC")
    ax2.plot(exits["ExitYear"].astype(str) + "-yr", exits["IRR"], color="#C0392B", marker="o", label="IRR")

    ax1.set_ylabel("MOIC (x)")
    ax2.set_ylabel("IRR (%)")
    ax1.set_title("Sponsor Returns by Exit Year")

    lines1, labels1 = ax1.get_legend_handles_labels()
    lines2, labels2 = ax2.get_legend_handles_labels()
    ax1.legend(lines1 + lines2, labels1 + labels2, loc="upper right")

    fig.tight_layout()
    fig.savefig(os.path.join(OUTPUT_DIR, "exit_scenarios.png"), dpi=150)
    plt.close(fig)


def main():
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    a = load_assumptions()
    drivers = load_drivers()

    su = sources_and_uses(a)
    schedule = run_debt_schedule(a, drivers, su["term_loan_0"], su["sub_notes_0"])
    exits = exit_scenarios(schedule, su["sponsor_equity"], a["ExitMultiple"], [3, 5, 7])

    schedule.round(2).to_csv(os.path.join(OUTPUT_DIR, "debt_schedule.csv"), index=False)
    exits.round(2).to_csv(os.path.join(OUTPUT_DIR, "exit_scenarios.csv"), index=False)

    with open(os.path.join(OUTPUT_DIR, "lbo_summary.txt"), "w") as f:
        f.write(f"Target: {a['TargetName']}\n\n")
        f.write("=== Sources & Uses ===\n")
        f.write(f"Entry EV ({a['EntryMultiple']:.1f}x EBITDA): ${su['entry_ev']:,.1f}mm\n")
        f.write(f"Term Loan ({a['TermLoanTurns']:.1f}x @ {a['TermLoanRate']:.1%}): ${su['term_loan_0']:,.1f}mm\n")
        f.write(f"Subordinated Notes ({a['SubNotesTurns']:.1f}x @ {a['SubNotesRate']:.1%}): ${su['sub_notes_0']:,.1f}mm\n")
        f.write(f"Revolver Capacity (undrawn at close): ${a['RevolverCapacity_mm']:,.1f}mm\n")
        f.write(f"Sponsor Equity: ${su['sponsor_equity']:,.1f}mm\n\n")
        f.write("=== Exit Scenarios ===\n")
        f.write(exits.round(2).to_string(index=False))

    plot_debt_paydown(schedule)
    plot_exit_scenarios(exits)

    print(f"=== Full LBO Model: {a['TargetName']} ===")
    print(f"Entry EV: ${su['entry_ev']:,.1f}mm  |  Sponsor Equity: ${su['sponsor_equity']:,.1f}mm\n")
    print("=== Debt Schedule ===")
    print(schedule.round(1).to_string(index=False))
    print("\n=== Exit Scenarios ===")
    print(exits.round(2).to_string(index=False))
    print(f"\nOutputs written to: {OUTPUT_DIR}")


if __name__ == "__main__":
    main()
