"""
Full Investment Memo - Vertex Retrieval (Quantitative Engine)

The VC capstone project: computes the Series A deal terms, ownership, and
Bear/Base/Bull exit scenario returns for a hypothetical vector database /
RAG infrastructure startup - correctly adjusting for future dilution from
anticipated follow-on rounds, the same way VC/vc-method-valuation does.
The full qualitative memo (market, team, risks, recommendation) lives in
theory/investment_memo_narrative.md - this script produces the
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
    path = os.path.join(DATA_DIR, "deal_assumptions.csv")
    df = pd.read_csv(path, index_col="Field")
    a = {k: v for k, v in df["Value"].items()}
    for k in a:
        if k != "StartupName":
            a[k] = float(a[k])
    return a


def load_exit_scenarios() -> pd.DataFrame:
    return pd.read_csv(os.path.join(DATA_DIR, "exit_scenarios.csv"))


def compute_irr(cf0: float, cf_final: float, years: float) -> float:
    if cf_final <= 0:
        return -1.0
    return (cf_final / -cf0) ** (1 / years) - 1


def build_deal_terms(a: dict) -> dict:
    post_money = a["PreMoneyValuation_mm"] + a["ProposedInvestment_mm"]
    ownership_pct_today = a["ProposedInvestment_mm"] / post_money
    effective_ownership_at_exit = ownership_pct_today * a["FutureRoundRetentionRatio"]
    implied_arr_multiple = post_money / a["CurrentARR_mm"]

    return {
        "post_money": post_money, "ownership_pct_today": ownership_pct_today,
        "effective_ownership_at_exit": effective_ownership_at_exit,
        "implied_arr_multiple": implied_arr_multiple,
    }


def run_scenarios(a: dict, deal: dict, scenarios: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for _, s in scenarios.iterrows():
        payout = deal["effective_ownership_at_exit"] * s["ExitValue_mm"]
        moic = payout / a["ProposedInvestment_mm"]
        irr = compute_irr(-a["ProposedInvestment_mm"], payout, a["YearsToExit"])
        rows.append({"Scenario": s["Scenario"], "ExitValue_mm": s["ExitValue_mm"],
                     "InvestorPayout_mm": payout, "MOIC": moic, "IRR": irr * 100})
    return pd.DataFrame(rows)


def plot_scenario_returns(df: pd.DataFrame, startup_name: str):
    fig, ax1 = plt.subplots(figsize=(8, 5))
    ax2 = ax1.twinx()
    colors = ["#C0392B", "#2E5090", "#1E8449"]
    ax1.bar(df["Scenario"], df["MOIC"], color=colors)
    ax2.plot(df["Scenario"], df["IRR"], color="black", marker="o", linewidth=2)
    ax1.axhline(1.0, color="grey", linestyle="--", linewidth=1)
    ax1.set_ylabel("MOIC (x)")
    ax2.set_ylabel("IRR (%)")
    ax1.set_title(f"Bear / Base / Bull Exit Returns - {startup_name}")
    fig.tight_layout()
    fig.savefig(os.path.join(OUTPUT_DIR, "scenario_returns.png"), dpi=150)
    plt.close(fig)


def plot_ownership_bridge(deal: dict, startup_name: str):
    fig, ax = plt.subplots(figsize=(6, 5))
    labels = ["Ownership Today\n(at close)", "Effective Ownership\nat Exit (post-dilution)"]
    values = [deal["ownership_pct_today"] * 100, deal["effective_ownership_at_exit"] * 100]
    bars = ax.bar(labels, values, color=["#2E5090", "#7FA6D9"])
    for bar in bars:
        h = bar.get_height()
        ax.annotate(f"{h:.1f}%", (bar.get_x() + bar.get_width() / 2, h), ha="center", va="bottom")
    ax.set_ylabel("Ownership (%)")
    ax.set_title(f"Ownership Dilution to Exit - {startup_name}")
    fig.tight_layout()
    fig.savefig(os.path.join(OUTPUT_DIR, "ownership_bridge.png"), dpi=150)
    plt.close(fig)


def main():
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    a = load_assumptions()
    scenarios = load_exit_scenarios()

    deal = build_deal_terms(a)
    results = run_scenarios(a, deal, scenarios)
    results.round(2).to_csv(os.path.join(OUTPUT_DIR, "scenario_returns.csv"), index=False)

    with open(os.path.join(OUTPUT_DIR, "quantitative_summary.txt"), "w") as f:
        f.write(f"Startup: {a['StartupName']}\n\n")
        f.write(f"Current ARR: ${a['CurrentARR_mm']:,.1f}mm ({a['CurrentCustomers']:.0f} customers)  |  "
                f"NRR: {a['NRR']:.0%}  |  Burn Multiple: {a['BurnMultiple']:.1f}x\n\n")
        f.write(f"Proposed Series A: ${a['ProposedInvestment_mm']:,.1f}mm at "
                f"${a['PreMoneyValuation_mm']:,.1f}mm pre-money "
                f"(${deal['post_money']:,.1f}mm post-money, {deal['implied_arr_multiple']:.1f}x current ARR)\n")
        f.write(f"Ownership at close: {deal['ownership_pct_today']:.1%}\n")
        f.write(f"Effective ownership at exit (after {1-a['FutureRoundRetentionRatio']:.0%} assumed future "
                f"dilution): {deal['effective_ownership_at_exit']:.1%}\n\n")
        f.write("=== Exit Scenarios ===\n")
        f.write(results.round(2).to_string(index=False))

    plot_scenario_returns(results, a["StartupName"])
    plot_ownership_bridge(deal, a["StartupName"])

    print(f"=== Investment Memo Quantitative Engine: {a['StartupName']} ===")
    print(f"Series A: ${a['ProposedInvestment_mm']:,.1f}mm at ${deal['post_money']:,.1f}mm post-money "
          f"({deal['implied_arr_multiple']:.1f}x current ARR)")
    print(f"Ownership today: {deal['ownership_pct_today']:.1%}  ->  "
          f"Effective at exit: {deal['effective_ownership_at_exit']:.1%}\n")
    print(results.round(2).to_string(index=False))
    print(f"\nOutputs written to: {OUTPUT_DIR}")


if __name__ == "__main__":
    main()
