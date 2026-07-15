"""
Full Investment Memo - Education Services (Quantitative Engine)

The capstone PE project: runs a full multi-tranche LBO (Revolver + Term
Loan + Subordinated Notes, cash sweep waterfall) across three scenarios
(Downside / Base / Upside) for a hypothetical K-12 supplemental education
platform, plus an Entry x Exit multiple sensitivity grid on the base case.
The qualitative market analysis, management assessment, and risk factors
that make this an actual "investment memo" (rather than just a model) live
in theory/investment_memo_narrative.md - this script produces the
quantitative exhibits that memo references.

Run:
    python investment_memo_model.py
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


def load_scenario_drivers() -> pd.DataFrame:
    return pd.read_csv(os.path.join(DATA_DIR, "scenario_drivers.csv"))


def sources_and_uses(a: dict):
    entry_ev = a["EntryMultiple"] * a["EntryEBITDA_mm"]
    fees = entry_ev * a["TransactionFeePct"]
    term_loan = a["TermLoanTurns"] * a["EntryEBITDA_mm"]
    sub_notes = a["SubNotesTurns"] * a["EntryEBITDA_mm"]
    total_funded_debt = term_loan + sub_notes
    total_uses = entry_ev + fees
    sponsor_equity = total_uses - total_funded_debt
    return {"entry_ev": entry_ev, "fees": fees, "term_loan_0": term_loan, "sub_notes_0": sub_notes,
            "total_funded_debt": total_funded_debt, "sponsor_equity": sponsor_equity}


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

        if fcf_after_mandatory < 0:
            shortfall = -fcf_after_mandatory
            draw = min(shortfall, a["RevolverCapacity_mm"] - revolver_balance)
            revolver_balance += draw
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

        rows.append({"Year": int(d["Year"]), "Revenue_mm": revenue, "EBITDA_mm": ebitda,
                     "TotalDebt_EOY_mm": revolver_balance + tl_balance + sub_balance})

    return pd.DataFrame(rows)


def run_scenario(a: dict, drivers_all: pd.DataFrame, scenario: str, su: dict) -> dict:
    drivers = drivers_all[drivers_all["Scenario"] == scenario].sort_values("Year")
    schedule = run_debt_schedule(a, drivers, su["term_loan_0"], su["sub_notes_0"])

    exit_ebitda = schedule["EBITDA_mm"].iloc[-1]
    exit_ev = a["ExitMultiple"] * exit_ebitda
    exit_debt = schedule["TotalDebt_EOY_mm"].iloc[-1]
    exit_equity = exit_ev - exit_debt
    moic = exit_equity / su["sponsor_equity"]
    irr = moic ** (1 / a["HoldPeriodYears"]) - 1

    return {"scenario": scenario, "schedule": schedule, "exit_ebitda": exit_ebitda, "exit_ev": exit_ev,
            "exit_debt": exit_debt, "exit_equity": exit_equity, "moic": moic, "irr": irr}


def entry_exit_sensitivity(a: dict, drivers_all: pd.DataFrame) -> pd.DataFrame:
    entry_mults = [7.0, 7.75, 8.5, 9.25, 10.0]
    exit_mults = [7.5, 8.25, 9.0, 9.75, 10.5]
    table = pd.DataFrame(index=[f"{e:.2f}x entry" for e in entry_mults],
                          columns=[f"{x:.2f}x exit" for x in exit_mults])

    drivers = drivers_all[drivers_all["Scenario"] == "Base"].sort_values("Year")
    for e in entry_mults:
        entry_ev = e * a["EntryEBITDA_mm"]
        fees = entry_ev * a["TransactionFeePct"]
        term_loan = a["TermLoanTurns"] * a["EntryEBITDA_mm"]
        sub_notes = a["SubNotesTurns"] * a["EntryEBITDA_mm"]
        sponsor_equity = entry_ev + fees - term_loan - sub_notes
        schedule = run_debt_schedule(a, drivers, term_loan, sub_notes)
        for x in exit_mults:
            exit_ev = x * schedule["EBITDA_mm"].iloc[-1]
            exit_equity = exit_ev - schedule["TotalDebt_EOY_mm"].iloc[-1]
            irr = (exit_equity / sponsor_equity) ** (1 / a["HoldPeriodYears"]) - 1
            table.loc[f"{e:.2f}x entry", f"{x:.2f}x exit"] = round(irr * 100, 1)
    return table


def plot_scenario_comparison(results: list):
    fig, ax1 = plt.subplots(figsize=(8, 5))
    ax2 = ax1.twinx()
    scenarios = [r["scenario"] for r in results]
    moics = [r["moic"] for r in results]
    irrs = [r["irr"] * 100 for r in results]

    colors = ["#C0392B", "#2E5090", "#1E8449"]
    ax1.bar(scenarios, moics, color=colors)
    ax2.plot(scenarios, irrs, color="black", marker="o", linewidth=2)

    ax1.set_ylabel("MOIC (x)")
    ax2.set_ylabel("IRR (%)")
    ax1.set_title("Sponsor Returns Across Scenarios")
    fig.tight_layout()
    fig.savefig(os.path.join(OUTPUT_DIR, "scenario_comparison.png"), dpi=150)
    plt.close(fig)


def plot_sensitivity_heatmap(table: pd.DataFrame):
    fig, ax = plt.subplots(figsize=(7, 5))
    data = table.astype(float).values
    im = ax.imshow(data, cmap="RdYlGn")
    ax.set_xticks(range(len(table.columns)))
    ax.set_xticklabels(table.columns, rotation=30, ha="right")
    ax.set_yticks(range(len(table.index)))
    ax.set_yticklabels(table.index)
    ax.set_title("Base Case IRR (%) Sensitivity - Entry x Exit Multiple")
    for i in range(data.shape[0]):
        for j in range(data.shape[1]):
            ax.text(j, i, f"{data[i, j]:.1f}%", ha="center", va="center", fontsize=8)
    fig.colorbar(im, ax=ax, label="IRR (%)")
    fig.tight_layout()
    fig.savefig(os.path.join(OUTPUT_DIR, "sensitivity_heatmap.png"), dpi=150)
    plt.close(fig)


def main():
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    a = load_assumptions()
    drivers_all = load_scenario_drivers()

    su = sources_and_uses(a)
    results = [run_scenario(a, drivers_all, s, su) for s in ["Downside", "Base", "Upside"]]
    sens = entry_exit_sensitivity(a, drivers_all)

    for r in results:
        r["schedule"].round(2).to_csv(os.path.join(OUTPUT_DIR, f"schedule_{r['scenario'].lower()}.csv"), index=False)
    sens.to_csv(os.path.join(OUTPUT_DIR, "entry_exit_sensitivity.csv"))

    summary_rows = [{"Scenario": r["scenario"], "ExitEBITDA_mm": r["exit_ebitda"], "ExitEquity_mm": r["exit_equity"],
                      "MOIC": r["moic"], "IRR_pct": r["irr"] * 100} for r in results]
    summary_df = pd.DataFrame(summary_rows)
    summary_df.round(2).to_csv(os.path.join(OUTPUT_DIR, "scenario_summary.csv"), index=False)

    with open(os.path.join(OUTPUT_DIR, "quantitative_summary.txt"), "w") as f:
        f.write(f"Target: {a['TargetName']}\n\n")
        f.write("=== Sources & Uses ===\n")
        f.write(f"Entry EV ({a['EntryMultiple']:.1f}x EBITDA): ${su['entry_ev']:,.1f}mm\n")
        f.write(f"Term Loan ({a['TermLoanTurns']:.1f}x): ${su['term_loan_0']:,.1f}mm\n")
        f.write(f"Subordinated Notes ({a['SubNotesTurns']:.1f}x): ${su['sub_notes_0']:,.1f}mm\n")
        f.write(f"Sponsor Equity: ${su['sponsor_equity']:,.1f}mm\n\n")
        f.write("=== Scenario Comparison (5-Year Hold) ===\n")
        f.write(summary_df.round(2).to_string(index=False))

    plot_scenario_comparison(results)
    plot_sensitivity_heatmap(sens)

    print(f"=== Investment Memo Quantitative Engine: {a['TargetName']} ===")
    print(f"Sponsor Equity: ${su['sponsor_equity']:,.1f}mm\n")
    print(summary_df.round(2).to_string(index=False))
    print("\n=== Base Case IRR Sensitivity: Entry x Exit Multiple ===")
    print(sens.to_string())
    print(f"\nOutputs written to: {OUTPUT_DIR}")


if __name__ == "__main__":
    main()
