"""
Bank Valuation - Price/Tangible Book Value & ROE-Driven Model
Meridian Community Bancorp

Banks aren't valued via EV/EBITDA (deposits are funding, not debt in the
traditional sense) - the standard framework is Justified P/TBV as a
function of ROE relative to Cost of Equity, a Gordon Growth-style
relationship. This project computes the simple blended-ROE justified
multiple, then a more precise sum-of-the-parts version that separates
"core" equity (supporting regulatory capital requirements, earning the
bank's true operating ROE) from "excess" capital (valued near book,
since it isn't compounding at the bank's core return) - a real technique
that avoids understating value when a bank holds capital above what its
risk-weighted assets require.

Run:
    python bank_valuation_model.py
"""

import os
import pandas as pd
import matplotlib.pyplot as plt

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, "data")
OUTPUT_DIR = os.path.join(BASE_DIR, "output")


def load_assumptions() -> dict:
    path = os.path.join(DATA_DIR, "bank_assumptions.csv")
    df = pd.read_csv(path, index_col="Field")
    a = {k: v for k, v in df["Value"].items()}
    for k in a:
        if k != "BankName":
            a[k] = float(a[k])
    return a


def justified_ptbv(roe: float, coe: float, g: float) -> float:
    return (roe - g) / (coe - g)


def compute_valuation(a: dict) -> dict:
    coe = a["RiskFreeRate"] + a["Beta"] * a["EquityRiskPremium"]
    blended_roe = a["NetIncomeLTM_mm"] / a["TangibleBookValue_mm"]
    blended_justified_ptbv = justified_ptbv(blended_roe, coe, a["LongTermGrowthRate"])
    blended_implied_equity = blended_justified_ptbv * a["TangibleBookValue_mm"]

    required_capital = a["RequiredCET1Ratio"] * a["RiskWeightedAssets_mm"]
    excess_capital = a["TangibleBookValue_mm"] - required_capital
    core_roe = a["NetIncomeLTM_mm"] / required_capital
    core_justified_ptbv = justified_ptbv(core_roe, coe, a["LongTermGrowthRate"])
    core_equity_value = core_justified_ptbv * required_capital
    excess_capital_value = excess_capital * 1.0  # valued at book - not compounding at core ROE

    sotp_implied_equity = core_equity_value + excess_capital_value
    sotp_implied_ptbv = sotp_implied_equity / a["TangibleBookValue_mm"]

    current_market_equity = a["CurrentTradingPTBV"] * a["TangibleBookValue_mm"]

    return {
        "coe": coe, "blended_roe": blended_roe, "blended_justified_ptbv": blended_justified_ptbv,
        "blended_implied_equity": blended_implied_equity, "required_capital": required_capital,
        "excess_capital": excess_capital, "core_roe": core_roe, "core_justified_ptbv": core_justified_ptbv,
        "core_equity_value": core_equity_value, "excess_capital_value": excess_capital_value,
        "sotp_implied_equity": sotp_implied_equity, "sotp_implied_ptbv": sotp_implied_ptbv,
        "current_market_equity": current_market_equity,
    }


def sensitivity_table(a: dict, coe: float) -> pd.DataFrame:
    roes = [0.10, 0.11, 0.12, 0.13, 0.14, 0.15, 0.16]
    coes = [coe - 0.02, coe - 0.01, coe, coe + 0.01, coe + 0.02]
    table = pd.DataFrame(index=[f"{r:.0%} ROE" for r in roes], columns=[f"{c:.2%} CoE" for c in coes])
    for r in roes:
        for c in coes:
            table.loc[f"{r:.0%} ROE", f"{c:.2%} CoE"] = round(justified_ptbv(r, c, a["LongTermGrowthRate"]), 2)
    return table


def plot_valuation_comparison(res: dict, a: dict):
    fig, ax = plt.subplots(figsize=(8, 6))
    labels = ["Current\nMarket Value", "Blended-ROE\nJustified", "Sum-of-Parts\n(Core + Excess)"]
    values = [res["current_market_equity"], res["blended_implied_equity"], res["sotp_implied_equity"]]
    ptbvs = [a["CurrentTradingPTBV"], res["blended_justified_ptbv"], res["sotp_implied_ptbv"]]
    bars = ax.bar(labels, values, color=["#C0392B", "#7FA6D9", "#1E8449"])
    for bar, ptbv in zip(bars, ptbvs):
        h = bar.get_height()
        ax.annotate(f"${h:,.0f}mm\n({ptbv:.2f}x TBV)", (bar.get_x() + bar.get_width() / 2, h),
                    ha="center", va="bottom", fontsize=9)
    ax.set_ylabel("Implied Equity Value ($mm)")
    ax.set_title(f"Bank Valuation Comparison - {a['BankName']}")
    fig.tight_layout()
    fig.savefig(os.path.join(OUTPUT_DIR, "valuation_comparison.png"), dpi=150)
    plt.close(fig)


