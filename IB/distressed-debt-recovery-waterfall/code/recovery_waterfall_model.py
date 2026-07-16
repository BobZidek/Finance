"""
Distressed Debt Recovery Waterfall & Fulcrum Security Analysis
Anchorage Retail Holdings

Distributes an assumed reorganization enterprise value across a
6-tranche capital structure in strict absolute-priority order (secured
super-senior first, common equity last), identifies the "fulcrum
security" - the tranche where recovery transitions from 100% to a
partial recovery, which is where the real economic ownership of the
reorganized company sits - and sensitizes recovery by tranche across a
range of reorganization enterprise values.

Run:
    python recovery_waterfall_model.py
"""

import os
import pandas as pd
import matplotlib.pyplot as plt

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, "data")
OUTPUT_DIR = os.path.join(BASE_DIR, "output")


def load_capital_structure() -> pd.DataFrame:
    return pd.read_csv(os.path.join(DATA_DIR, "capital_structure.csv"))


def load_reorg_assumptions() -> dict:
    path = os.path.join(DATA_DIR, "reorg_assumptions.csv")
    df = pd.read_csv(path, index_col="Field")
    a = {k: v for k, v in df["Value"].items()}
    for k in a:
        if k != "CompanyName":
            a[k] = float(a[k])
    return a


def run_waterfall(cap_structure: pd.DataFrame, reorg_ev: float) -> pd.DataFrame:
    cap_structure = cap_structure.sort_values("Rank").copy()
    remaining = reorg_ev
    recoveries, recovery_pcts = [], []

    for _, row in cap_structure.iterrows():
        par = row["ParAmount_mm"]
        recovery = min(remaining, par) if par > 0 else remaining  # equity gets whatever's left
        recovery = max(recovery, 0)
        recoveries.append(recovery)
        recovery_pcts.append(recovery / par if par > 0 else None)
        remaining = max(remaining - recovery, 0)

    cap_structure["Recovery_mm"] = recoveries
    cap_structure["RecoveryPct"] = recovery_pcts
    return cap_structure


def identify_fulcrum(waterfall: pd.DataFrame) -> str:
    debt_tranches = waterfall[waterfall["Type"] != "Equity"]
    partial = debt_tranches[(debt_tranches["RecoveryPct"] > 0) & (debt_tranches["RecoveryPct"] < 1.0)]
    if len(partial) > 0:
        return partial.iloc[0]["Tranche"]
    zero_recovery = debt_tranches[debt_tranches["RecoveryPct"] == 0]
    if len(zero_recovery) > 0:
        return zero_recovery.iloc[0]["Tranche"] + " (fully impaired - fulcrum sits above it)"
    return "Common Equity (all debt recovers in full)"


def sensitivity_by_ev(cap_structure: pd.DataFrame, ev_range: list) -> pd.DataFrame:
    rows = []
    for ev in ev_range:
        wf = run_waterfall(cap_structure, ev)
        row = {"ReorgEV_mm": ev}
        for _, tranche in wf.iterrows():
            row[tranche["Tranche"]] = round((tranche["RecoveryPct"] or 0) * 100, 1)
        rows.append(row)
    return pd.DataFrame(rows)


def plot_recovery_by_ev(sens: pd.DataFrame, tranches: list, base_ev: float):
    fig, ax = plt.subplots(figsize=(10, 6))
    colors = plt.cm.viridis_r([i / len(tranches) for i in range(len(tranches))])
    for tranche, color in zip(tranches, colors):
        ax.plot(sens["ReorgEV_mm"], sens[tranche], label=tranche, color=color, linewidth=2)
    ax.axvline(base_ev, color="grey", linestyle="--", linewidth=1, label=f"Base Case EV (${base_ev:,.0f}mm)")
    ax.set_xlabel("Reorganization Enterprise Value ($mm)")
    ax.set_ylabel("Recovery (%)")
    ax.set_title("Recovery by Tranche Across Reorganization Enterprise Value")
    ax.legend(fontsize=7, loc="upper left")
    fig.tight_layout()
    fig.savefig(os.path.join(OUTPUT_DIR, "recovery_by_ev.png"), dpi=150)
    plt.close(fig)


