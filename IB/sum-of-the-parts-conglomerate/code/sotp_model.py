"""
Sum-of-the-Parts (SOTP) Valuation - Meridian Industrial Group

Values a diversified industrial conglomerate by applying each business
segment's OWN peer trading multiple (rather than a single blended
multiple for the whole company), nets out capitalized corporate overhead
and net debt, and compares the resulting SOTP equity value against the
company's current single-multiple trading value to quantify the implied
"conglomerate discount" - the standard analytical basis for a spin-off
or break-up thesis.

Run:
    python sotp_model.py
"""

import os
import pandas as pd
import matplotlib.pyplot as plt

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, "data")
OUTPUT_DIR = os.path.join(BASE_DIR, "output")


def load_segments() -> pd.DataFrame:
    return pd.read_csv(os.path.join(DATA_DIR, "segments.csv"))


def load_corporate() -> dict:
    path = os.path.join(DATA_DIR, "corporate_assumptions.csv")
    df = pd.read_csv(path, index_col="Field")
    a = {k: v for k, v in df["Value"].items()}
    for k in a:
        if k != "CompanyName":
            a[k] = float(a[k])
    return a


def compute_sotp(segments: pd.DataFrame, corp: dict) -> dict:
    segments = segments.copy()
    segments["SegmentEV_mm"] = segments["EBITDA_mm"] * segments["PeerMultiple_EVEBITDA"]

    total_segment_ev = segments["SegmentEV_mm"].sum()
    corporate_overhead_value = corp["CorporateOverheadEBITDA_mm"] * corp["CorporateOverheadMultiple"]
    sotp_ev = total_segment_ev - corporate_overhead_value
    sotp_equity = sotp_ev - corp["NetDebt_mm"]
    sotp_per_share = sotp_equity / corp["SharesOutstanding_mm"]

    total_ebitda = segments["EBITDA_mm"].sum() - corp["CorporateOverheadEBITDA_mm"]
    current_ev = total_ebitda * corp["CurrentBlendedMultiple"]
    current_equity = current_ev - corp["NetDebt_mm"]
    current_per_share = current_equity / corp["SharesOutstanding_mm"]

    conglomerate_discount = (sotp_ev - current_ev) / sotp_ev
    upside_pct = sotp_per_share / current_per_share - 1

    return {
        "segments": segments, "total_segment_ev": total_segment_ev,
        "corporate_overhead_value": corporate_overhead_value, "sotp_ev": sotp_ev,
        "sotp_equity": sotp_equity, "sotp_per_share": sotp_per_share,
        "total_ebitda": total_ebitda, "current_ev": current_ev, "current_equity": current_equity,
        "current_per_share": current_per_share, "conglomerate_discount": conglomerate_discount,
        "upside_pct": upside_pct,
    }


def sensitivity_table(segments: pd.DataFrame, corp: dict) -> pd.DataFrame:
    deltas = [-1.5, -1.0, -0.5, 0.0, 0.5, 1.0, 1.5]
    table = pd.DataFrame(index=[f"{d:+.1f}x all multiples" for d in deltas], columns=["SOTP_PerShare", "Upside_pct"])
    for d in deltas:
        adj = segments.copy()
        adj["PeerMultiple_EVEBITDA"] = adj["PeerMultiple_EVEBITDA"] + d
        res = compute_sotp(adj, corp)
        table.loc[f"{d:+.1f}x all multiples", "SOTP_PerShare"] = round(res["sotp_per_share"], 2)
        table.loc[f"{d:+.1f}x all multiples", "Upside_pct"] = round(res["upside_pct"] * 100, 1)
    return table


def plot_sotp_bridge(res: dict, corp: dict):
    fig, ax = plt.subplots(figsize=(10, 6))
    segs = res["segments"]
    labels = list(segs["Segment"]) + ["Corporate\nOverhead", "SOTP\nEV", "Net\nDebt", "SOTP\nEquity"]
    values = list(segs["SegmentEV_mm"]) + [-res["corporate_overhead_value"], None, -corp["NetDebt_mm"], None]

    cumulative = 0
    bottoms, heights, colors = [], [], []
    for i, (label, val) in enumerate(zip(labels, values)):
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
    ax.set_title(f"Sum-of-the-Parts Bridge - {corp['CompanyName']}")
    plt.xticks(rotation=15, ha="right")
    fig.tight_layout()
    fig.savefig(os.path.join(OUTPUT_DIR, "sotp_bridge.png"), dpi=150)
    plt.close(fig)


