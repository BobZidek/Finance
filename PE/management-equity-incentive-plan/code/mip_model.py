"""
Management Equity Incentive Plan (MIP) with Ratchet Design
Bridgeway Logistics Partners

Models a tiered management "ratchet" incentive structure: management's
share of total exit equity proceeds increases in steps as total deal
performance (measured here by total exit value relative to total
initial invested equity) improves, well beyond management's small
initial pro-rata investment - the standard way PE sponsors align
management incentives with maximizing THEIR return, not just growing
the business in the abstract.

Run:
    python mip_model.py
"""

import os
import pandas as pd
import matplotlib.pyplot as plt

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, "data")
OUTPUT_DIR = os.path.join(BASE_DIR, "output")


def load_assumptions() -> dict:
    path = os.path.join(DATA_DIR, "mip_assumptions.csv")
    df = pd.read_csv(path, index_col="Field")
    a = {k: v for k, v in df["Value"].items()}
    for k in a:
        if k != "CompanyName":
            a[k] = float(a[k])
    return a


def load_ratchet_tiers() -> pd.DataFrame:
    return pd.read_csv(os.path.join(DATA_DIR, "ratchet_tiers.csv"))


def management_share_for_moic(total_moic: float, tiers: pd.DataFrame) -> float:
    for _, t in tiers.iterrows():
        if t["MOICLowerBound"] <= total_moic < t["MOICUpperBound"]:
            return t["ManagementSharePct"]
    return tiers.iloc[-1]["ManagementSharePct"]


def compute_split(exit_value: float, a: dict, tiers: pd.DataFrame) -> dict:
    total_invested = a["SponsorInvestment_mm"] + a["ManagementInvestment_mm"]
    total_moic = exit_value / total_invested
    mgmt_pct = management_share_for_moic(total_moic, tiers)

    mgmt_proceeds = exit_value * mgmt_pct
    sponsor_proceeds = exit_value - mgmt_proceeds

    sponsor_moic = sponsor_proceeds / a["SponsorInvestment_mm"]
    mgmt_moic = mgmt_proceeds / a["ManagementInvestment_mm"]

    return {"ExitValue_mm": exit_value, "TotalMOIC": total_moic, "ManagementSharePct": mgmt_pct * 100,
            "SponsorProceeds_mm": sponsor_proceeds, "ManagementProceeds_mm": mgmt_proceeds,
            "SponsorMOIC": sponsor_moic, "ManagementMOIC": mgmt_moic}


def build_scenarios(a: dict, tiers: pd.DataFrame) -> pd.DataFrame:
    total_invested = a["SponsorInvestment_mm"] + a["ManagementInvestment_mm"]
    exit_values = [300, 410, 500, 615, 700, 820, 1000, 1200]
    return pd.DataFrame([compute_split(ev, a, tiers) for ev in exit_values])


def plot_proceeds_split(scenarios: pd.DataFrame):
    fig, ax = plt.subplots(figsize=(10, 6))
    x = scenarios["ExitValue_mm"].astype(str)
    ax.bar(x, scenarios["SponsorProceeds_mm"], label="Sponsor Proceeds", color="#2E5090")
    ax.bar(x, scenarios["ManagementProceeds_mm"], bottom=scenarios["SponsorProceeds_mm"],
           label="Management Proceeds", color="#1E8449")
    ax.set_xlabel("Total Exit Equity Value ($mm)")
    ax.set_ylabel("$mm")
    ax.set_title("Exit Proceeds Split: Sponsor vs. Management (Ratchet)")
    ax.legend()
    fig.tight_layout()
    fig.savefig(os.path.join(OUTPUT_DIR, "proceeds_split.png"), dpi=150)
    plt.close(fig)


def plot_moic_comparison(scenarios: pd.DataFrame):
    fig, ax1 = plt.subplots(figsize=(10, 6))
    ax2 = ax1.twinx()
    x = scenarios["ExitValue_mm"].astype(str)

    ax1.plot(x, scenarios["SponsorMOIC"], marker="o", color="#2E5090", label="Sponsor MOIC", linewidth=2)
    ax2.plot(x, scenarios["ManagementMOIC"], marker="s", color="#1E8449", label="Management MOIC", linewidth=2)

    ax1.set_xlabel("Total Exit Equity Value ($mm)")
    ax1.set_ylabel("Sponsor MOIC (x)", color="#2E5090")
    ax2.set_ylabel("Management MOIC (x)", color="#1E8449")
    ax1.set_title("Sponsor vs. Management MOIC Across Exit Scenarios\n(Management MOIC accelerates due to the ratchet + small initial check)")
    lines1, labels1 = ax1.get_legend_handles_labels()
    lines2, labels2 = ax2.get_legend_handles_labels()
    ax1.legend(lines1 + lines2, labels1 + labels2, loc="upper left", fontsize=8)
    fig.tight_layout()
    fig.savefig(os.path.join(OUTPUT_DIR, "moic_comparison.png"), dpi=150)
    plt.close(fig)


def main():
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    a = load_assumptions()
    tiers = load_ratchet_tiers()

    scenarios = build_scenarios(a, tiers)
    scenarios.round(2).to_csv(os.path.join(OUTPUT_DIR, "ratchet_scenarios.csv"), index=False)

    with open(os.path.join(OUTPUT_DIR, "mip_summary.txt"), "w") as f:
        f.write(f"Company: {a['CompanyName']}\n\n")
        f.write(f"Sponsor Investment: ${a['SponsorInvestment_mm']:,.0f}mm\n")
        f.write(f"Management Investment: ${a['ManagementInvestment_mm']:,.1f}mm\n\n")
        f.write("=== Ratchet Tiers (by Total Deal MOIC) ===\n")
        f.write(tiers.to_string(index=False))
        f.write("\n\n=== Exit Scenarios ===\n")
        f.write(scenarios.round(2).to_string(index=False))
        f.write("\n\nNote: Management's investment is small ($5mm) relative to the sponsor's ($200mm), "
                "so even a modest ratchet percentage of total proceeds produces a dramatically higher "
                "MOIC for management than for the sponsor at the same exit value - by design, this is "
                "what makes the ratchet a powerful incentive tool.\n")

    plot_proceeds_split(scenarios)
    plot_moic_comparison(scenarios)

    print(f"=== Management Equity Incentive Plan: {a['CompanyName']} ===")
    print(scenarios.round(2).to_string(index=False))
    print(f"\nOutputs written to: {OUTPUT_DIR}")


if __name__ == "__main__":
    main()
