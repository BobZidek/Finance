"""
Asset-Based Lending (ABL) Borrowing Base Model - Ferrous Metals Distribution Co.

Builds a revolving credit facility borrowing base from the lender's
perspective: eligible accounts receivable and inventory (net of
ineligibles), advance rates, and reserves determine total availability,
which is then compared against the facility commitment and current
draws to compute excess availability - and checks whether that
availability trips the springing minimum-availability covenant common in
ABL facilities. Includes a working-capital stress scenario.

Run:
    python borrowing_base_model.py
"""

import os
import pandas as pd
import matplotlib.pyplot as plt

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, "data")
OUTPUT_DIR = os.path.join(BASE_DIR, "output")


def load_assumptions() -> dict:
    path = os.path.join(DATA_DIR, "borrowing_base_assumptions.csv")
    df = pd.read_csv(path, index_col="Field")
    a = {k: v for k, v in df["Value"].items()}
    for k in a:
        if k != "BorrowerName":
            a[k] = float(a[k])
    return a


def compute_borrowing_base(a: dict, ar_shock: float = 0.0, inventory_shock: float = 0.0) -> dict:
    gross_ar = a["GrossAR_mm"] * (1 + ar_shock)
    eligible_ar = gross_ar - a["IneligibleAR_mm"]
    ar_component = eligible_ar * a["ARAdvanceRate"]

    gross_inventory = a["GrossInventory_mm"] * (1 + inventory_shock)
    eligible_inventory_cost = gross_inventory - a["IneligibleInventory_mm"]
    eligible_inventory_nolv = eligible_inventory_cost * a["InventoryNOLVPct"]
    inventory_component = eligible_inventory_nolv * a["InventoryAdvanceRate"]

    gross_borrowing_base = ar_component + inventory_component
    net_borrowing_base = gross_borrowing_base - a["Reserves_mm"]

    availability = min(net_borrowing_base, a["FacilityCommitment_mm"])
    excess_availability = availability - a["OutstandingDraws_mm"] - a["LettersOfCredit_mm"]

    covenant_threshold = a["MinExcessAvailabilityCovenantPct"] * a["FacilityCommitment_mm"]
    covenant_triggered = excess_availability < covenant_threshold

    return {
        "gross_ar": gross_ar, "eligible_ar": eligible_ar, "ar_component": ar_component,
        "gross_inventory": gross_inventory, "eligible_inventory_cost": eligible_inventory_cost,
        "eligible_inventory_nolv": eligible_inventory_nolv, "inventory_component": inventory_component,
        "gross_borrowing_base": gross_borrowing_base, "net_borrowing_base": net_borrowing_base,
        "availability": availability, "excess_availability": excess_availability,
        "covenant_threshold": covenant_threshold, "covenant_triggered": covenant_triggered,
    }


def stress_test(a: dict) -> pd.DataFrame:
    scenarios = [
        ("Base Case", 0.0, 0.0),
        ("Mild Contraction (-10% AR, -8% Inv)", -0.10, -0.08),
        ("Moderate Downturn (-20% AR, -15% Inv)", -0.20, -0.15),
        ("Severe Stress (-35% AR, -25% Inv)", -0.35, -0.25),
    ]
    rows = []
    for name, ar_shock, inv_shock in scenarios:
        res = compute_borrowing_base(a, ar_shock, inv_shock)
        rows.append({"Scenario": name, "NetBorrowingBase_mm": res["net_borrowing_base"],
                     "Availability_mm": res["availability"], "ExcessAvailability_mm": res["excess_availability"],
                     "CovenantTriggered": res["covenant_triggered"]})
    return pd.DataFrame(rows)


def plot_borrowing_base_bridge(res: dict, a: dict):
    fig, ax = plt.subplots(figsize=(10, 6))
    labels = ["Eligible AR\n(x85% adv. rate)", "Eligible Inventory\n(NOLV x60% adv. rate)", "Reserves",
              "Net Borrowing\nBase", "Outstanding\nDraws + LCs", "Excess\nAvailability"]
    values = [res["ar_component"], res["inventory_component"], -a["Reserves_mm"], None,
              -(a["OutstandingDraws_mm"] + a["LettersOfCredit_mm"]), None]

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
    ax.axhline(res["covenant_threshold"], color="#F1C40F", linestyle="--",
               label=f"Min. Covenant Threshold (${res['covenant_threshold']:,.1f}mm)")
    ax.set_ylabel("$mm")
    ax.set_title(f"Borrowing Base Bridge - {a['BorrowerName']}")
    ax.legend(fontsize=8)
    plt.xticks(rotation=15, ha="right")
    fig.tight_layout()
    fig.savefig(os.path.join(OUTPUT_DIR, "borrowing_base_bridge.png"), dpi=150)
    plt.close(fig)


