"""
Term Sheet Analyzer - Liquidation Preference Structures - Brightline Robotics

Compares three liquidation preference structures for a Series B investment
across a range of exit values: 1x non-participating preferred, 1x
participating preferred (uncapped), and 1x participating preferred with a
3x cap. Shows exactly how much each structure pays the investor (and
common/founders) at each exit value, and identifies the crossover exit
values where the economically optimal choice for the investor changes.

Run:
    python term_sheet_model.py
"""

import os
import pandas as pd
import matplotlib.pyplot as plt

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, "data")
OUTPUT_DIR = os.path.join(BASE_DIR, "output")


def load_assumptions() -> dict:
    path = os.path.join(DATA_DIR, "term_sheet_assumptions.csv")
    df = pd.read_csv(path, index_col="Field")
    a = {k: v for k, v in df["Value"].items()}
    for k in a:
        if k != "StartupName":
            a[k] = float(a[k])
    return a


def non_participating_payout(exit_value: float, investment: float, ownership_pct: float,
                              pref_multiple: float) -> float:
    preference = investment * pref_multiple
    as_converted = exit_value * ownership_pct
    return min(exit_value, max(preference, as_converted))


def participating_uncapped_payout(exit_value: float, investment: float, ownership_pct: float,
                                    pref_multiple: float) -> float:
    preference = investment * pref_multiple
    if exit_value <= preference:
        return exit_value
    remainder = exit_value - preference
    return preference + ownership_pct * remainder


def participating_capped_payout(exit_value: float, investment: float, ownership_pct: float,
                                  pref_multiple: float, cap_multiple: float) -> float:
    capped_amount = investment * cap_multiple
    uncapped = participating_uncapped_payout(exit_value, investment, ownership_pct, pref_multiple)
    as_converted = exit_value * ownership_pct
    return max(as_converted, min(uncapped, capped_amount))


def build_comparison(a: dict, exit_values: list) -> pd.DataFrame:
    rows = []
    for ev in exit_values:
        non_part = non_participating_payout(ev, a["SeriesBInvestment_mm"], a["SeriesBOwnershipPct"],
                                              a["LiquidationPreferenceMultiple"])
        part_uncapped = participating_uncapped_payout(ev, a["SeriesBInvestment_mm"], a["SeriesBOwnershipPct"],
                                                        a["LiquidationPreferenceMultiple"])
        part_capped = participating_capped_payout(ev, a["SeriesBInvestment_mm"], a["SeriesBOwnershipPct"],
                                                     a["LiquidationPreferenceMultiple"], a["ParticipatingCapMultiple"])
        rows.append({
            "ExitValue_mm": ev,
            "NonParticipating_SeriesB_mm": non_part, "NonParticipating_Common_mm": ev - non_part,
            "ParticipatingUncapped_SeriesB_mm": part_uncapped, "ParticipatingUncapped_Common_mm": ev - part_uncapped,
            "ParticipatingCapped_SeriesB_mm": part_capped, "ParticipatingCapped_Common_mm": ev - part_capped,
            "NonParticipating_ROI": non_part / a["SeriesBInvestment_mm"],
            "ParticipatingUncapped_ROI": part_uncapped / a["SeriesBInvestment_mm"],
            "ParticipatingCapped_ROI": part_capped / a["SeriesBInvestment_mm"],
        })
    return pd.DataFrame(rows)


def plot_payout_comparison(df: pd.DataFrame, startup_name: str):
    fig, ax = plt.subplots(figsize=(9, 6))
    ax.plot(df["ExitValue_mm"], df["NonParticipating_SeriesB_mm"], marker="o", label="1x Non-Participating",
            color="#2E5090")
    ax.plot(df["ExitValue_mm"], df["ParticipatingUncapped_SeriesB_mm"], marker="o", label="1x Participating (Uncapped)",
            color="#C0392B")
    ax.plot(df["ExitValue_mm"], df["ParticipatingCapped_SeriesB_mm"], marker="o", label="1x Participating (3x Cap)",
            color="#1E8449")
    ax.plot(df["ExitValue_mm"], df["ExitValue_mm"] * 0.20, linestyle="--", color="grey",
            label="Straight 20% As-Converted (no preference)")
    ax.set_xlabel("Exit Value ($mm)")
    ax.set_ylabel("Series B Payout ($mm)")
    ax.set_title(f"Series B Payout by Liquidation Preference Structure - {startup_name}")
    ax.legend(fontsize=8)
    fig.tight_layout()
    fig.savefig(os.path.join(OUTPUT_DIR, "payout_comparison.png"), dpi=150)
    plt.close(fig)


