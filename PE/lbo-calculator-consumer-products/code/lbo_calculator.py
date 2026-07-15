"""
Quick LBO Returns Calculator - Consumer Products

A deliberately simplified "back of the envelope" LBO calculator - the kind
of quick mental-math model used to sanity check a deal in minutes, before
building the full multi-tranche debt schedule (see
IB/lbo-model-healthcare-services or PE/full-lbo-model-business-services for
the detailed version). Debt paydown here is approximated as a flat % of
EBITDA swept each year, rather than a full interest/tax/capex-driven free
cash flow build.

Also computes the equivalent unlevered (100% equity) return, to isolate
how much of the levered IRR is coming from leverage itself.

Run:
    python lbo_calculator.py
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


def run_quick_lbo(a: dict, entry_multiple: float = None, exit_multiple: float = None,
                   hold_years: int = None) -> dict:
    entry_multiple = a["EntryMultiple"] if entry_multiple is None else entry_multiple
    exit_multiple = a["ExitMultiple"] if exit_multiple is None else exit_multiple
    hold_years = a["HoldPeriodYears"] if hold_years is None else hold_years

    entry_ev = entry_multiple * a["EntryEBITDA_mm"]
    debt = a["LeverageMultiple"] * a["EntryEBITDA_mm"]
    sponsor_equity = entry_ev - debt

    ebitda = a["EntryEBITDA_mm"]
    remaining_debt = debt
    schedule = []
    for year in range(1, hold_years + 1):
        ebitda = ebitda * (1 + a["EBITDAGrowthRate"])
        paydown = min(a["DebtPaydownPctEBITDA"] * ebitda, remaining_debt)
        remaining_debt -= paydown
        schedule.append({"Year": year, "EBITDA_mm": ebitda, "DebtPaydown_mm": paydown,
                          "RemainingDebt_mm": remaining_debt})

    exit_ebitda = ebitda
    exit_ev = exit_multiple * exit_ebitda
    exit_equity = exit_ev - remaining_debt

    moic = exit_equity / sponsor_equity
    irr = moic ** (1 / hold_years) - 1

    # Unlevered comparison: same entry/exit EV, no debt, 100% equity funded
    unlevered_moic = exit_ev / entry_ev
    unlevered_irr = unlevered_moic ** (1 / hold_years) - 1

    return {
        "entry_ev": entry_ev, "debt": debt, "sponsor_equity": sponsor_equity,
        "exit_ebitda": exit_ebitda, "exit_ev": exit_ev, "remaining_debt": remaining_debt,
        "exit_equity": exit_equity, "moic": moic, "irr": irr,
        "unlevered_moic": unlevered_moic, "unlevered_irr": unlevered_irr,
        "schedule": pd.DataFrame(schedule),
    }


def sensitivity_grid(a: dict) -> pd.DataFrame:
    entry_mults = [7.0, 7.75, 8.5, 9.25, 10.0]
    exit_mults = [7.0, 7.75, 8.5, 9.25, 10.0]
    table = pd.DataFrame(index=[f"{e:.2f}x entry" for e in entry_mults],
                          columns=[f"{x:.2f}x exit" for x in exit_mults])
    for e in entry_mults:
        for x in exit_mults:
            res = run_quick_lbo(a, entry_multiple=e, exit_multiple=x)
            table.loc[f"{e:.2f}x entry", f"{x:.2f}x exit"] = round(res["irr"] * 100, 1)
    return table


def plot_equity_bridge(base: dict, a: dict):
    fig, ax = plt.subplots(figsize=(6, 5))
    bars = ax.bar(["Entry Equity", "Exit Equity"], [base["sponsor_equity"], base["exit_equity"]],
                   color=["#7FA6D9", "#2E5090"])
    for bar in bars:
        h = bar.get_height()
        ax.annotate(f"${h:,.1f}mm", (bar.get_x() + bar.get_width() / 2, h), ha="center", va="bottom")
    ax.set_ylabel("$mm")
    ax.set_title(f"Sponsor Equity: Entry vs. Exit ({a['HoldPeriodYears']:.0f}-yr hold)\n"
                 f"MOIC {base['moic']:.2f}x | IRR {base['irr']:.1%}")
    fig.tight_layout()
    fig.savefig(os.path.join(OUTPUT_DIR, "equity_bridge.png"), dpi=150)
    plt.close(fig)


def plot_sensitivity_heatmap(table: pd.DataFrame):
    fig, ax = plt.subplots(figsize=(7, 5))
    data = table.astype(float).values
    im = ax.imshow(data, cmap="RdYlGn")
    ax.set_xticks(range(len(table.columns)))
    ax.set_xticklabels(table.columns, rotation=30, ha="right")
    ax.set_yticks(range(len(table.index)))
    ax.set_yticklabels(table.index)
    ax.set_title("Quick IRR Sensitivity (%) - Entry x Exit Multiple")
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

    base = run_quick_lbo(a)
    sens = sensitivity_grid(a)

    base["schedule"].round(2).to_csv(os.path.join(OUTPUT_DIR, "debt_paydown_schedule.csv"), index=False)
    sens.to_csv(os.path.join(OUTPUT_DIR, "irr_sensitivity.csv"))

    with open(os.path.join(OUTPUT_DIR, "summary.txt"), "w") as f:
        f.write(f"Target: {a['TargetName']}\n\n")
        f.write(f"Entry EV ({a['EntryMultiple']:.2f}x EBITDA): ${base['entry_ev']:,.1f}mm\n")
        f.write(f"Entry Debt ({a['LeverageMultiple']:.1f}x EBITDA): ${base['debt']:,.1f}mm\n")
        f.write(f"Sponsor Equity: ${base['sponsor_equity']:,.1f}mm\n\n")
        f.write(f"Exit EBITDA (Year {a['HoldPeriodYears']:.0f}): ${base['exit_ebitda']:,.1f}mm\n")
        f.write(f"Exit EV ({a['ExitMultiple']:.2f}x): ${base['exit_ev']:,.1f}mm\n")
        f.write(f"Remaining Debt at Exit: ${base['remaining_debt']:,.1f}mm\n")
        f.write(f"Exit Equity: ${base['exit_equity']:,.1f}mm\n\n")
        f.write(f"Levered MOIC: {base['moic']:.2f}x   |   Levered IRR: {base['irr']:.1%}\n")
        f.write(f"Unlevered (100% equity) MOIC: {base['unlevered_moic']:.2f}x   |   "
                f"Unlevered IRR: {base['unlevered_irr']:.1%}\n")
        f.write(f"\nLeverage contribution to IRR: {(base['irr'] - base['unlevered_irr'])*100:.1f} points\n")

    plot_equity_bridge(base, a)
    plot_sensitivity_heatmap(sens)

    print(f"=== Quick LBO Calculator: {a['TargetName']} ===")
    print(f"Entry EV: ${base['entry_ev']:,.1f}mm  |  Debt: ${base['debt']:,.1f}mm  |  "
          f"Sponsor Equity: ${base['sponsor_equity']:,.1f}mm")
    print(f"Exit Equity: ${base['exit_equity']:,.1f}mm")
    print(f"Levered:   MOIC {base['moic']:.2f}x  |  IRR {base['irr']:.1%}")
    print(f"Unlevered: MOIC {base['unlevered_moic']:.2f}x  |  IRR {base['unlevered_irr']:.1%}")
    print(f"Leverage contributes {(base['irr'] - base['unlevered_irr'])*100:.1f} IRR points\n")
    print("=== IRR Sensitivity: Entry Multiple x Exit Multiple ===")
    print(sens.to_string())
    print(f"\nOutputs written to: {OUTPUT_DIR}")


if __name__ == "__main__":
    main()
