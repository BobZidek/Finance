"""
REIT Net Asset Value (NAV) Valuation - Coastal Retail Properties Trust

Values a shopping center REIT via the standard real estate methodology:
applies market cap rates by property type to each segment's Net
Operating Income to derive gross asset value, nets out debt and
preferred equity to arrive at NAV per share, and cross-checks against a
P/FFO (Funds From Operations) multiple approach - the REIT-specific
"cash earnings" metric that adds back real estate depreciation, since
real estate typically appreciates rather than depreciates economically.

Run:
    python reit_nav_model.py
"""

import os
import pandas as pd
import matplotlib.pyplot as plt

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, "data")
OUTPUT_DIR = os.path.join(BASE_DIR, "output")


def load_portfolio() -> pd.DataFrame:
    return pd.read_csv(os.path.join(DATA_DIR, "property_portfolio.csv"))


def load_balance_sheet() -> dict:
    path = os.path.join(DATA_DIR, "balance_sheet_assumptions.csv")
    df = pd.read_csv(path, index_col="Field")
    a = {k: v for k, v in df["Value"].items()}
    for k in a:
        if k != "REITName":
            a[k] = float(a[k])
    return a


def compute_nav(portfolio: pd.DataFrame, a: dict, cap_rate_shift: float = 0.0) -> dict:
    portfolio = portfolio.copy()
    portfolio["ShiftedCapRate"] = portfolio["MarketCapRate"] + cap_rate_shift
    portfolio["PropertyValue_mm"] = portfolio["NOI_mm"] / portfolio["ShiftedCapRate"]

    total_re_value = portfolio["PropertyValue_mm"].sum()
    total_gross_assets = total_re_value + a["Cash_mm"] + a["OtherInvestments_mm"]
    nav_to_common = total_gross_assets - a["TotalDebt_mm"] - a["PreferredEquity_mm"]
    nav_per_share = nav_to_common / a["DilutedShares_mm"]

    return {"portfolio": portfolio, "total_re_value": total_re_value,
            "total_gross_assets": total_gross_assets, "nav_to_common": nav_to_common,
            "nav_per_share": nav_per_share}


def compute_ffo_valuation(a: dict) -> dict:
    ffo = a["NetIncome_mm"] + a["RealEstateDA_mm"]
    ffo_per_share = ffo / a["DilutedShares_mm"]
    current_pffo = a["CurrentStockPrice"] / ffo_per_share
    implied_value_pffo = a["PeerPFFOMultiple"] * ffo_per_share
    return {"ffo": ffo, "ffo_per_share": ffo_per_share, "current_pffo": current_pffo,
            "implied_value_pffo": implied_value_pffo}


def cap_rate_sensitivity(portfolio: pd.DataFrame, a: dict) -> pd.DataFrame:
    shifts_bps = [-100, -75, -50, -25, 0, 25, 50, 75, 100]
    rows = []
    for shift_bps in shifts_bps:
        res = compute_nav(portfolio, a, cap_rate_shift=shift_bps / 10000)
        rows.append({"CapRateShiftBps": shift_bps, "NAVPerShare": res["nav_per_share"]})
    return pd.DataFrame(rows)


def plot_nav_bridge(base: dict, a: dict):
    fig, ax = plt.subplots(figsize=(10, 6))
    portfolio = base["portfolio"]
    labels = list(portfolio["PropertyType"]) + ["Cash + Other\nInvestments", "Total Debt", "Preferred\nEquity",
                                                  "NAV to\nCommon"]
    values = list(portfolio["PropertyValue_mm"]) + [a["Cash_mm"] + a["OtherInvestments_mm"],
                                                       -a["TotalDebt_mm"], -a["PreferredEquity_mm"], None]

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
    ax.set_ylabel("$mm")
    ax.set_title(f"NAV Bridge - {a['REITName']}")
    plt.xticks(rotation=20, ha="right")
    fig.tight_layout()
    fig.savefig(os.path.join(OUTPUT_DIR, "nav_bridge.png"), dpi=150)
    plt.close(fig)