def plot_sotp_vs_current(res: dict):
    fig, ax = plt.subplots(figsize=(7, 6))
    labels = ["Current Trading\n(blended multiple)", "SOTP\n(segment multiples)"]
    values = [res["current_per_share"], res["sotp_per_share"]]
    bars = ax.bar(labels, values, color=["#C0392B", "#1E8449"])
    for bar in bars:
        h = bar.get_height()
        ax.annotate(f"${h:.2f}", (bar.get_x() + bar.get_width() / 2, h), ha="center", va="bottom")
    ax.set_ylabel("Value per Share ($)")
    ax.set_title(f"Current Value vs. SOTP Value ({res['upside_pct']:.1%} upside)")
    fig.tight_layout()
    fig.savefig(os.path.join(OUTPUT_DIR, "sotp_vs_current.png"), dpi=150)
    plt.close(fig)


def main():
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    segments = load_segments()
    corp = load_corporate()

    res = compute_sotp(segments, corp)
    sens = sensitivity_table(segments, corp)

    res["segments"].round(2).to_csv(os.path.join(OUTPUT_DIR, "segment_valuations.csv"), index=False)
    sens.to_csv(os.path.join(OUTPUT_DIR, "multiple_sensitivity.csv"))

    with open(os.path.join(OUTPUT_DIR, "sotp_summary.txt"), "w") as f:
        f.write(f"Company: {corp['CompanyName']}\n\n")
        f.write("=== Segment Valuations ===\n")
        f.write(res["segments"].round(2).to_string(index=False))
        f.write(f"\n\nTotal Segment EV: ${res['total_segment_ev']:,.1f}mm\n")
        f.write(f"Less: Corporate Overhead (${corp['CorporateOverheadEBITDA_mm']:,.0f}mm EBITDA @ "
                f"{corp['CorporateOverheadMultiple']:.1f}x): -${res['corporate_overhead_value']:,.1f}mm\n")
        f.write(f"SOTP Enterprise Value: ${res['sotp_ev']:,.1f}mm\n")
        f.write(f"Less: Net Debt: -${corp['NetDebt_mm']:,.1f}mm\n")
        f.write(f"SOTP Equity Value: ${res['sotp_equity']:,.1f}mm\n")
        f.write(f"SOTP Value per Share: ${res['sotp_per_share']:.2f}\n\n")
        f.write(f"=== Current Trading (blended {corp['CurrentBlendedMultiple']:.1f}x multiple) ===\n")
        f.write(f"Current EV: ${res['current_ev']:,.1f}mm\n")
        f.write(f"Current Equity Value: ${res['current_equity']:,.1f}mm\n")
        f.write(f"Current Value per Share: ${res['current_per_share']:.2f}\n\n")
        f.write(f"Implied Conglomerate Discount: {res['conglomerate_discount']:.1%}\n")
        f.write(f"SOTP Upside vs. Current: {res['upside_pct']:.1%}\n")

    plot_sotp_bridge(res, corp)
    plot_sotp_vs_current(res)

    print(f"=== SOTP Valuation: {corp['CompanyName']} ===")
    print(res["segments"].round(2).to_string(index=False))
    print(f"\nSOTP EV: ${res['sotp_ev']:,.1f}mm  |  SOTP Equity: ${res['sotp_equity']:,.1f}mm  |  "
          f"SOTP/Share: ${res['sotp_per_share']:.2f}")
    print(f"Current EV: ${res['current_ev']:,.1f}mm  |  Current/Share: ${res['current_per_share']:.2f}")
    print(f"Implied Conglomerate Discount: {res['conglomerate_discount']:.1%}  |  "
          f"SOTP Upside: {res['upside_pct']:.1%}")
    print(f"\nOutputs written to: {OUTPUT_DIR}")


if __name__ == "__main__":
    main()
