"""
LBO Model - Healthcare Services (Dental/Vet Roll-up)

Builds a 5-year leveraged buyout of a hypothetical dental/vet roll-up
platform: sources & uses, a two-tranche debt schedule with mandatory
amortization and a cash flow sweep, an exit at a chosen multiple, and
sponsor IRR/MOIC. Includes an Entry Multiple x Exit Multiple IRR
sensitivity grid.

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
    a["HoldPeriodYears"] = int(a["HoldPeriodYears"])
    return a


def load_drivers() -> pd.DataFrame:
    return pd.read_csv(os.path.join(DATA_DIR, "forecast_drivers.csv"))


def sources_and_uses(a: dict, entry_multiple: float):
    entry_ev = entry_multiple * a["EntryEBITDA_mm"]
    fees = entry_ev * a["TransactionFeePct"]
    term_loan = a["TermLoanTurns"] * a["EntryEBITDA_mm"]
    sub_notes = a["SubNotesTurns"] * a["EntryEBITDA_mm"]
    total_debt = term_loan + sub_notes
    total_uses = entry_ev + fees
    sponsor_equity = total_uses - total_debt
    return {
        "entry_ev": entry_ev, "fees": fees, "term_loan": term_loan, "sub_notes": sub_notes,
        "total_debt": total_debt, "total_uses": total_uses, "sponsor_equity": sponsor_equity,
    }


def run_debt_schedule(a: dict, drivers: pd.DataFrame, term_loan_0: float, sub_notes_0: float) -> pd.DataFrame:
    rows = []
    revenue = a["EntryRevenue_mm"]
    prev_nwc = a["EntryRevenue_mm"] * drivers["NWC_pctRevenue"].iloc[0]  # entry NWC balance (approx at Y0 margin)
    tl_balance = term_loan_0
    sub_balance = sub_notes_0
    tl_mandatory_amort = term_loan_0 * a["TermLoanMandatoryAmortPct"]

    for _, d in drivers.iterrows():
        revenue = revenue * (1 + d["RevenueGrowth"])
        ebitda = revenue * d["EBITDAMargin"]
        da = revenue * d["DA_pctRevenue"]
        ebit = ebitda - da

        interest_tl = tl_balance * a["TermLoanRate"]
        interest_sub = sub_balance * a["SubNotesRate"]
        total_interest = interest_tl + interest_sub

        ebt = ebit - total_interest
        taxes = max(ebt, 0) * a["TaxRate"]
        net_income = ebt - taxes

        capex = revenue * d["Capex_pctRevenue"]
        nwc_balance = revenue * d["NWC_pctRevenue"]
        delta_nwc = nwc_balance - prev_nwc
        prev_nwc = nwc_balance

        fcf_pre_debt_service = net_income + da - capex - delta_nwc

        mandatory_amort = min(tl_mandatory_amort, tl_balance)
        fcf_after_mandatory = max(fcf_pre_debt_service - mandatory_amort, 0)

        sweep_available = fcf_after_mandatory * a["CashSweepPct"]
        tl_after_mandatory = tl_balance - mandatory_amort
        sweep_to_tl = min(sweep_available, tl_after_mandatory)
        sweep_to_sub = min(sweep_available - sweep_to_tl, sub_balance)

        tl_end = tl_after_mandatory - sweep_to_tl
        sub_end = sub_balance - sweep_to_sub

        rows.append({
            "Year": int(d["Year"]), "Revenue_mm": revenue, "EBITDA_mm": ebitda, "EBIT_mm": ebit,
            "InterestExpense_mm": total_interest, "NetIncome_mm": net_income,
            "FCF_PreDebtService_mm": fcf_pre_debt_service,
            "MandatoryAmort_mm": mandatory_amort, "CashSweep_mm": sweep_to_tl + sweep_to_sub,
            "TermLoan_EOY_mm": tl_end, "SubNotes_EOY_mm": sub_end,
            "TotalDebt_EOY_mm": tl_end + sub_end,
        })

        tl_balance = tl_end
        sub_balance = sub_end

    return pd.DataFrame(rows)


def compute_returns(schedule: pd.DataFrame, sponsor_equity: float, exit_multiple: float, hold_years: int):
    exit_ebitda = schedule["EBITDA_mm"].iloc[-1]
    exit_ev = exit_multiple * exit_ebitda
    exit_debt = schedule["TotalDebt_EOY_mm"].iloc[-1]
    exit_equity = exit_ev - exit_debt

    moic = exit_equity / sponsor_equity
    irr = moic ** (1 / hold_years) - 1

    return {
        "exit_ebitda": exit_ebitda, "exit_ev": exit_ev, "exit_debt": exit_debt,
        "exit_equity": exit_equity, "moic": moic, "irr": irr,
    }


def full_run(a: dict, drivers: pd.DataFrame, entry_multiple: float, exit_multiple: float):
    su = sources_and_uses(a, entry_multiple)
    schedule = run_debt_schedule(a, drivers, su["term_loan"], su["sub_notes"])
    returns = compute_returns(schedule, su["sponsor_equity"], exit_multiple, a["HoldPeriodYears"])
    return su, schedule, returns


def sensitivity_grid(a: dict, drivers: pd.DataFrame) -> pd.DataFrame:
    entry_mults = [9.0, 9.5, 10.0, 10.5, 11.0]
    exit_mults = [9.0, 9.5, 10.0, 10.5, 11.0]
    table = pd.DataFrame(index=[f"{e:.1f}x entry" for e in entry_mults],
                          columns=[f"{x:.1f}x exit" for x in exit_mults])
    for e in entry_mults:
        for x in exit_mults:
            _, _, returns = full_run(a, drivers, e, x)
            table.loc[f"{e:.1f}x entry", f"{x:.1f}x exit"] = round(returns["irr"] * 100, 1)
    return table


def plot_debt_paydown(schedule: pd.DataFrame):
    fig, ax = plt.subplots(figsize=(8, 5))
    ax.bar(schedule["Year"], schedule["TermLoan_EOY_mm"], label="Term Loan", color="#2E5090")
    ax.bar(schedule["Year"], schedule["SubNotes_EOY_mm"], bottom=schedule["TermLoan_EOY_mm"],
           label="Subordinated Notes", color="#7FA6D9")
    ax.set_xlabel("Year")
    ax.set_ylabel("Debt Balance ($mm)")
    ax.set_title("Debt Paydown Schedule")
    ax.legend()
    fig.tight_layout()
    fig.savefig(os.path.join(OUTPUT_DIR, "debt_paydown.png"), dpi=150)
    plt.close(fig)


def plot_irr_heatmap(table: pd.DataFrame):
    fig, ax = plt.subplots(figsize=(7, 5))
    data = table.astype(float).values
    im = ax.imshow(data, cmap="RdYlGn")
    ax.set_xticks(range(len(table.columns)))
    ax.set_xticklabels(table.columns, rotation=30, ha="right")
    ax.set_yticks(range(len(table.index)))
    ax.set_yticklabels(table.index)
    ax.set_title("Sponsor IRR (%) — Entry Multiple x Exit Multiple")
    for i in range(data.shape[0]):
        for j in range(data.shape[1]):
            ax.text(j, i, f"{data[i, j]:.1f}%", ha="center", va="center", fontsize=8)
    fig.colorbar(im, ax=ax, label="IRR (%)")
    fig.tight_layout()
    fig.savefig(os.path.join(OUTPUT_DIR, "irr_sensitivity_heatmap.png"), dpi=150)
    plt.close(fig)


def main():
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    a = load_assumptions()
    drivers = load_drivers()

    su, schedule, returns = full_run(a, drivers, a["EntryMultiple"], a["ExitMultiple"])
    sens = sensitivity_grid(a, drivers)

    schedule.round(2).to_csv(os.path.join(OUTPUT_DIR, "debt_schedule.csv"), index=False)
    sens.to_csv(os.path.join(OUTPUT_DIR, "irr_sensitivity.csv"))

    with open(os.path.join(OUTPUT_DIR, "lbo_summary.txt"), "w") as f:
        f.write(f"Target: {a['TargetName']}\n\n")
        f.write("=== Sources & Uses ===\n")
        f.write(f"Entry EV ({a['EntryMultiple']:.1f}x EBITDA): ${su['entry_ev']:,.1f}mm\n")
        f.write(f"Transaction Fees: ${su['fees']:,.1f}mm\n")
        f.write(f"Total Uses: ${su['total_uses']:,.1f}mm\n\n")
        f.write(f"Term Loan ({a['TermLoanTurns']:.1f}x EBITDA @ {a['TermLoanRate']:.1%}): ${su['term_loan']:,.1f}mm\n")
        f.write(f"Subordinated Notes ({a['SubNotesTurns']:.1f}x EBITDA @ {a['SubNotesRate']:.1%}): ${su['sub_notes']:,.1f}mm\n")
        f.write(f"Total Debt: ${su['total_debt']:,.1f}mm ({(su['total_debt']/a['EntryEBITDA_mm']):.1f}x EBITDA)\n")
        f.write(f"Sponsor Equity: ${su['sponsor_equity']:,.1f}mm\n\n")
        f.write("=== Exit (Year 5) ===\n")
        f.write(f"Exit EBITDA: ${returns['exit_ebitda']:,.1f}mm\n")
        f.write(f"Exit EV ({a['ExitMultiple']:.1f}x): ${returns['exit_ev']:,.1f}mm\n")
        f.write(f"Remaining Debt at Exit: ${returns['exit_debt']:,.1f}mm\n")
        f.write(f"Exit Equity Value: ${returns['exit_equity']:,.1f}mm\n\n")
        f.write(f"MOIC: {returns['moic']:.2f}x\n")
        f.write(f"IRR: {returns['irr']:.1%}\n")

    plot_debt_paydown(schedule)
    plot_irr_heatmap(sens)

    print(f"=== LBO Model: {a['TargetName']} ===")
    print(f"Entry EV: ${su['entry_ev']:,.1f}mm  |  Total Debt: ${su['total_debt']:,.1f}mm "
          f"({su['total_debt']/a['EntryEBITDA_mm']:.1f}x)  |  Sponsor Equity: ${su['sponsor_equity']:,.1f}mm")
    print("\n=== Debt Schedule ===")
    print(schedule.round(1).to_string(index=False))
    print(f"\nExit Equity Value: ${returns['exit_equity']:,.1f}mm")
    print(f"MOIC: {returns['moic']:.2f}x  |  IRR: {returns['irr']:.1%}")
    print("\n=== IRR Sensitivity: Entry Multiple x Exit Multiple ===")
    print(sens.to_string())
    print(f"\nOutputs written to: {OUTPUT_DIR}")


if __name__ == "__main__":
    main()
