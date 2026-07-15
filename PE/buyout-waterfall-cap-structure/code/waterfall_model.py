"""
Buyout Capital Structure & Sponsor / Management Return Waterfall

Models a buyout equity structure (sponsor participating preferred, sponsor
common, management rollover, management option pool), computes exit
equity proceeds from a simplified LBO, and runs those proceeds through a
distribution waterfall: return of preferred capital, then accrued
preferred return, then pro-rata participation in the residual by all
common-equivalent holders (including preferred, since it's participating).

This is a deal-level equity capitalization table and exit waterfall -
distinct from a VC-style priced-round cap table (see VC/ for that) and
from a fund-level LP/GP carry waterfall (see PE/fund-model-waterfall).

Run:
    python waterfall_model.py
"""

import os
import pandas as pd
import matplotlib.pyplot as plt

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, "data")
OUTPUT_DIR = os.path.join(BASE_DIR, "output")


def load_assumptions() -> dict:
    path = os.path.join(DATA_DIR, "deal_assumptions.csv")
    df = pd.read_csv(path, index_col="Field")
    a = {k: v for k, v in df["Value"].items()}
    for k in a:
        if k != "TargetName":
            a[k] = float(a[k])
    a["HoldPeriodYears"] = int(a["HoldPeriodYears"])
    return a


def build_cap_structure(a: dict) -> dict:
    entry_ev = a["EntryMultiple"] * a["EntryEBITDA_mm"]
    fees = entry_ev * a["TransactionFeePct"]
    debt = a["LeverageMultiple"] * a["EntryEBITDA_mm"]
    total_equity_required = entry_ev + fees - debt

    mgmt_rollover = a["ManagementRollover_mm"]
    sponsor_commitment = total_equity_required - mgmt_rollover
    sponsor_preferred = sponsor_commitment * a["SponsorPreferredPct"]
    sponsor_common = sponsor_commitment * (1 - a["SponsorPreferredPct"])

    # $1 invested = 1 unit for preferred, sponsor common, and management rollover
    pref_units = sponsor_preferred
    sponsor_common_units = sponsor_common
    rollover_units = mgmt_rollover
    common_ex_options = sponsor_common_units + rollover_units
    option_units = common_ex_options * a["OptionPoolPctOfCommon"] / (1 - a["OptionPoolPctOfCommon"])

    return {
        "entry_ev": entry_ev, "fees": fees, "debt": debt,
        "total_equity_required": total_equity_required,
        "sponsor_preferred": sponsor_preferred, "sponsor_common": sponsor_common,
        "mgmt_rollover": mgmt_rollover,
        "pref_units": pref_units, "sponsor_common_units": sponsor_common_units,
        "rollover_units": rollover_units, "option_units": option_units,
    }


def run_exit_equity(a: dict, cap: dict) -> dict:
    ebitda = a["EntryEBITDA_mm"]
    remaining_debt = cap["debt"]
    for _ in range(a["HoldPeriodYears"]):
        ebitda = ebitda * (1 + a["EBITDAGrowthRate"])
        paydown = min(a["DebtPaydownPctEBITDA"] * ebitda, remaining_debt)
        remaining_debt -= paydown

    exit_ev = a["ExitMultiple"] * ebitda
    exit_equity = exit_ev - remaining_debt
    return {"exit_ebitda": ebitda, "exit_ev": exit_ev, "remaining_debt": remaining_debt,
            "exit_equity": exit_equity}


def run_waterfall(a: dict, cap: dict, exit_equity: float) -> pd.DataFrame:
    remaining = exit_equity

    # Tier 1: return of preferred capital
    tier1_pref = min(remaining, cap["sponsor_preferred"])
    remaining -= tier1_pref

    # Tier 2: accrued preferred return (cumulative compounding)
    accrued_pref_return = cap["sponsor_preferred"] * ((1 + a["PreferredRate"]) ** a["HoldPeriodYears"] - 1)
    tier2_pref = min(remaining, accrued_pref_return)
    remaining -= tier2_pref

    # Tier 3: pro-rata participation among all common-equivalent units
    # (participating preferred converts 1:1 alongside sponsor common, rollover, and options)
    total_participating_units = (cap["pref_units"] + cap["sponsor_common_units"]
                                  + cap["rollover_units"] + cap["option_units"])

    def tier3_share(units):
        return remaining * (units / total_participating_units) if total_participating_units > 0 else 0

    tier3_pref = tier3_share(cap["pref_units"])
    tier3_sponsor_common = tier3_share(cap["sponsor_common_units"])
    tier3_rollover = tier3_share(cap["rollover_units"])
    tier3_options = tier3_share(cap["option_units"])

    rows = [
        {"Class": "Sponsor Preferred", "InvestedCapital_mm": cap["sponsor_preferred"],
         "ReturnOfCapital_mm": tier1_pref, "AccruedPrefReturn_mm": tier2_pref,
         "CommonParticipation_mm": tier3_pref,
         "TotalProceeds_mm": tier1_pref + tier2_pref + tier3_pref},
        {"Class": "Sponsor Common", "InvestedCapital_mm": cap["sponsor_common"],
         "ReturnOfCapital_mm": 0.0, "AccruedPrefReturn_mm": 0.0,
         "CommonParticipation_mm": tier3_sponsor_common,
         "TotalProceeds_mm": tier3_sponsor_common},
        {"Class": "Management Rollover", "InvestedCapital_mm": cap["mgmt_rollover"],
         "ReturnOfCapital_mm": 0.0, "AccruedPrefReturn_mm": 0.0,
         "CommonParticipation_mm": tier3_rollover,
         "TotalProceeds_mm": tier3_rollover},
        {"Class": "Management Option Pool", "InvestedCapital_mm": 0.0,
         "ReturnOfCapital_mm": 0.0, "AccruedPrefReturn_mm": 0.0,
         "CommonParticipation_mm": tier3_options,
         "TotalProceeds_mm": tier3_options},
    ]
    df = pd.DataFrame(rows)
    df["MOIC"] = df.apply(
        lambda r: (r["TotalProceeds_mm"] / r["InvestedCapital_mm"]) if r["InvestedCapital_mm"] > 0 else None,
        axis=1,
    )
    return df