def plot_cap_rate_sensitivity(sens: pd.DataFrame, current_price: float):
    fig, ax = plt.subplots(figsize=(9, 6))
    ax.plot(sens["CapRateShiftBps"], sens["NAVPerShare"], marker="o", color="#2E5090")
    ax.axhline(current_price, color="#C0392B", linestyle="--", label=f"Current Stock Price (${current_price:.2f})")
    ax.axvline(0, color="grey", linestyle=":", linewidth=1)
    ax.set_xlabel("Cap Rate Shift (bps, applied to all property types)")
    ax.set_ylabel("NAV per Share ($)")
    ax.set_title("NAV per Share Sensitivity to Cap Rate Movement")
    ax.legend()
    fig.tight_layout()
    fig.savefig(os.path.join(OUTPUT_DIR, "cap_rate_sensitivity.png"), dpi=150)
    plt.close(fig)


def main():
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    portfolio = load_portfolio()
    a = load_balance_sheet()

    base = compute_nav(portfolio, a)
    ffo = compute_ffo_valuation(a)
    sens = cap_rate_sensitivity(portfolio, a)
    sens.round(2).to_csv(os.path.join(OUTPUT_DIR, "cap_rate_sensitivity.csv"), index=False)

    base["portfolio"].round(2).to_csv(os.path.join(OUTPUT_DIR, "property_valuations.csv"), index=False)

    premium_discount_nav = a["CurrentStockPrice"] / base["nav_per_share"] - 1
    premium_discount_pffo = a["CurrentStockPrice"] / ffo["implied_value_pffo"] - 1

    with open(os.path.join(OUTPUT_DIR, "reit_nav_summary.txt"), "w") as f:
        f.write(f"REIT: {a['REITName']}\n\n")
        f.write("=== NAV Approach ===\n")
        f.write(base["portfolio"].round(2).to_string(index=False))
        f.write(f"\n\nTotal Real Estate Value: ${base['total_re_value']:,.1f}mm\n")
        f.write(f"Cash + Other Investments: ${a['Cash_mm'] + a['OtherInvestments_mm']:,.1f}mm\n")
        f.write(f"Total Gross Asset Value: ${base['total_gross_assets']:,.1f}mm\n")
        f.write(f"Less: Total Debt: -${a['TotalDebt_mm']:,.1f}mm\n")
        f.write(f"Less: Preferred Equity: -${a['PreferredEquity_mm']:,.1f}mm\n")
        f.write(f"NAV to Common: ${base['nav_to_common']:,.1f}mm\n")
        f.write(f"NAV per Share: ${base['nav_per_share']:.2f}\n\n")
        f.write("=== FFO / P-FFO Cross-Check ===\n")
        f.write(f"FFO (Net Income + Real Estate D&A): ${ffo['ffo']:,.1f}mm\n")
        f.write(f"FFO per Share: ${ffo['ffo_per_share']:.2f}\n")
        f.write(f"Current P/FFO: {ffo['current_pffo']:.2f}x\n")
        f.write(f"Peer P/FFO Multiple: {a['PeerPFFOMultiple']:.1f}x\n")
        f.write(f"Implied Value (P/FFO approach): ${ffo['implied_value_pffo']:.2f}/share\n\n")
        f.write(f"=== Current Trading ===\n")
        f.write(f"Current Stock Price: ${a['CurrentStockPrice']:.2f}\n")
        f.write(f"Premium/(Discount) to NAV: {premium_discount_nav:+.1%}\n")
        f.write(f"Premium/(Discount) to P/FFO-implied value: {premium_discount_pffo:+.1%}\n")

    plot_nav_bridge(base, a)
    plot_cap_rate_sensitivity(sens, a["CurrentStockPrice"])

    print(f"=== REIT NAV Valuation: {a['REITName']} ===")
    print(base["portfolio"].round(2).to_string(index=False))
    print(f"\nNAV per Share: ${base['nav_per_share']:.2f}")
    print(f"FFO per Share: ${ffo['ffo_per_share']:.2f}  |  Current P/FFO: {ffo['current_pffo']:.2f}x  |  "
          f"P/FFO-Implied Value: ${ffo['implied_value_pffo']:.2f}")
    print(f"Current Stock Price: ${a['CurrentStockPrice']:.2f}")
    print(f"Discount to NAV: {premium_discount_nav:+.1%}  |  Discount to P/FFO value: {premium_discount_pffo:+.1%}")
    print(f"\nOutputs written to: {OUTPUT_DIR}")


if __name__ == "__main__":
    main()