def plot_stress_test(stress_df: pd.DataFrame, covenant_threshold: float):
    fig, ax = plt.subplots(figsize=(10, 6))
    colors = ["#C0392B" if t else "#1E8449" for t in stress_df["CovenantTriggered"]]
    ax.bar(stress_df["Scenario"], stress_df["ExcessAvailability_mm"], color=colors)
    ax.axhline(covenant_threshold, color="#F1C40F", linestyle="--",
               label=f"Min. Covenant Threshold (${covenant_threshold:,.1f}mm)")
    ax.axhline(0, color="black", linewidth=0.8)
    ax.set_ylabel("Excess Availability ($mm)")
    ax.set_title("Excess Availability Under Working Capital Stress Scenarios")
    ax.legend()
    plt.xticks(rotation=15, ha="right", fontsize=8)
    fig.tight_layout()
    fig.savefig(os.path.join(OUTPUT_DIR, "stress_test.png"), dpi=150)
    plt.close(fig)


def main():
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    a = load_assumptions()

    base = compute_borrowing_base(a)
    stress_df = stress_test(a)
    stress_df.round(2).to_csv(os.path.join(OUTPUT_DIR, "stress_test.csv"), index=False)

    with open(os.path.join(OUTPUT_DIR, "borrowing_base_summary.txt"), "w") as f:
        f.write(f"Borrower: {a['BorrowerName']}\n\n")
        f.write("=== Accounts Receivable Component ===\n")
        f.write(f"Gross AR: ${base['gross_ar']:,.1f}mm\n")
        f.write(f"Less: Ineligible AR: -${a['IneligibleAR_mm']:,.1f}mm\n")
        f.write(f"Eligible AR: ${base['eligible_ar']:,.1f}mm\n")
        f.write(f"AR Advance Rate: {a['ARAdvanceRate']:.0%}\n")
        f.write(f"AR Borrowing Base Component: ${base['ar_component']:,.2f}mm\n\n")
        f.write("=== Inventory Component ===\n")
        f.write(f"Gross Inventory (at cost): ${base['gross_inventory']:,.1f}mm\n")
        f.write(f"Less: Ineligible Inventory: -${a['IneligibleInventory_mm']:,.1f}mm\n")
        f.write(f"Eligible Inventory (at cost): ${base['eligible_inventory_cost']:,.1f}mm\n")
        f.write(f"NOLV %: {a['InventoryNOLVPct']:.0%}\n")
        f.write(f"Eligible Inventory (at NOLV): ${base['eligible_inventory_nolv']:,.2f}mm\n")
        f.write(f"Inventory Advance Rate: {a['InventoryAdvanceRate']:.0%}\n")
        f.write(f"Inventory Borrowing Base Component: ${base['inventory_component']:,.2f}mm\n\n")
        f.write("=== Total Borrowing Base ===\n")
        f.write(f"Gross Borrowing Base: ${base['gross_borrowing_base']:,.2f}mm\n")
        f.write(f"Less: Reserves: -${a['Reserves_mm']:,.1f}mm\n")
        f.write(f"Net Borrowing Base: ${base['net_borrowing_base']:,.2f}mm\n")
        f.write(f"Facility Commitment: ${a['FacilityCommitment_mm']:,.1f}mm\n")
        f.write(f"Availability (lesser of the two): ${base['availability']:,.2f}mm\n\n")
        f.write(f"Outstanding Draws: ${a['OutstandingDraws_mm']:,.1f}mm\n")
        f.write(f"Letters of Credit: ${a['LettersOfCredit_mm']:,.1f}mm\n")
        f.write(f"Excess Availability: ${base['excess_availability']:,.2f}mm\n\n")
        f.write(f"Springing Covenant Threshold ({a['MinExcessAvailabilityCovenantPct']:.0%} of commitment): "
                f"${base['covenant_threshold']:,.1f}mm\n")
        f.write(f"Covenant Triggered: {base['covenant_triggered']}\n\n")
        f.write("=== Working Capital Stress Test ===\n")
        f.write(stress_df.round(2).to_string(index=False))

    plot_borrowing_base_bridge(base, a)
    plot_stress_test(stress_df, base["covenant_threshold"])

    print(f"=== ABL Borrowing Base: {a['BorrowerName']} ===")
    print(f"Net Borrowing Base: ${base['net_borrowing_base']:,.2f}mm  |  "
          f"Availability: ${base['availability']:,.2f}mm")
    print(f"Excess Availability: ${base['excess_availability']:,.2f}mm  |  "
          f"Covenant Threshold: ${base['covenant_threshold']:,.1f}mm  |  "
          f"Triggered: {base['covenant_triggered']}\n")
    print(stress_df.round(2).to_string(index=False))
    print(f"\nOutputs written to: {OUTPUT_DIR}")


if __name__ == "__main__":
    main()
