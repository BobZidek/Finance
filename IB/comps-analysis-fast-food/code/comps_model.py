"""
Comparable Company Analysis (Comps) - Fast Food / QSR Peer Group

Loads a peer group's market and financial data, computes enterprise value
and trading multiples for each peer, summarizes the peer set statistically,
and applies the resulting multiple ranges to a target company to derive
an implied valuation range (EV and equity value).

Run:
    python comps_model.py
"""

import os
import pandas as pd
import matplotlib.pyplot as plt

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, "data")
OUTPUT_DIR = os.path.join(BASE_DIR, "output")


def load_peer_data() -> pd.DataFrame:
    path = os.path.join(DATA_DIR, "fast_food_comps.csv")
    return pd.read_csv(path)


def load_target() -> dict:
    path = os.path.join(DATA_DIR, "target_company.csv")
    df = pd.read_csv(path, index_col="Field")
    target = {
        "name": df.loc["Name", "Value"],
        "revenue": float(df.loc["Revenue_LTM_mm", "Value"]),
        "ebitda": float(df.loc["EBITDA_LTM_mm", "Value"]),
        "ebit": float(df.loc["EBIT_LTM_mm", "Value"]),
        "net_income": float(df.loc["NetIncome_LTM_mm", "Value"]),
        "net_debt": float(df.loc["NetDebt_mm", "Value"]),
    }
    return target