def plot_base_case_waterfall(waterfall: pd.DataFrame, reorg_ev: float):
    fig, ax = plt.subplots(figsize=(10, 6))
    colors = ["#1E8449" if (r or 0) == 1.0 else "#F1C40F" if (r or 0) > 0 else "#C0392B"
              for r in waterfall["RecoveryPct"]]
    ax.bar(waterfall["Tranche"], waterfall["Recovery_mm"], color=colors)
    for i, (_, row) in enumerate(waterfall.iterrows()):
        pct = row["RecoveryPct"]
        label = f"{pct:.0%}" if pct is not None else "N/A"
        ax.annotate(label, (i, row["Recovery_mm"]), ha="center", va="bottom", fontsize=9)
    ax.set_ylabel("Recovery ($mm)")
    ax.set_title(f"Base Case Recovery Waterfall (Reorg EV = ${reorg_ev:,.0f}mm)")
    plt.xticks(rotation=20, ha="right")
    fig.tight_layout()
    fig.savefig(os.path.join(OUTPUT_DIR, "base_case_waterfall.png"), dpi=150)
    plt.close(fig)


def main():
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    cap_structure = load_capital_structure()
    a = load_reorg_assumptions()

    reorg_ev = a["EmergenceEBITDA_mm"] * a["ReorgMultiple"]
    waterfall = run_waterfall(cap_structure, reorg_ev)
    fulcrum = identify_fulcrum(waterfall)

    waterfall.round(3).to_csv(os.path.join(OUTPUT_DIR, "base_case_waterfall.csv"), index=False)

    ev_range = list(range(300, 950, 50))
    sens = sensitivity_by_ev(cap_structure, ev_range)
    sens.to_csv(os.path.join(OUTPUT_DIR, "recovery_sensitivity.csv"), index=False)

    total_debt = cap_structure[cap_structure["Type"] != "Equity"]["ParAmount_mm"].sum()

    with open(os.path.join(OUTPUT_DIR, "recovery_summary.txt"), "w") as f:
        f.write(f"Company: {a['CompanyName']}\n\n")
        f.write(f"Total Funded Debt: ${total_debt:,.0f}mm\n")
        f.write(f"Reorganization Enterprise Value: ${a['EmergenceEBITDA_mm']:,.0f}mm EBITDA x "
                f"{a['ReorgMultiple']:.1f}x = ${reorg_ev:,.0f}mm\n")
        f.write(f"Implied overall impairment: {reorg_ev / total_debt - 1:.1%} of total debt claims\n\n")
        f.write("=== Base Case Recovery Waterfall ===\n")
        f.write(waterfall[["Rank", "Tranche", "ParAmount_mm", "Recovery_mm", "RecoveryPct"]]
                .round(3).to_string(index=False))
        f.write(f"\n\nFulcrum Security: {fulcrum}\n")
        f.write("(The fulcrum security is the tranche where recovery value runs out mid-claim - "
                "in a real restructuring, holders of this tranche typically receive the new equity "
                "of the reorganized company, making them the fulcrum security's true economic owners.)\n")

    plot_base_case_waterfall(waterfall, reorg_ev)
    tranches = cap_structure["Tranche"].tolist()
    plot_recovery_by_ev(sens, tranches, reorg_ev)

    print(f"=== Distressed Debt Recovery Waterfall: {a['CompanyName']} ===")
    print(f"Reorg EV: ${reorg_ev:,.0f}mm  |  Total Debt: ${total_debt:,.0f}mm\n")
    print(waterfall[["Rank", "Tranche", "ParAmount_mm", "Recovery_mm", "RecoveryPct"]]
          .round(3).to_string(index=False))
    print(f"\nFulcrum Security: {fulcrum}")
    print(f"\nOutputs written to: {OUTPUT_DIR}")


if __name__ == "__main__":
    main()