def plot_proceeds_split(df: pd.DataFrame, target_name: str):
    fig, ax = plt.subplots(figsize=(7, 6))
    ax.pie(df["TotalProceeds_mm"], labels=df["Class"], autopct="%1.1f%%",
           colors=["#2E5090", "#7FA6D9", "#1E8449", "#F1C40F"])
    ax.set_title(f"Exit Proceeds Split by Equity Class - {target_name}")
    fig.tight_layout()
    fig.savefig(os.path.join(OUTPUT_DIR, "proceeds_split.png"), dpi=150)
    plt.close(fig)


def plot_waterfall_tiers(df: pd.DataFrame):
    fig, ax = plt.subplots(figsize=(9, 5))
    bottom = pd.Series([0.0] * len(df))
    for col, color, label in [("ReturnOfCapital_mm", "#2E5090", "Return of Preferred Capital"),
                                ("AccruedPrefReturn_mm", "#7FA6D9", "Accrued Preferred Return"),
                                ("CommonParticipation_mm", "#1E8449", "Common Participation")]:
        ax.bar(df["Class"], df[col], bottom=bottom, label=label, color=color)
        bottom += df[col]
    ax.set_ylabel("$mm")
    ax.set_title("Exit Proceeds by Waterfall Tier and Equity Class")
    ax.legend()
    plt.xticks(rotation=20, ha="right")
    fig.tight_layout()
    fig.savefig(os.path.join(OUTPUT_DIR, "waterfall_tiers.png"), dpi=150)
    plt.close(fig)


def main():
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    a = load_assumptions()

    cap = build_cap_structure(a)
    exit_res = run_exit_equity(a, cap)
    waterfall = run_waterfall(a, cap, exit_res["exit_equity"])

    waterfall.round(2).to_csv(os.path.join(OUTPUT_DIR, "waterfall_detail.csv"), index=False)

    with open(os.path.join(OUTPUT_DIR, "deal_summary.txt"), "w") as f:
        f.write(f"Target: {a['TargetName']}\n\n")
        f.write("=== Sources & Uses ===\n")
        f.write(f"Entry EV ({a['EntryMultiple']:.1f}x EBITDA): ${cap['entry_ev']:,.1f}mm\n")
        f.write(f"Debt ({a['LeverageMultiple']:.1f}x EBITDA): ${cap['debt']:,.1f}mm\n")
        f.write(f"Total Equity Required: ${cap['total_equity_required']:,.1f}mm\n")
        f.write(f"  Sponsor Preferred: ${cap['sponsor_preferred']:,.1f}mm ({a['PreferredRate']:.0%} cumulative, participating)\n")
        f.write(f"  Sponsor Common: ${cap['sponsor_common']:,.1f}mm\n")
        f.write(f"  Management Rollover: ${cap['mgmt_rollover']:,.1f}mm\n")
        f.write(f"  Management Option Pool: {a['OptionPoolPctOfCommon']:.0%} of fully diluted common "
                f"({cap['option_units']:,.2f}mm units)\n\n")
        f.write(f"=== Exit (Year {a['HoldPeriodYears']:.0f}) ===\n")
        f.write(f"Exit EBITDA: ${exit_res['exit_ebitda']:,.1f}mm\n")
        f.write(f"Exit EV ({a['ExitMultiple']:.1f}x): ${exit_res['exit_ev']:,.1f}mm\n")
        f.write(f"Remaining Debt: ${exit_res['remaining_debt']:,.1f}mm\n")
        f.write(f"Exit Equity Value: ${exit_res['exit_equity']:,.1f}mm\n\n")
        f.write("=== Waterfall Distribution ===\n")
        f.write(waterfall.round(2).to_string(index=False))

    plot_proceeds_split(waterfall, a["TargetName"])
    plot_waterfall_tiers(waterfall)

    print(f"=== Buyout Waterfall: {a['TargetName']} ===")
    print(f"Exit Equity Value: ${exit_res['exit_equity']:,.1f}mm\n")
    print(waterfall.round(2).to_string(index=False))
    print(f"\nOutputs written to: {OUTPUT_DIR}")


if __name__ == "__main__":
    main()