def compute_comps(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()

    # Enterprise Value = Market Cap + Total Debt + Minority Interest + Preferred - Cash
    df["MarketCap_mm"] = df["Price"] * df["SharesOut_mm"]
    df["EV_mm"] = (
        df["MarketCap_mm"]
        + df["TotalDebt_mm"]
        + df["MinorityInterest_mm"]
        + df["PreferredEquity_mm"]
        - df["Cash_mm"]
    )

    # Trading multiples
    df["EV_Revenue"] = df["EV_mm"] / df["Revenue_LTM_mm"]
    df["EV_EBITDA"] = df["EV_mm"] / df["EBITDA_LTM_mm"]
    df["EV_EBIT"] = df["EV_mm"] / df["EBIT_LTM_mm"]
    df["PE"] = df["Price"] / df["DilutedEPS"]
    df["EBITDA_Margin"] = df["EBITDA_LTM_mm"] / df["Revenue_LTM_mm"]

    return df


def summarize_multiples(df: pd.DataFrame) -> pd.DataFrame:
    cols = ["EV_Revenue", "EV_EBITDA", "EV_EBIT", "PE"]
    summary = df[cols].agg(["mean", "median", "min", "max",
                             lambda x: x.quantile(0.25),
                             lambda x: x.quantile(0.75)])
    summary.index = ["Mean", "Median", "Min", "Max", "25th Pctile", "75th Pctile"]
    return summary.round(2)


def implied_valuation(target: dict, summary: pd.DataFrame) -> pd.DataFrame:
    """Apply 25th/median/75th percentile EV/Revenue and EV/EBITDA multiples
    to the target's financials to derive an implied EV and equity value range."""
    rows = []
    for label in ["25th Pctile", "Median", "75th Pctile"]:
        ev_rev_mult = summary.loc[label, "EV_Revenue"]
        ev_ebitda_mult = summary.loc[label, "EV_EBITDA"]

        ev_from_revenue = ev_rev_mult * target["revenue"]
        ev_from_ebitda = ev_ebitda_mult * target["ebitda"]

        rows.append({
            "Percentile": label,
            "EV_Revenue_Multiple": round(ev_rev_mult, 2),
            "Implied_EV_from_Revenue_mm": round(ev_from_revenue, 1),
            "Implied_Equity_from_Revenue_mm": round(ev_from_revenue - target["net_debt"], 1),
            "EV_EBITDA_Multiple": round(ev_ebitda_mult, 2),
            "Implied_EV_from_EBITDA_mm": round(ev_from_ebitda, 1),
            "Implied_Equity_from_EBITDA_mm": round(ev_from_ebitda - target["net_debt"], 1),
        })
    return pd.DataFrame(rows)


def plot_ev_ebitda(df: pd.DataFrame):
    fig, ax = plt.subplots(figsize=(8, 5))
    ordered = df.sort_values("EV_EBITDA")
    ax.barh(ordered["Ticker"], ordered["EV_EBITDA"], color="#2E5090")
    ax.set_xlabel("EV / EBITDA (x)")
    ax.set_title("Fast Food / QSR Peer Group - EV/EBITDA Multiples")
    ax.axvline(df["EV_EBITDA"].median(), color="grey", linestyle="--", linewidth=1,
                label=f"Median = {df['EV_EBITDA'].median():.1f}x")
    ax.legend()
    fig.tight_layout()
    fig.savefig(os.path.join(OUTPUT_DIR, "ev_ebitda_multiples.png"), dpi=150)
    plt.close(fig)


def plot_valuation_range(implied: pd.DataFrame, target_name: str):
    fig, ax = plt.subplots(figsize=(8, 3))
    methods = ["Implied EV from Revenue", "Implied EV from EBITDA"]
    low = [
        implied.loc[implied["Percentile"] == "25th Pctile", "Implied_EV_from_Revenue_mm"].values[0],
        implied.loc[implied["Percentile"] == "25th Pctile", "Implied_EV_from_EBITDA_mm"].values[0],
    ]
    high = [
        implied.loc[implied["Percentile"] == "75th Pctile", "Implied_EV_from_Revenue_mm"].values[0],
        implied.loc[implied["Percentile"] == "75th Pctile", "Implied_EV_from_EBITDA_mm"].values[0],
    ]
    mid = [
        implied.loc[implied["Percentile"] == "Median", "Implied_EV_from_Revenue_mm"].values[0],
        implied.loc[implied["Percentile"] == "Median", "Implied_EV_from_EBITDA_mm"].values[0],
    ]

    y_pos = range(len(methods))
    for i, (l, h, m) in enumerate(zip(low, high, mid)):
        ax.barh(i, h - l, left=l, height=0.4, color="#7FA6D9")
        ax.plot(m, i, "o", color="#2E5090")

    ax.set_yticks(list(y_pos))
    ax.set_yticklabels(methods)
    ax.set_xlabel("Implied Enterprise Value ($mm)")
    ax.set_title(f"Implied Valuation Range - {target_name}")
    fig.tight_layout()
    fig.savefig(os.path.join(OUTPUT_DIR, "implied_valuation_range.png"), dpi=150)
    plt.close(fig)


def main():
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    peers_raw = load_peer_data()
    target = load_target()

    comps = compute_comps(peers_raw)
    summary = summarize_multiples(comps)
    implied = implied_valuation(target, summary)

    display_cols = ["Ticker", "Company", "MarketCap_mm", "EV_mm",
                     "EV_Revenue", "EV_EBITDA", "EV_EBIT", "PE", "EBITDA_Margin"]
    comps_display = comps[display_cols].round(2)

    comps_display.to_csv(os.path.join(OUTPUT_DIR, "comps_table.csv"), index=False)
    summary.to_csv(os.path.join(OUTPUT_DIR, "multiple_summary_stats.csv"))
    implied.to_csv(os.path.join(OUTPUT_DIR, "implied_valuation.csv"), index=False)

    plot_ev_ebitda(comps)
    plot_valuation_range(implied, target["name"])

    print("=== Peer Comp Table ===")
    print(comps_display.to_string(index=False))
    print("\n=== Multiple Summary Statistics ===")
    print(summary.to_string())
    print(f"\n=== Implied Valuation for {target['name']} ===")
    print(implied.to_string(index=False))
    print(f"\nOutputs written to: {OUTPUT_DIR}")


if __name__ == "__main__":
    main()
