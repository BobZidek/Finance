"""
Growth Equity Structured Minority Investment - Vertex Nutrition Brands

Models a non-control growth equity investment structured as preferred
equity with an 8% cumulative PIK dividend (accrues without requiring
cash payment, preserving company cash), a 1x non-participating
liquidation preference, and a redemption right - if no qualified
liquidity event occurs within a set window, the investor can force
redemption at the GREATER of its accreted cost or a minimum IRR floor.
At exit, the investor takes whichever payout is largest: convert to
common (as-converted value), take the accreted liquidation preference,
or exercise redemption - exactly the downside-protection logic real
growth equity preferred structures are built around.

Run:
    python growth_equity_model.py
"""

import os
import pandas as pd
import matplotlib.pyplot as plt

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, "data")
OUTPUT_DIR = os.path.join(BASE_DIR, "output")


def load_assumptions() -> dict:
    path = os.path.join(DATA_DIR, "investment_assumptions.csv")
    df = pd.read_csv(path, index_col="Field")
    a = {k: v for k, v in df["Value"].items()}
    for k in a:
        if k != "CompanyName":
            a[k] = float(a[k])
    a["RedemptionEligibilityYears"] = int(a["RedemptionEligibilityYears"])
    return a


def load_scenarios() -> pd.DataFrame:
    return pd.read_csv(os.path.join(DATA_DIR, "exit_scenarios.csv"))


def evaluate_scenario(a: dict, exit_year: int, exit_equity_value: float, is_redemption: bool) -> dict:
    as_converted_value = a["AsConvertedOwnershipPct"] * exit_equity_value

    accreted_liq_pref = (a["InvestmentAmount_mm"] * a["LiquidationPreferenceMultiple"]
                          * (1 + a["PIKDividendRate"]) ** exit_year)

    redemption_value = None
    if is_redemption:
        irr_floor_value = a["InvestmentAmount_mm"] * (1 + a["RedemptionMinimumIRR"]) ** exit_year
        redemption_value = max(accreted_liq_pref, irr_floor_value)

    candidates = {"As-Converted (common)": as_converted_value,
                  "Accreted Liquidation Preference": accreted_liq_pref}
    if is_redemption:
        candidates["Redemption (greater of accreted cost or IRR floor)"] = redemption_value

    chosen_path = max(candidates, key=candidates.get)
    payout = candidates[chosen_path]

    moic = payout / a["InvestmentAmount_mm"]
    irr = moic ** (1 / exit_year) - 1

    return {"as_converted_value": as_converted_value, "accreted_liq_pref": accreted_liq_pref,
            "redemption_value": redemption_value, "chosen_path": chosen_path, "payout": payout,
            "moic": moic, "irr": irr}


def build_comparison(a: dict, scenarios: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for _, s in scenarios.iterrows():
        res = evaluate_scenario(a, int(s["ExitYear"]), s["CompanyExitEquityValue_mm"], bool(s["IsRedemption"]))
        rows.append({"Scenario": s["Scenario"], "ExitYear": s["ExitYear"],
                     "CompanyExitEquityValue_mm": s["CompanyExitEquityValue_mm"],
                     "AsConvertedValue_mm": res["as_converted_value"],
                     "AccretedLiqPref_mm": res["accreted_liq_pref"],
                     "RedemptionValue_mm": res["redemption_value"],
                     "ChosenPath": res["chosen_path"], "Payout_mm": res["payout"],
                     "MOIC": res["moic"], "IRR_pct": res["irr"] * 100})
    return pd.DataFrame(rows)


def plot_payout_by_path(comparison: pd.DataFrame, a: dict):
    fig, ax = plt.subplots(figsize=(10, 6))
    x = range(len(comparison))
    width = 0.25
    ax.bar([i - width for i in x], comparison["AsConvertedValue_mm"], width, label="As-Converted (common)",
           color="#7FA6D9")
    ax.bar(x, comparison["AccretedLiqPref_mm"], width, label="Accreted Liquidation Preference", color="#F1C40F")
    redemption_vals = comparison["RedemptionValue_mm"].fillna(0)
    ax.bar([i + width for i in x], redemption_vals, width, label="Redemption Value", color="#C0392B")

    for i, row in comparison.iterrows():
        ax.annotate(f"Chosen:\n{row['ChosenPath'].split('(')[0].strip()}", (i, row["Payout_mm"] + 5),
                    ha="center", fontsize=7)

    ax.set_xticks(list(x))
    ax.set_xticklabels(comparison["Scenario"], fontsize=8)
    ax.set_ylabel("$mm")
    ax.set_title(f"Payout Path Comparison by Scenario - {a['CompanyName']}")
    ax.legend(fontsize=8)
    fig.tight_layout()
    fig.savefig(os.path.join(OUTPUT_DIR, "payout_comparison.png"), dpi=150)
    plt.close(fig)


def plot_returns(comparison: pd.DataFrame):
    fig, ax1 = plt.subplots(figsize=(9, 6))
    ax2 = ax1.twinx()
    ax1.bar(comparison["Scenario"], comparison["MOIC"], color="#2E5090", alpha=0.8)
    ax2.plot(comparison["Scenario"], comparison["IRR_pct"], color="black", marker="o", linewidth=2)
    ax1.set_ylabel("MOIC (x)")
    ax2.set_ylabel("IRR (%)")
    ax1.set_title("Investor Returns by Scenario")
    plt.setp(ax1.get_xticklabels(), fontsize=8)
    fig.tight_layout()
    fig.savefig(os.path.join(OUTPUT_DIR, "returns_by_scenario.png"), dpi=150)
    plt.close(fig)


def main():
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    a = load_assumptions()
    scenarios = load_scenarios()

    comparison = build_comparison(a, scenarios)
    comparison.round(2).to_csv(os.path.join(OUTPUT_DIR, "scenario_comparison.csv"), index=False)

    with open(os.path.join(OUTPUT_DIR, "growth_equity_summary.txt"), "w") as f:
        f.write(f"Company: {a['CompanyName']}\n\n")
        f.write(f"Investment: ${a['InvestmentAmount_mm']:,.0f}mm for {a['AsConvertedOwnershipPct']:.0%} "
                f"as-converted ownership\n")
        f.write(f"Structure: {a['LiquidationPreferenceMultiple']:.1f}x non-participating liquidation preference, "
                f"{a['PIKDividendRate']:.0%} cumulative PIK dividend, redemption right after "
                f"{a['RedemptionEligibilityYears']:.0f} years at the greater of accreted cost or "
                f"{a['RedemptionMinimumIRR']:.0%} minimum IRR\n\n")
        f.write("=== Scenario Comparison ===\n")
        f.write(comparison.round(2).to_string(index=False))
        f.write("\n\nAt each exit, the investor takes whichever payout path is largest: converting to common, "
                "taking the accreted liquidation preference, or (if eligible) exercising redemption rights - "
                "exactly the downside protection a structured minority investment is designed to provide.\n")

    plot_payout_by_path(comparison, a)
    plot_returns(comparison)

    print(f"=== Growth Equity Structured Minority Investment: {a['CompanyName']} ===")
    print(comparison[["Scenario", "ChosenPath", "Payout_mm", "MOIC", "IRR_pct"]].round(2).to_string(index=False))
    print(f"\nOutputs written to: {OUTPUT_DIR}")


if __name__ == "__main__":
    main()