def plot_sensitivity_heatmap(table: pd.DataFrame):
    fig, ax = plt.subplots(figsize=(8, 5))
    data = table.astype(float).values
    im = ax.imshow(data, cmap="RdYlGn")
    ax.set_xticks(range(len(table.columns)))
    ax.set_xticklabels(table.columns, rotation=30, ha="right")
    ax.set_yticks(range(len(table.index)))
    ax.set_yticklabels(table.index)
    ax.set_title("Justified P/TBV - ROE x Cost of Equity")
    for i in range(data.shape[0]):
        for j in range(data.shape[1]):
            ax.text(j, i, f"{data[i, j]:.2f}x", ha="center", va="center", fontsize=8)
    fig.colorbar(im, ax=ax, label="Justified P/TBV")
    fig.tight_layout()
    fig.savefig(os.path.join(OUTPUT_DIR, "sensitivity_heatmap.png"), dpi=150)
    plt.close(fig)


def main():
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    a = load_assumptions()
    res = compute_valuation(a)
    sens = sensitivity_table(a, res["coe"])
    sens.to_csv(os.path.join(OUTPUT_DIR, "ptbv_sensitivity.csv"))

    with open(os.path.join(OUTPUT_DIR, "bank_valuation_summary.txt"), "w") as f:
        f.write(f"Bank: {a['BankName']}\n\n")
        f.write(f"Cost of Equity (CAPM): {res['coe']:.2%}\n")
        f.write(f"Tangible Book Value: ${a['TangibleBookValue_mm']:,.0f}mm\n")
        f.write(f"Net Income (LTM): ${a['NetIncomeLTM_mm']:,.0f}mm\n\n")
        f.write("=== Blended (Simple) Approach ===\n")
        f.write(f"Blended ROE: {res['blended_roe']:.2%}\n")
        f.write(f"Justified P/TBV: {res['blended_justified_ptbv']:.2f}x\n")
        f.write(f"Implied Equity Value: ${res['blended_implied_equity']:,.1f}mm\n\n")
        f.write("=== Sum-of-Parts Approach (Core + Excess Capital) ===\n")
        f.write(f"Required Capital ({a['RequiredCET1Ratio']:.1%} CET1 on "
                f"${a['RiskWeightedAssets_mm']:,.0f}mm RWA): ${res['required_capital']:,.1f}mm\n")
        f.write(f"Excess Capital: ${res['excess_capital']:,.1f}mm\n")
        f.write(f"Core ROE (Net Income / Required Capital): {res['core_roe']:.2%}\n")
        f.write(f"Core Justified P/TBV: {res['core_justified_ptbv']:.2f}x\n")
        f.write(f"Core Equity Value: ${res['core_equity_value']:,.1f}mm\n")
        f.write(f"Excess Capital Value (at book): ${res['excess_capital_value']:,.1f}mm\n")
        f.write(f"Sum-of-Parts Implied Equity Value: ${res['sotp_implied_equity']:,.1f}mm "
                f"({res['sotp_implied_ptbv']:.2f}x blended TBV)\n\n")
        f.write(f"=== Current Market ===\n")
        f.write(f"Current Trading P/TBV: {a['CurrentTradingPTBV']:.2f}x\n")
        f.write(f"Current Market Equity Value: ${res['current_market_equity']:,.1f}mm\n\n")
        f.write(f"Sum-of-Parts approach implies "
                f"{res['sotp_implied_equity']/res['current_market_equity']-1:.1%} upside vs. current market value, "
                f"vs. only {res['blended_implied_equity']/res['current_market_equity']-1:.1%} upside from the "
                f"simpler blended-ROE approach.\n")

    plot_valuation_comparison(res, a)
    plot_sensitivity_heatmap(sens)

    print(f"=== Bank Valuation: {a['BankName']} ===")
    print(f"Cost of Equity: {res['coe']:.2%}")
    print(f"Blended ROE: {res['blended_roe']:.2%}  ->  Justified P/TBV: {res['blended_justified_ptbv']:.2f}x  ->  "
          f"Equity Value: ${res['blended_implied_equity']:,.1f}mm")
    print(f"Core ROE (excl. excess capital): {res['core_roe']:.2%}  ->  Core P/TBV: "
          f"{res['core_justified_ptbv']:.2f}x")
    print(f"Sum-of-Parts Implied Equity Value: ${res['sotp_implied_equity']:,.1f}mm "
          f"({res['sotp_implied_ptbv']:.2f}x TBV)")
    print(f"Current Market Value: ${res['current_market_equity']:,.1f}mm ({a['CurrentTradingPTBV']:.2f}x TBV)")
    print(f"\nOutputs written to: {OUTPUT_DIR}")


if __name__ == "__main__":
    main()