def plot_common_impact(df: pd.DataFrame):
    fig, ax = plt.subplots(figsize=(9, 6))
    ax.plot(df["ExitValue_mm"], df["NonParticipating_Common_mm"], marker="o", label="1x Non-Participating",
            color="#2E5090")
    ax.plot(df["ExitValue_mm"], df["ParticipatingUncapped_Common_mm"], marker="o", label="1x Participating (Uncapped)",
            color="#C0392B")
    ax.plot(df["ExitValue_mm"], df["ParticipatingCapped_Common_mm"], marker="o", label="1x Participating (3x Cap)",
            color="#1E8449")
    ax.set_xlabel("Exit Value ($mm)")
    ax.set_ylabel("Common / Founder Payout ($mm)")
    ax.set_title("What's Left for Common/Founders, by Structure")
    ax.legend(fontsize=8)
    fig.tight_layout()
    fig.savefig(os.path.join(OUTPUT_DIR, "common_impact.png"), dpi=150)
    plt.close(fig)


def main():
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    a = load_assumptions()

    exit_values = [10, 20, 30, 45, 60, 75, 100, 150, 200, 250, 350]
    df = build_comparison(a, exit_values)
    df.round(2).to_csv(os.path.join(OUTPUT_DIR, "liquidation_preference_comparison.csv"), index=False)

    plot_payout_comparison(df, a["StartupName"])
    plot_common_impact(df)

    conversion_crossover = a["SeriesBInvestment_mm"] * a["LiquidationPreferenceMultiple"] / a["SeriesBOwnershipPct"]
    cap_crossover_approx = df.loc[
        (df["ParticipatingUncapped_SeriesB_mm"] >= a["SeriesBInvestment_mm"] * a["ParticipatingCapMultiple"]),
        "ExitValue_mm"].min()

    with open(os.path.join(OUTPUT_DIR, "term_sheet_summary.txt"), "w") as f:
        f.write(f"Startup: {a['StartupName']}\n\n")
        f.write(f"Series B Investment: ${a['SeriesBInvestment_mm']:,.1f}mm  |  "
                f"As-converted ownership: {a['SeriesBOwnershipPct']:.0%}  |  "
                f"Preference: {a['LiquidationPreferenceMultiple']:.1f}x\n\n")
        f.write(f"Non-participating conversion crossover: Series B converts to common (rather than taking the "
                f"preference) once exit value exceeds ~${conversion_crossover:,.1f}mm "
                f"(where {a['SeriesBOwnershipPct']:.0%} of exit value = the {a['LiquidationPreferenceMultiple']:.1f}x preference)\n")
        f.write(f"Participating cap binds once exit value exceeds ~${cap_crossover_approx:,.0f}mm "
                f"(where uncapped participating payout would exceed the {a['ParticipatingCapMultiple']:.1f}x cap of "
                f"${a['SeriesBInvestment_mm']*a['ParticipatingCapMultiple']:,.1f}mm)\n\n")
        f.write(df.round(2).to_string(index=False))

    print(f"=== Term Sheet Analyzer: {a['StartupName']} ===")
    print(df[["ExitValue_mm", "NonParticipating_SeriesB_mm", "ParticipatingUncapped_SeriesB_mm",
              "ParticipatingCapped_SeriesB_mm"]].round(2).to_string(index=False))
    print(f"\nNon-participating conversion crossover: ~${conversion_crossover:,.1f}mm exit value")
    print(f"Participating cap binds above: ~${cap_crossover_approx:,.0f}mm exit value")
    print(f"\nOutputs written to: {OUTPUT_DIR}")


if __name__ == "__main__":
    main()
